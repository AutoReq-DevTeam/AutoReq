"""
modules/logging_utils.py — Modüller için ortak loglama yardımcıları
Sorumlu: Üye 2 (Akıllı Analiz Modülleri)

Açıklama:
Bu modül, AutoReq içindeki tüm analiz modülleri (conflict_detector, gap_analyzer,
improver, llm_client, vb.) için tutarlı bir loglama (logging) yapısı sağlar.

Temel hedefler:
- Tüm modüllerde aynı logger arayüzünü kullanmak
- Modül adını ve isteğe bağlı request_id / feature bilgilerini log'lara eklemek
- Geliştirme ortamında okunabilir, üretimde yapılandırılabilir bir format sağlamak
"""

from __future__ import annotations

from typing import Any, Optional

from loguru import logger


def get_module_logger(module_name: str) -> Any:
    """
    Verilen modül adı için isimlendirilmiş bir logger döndürür.

    Not:
        loguru.logger zaten global bir logger nesnesi olduğu için, burada
        esas yaptığımız şey log mesajlarına modül bilgisini standart bir
        pattern ile eklemektir.

    Örnek:
        log = get_module_logger("conflict_detector")
        log.info("Çelişki analizi başlatıldı")
    """
    # Şimdilik doğrudan global logger'ı dönüyoruz.
    # İleride format / seviye / sink yapılandırmaları burada merkezileştirilebilir.
    return logger.bind(module=module_name)


def log_with_context(
    module_name: str,
    level: str,
    message: str,
    *,
    request_id: Optional[str] = None,
    **extra: Any,
) -> None:
    """
    Modül adı ve isteğe bağlı request_id ile bağlanmış log kaydı üretir.

    Parametreler:
        module_name: Logu üreten modülün teknik adı (örn. "conflict_detector").
        level: "debug" | "info" | "warning" | "error" | "critical"
        message: Log mesajı.
        request_id: (opsiyonel) Akış / istek izlenebilirliği için benzersiz id.
        extra: (opsiyonel) Ek anahtar-değer çiftleri (örn. feature="gap_analysis").
    """
    bound = logger.bind(module=module_name)
    if request_id is not None:
        bound = bound.bind(request_id=request_id)

    if extra:
        bound = bound.bind(**extra)

    level = level.lower()
    if level == "debug":
        bound.debug(message)
    elif level == "info":
        bound.info(message)
    elif level in {"warn", "warning"}:
        bound.warning(message)
    elif level == "error":
        bound.error(message)
    elif level == "critical":
        bound.critical(message)
    else:
        bound.info(message)


__all__ = ["get_module_logger", "log_with_context"]

