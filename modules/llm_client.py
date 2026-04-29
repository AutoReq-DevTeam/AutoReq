"""
modules/llm_client.py — Merkezi LLM İstemcisi
Sorumlu: Eren Eyyüpkoca

Açıklama:
Gemini 3.0 Flash modelini (ve gerekirse diğer LLM sağlayıcılarını) projeye
tek bir arabirim üzerinden bağlamak için merkezi istemci katmanı.

Notlar:
- Bu modül sadece LLM çağrılarının teknik detayını kapsar.
- İş kuralları, prompt şablonları ve analiz mantığı ilgili modüllerde
  (örn. conflict_detector, gap_analyzer, improver) tutulmalıdır.
- API anahtarları ortam değişkenlerinden okunur; koda gömülmez.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from loguru import logger

from modules.llm_cache import LLMPromptCache, get_shared_prompt_cache

# Yaklaşık Gemini Flash fiyatlandırması (USD / 1M token); ortam değişkeni ile güncellenebilir.
_DEFAULT_INPUT_PER_MTOK = 0.10
_DEFAULT_OUTPUT_PER_MTOK = 0.40


class LLMClientError(RuntimeError):
    """LLM istemcisi ile ilgili hata durumları için özel istisna sınıfı."""


@dataclass
class LLMResponse:
    """
    Merkezi cevap modeli.

    Diğer modüller mümkün olduğunca bu sınıfa bağımlı olmalı; alttaki
    sağlayıcıya (Gemini, OpenAI, vs.) doğrudan bağımlı olmamalı.
    """

    content: str
    """Modelden dönen ham metin cevabı."""

    raw: Dict[str, Any]
    """Sağlayıcıdan dönen ham response nesnesi (debug / logging için)."""


def _estimate_gemini_flash_cost_usd(input_tokens: int, output_tokens: int) -> float:
    """
    Tahmini API maliyetini (USD) hesaplar.

    Args:
        input_tokens: Giriş token sayısı.
        output_tokens: Çıkış token sayısı.

    Returns:
        float: Tahmini toplam maliyet (USD).
    """
    in_rate = float(os.getenv("GEMINI_PRICE_INPUT_PER_MTOK", str(_DEFAULT_INPUT_PER_MTOK)))
    out_rate = float(os.getenv("GEMINI_PRICE_OUTPUT_PER_MTOK", str(_DEFAULT_OUTPUT_PER_MTOK)))
    return (input_tokens / 1_000_000.0) * in_rate + (output_tokens / 1_000_000.0) * out_rate


def _extract_usage_counts(response: Any) -> tuple[int, int]:
    """
    Gemini yanıt nesnesinden token sayılarını okur.

    Args:
        response: google-generativeai GenerateContentResponse benzeri nesne.

    Returns:
        tuple[int, int]: (input_tokens, output_tokens).
    """
    um = getattr(response, "usage_metadata", None)
    if um is None:
        return 0, 0
    inp = getattr(um, "prompt_token_count", None)
    if inp is None:
        inp = getattr(um, "prompt_tokens", None) or 0
    out = getattr(um, "candidates_token_count", None)
    if out is None:
        out = getattr(um, "candidates_tokens", None) or 0
    return int(inp or 0), int(out or 0)


def _build_usage_metadata(input_tokens: int, output_tokens: int) -> Dict[str, Any]:
    """
    LLMResponse.raw için usage_metadata / usage sözlüğünü üretir.

    Args:
        input_tokens: Giriş token sayısı.
        output_tokens: Çıkış token sayısı.

    Returns:
        dict: input_tokens, output_tokens, estimated_cost_usd alanları.
    """
    cost = _estimate_gemini_flash_cost_usd(input_tokens, output_tokens)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(cost, 6),
    }


def _is_retryable_gemini_error(exc: BaseException) -> bool:
    """
    Geçici (429 / 5xx / deadline) hataları ayırt eder.

    Args:
        exc: Yakalanan istisna.

    Returns:
        bool: Yeniden denenebilirse True.
    """
    try:
        from google.api_core import exceptions as google_exc  # type: ignore[import-not-found]

        if isinstance(
            exc,
            (
                google_exc.ResourceExhausted,
                google_exc.ServiceUnavailable,
                google_exc.InternalServerError,
                google_exc.DeadlineExceeded,
            ),
        ):
            return True
    except ImportError:
        pass

    msg = str(exc).lower()
    for fragment in ("429", "500", "502", "503", "504", "resource exhausted", "rate", "unavailable"):
        if fragment in msg:
            return True
    return False


def _accumulate_streamlit_session_usage(usage_metadata: Dict[str, Any]) -> None:
    """
    Streamlit oturumunda token ve maliyet birikimini günceller (varsa).

    Args:
        usage_metadata: input_tokens, output_tokens, estimated_cost_usd içeren sözlük.
    """
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
    Gemini 3.0 Flash tabanlı merkezi LLM istemcisi.

    Varsayılan yapılandırma:
    - Model adı: GEMINI_MODEL_NAME ortam değişkeni ya da 'gemini-3.0-flash'
    - API anahtarı: GEMINI_API_KEY ortam değişkeni
    - Önbellek TTL: LLM_CACHE_TTL_SECONDS veya 86400 (24 saat)
    """

    def __init__(
        self,
        provider: str = "gemini",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        max_output_tokens: int = 2048,
        temperature: float = 0.2,
        *,
        cache_ttl_seconds: int = 86400,
        prompt_cache: Optional[LLMPromptCache] = None,
    ) -> None:
        self.provider = provider.lower()
        self.model_name = model_name or os.getenv("GEMINI_MODEL_NAME", "gemini-3.0-flash")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature

        ttl_env = os.getenv("LLM_CACHE_TTL_SECONDS")
        effective_ttl = int(ttl_env) if ttl_env is not None else cache_ttl_seconds

        if prompt_cache is not None:
            self._prompt_cache = prompt_cache
        else:
            self._prompt_cache = get_shared_prompt_cache(default_ttl_seconds=effective_ttl)

        if self.provider != "gemini":
            raise ValueError(f"Şu an sadece 'gemini' provider'ı destekleniyor, gelen: {self.provider!r}")

        if not self.api_key:
            raise LLMClientError(
                "GEMINI_API_KEY ortam değişkeni tanımlı değil. "
                "Lütfen .env veya sistem ortam değişkenleri üzerinden ayarlayın."
            )

        try:
            import google.generativeai as genai  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - ortam bağımlı
            raise LLMClientError(
                "Gemini entegrasyonu için 'google-generativeai' paketinin kurulu olması gerekiyor. "
                "Kurulum: pip install google-generativeai"
            ) from exc

        genai.configure(api_key=self.api_key)
        self._genai = genai
        self._model = genai.GenerativeModel(self.model_name)

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
        """
        Temel sohbet/generatif çağrı metodu.

        Parametreler:
            system_prompt: Modelin genel rolünü / davranışını tanımlar.
            user_prompt: Kullanıcı veya üst katmandan gelen asıl istem.
            metadata: Loglama ve izlenebilirlik için ek meta bilgiler
                      (örn. module, feature, request_id).
            history: Önceki mesaj geçmişi; her eleman {'role', 'content'} formatında.
            bypass_cache: True ise önbellek atlanır ve doğrudan API çağrılır.

        Döndürür:
            LLMResponse: Normalleştirilmiş cevap nesnesi.
        """
        if self.provider == "gemini":
            return self._chat_gemini(
                system_prompt,
                user_prompt,
                metadata=metadata,
                history=history,
                bypass_cache=bypass_cache,
            )

        raise LLMClientError(f"Desteklenmeyen provider: {self.provider!r}")

    def _response_from_cache_hit(self, cached: LLMResponse) -> LLMResponse:
        """
        Önbellek isabeti için usage alanlarını sıfırlayan yanıt üretir.

        Args:
            cached: Önbellekteki özgün yanıt.

        Returns:
            LLMResponse: cache_hit işaretli kopya.
        """
        meta = {
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost_usd": 0.0,
            "cache_hit": True,
        }
        raw_out = dict(cached.raw)
        raw_out["usage_metadata"] = meta
        raw_out["usage"] = dict(meta)
        return LLMResponse(content=cached.content, raw=raw_out)

    def _invoke_gemini_generating(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        history: Optional[List[Dict[str, str]]],
    ) -> Any:
        """
        Tek bir Gemini API turunu çalıştırır (yeniden deneme yok).

        Args:
            system_prompt: Sistem istemi.
            user_prompt: Kullanıcı istemi.
            history: Opsiyonel mesaj geçmişi.

        Returns:
            GenerateContentResponse benzeri ham yanıt nesnesi.

        Raises:
            Exception: SDK'nın fırlattığı ham istisnalar (üst katmanda sarılır).
        """
        messages: List[Dict[str, Any]] = []

        if system_prompt:
            messages.append({"role": "user", "parts": system_prompt})

        for msg in history or []:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if not content:
                continue
            messages.append({"role": role, "parts": content})

        messages.append({"role": "user", "parts": user_prompt})

        logger.debug(
            "Gemini çağrısı yapılıyor | model='{}'",
            self.model_name,
        )

        chat_session = self._model.start_chat(history=messages[:-1])
        return chat_session.send_message(
            messages[-1]["parts"],
            generation_config={
                "max_output_tokens": self.max_output_tokens,
                "temperature": self.temperature,
            },
        )

    def _normalize_gemini_text(self, response: Any) -> str:
        """
        Gemini yanıtından metin çıkarır.

        Args:
            response: Ham SDK yanıtı.

        Returns:
            str: Model metni.

        Raises:
            LLMClientError: Metin yoksa veya boşsa.
        """
        text = getattr(response, "text", None)
        if text is None and hasattr(response, "candidates"):
            try:
                candidate = response.candidates[0]
                part = candidate.content.parts[0]
                text = getattr(part, "text", "")
            except Exception:
                text = ""

        if not text:
            raise LLMClientError("Gemini yanıtı boş döndü veya metin alanı bulunamadı.")
        return text

    def _chat_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        metadata: Optional[Dict[str, Any]],
        history: Optional[List[Dict[str, str]]],
        bypass_cache: bool,
    ) -> LLMResponse:
        """
        Önbellek, yeniden deneme ve kullanım metadatası ile Gemini çağrısı.
        """
        key = LLMPromptCache.make_key(system_prompt, user_prompt)

        if not bypass_cache:
            cached = self._prompt_cache.get(key)
            if cached is not None:
                hit = self._response_from_cache_hit(cached)
                _accumulate_streamlit_session_usage(hit.raw.get("usage_metadata", {}))
                logger.debug("Gemini önbellek isabeti | meta={}", metadata or {})
                return hit

        backoff_seconds = [1, 2, 4]
        last_exc: Optional[BaseException] = None

        for attempt in range(len(backoff_seconds) + 1):
            try:
                if attempt > 0:
                    time.sleep(backoff_seconds[attempt - 1])

                response = self._invoke_gemini_generating(
                    system_prompt,
                    user_prompt,
                    history=history,
                )
                text = self._normalize_gemini_text(response)
                inp, out = _extract_usage_counts(response)
                usage_meta = _build_usage_metadata(inp, out)
                raw: Dict[str, Any] = {
                    "provider": "gemini",
                    "response": response,
                    "usage_metadata": usage_meta,
                    "usage": dict(usage_meta),
                }
                llm_response = LLMResponse(content=text, raw=raw)

                if not bypass_cache:
                    self._prompt_cache.set(key, llm_response)

                _accumulate_streamlit_session_usage(usage_meta)

                logger.debug(
                    "Gemini cevabı alındı | chars={} tokens={}+{} meta={}",
                    len(text),
                    inp,
                    out,
                    metadata or {},
                )
                return llm_response

            except LLMClientError:
                raise
            except Exception as exc:
                last_exc = exc
                retryable = _is_retryable_gemini_error(exc)
                if not retryable or attempt >= len(backoff_seconds):
                    logger.error(
                        "Gemini çağrısı sırasında hata oluştu | model='{}' meta={} error={}",
                        self.model_name,
                        metadata or {},
                        exc,
                    )
                    raise LLMClientError(f"Gemini çağrısı başarısız oldu: {exc}") from exc
                logger.warning(
                    "Gemini geçici hata — yeniden deneniyor ({} / {}) | {}",
                    attempt + 1,
                    len(backoff_seconds),
                    exc,
                )

        raise LLMClientError(f"Gemini çağrısı başarısız oldu: {last_exc}") from last_exc


__all__ = ["LLMClient", "LLMClientError", "LLMResponse"]
