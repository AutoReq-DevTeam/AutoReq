"""
modules/llm_client.py — Merkezi LLM İstemcisi
Sorumlu: Eren Eyyüpkoca

Açıklama:
Gemini ve DeepSeek modellerini projeye tek bir arabirim üzerinden bağlamak 
için merkezi istemci katmanı.
"""

from __future__ import annotations

import os
import time
import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from loguru import logger

from modules.llm_cache import LLMPromptCache, get_shared_prompt_cache

_DEFAULT_INPUT_PER_MTOK = 0.10
_DEFAULT_OUTPUT_PER_MTOK = 0.40


class LLMClientError(RuntimeError):
    """LLM istemcisi ile ilgili hata durumları için özel istisna sınıfı."""


@dataclass
class LLMResponse:
    """Merkezi cevap modeli."""

    content: str
    raw: Dict[str, Any]


def _estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    """Token sayılarına göre tahmini USD maliyet hesaplar.

    OpenRouter üzerinden kullanılan model (varsayılan deepseek-chat) baz alınarak
    maliyet hesabı yapılır (giriş: $0.14/Mtok, çıkış: $0.28/Mtok).
    """
    in_rate = 0.14
    out_rate = 0.28
    return (input_tokens / 1_000_000.0) * in_rate + (output_tokens / 1_000_000.0) * out_rate


def _build_usage_metadata(input_tokens: int, output_tokens: int) -> Dict[str, Any]:
    """Kullanım metadatası sözlüğü oluşturur."""
    cost = _estimate_cost_usd(input_tokens, output_tokens)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(cost, 6),
    }


_usage_lock = threading.Lock()
_session_usages: dict[str, dict[str, Any]] = {}
_thread_local = threading.local()


def set_thread_session_id(session_id: str) -> None:
    """Aktif iş parçacığı için Streamlit session ID'sini kaydeder."""
    _thread_local.session_id = session_id


def get_thread_session_id() -> str | None:
    """İş parçacığı için kayıtlı session ID'yi döner."""
    return getattr(_thread_local, "session_id", None)


def _get_current_session_id() -> str:
    """Mevcut Streamlit session ID'sini bulur, bulamazsa varsayılan döndürür."""
    tid = get_thread_session_id()
    if tid:
        return tid
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx and ctx.session_id:
            return ctx.session_id
    except Exception:
        pass
    return "default"


def _accumulate_streamlit_session_usage(usage_metadata: Dict[str, Any]) -> None:
    """Token ve maliyet verilerini oturum bazlı thread-safe sayaca ekler.

    Worker thread'lerden güvenle çağrılabilir. Streamlit session_state'e
    doğrudan yazmaz; flush_usage_to_session() ana thread'den çağrılmalıdır.

    Args:
        usage_metadata: input_tokens, output_tokens, estimated_cost_usd içeren sözlük.
    """
    inp = int(usage_metadata.get("input_tokens", 0) or 0)
    out = int(usage_metadata.get("output_tokens", 0) or 0)
    cost = float(usage_metadata.get("estimated_cost_usd", 0.0) or 0.0)
    session_id = _get_current_session_id()
    with _usage_lock:
        if session_id not in _session_usages:
            _session_usages[session_id] = {"tokens": 0, "cost": 0.0}
        _session_usages[session_id]["tokens"] += inp + out
        _session_usages[session_id]["cost"] += cost


def flush_usage_to_session() -> None:
    """Biriken token/maliyet değerlerini ilgili oturumun Streamlit session_state'ine aktarır.

    Ana thread'den (pipeline tamamlandıktan sonra) çağrılmalıdır.
    """
    session_id = _get_current_session_id()
    try:
        import streamlit as st  # type: ignore[import-untyped]
    except ImportError:
        return
    try:
        with _usage_lock:
            usage = _session_usages.pop(session_id, None)
        if not usage:
            return
        tokens = usage["tokens"]
        cost = usage["cost"]
        if "total_tokens_used" not in st.session_state:
            st.session_state.total_tokens_used = 0
        if "total_cost_usd" not in st.session_state:
            st.session_state.total_cost_usd = 0.0
        st.session_state.total_tokens_used += tokens
        st.session_state.total_cost_usd += cost
    except Exception:
        return


