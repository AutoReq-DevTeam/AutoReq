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
    """Token sayılarına göre tahmini USD maliyet hesaplar.

    Args:
        provider: LLM sağlayıcısı (``"gemini"`` veya ``"deepseek"``).
        input_tokens: Giriş token sayısı.
        output_tokens: Çıkış token sayısı.

    Returns:
        float: Tahmini maliyet (USD).
    """
    if provider == "deepseek":
        in_rate = 0.14
        out_rate = 0.28
    elif provider == "openrouter":
        return 0.0  # OpenRouter fiyatı modele göre değişkendir.
    else:
        in_rate = float(os.getenv("GEMINI_PRICE_INPUT_PER_MTOK", str(_DEFAULT_INPUT_PER_MTOK)))
        out_rate = float(os.getenv("GEMINI_PRICE_OUTPUT_PER_MTOK", str(_DEFAULT_OUTPUT_PER_MTOK)))
    return (input_tokens / 1_000_000.0) * in_rate + (output_tokens / 1_000_000.0) * out_rate


def _extract_usage_counts(response: Any) -> tuple[int, int]:
    """Gemini API yanıtından girdi ve çıktı token sayılarını çıkarır.

    Args:
        response: Gemini API yanıt nesnesi.

    Returns:
        tuple[int, int]: (input_tokens, output_tokens) çifti.
    """
    um = getattr(response, "usage_metadata", None)
    if um is None:
        return 0, 0
    inp = getattr(um, "prompt_token_count", None) or getattr(um, "prompt_tokens", None) or 0
    out = getattr(um, "candidates_token_count", None) or getattr(um, "candidates_tokens", None) or 0
    return int(inp), int(out)


def _build_usage_metadata(provider: str, input_tokens: int, output_tokens: int) -> Dict[str, Any]:
    """Kullanım metadatası sözlüğü oluşturur.

    Args:
        provider: LLM sağlayıcısı adı.
        input_tokens: Girdi token sayısı.
        output_tokens: Çıktı token sayısı.

    Returns:
        Dict[str, Any]: input_tokens, output_tokens, estimated_cost_usd içeren sözlük.
    """
    cost = _estimate_cost_usd(provider, input_tokens, output_tokens)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(cost, 6),
    }


def _is_retryable_gemini_error(exc: BaseException) -> bool:
    """HTTP 429 / 5xx gibi geçici Gemini hatalarını tanır.

    Args:
        exc: Yakalanan istisna.

    Returns:
        bool: True ise yeniden deneme yapılabilir.
    """
    msg = str(exc).lower()
    for fragment in ("429", "500", "502", "503", "504", "resource exhausted", "rate", "unavailable"):
        if fragment in msg:
            return True
    return False


_usage_lock = threading.Lock()
_pending_tokens: int = 0
_pending_cost: float = 0.0


def _accumulate_streamlit_session_usage(usage_metadata: Dict[str, Any]) -> None:
    """Token ve maliyet verilerini thread-safe sayaca ekler.

    Worker thread'lerden güvenle çağrılabilir. Streamlit session_state'e
    doğrudan yazmaz; flush_usage_to_session() ana thread'den çağrılmalıdır.

    Args:
        usage_metadata: input_tokens, output_tokens, estimated_cost_usd içeren sözlük.
    """
    global _pending_tokens, _pending_cost
    inp = int(usage_metadata.get("input_tokens", 0) or 0)
    out = int(usage_metadata.get("output_tokens", 0) or 0)
    cost = float(usage_metadata.get("estimated_cost_usd", 0.0) or 0.0)
    with _usage_lock:
        _pending_tokens += inp + out
        _pending_cost += cost


