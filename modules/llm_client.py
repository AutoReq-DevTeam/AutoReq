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


def _estimate_cost_usd(provider: str, input_tokens: int, output_tokens: int) -> float:
    if provider == "deepseek":
        in_rate = 0.14
        out_rate = 0.28
    else:
        in_rate = float(os.getenv("GEMINI_PRICE_INPUT_PER_MTOK", str(_DEFAULT_INPUT_PER_MTOK)))
        out_rate = float(os.getenv("GEMINI_PRICE_OUTPUT_PER_MTOK", str(_DEFAULT_OUTPUT_PER_MTOK)))
    return (input_tokens / 1_000_000.0) * in_rate + (output_tokens / 1_000_000.0) * out_rate


def _extract_usage_counts(response: Any) -> tuple[int, int]:
    um = getattr(response, "usage_metadata", None)
    if um is None:
        return 0, 0
    inp = getattr(um, "prompt_token_count", None) or getattr(um, "prompt_tokens", None) or 0
    out = getattr(um, "candidates_token_count", None) or getattr(um, "candidates_tokens", None) or 0
    return int(inp), int(out)


def _build_usage_metadata(provider: str, input_tokens: int, output_tokens: int) -> Dict[str, Any]:
    cost = _estimate_cost_usd(provider, input_tokens, output_tokens)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(cost, 6),
    }


def _is_retryable_gemini_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    for fragment in ("429", "500", "502", "503", "504", "resource exhausted", "rate", "unavailable"):
        if fragment in msg:
            return True
    return False


_usage_lock = threading.Lock()


def _accumulate_streamlit_session_usage(usage_metadata: Dict[str, Any]) -> None:
    try:
        import streamlit as st  # type: ignore[import-untyped]
    except ImportError:
        return
    try:
        if not hasattr(st, "session_state"):
            return
        inp = int(usage_metadata.get("input_tokens", 0) or 0)
        out = int(usage_metadata.get("output_tokens", 0) or 0)
        cost = float(usage_metadata.get("estimated_cost_usd", 0.0) or 0.0)
        with _usage_lock:
            if "total_tokens_used" not in st.session_state:
                st.session_state.total_tokens_used = 0
            if "total_cost_usd" not in st.session_state:
                st.session_state.total_cost_usd = 0.0
            st.session_state.total_tokens_used += inp + out
            st.session_state.total_cost_usd += cost
    except Exception:
        return


class LLMClient:
    """
    Otomatik Algılamalı (DeepSeek / Gemini) LLM İstemcisi.
    """

    def __init__(
        self,
        provider: str = "auto",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        max_output_tokens: int = 2048,
        temperature: float = 0.2,
        *,
        cache_ttl_seconds: int = 86400,
        prompt_cache: Optional[LLMPromptCache] = None,
    ) -> None:
        self.provider = provider.lower()
        if self.provider == "auto":
            if os.getenv("DEEPSEEK_API_KEY"):
                self.provider = "deepseek"
            else:
                self.provider = "gemini"

        if self.provider == "deepseek":
            self.model_name = model_name or os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        else:
            self.model_name = model_name or os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        self.max_output_tokens = max_output_tokens
        self.temperature = temperature

        ttl_env = os.getenv("LLM_CACHE_TTL_SECONDS")
        effective_ttl = int(ttl_env) if ttl_env is not None else cache_ttl_seconds
        self._prompt_cache = prompt_cache or get_shared_prompt_cache(default_ttl_seconds=effective_ttl)

        if not self.api_key:
            raise LLMClientError(f"{self.provider.upper()}_API_KEY tanımlı değil.")

        if self.provider == "deepseek":
            try:
                import openai
            except ImportError as exc:
                raise LLMClientError("DeepSeek için 'openai' paketi kurulu olmalı: pip install openai") from exc
            self._openai_client = openai.OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

        elif self.provider == "gemini":
            try:
                import google.generativeai as genai  # type: ignore[import-not-found]
            except Exception as exc:
                raise LLMClientError("Gemini için 'google-generativeai' paketi kurulu olmalı.") from exc
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)
        else:
            raise ValueError(f"Desteklenmeyen provider: {self.provider}")

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

        if self.provider == "deepseek":
            return self._chat_deepseek(system_prompt, user_prompt, history=history, metadata=metadata, key=key)
        else:
            return self._chat_gemini(system_prompt, user_prompt, history=history, metadata=metadata, key=key)

    def _chat_deepseek(
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
            usage_meta = _build_usage_metadata("deepseek", inp, out)
            
            raw = {
                "provider": "deepseek",
                "response": response.model_dump(),
                "usage_metadata": usage_meta,
                "usage": usage_meta,
            }
            llm_response = LLMResponse(content=text, raw=raw)
            self._prompt_cache.set(key, llm_response)
            _accumulate_streamlit_session_usage(usage_meta)
            return llm_response
        except Exception as exc:
            raise LLMClientError(f"DeepSeek çağrısı başarısız: {exc}") from exc

    def _chat_gemini(
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
            messages.append({"role": "user", "parts": system_prompt})
        for msg in history or []:
            if msg.get("content"):
                messages.append({"role": msg.get("role", "user"), "parts": msg["content"]})
        messages.append({"role": "user", "parts": user_prompt})

        backoff_seconds = [1, 2, 4]
        last_exc: Optional[BaseException] = None

        for attempt in range(len(backoff_seconds) + 1):
            try:
                if attempt > 0:
                    time.sleep(backoff_seconds[attempt - 1])

                chat_session = self._model.start_chat(history=messages[:-1])
                response = chat_session.send_message(
                    messages[-1]["parts"],
                    generation_config={
                        "max_output_tokens": self.max_output_tokens,
                        "temperature": self.temperature,
                    },
                )
                
                text = getattr(response, "text", None)
                if text is None and hasattr(response, "candidates"):
                    try:
                        text = response.candidates[0].content.parts[0].text
                    except Exception:
                        text = ""
                if not text:
                    raise LLMClientError("Boş yanıt döndü.")

                inp, out = _extract_usage_counts(response)
                usage_meta = _build_usage_metadata("gemini", inp, out)
                
                raw = {
                    "provider": "gemini",
                    "response": response,
                    "usage_metadata": usage_meta,
                    "usage": dict(usage_meta),
                }
                llm_response = LLMResponse(content=text, raw=raw)
                self._prompt_cache.set(key, llm_response)
                _accumulate_streamlit_session_usage(usage_meta)
                return llm_response

            except Exception as exc:
                last_exc = exc
                if not _is_retryable_gemini_error(exc) or attempt >= len(backoff_seconds):
                    raise LLMClientError(f"Gemini çağrısı başarısız oldu: {exc}") from exc

        raise LLMClientError(f"Gemini çağrısı başarısız: {last_exc}") from last_exc


__all__ = ["LLMClient", "LLMClientError", "LLMResponse"]
