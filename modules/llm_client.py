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

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import os

from loguru import logger


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


class LLMClient:
    """
    Gemini 3.0 Flash tabanlı merkezi LLM istemcisi.

    Kullanım (örnek):

    ```python
    from modules.llm_client import LLMClient

    client = LLMClient()  # Varsayılan: Gemini 3.0 Flash
    resp = client.chat(
        system_prompt="Kısa ve net gerekçeler ver.",
        user_prompt="Bu iki gereksinim arasında çelişki var mı?",
        metadata={"module": "conflict_detector"},
    )
    print(resp.content)
    ```

    Varsayılan yapılandırma:
    - Model adı: GEMINI_MODEL_NAME ortam değişkeni ya da 'gemini-3.0-flash'
    - API anahtarı: GEMINI_API_KEY ortam değişkeni
    """

    def __init__(
        self,
        provider: str = "gemini",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        max_output_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> None:
        self.provider = provider.lower()
        self.model_name = model_name or os.getenv("GEMINI_MODEL_NAME", "gemini-3.0-flash")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature

        if self.provider != "gemini":
            raise ValueError(f"Şu an sadece 'gemini' provider'ı destekleniyor, gelen: {self.provider!r}")

        if not self.api_key:
            raise LLMClientError(
                "GEMINI_API_KEY ortam değişkeni tanımlı değil. "
                "Lütfen .env veya sistem ortam değişkenleri üzerinden ayarlayın."
            )

        # Lazy import: Modul yüklenmezse proje yine de çalışsın, hata ancak ilk çağrıda alınsın.
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
    ) -> LLMResponse:
        """
        Temel sohbet/generatif çağrı metodu.

        Parametreler:
            system_prompt: Modelin genel rolünü / davranışını tanımlar.
            user_prompt: Kullanıcı veya üst katmandan gelen asıl istem.
            metadata: Loglama ve izlenebilirlik için ek meta bilgiler
                      (örn. module, feature, request_id).
            history: Önceki mesaj geçmişi; her eleman {'role', 'content'} formatında.

        Döndürür:
            LLMResponse: Normalleştirilmiş cevap nesnesi.
        """
        if self.provider == "gemini":
            return self._chat_gemini(system_prompt, user_prompt, metadata=metadata, history=history)

        # Gelecekte başka provider eklenirse buraya dallanır.
        raise LLMClientError(f"Desteklenmeyen provider: {self.provider!r}")

    # -------------------------------------------------------------------------
    # ÖZEL (provider-spesifik) UYGULAMALAR
    # -------------------------------------------------------------------------
    def _chat_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        metadata: Optional[Dict[str, Any]],
        history: Optional[List[Dict[str, str]]],
    ) -> LLMResponse:
        """
        Gemini 3.0 Flash üzerinden sohbet/generatif çağrı.
        """
        # Gemini için mesaj sıralaması:
        # - Önce sistem prompt, ardından varsa geçmiş, en sonda güncel kullanıcı mesajı.
        messages: List[Dict[str, str]] = []

        if system_prompt:
            messages.append({"role": "user", "parts": system_prompt})

        for msg in history or []:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if not content:
                continue
            messages.append({"role": role, "parts": content})

        messages.append({"role": "user", "parts": user_prompt})

        genai = self._genai

        try:
            logger.debug(
                "Gemini çağrısı yapılıyor | model='{}' meta={}",
                self.model_name,
                metadata or {},
            )

            chat_session = self._model.start_chat(history=messages[:-1])
            response = chat_session.send_message(
                messages[-1]["parts"],
                generation_config={
                    "max_output_tokens": self.max_output_tokens,
                    "temperature": self.temperature,
                },
            )

            # google-generativeai 3.x çıktı yapısına göre, text içeriğini normalize et
            text = getattr(response, "text", None)
            if text is None and hasattr(response, "candidates"):
                # Yedek yol: bazı sürümlerde candidates[0].content.parts[0].text yapısı kullanılabiliyor
                try:
                    candidate = response.candidates[0]
                    part = candidate.content.parts[0]
                    text = getattr(part, "text", "")  # type: ignore[assignment]
                except Exception:  # pragma: no cover - sürüm farkları
                    text = ""

            if not text:
                raise LLMClientError("Gemini yanıtı boş döndü veya metin alanı bulunamadı.")

            logger.debug(
                "Gemini cevabı alındı | chars={} meta={}",
                len(text),
                metadata or {},
            )

            return LLMResponse(content=text, raw={"provider": "gemini", "response": response})
        except Exception as exc:  # pragma: no cover - dış servis bağımlı
            logger.error(
                "Gemini çağrısı sırasında hata oluştu | model='{}' meta={} error={}",
                self.model_name,
                metadata or {},
                exc,
            )
            raise LLMClientError(f"Gemini çağrısı başarısız oldu: {exc}") from exc


__all__ = ["LLMClient", "LLMClientError", "LLMResponse"]