class LLMClient:
    """
    OpenRouter LLM İstemcisi.
    """

    def __init__(
        self,
        provider: str = "openrouter",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        max_output_tokens: int = 2048,
        temperature: float = 0.2,
        *,
        cache_ttl_seconds: int = 86400,
        prompt_cache: Optional[LLMPromptCache] = None,
    ) -> None:
        self.provider = "openrouter"
        self.model_name = model_name or os.getenv("OPENROUTER_MODEL_NAME", "deepseek/deepseek-chat")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")

        self.max_output_tokens = max_output_tokens
        self.temperature = temperature

        ttl_env = os.getenv("LLM_CACHE_TTL_SECONDS")
        effective_ttl = int(ttl_env) if ttl_env is not None else cache_ttl_seconds
        self._prompt_cache = prompt_cache or get_shared_prompt_cache(default_ttl_seconds=effective_ttl)

        if not self.api_key:
            raise LLMClientError("OPENROUTER_API_KEY tanımlı değil.")

        try:
            import openai
        except ImportError as exc:
            raise LLMClientError("OpenRouter için 'openai' paketi kurulu olmalı: pip install openai") from exc
        self._openai_client = openai.OpenAI(api_key=self.api_key, base_url="https://openrouter.ai/api/v1")

        logger.info(
            "LLMClient başlatıldı | provider='{}' model='{}' max_output_tokens={} temperature={}",
            self.provider,
            self.model_name,
            self.max_output_tokens,
            self.temperature,
        )

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None,
        bypass_cache: bool = False,
    ) -> LLMResponse:
        key = LLMPromptCache.make_key(system_prompt, user_prompt)

        if not bypass_cache:
            cached = self._prompt_cache.get(key)
            if cached is not None:
                meta = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "estimated_cost_usd": 0.0,
                    "cache_hit": True,
                }
                raw_out = dict(cached.raw)
                raw_out["usage_metadata"] = meta
                raw_out["usage"] = meta
                hit = LLMResponse(content=cached.content, raw=raw_out)
                _accumulate_streamlit_session_usage(meta)
                logger.debug("Önbellek isabeti | meta={}", metadata or {})
                return hit

        return self._chat_openrouter(system_prompt, user_prompt, history=history, metadata=metadata, key=key)

    def _chat_openrouter(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        history: Optional[List[Dict[str, str]]],
        metadata: Optional[Dict[str, Any]],
        key: str,
    ) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        for msg in history or []:
            if msg.get("content"):
                messages.append({"role": msg.get("role", "user"), "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = self._openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_output_tokens,
                temperature=self.temperature,
            )
            text = response.choices[0].message.content or ""
            inp = response.usage.prompt_tokens if response.usage else 0
            out = response.usage.completion_tokens if response.usage else 0
            usage_meta = _build_usage_metadata(inp, out)
            
            raw = {
                "provider": self.provider,
                "response": response.model_dump(),
                "usage_metadata": usage_meta,
                "usage": usage_meta,
            }
            llm_response = LLMResponse(content=text, raw=raw)
            self._prompt_cache.set(key, llm_response)
            _accumulate_streamlit_session_usage(usage_meta)
            return llm_response
        except Exception as exc:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                logger.warning(f"OpenRouter call failed: {exc}. Retrying directly with Google Gemini API...")
                try:
                    import openai
                    direct_client = openai.OpenAI(
                        api_key=gemini_key,
                        base_url="https://generativelanguage.googleapis.com/v1beta/"
                    )
                    
                    # Convert model name (e.g., google/gemini-2.5-flash -> gemini-2.5-flash)
                    model_to_use = self.model_name
                    if "/" in model_to_use:
                        model_to_use = model_to_use.split("/")[-1]
                    if model_to_use == "deepseek-chat":
                        model_to_use = "gemini-2.5-flash"
                        
                    response = direct_client.chat.completions.create(
                        model=model_to_use,
                        messages=messages,
                        max_tokens=self.max_output_tokens,
                        temperature=self.temperature,
                    )
                    text = response.choices[0].message.content or ""
                    inp = response.usage.prompt_tokens if response.usage else 0
                    out = response.usage.completion_tokens if response.usage else 0
                    usage_meta = _build_usage_metadata(inp, out)
                    
                    raw = {
                        "provider": "google-direct",
                        "response": response.model_dump(),
                        "usage_metadata": usage_meta,
                        "usage": usage_meta,
                    }
                    llm_response = LLMResponse(content=text, raw=raw)
                    self._prompt_cache.set(key, llm_response)
                    _accumulate_streamlit_session_usage(usage_meta)
                    return llm_response
                except Exception as gemini_exc:
                    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
                    if deepseek_key:
                        logger.warning(f"Gemini call failed: {gemini_exc}. Retrying directly with DeepSeek API...")
                        try:
                            direct_client = openai.OpenAI(
                                api_key=deepseek_key,
                                base_url="https://api.deepseek.com"
                            )
                            response = direct_client.chat.completions.create(
                                model="deepseek-chat",
                                messages=messages,
                                max_tokens=self.max_output_tokens,
                                temperature=self.temperature,
                            )
                            text = response.choices[0].message.content or ""
                            inp = response.usage.prompt_tokens if response.usage else 0
                            out = response.usage.completion_tokens if response.usage else 0
                            usage_meta = _build_usage_metadata(inp, out)
                            
                            raw = {
                                "provider": "deepseek-direct",
                                "response": response.model_dump(),
                                "usage_metadata": usage_meta,
                                "usage": usage_meta,
                            }
                            llm_response = LLMResponse(content=text, raw=raw)
                            self._prompt_cache.set(key, llm_response)
                            _accumulate_streamlit_session_usage(usage_meta)
                            return llm_response
                        except Exception as ds_exc:
                            raise LLMClientError(
                                f"All calls failed. OpenRouter: {exc}. Gemini: {gemini_exc}. DeepSeek: {ds_exc}"
                            ) from ds_exc
                    else:
                        raise LLMClientError(
                            f"Both OpenRouter and Gemini direct calls failed. OpenRouter: {exc}. Gemini: {gemini_exc}"
                        ) from gemini_exc
            else:
                raise LLMClientError(f"OpenRouter çağrısı başarısız: {exc}") from exc


__all__ = ["LLMClient", "LLMClientError", "LLMResponse", "set_thread_session_id", "get_thread_session_id"]
