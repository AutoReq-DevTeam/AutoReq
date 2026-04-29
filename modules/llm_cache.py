"""
modules/llm_cache.py — LLM prompt önbelleği (TTL destekli)

Aynı (system_prompt + user_prompt) çifti için tekrarlayan Gemini çağrılarını
önlemek için process içi paylaşımlı önbellek sağlar.
"""

from __future__ import annotations

import hashlib
import threading
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from modules.llm_client import LLMResponse


@dataclass
class _CacheEntry:
    """Önbellek girdisi: değer ve son geçerlilik zamanı (Unix time)."""

    value: "LLMResponse"
    expires_at: float


class LLMPromptCache:
    """
    Bellek içi prompt önbelleği; anahtar SHA-256(system_prompt + user_prompt).

    Args:
        default_ttl_seconds: Varsayılan kayıt yaşam süresi (saniye).
    """

    def __init__(self, default_ttl_seconds: int = 86400) -> None:
        self.default_ttl_seconds = default_ttl_seconds
        self._store: dict[str, _CacheEntry] = {}
        self._lock = threading.Lock()

    @staticmethod
    def make_key(system_prompt: str, user_prompt: str) -> str:
        """
        Önbellek anahtarını üretir.

        Args:
            system_prompt: Sistem istemi.
            user_prompt: Kullanıcı istemi.

        Returns:
            str: SHA-256 hex digest.
        """
        payload = f"{system_prompt}\n\n{user_prompt}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def get(self, key: str) -> Optional["LLMResponse"]:
        """
        Anahtar için geçerli bir girdi döndürür veya süresi dolmuşsa siler.

        Args:
            key: make_key ile üretilmiş anahtar.

        Returns:
            Önbellekteki LLMResponse veya None.
        """
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if time.monotonic() > entry.expires_at:
                del self._store[key]
                return None
            return entry.value

    def set(self, key: str, value: "LLMResponse", ttl_seconds: Optional[int] = None) -> None:
        """
        Önbelleğe yazar.

        Args:
            key: make_key çıktısı.
            value: Saklanacak yanıt.
            ttl_seconds: Bu kayıt için TTL; None ise varsayılan kullanılır.
        """
        ttl = self.default_ttl_seconds if ttl_seconds is None else ttl_seconds
        expires_at = time.monotonic() + float(ttl)
        with self._lock:
            self._store[key] = _CacheEntry(value=value, expires_at=expires_at)

    def clear(self) -> None:
        """Tüm girdileri temizler (testler için)."""
        with self._lock:
            self._store.clear()


_shared_cache: Optional[LLMPromptCache] = None
_shared_lock = threading.Lock()


def get_shared_prompt_cache(default_ttl_seconds: int = 86400) -> LLMPromptCache:
    """
    Process genelinde tek bir LLMPromptCache örneği döndürür.

    İlk çağrıda TTL ile oluşturulur; sonraki çağrılar aynı örneği paylaşır
    (farklı LLMClient örnekleri arasında cache tutarlılığı için).

    Args:
        default_ttl_seconds: Önbellek henüz yoksa kullanılacak TTL.

    Returns:
        LLMPromptCache: Paylaşımlı önbellek.
    """
    global _shared_cache
    with _shared_lock:
        if _shared_cache is None:
            _shared_cache = LLMPromptCache(default_ttl_seconds=default_ttl_seconds)
        return _shared_cache


def reset_shared_prompt_cache_for_tests() -> None:
    """Yalnızca testlerde paylaşımlı önbelleği sıfırlar."""
    global _shared_cache
    with _shared_lock:
        if _shared_cache is not None:
            _shared_cache.clear()
        _shared_cache = None


__all__ = ["LLMPromptCache", "get_shared_prompt_cache", "reset_shared_prompt_cache_for_tests"]