def flush_usage_to_session() -> None:
    """Biriken token/maliyet değerlerini Streamlit session_state'e aktarır.

    Ana thread'den (pipeline tamamlandıktan sonra) çağrılmalıdır.
    """
    global _pending_tokens, _pending_cost
    try:
        import streamlit as st  # type: ignore[import-untyped]
    except ImportError:
        return
    try:
        with _usage_lock:
            tokens = _pending_tokens
            cost = _pending_cost
            _pending_tokens = 0
            _pending_cost = 0.0
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
            if os.getenv("OPENROUTER_API_KEY"):
                self.provider = "openrouter"
            elif os.getenv("DEEPSEEK_API_KEY"):
                self.provider = "deepseek"
            else:
                self.provider = "gemini"

        if self.provider == "openrouter":
            self.model_name = model_name or os.getenv("OPENROUTER_MODEL_NAME", "deepseek/deepseek-chat")
            self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        elif self.provider == "deepseek":
            self.model_name = model_name or os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        else:
            self.model_name = model_name or os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            if self.model_name and "/" in self.model_name:
                self.model_name = self.model_name.split("/")[-1]

        self.max_output_tokens = max_output_tokens
        self.temperature = temperature

        ttl_env = os.getenv("LLM_CACHE_TTL_SECONDS")
        effective_ttl = int(ttl_env) if ttl_env is not None else cache_ttl_seconds
        self._prompt_cache = prompt_cache or get_shared_prompt_cache(default_ttl_seconds=effective_ttl)

        if not self.api_key:
            raise LLMClientError(f"{self.provider.upper()}_API_KEY tanımlı değil.")

        if self.provider == "openrouter":
            try:
                import openai
            except ImportError as exc:
                raise LLMClientError("OpenRouter için 'openai' paketi kurulu olmalı: pip install openai") from exc
            self._openai_client = openai.OpenAI(api_key=self.api_key, base_url="https://openrouter.ai/api/v1")

        elif self.provider == "deepseek":
            try:
                import openai
            except ImportError as exc:
                raise LLMClientError("DeepSeek için 'openai' paketi kurulu olmalı: pip install openai") from exc
            self._openai_client = openai.OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

        elif self.provider == "gemini":
            try:
                from google import genai as _google_genai  # type: ignore[import-not-found]
            except ImportError as exc:
                raise LLMClientError(
                    "Gemini için 'google-genai' paketi kurulu olmalı: pip install google-genai"
                ) from exc
            self._genai_client = _google_genai.Client(api_key=self.api_key)
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

        if self.provider in ("deepseek", "openrouter"):
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
            usage_meta = _build_usage_metadata(self.provider, inp, out)
            
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
            provider_name = "OpenRouter" if self.provider == "openrouter" else "DeepSeek"
            raise LLMClientError(f"{provider_name} çağrısı başarısız: {exc}") from exc

    def _chat_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        history: Optional[List[Dict[str, str]]],
        metadata: Optional[Dict[str, Any]],
        key: str,
    ) -> LLMResponse:
        try:
            from google.genai import types as _genai_types  # type: ignore[import-not-found]
        except ImportError as exc:
            raise LLMClientError("Gemini için 'google-genai' paketi gerekli.") from exc

        contents = []
        for msg in history or []:
            if msg.get("content"):
                role = "user" if msg.get("role") == "user" else "model"
                contents.append(
                    _genai_types.Content(
                        role=role,
                        parts=[_genai_types.Part(text=msg["content"])],
                    )
                )
        contents.append(
            _genai_types.Content(
                role="user",
                parts=[_genai_types.Part(text=user_prompt)],
            )
        )

        config = _genai_types.GenerateContentConfig(
            system_instruction=system_prompt or None,
            max_output_tokens=self.max_output_tokens,
            temperature=self.temperature,
        )

        backoff_seconds = [1, 2, 4]
        last_exc: Optional[BaseException] = None

        for attempt in range(len(backoff_seconds) + 1):
            try:
                if attempt > 0:
                    time.sleep(backoff_seconds[attempt - 1])

                response = self._genai_client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config,
                )

                text = getattr(response, "text", None) or ""
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

            except LLMClientError:
                raise
            except Exception as exc:
                last_exc = exc
                if not _is_retryable_gemini_error(exc) or attempt >= len(backoff_seconds):
                    raise LLMClientError(f"Gemini çağrısı başarısız oldu: {exc}") from exc

        raise LLMClientError(f"Gemini çağrısı başarısız: {last_exc}") from last_exc


__all__ = ["LLMClient", "LLMClientError", "LLMResponse"]
