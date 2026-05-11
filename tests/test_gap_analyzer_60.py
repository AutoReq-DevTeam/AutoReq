"""60 bağımsız vaka ile gap_analyzer post-processing doğruluk testi.

Tüm vakalar deterministik (LLM çağrısı yok):
  gaps_payload_to_report_dicts  — 20 vaka
  _post_process_gaps            — 25 vaka
  _append_auth_recovery_gap     — 8 vaka
  GapAnalyzer mock entegrasyon  — 7 vaka
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from modules.analysis_report_parsing import gaps_payload_to_report_dicts
from modules.gap_analyzer import (
    GAP_CONFIDENCE_THRESHOLD,
    GapAnalyzer,
    _append_auth_recovery_gap_if_needed,
    _deduplicate_gaps,
    _post_process_gaps,
)
from core.models import ParsedDocument, Requirement


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------

def _doc(raw_text: str, *req_texts: str) -> ParsedDocument:
    reqs = [Requirement(id=f"R{i+1}", text=t) for i, t in enumerate(req_texts)]
    return ParsedDocument(raw_text=raw_text, requirements=reqs)


def _gap(
    missing_area: str,
    severity: str = "medium",
    confidence: float | None = None,
    scenario: str = "authentication",
) -> dict:
    g: dict[str, Any] = {
        "missing_area": missing_area,
        "suggestion": f"{missing_area} gereksinimi ekle.",
        "severity": severity,
        "scenario": scenario,
        "rationale": "Eksik.",
    }
    if confidence is not None:
        g["confidence"] = confidence
    return g


def _gap_payload(*gaps) -> dict:
    return {"gaps": list(gaps), "meta": {"total_gaps": len(gaps)}}


# ---------------------------------------------------------------------------
# 1) gaps_payload_to_report_dicts — 20 vaka
# ---------------------------------------------------------------------------

PARSING_CASES: list[tuple[dict, list]] = [
    # Temel dönüşüm
    (
        _gap_payload(_gap("Parola sıfırlama", confidence=0.9)),
        [{"missing_area": "Parola sıfırlama", "suggestion": "Parola sıfırlama gereksinimi ekle.",
          "severity": "medium", "scenario": "authentication", "rationale": "Eksik.",
          "confidence": 0.9}],
    ),
    # confidence yok → satırda confidence alanı olmamalı
    (
        _gap_payload(_gap("MFA")),
        [{"missing_area": "MFA", "suggestion": "MFA gereksinimi ekle.",
          "severity": "medium", "scenario": "authentication", "rationale": "Eksik."}],
    ),
    # Boş gaps
    ({"gaps": []}, []),
    # gaps anahtarı yok
    ({}, []),
    # None gaps
    ({"gaps": None}, []),
    # severity geçersiz → "medium" varsayılan
    (
        {"gaps": [{"missing_area": "Test", "suggestion": "S", "severity": "kritik"}]},
        [{"missing_area": "Test", "suggestion": "S", "severity": "medium"}],
    ),
    # severity high
    (
        {"gaps": [{"missing_area": "Güvenlik", "suggestion": "S", "severity": "high",
                   "confidence": 0.95}]},
        [{"missing_area": "Güvenlik", "suggestion": "S", "severity": "high",
          "confidence": 0.95}],
    ),
    # severity low
    (
        {"gaps": [{"missing_area": "UX", "suggestion": "S", "severity": "low",
                   "confidence": 0.6}]},
        [{"missing_area": "UX", "suggestion": "S", "severity": "low", "confidence": 0.6}],
    ),
    # id taşınmalı
    (
        {"gaps": [{"id": "G1", "missing_area": "Çıkış", "suggestion": "S",
                   "severity": "medium", "confidence": 0.8}]},
        [{"missing_area": "Çıkış", "suggestion": "S", "severity": "medium",
          "id": "G1", "confidence": 0.8}],
    ),
    # scenario taşınmalı
    (
        {"gaps": [{"missing_area": "Rate limit", "suggestion": "S", "severity": "high",
                   "scenario": "rate_limiting", "confidence": 0.85}]},
        [{"missing_area": "Rate limit", "suggestion": "S", "severity": "high",
          "scenario": "rate_limiting", "confidence": 0.85}],
    ),
    # related_standard_step taşınmalı
    (
        {"gaps": [{"missing_area": "Token yenileme", "suggestion": "S", "severity": "medium",
                   "related_standard_step": "Token refresh akışı", "confidence": 0.75}]},
        [{"missing_area": "Token yenileme", "suggestion": "S", "severity": "medium",
          "related_standard_step": "Token refresh akışı", "confidence": 0.75}],
    ),
    # rationale taşınmalı
    (
        {"gaps": [{"missing_area": "Logout", "suggestion": "S", "severity": "medium",
                   "rationale": "Belgede çıkış senaryosu yok.", "confidence": 0.7}]},
        [{"missing_area": "Logout", "suggestion": "S", "severity": "medium",
          "rationale": "Belgede çıkış senaryosu yok.", "confidence": 0.7}],
    ),
    # confidence string → float
    (
        {"gaps": [{"missing_area": "CORS", "suggestion": "S", "severity": "high",
                   "confidence": "0.88"}]},
        [{"missing_area": "CORS", "suggestion": "S", "severity": "high", "confidence": 0.88}],
    ),
    # confidence geçersiz string → alan atlanır
    (
        {"gaps": [{"missing_area": "Versioning", "suggestion": "S", "severity": "medium",
                   "confidence": "yüksek"}]},
        [{"missing_area": "Versioning", "suggestion": "S", "severity": "medium"}],
    ),
    # missing_area boş → "(tanımsız alan)"
    (
        {"gaps": [{"missing_area": "", "suggestion": "S", "severity": "medium"}]},
        [{"missing_area": "(tanımsız alan)", "suggestion": "S", "severity": "medium"}],
    ),
    # missing_area yok → "(tanımsız alan)"
    (
        {"gaps": [{"suggestion": "S", "severity": "low"}]},
        [{"missing_area": "(tanımsız alan)", "suggestion": "S", "severity": "low"}],
    ),
    # İki gap
    (
        _gap_payload(_gap("Parola", confidence=0.9), _gap("MFA", confidence=0.7)),
        [
            {"missing_area": "Parola", "suggestion": "Parola gereksinimi ekle.",
             "severity": "medium", "scenario": "authentication",
             "rationale": "Eksik.", "confidence": 0.9},
            {"missing_area": "MFA", "suggestion": "MFA gereksinimi ekle.",
             "severity": "medium", "scenario": "authentication",
             "rationale": "Eksik.", "confidence": 0.7},
        ],
    ),
    # Dict olmayan öğe → atlanmalı
    (
        {"gaps": [_gap("Parola", confidence=0.8), "bozuk", None]},
        [{"missing_area": "Parola", "suggestion": "Parola gereksinimi ekle.",
          "severity": "medium", "scenario": "authentication",
          "rationale": "Eksik.", "confidence": 0.8}],
    ),
    # confidence 0.0
    (
        {"gaps": [{"missing_area": "Test", "suggestion": "S", "severity": "low",
                   "confidence": 0.0}]},
        [{"missing_area": "Test", "suggestion": "S", "severity": "low", "confidence": 0.0}],
    ),
    # confidence 1.0
    (
        {"gaps": [{"missing_area": "Kritik", "suggestion": "S", "severity": "high",
                   "confidence": 1.0}]},
        [{"missing_area": "Kritik", "suggestion": "S", "severity": "high", "confidence": 1.0}],
    ),
]


# ---------------------------------------------------------------------------
# 2) _post_process_gaps — 25 vaka
# ---------------------------------------------------------------------------

def _row(area: str, confidence: float | None = None, sev: str = "medium") -> dict:
    r: dict[str, Any] = {"missing_area": area, "suggestion": "S", "severity": sev}
    if confidence is not None:
        r["confidence"] = confidence
    return r


POST_CASES: list[tuple[list, list]] = [
    # Temel geçen vaka (confidence ≥ 0.5)
    ([_row("Parola", 0.8)], [_row("Parola", 0.8)]),
    # confidence < 0.5 → filtrelenmeli
    ([_row("Parola", 0.4)], []),
    # Eşik tam 0.5 → geçmeli
    ([_row("Parola", 0.5)], [_row("Parola", 0.5)]),
    # confidence yok → 1.0 varsayılan → geçer
    ([_row("Parola")], [_row("Parola")]),
    # confidence 0.0 → filtrelenmeli (falsy trap)
    ([_row("Parola", 0.0)], []),
    # Boş liste
    ([], []),
    # Sıralama: düşük önce, yüksek sonra girilmiş
    (
        [_row("MFA", 0.7), _row("Parola", 0.9)],
        [_row("Parola", 0.9), _row("MFA", 0.7)],
    ),
    # Dedup: aynı missing_area → yüksek confidence kalır
    (
        [_row("Parola", 0.7), _row("Parola", 0.9)],
        [_row("Parola", 0.9)],
    ),
    # Dedup: büyük/küçük harf farkı → aynı key, dedup
    (
        [_row("parola sıfırlama", 0.8), _row("Parola Sıfırlama", 0.6)],
        [_row("parola sıfırlama", 0.8)],
    ),
    # Dedup: confidence yok → 1.0 > 0.9 → yok olan kalır
    (
        [_row("Logout", 0.9), _row("Logout")],
        [_row("Logout")],
    ),
    # Karma: filtre + dedup + sıralama
    (
        [
            _row("Parola", 0.9),
            _row("Parola", 0.7),   # dedup → atılır
            _row("MFA", 0.3),      # confidence < 0.5 → atılır
            _row("CORS", 0.75),
        ],
        [_row("Parola", 0.9), _row("CORS", 0.75)],
    ),
    # Tüm confidence < 0.5 → boş
    ([_row("A", 0.1), _row("B", 0.2)], []),
    # Üç farklı alan, doğru sıralama
    (
        [_row("C", 0.6), _row("A", 0.9), _row("B", 0.75)],
        [_row("A", 0.9), _row("B", 0.75), _row("C", 0.6)],
    ),
    # missing_area boş → ID filtresi atlanır, no_area listesine eklenir
    (
        [{"missing_area": "", "suggestion": "S", "severity": "medium", "confidence": 0.8}],
        [{"missing_area": "", "suggestion": "S", "severity": "medium", "confidence": 0.8}],
    ),
    # Tek gap, eşiğin üstünde
    ([_row("Rate limit", 0.95)], [_row("Rate limit", 0.95)]),
    # Dedup üç tekrar → en yüksek
    (
        [_row("Auth", 0.6), _row("Auth", 0.8), _row("Auth", 0.7)],
        [_row("Auth", 0.8)],
    ),
    # confidence tam 0.49 → filtrelenmeli
    ([_row("X", 0.49)], []),
    # confidence tam 0.51 → geçmeli
    ([_row("X", 0.51)], [_row("X", 0.51)]),
    # Dört gap, iki çift dedup
    (
        [_row("A", 0.9), _row("B", 0.8), _row("A", 0.6), _row("B", 0.7)],
        [_row("A", 0.9), _row("B", 0.8)],
    ),
    # Severity bilgisi korunmalı
    (
        [_row("Güvenlik", 0.85, "high"), _row("UX", 0.65, "low")],
        [_row("Güvenlik", 0.85, "high"), _row("UX", 0.65, "low")],
    ),
    # Büyük batch: 5 farklı alan
    (
        [_row("A", 0.72), _row("B", 0.88), _row("C", 0.55), _row("D", 0.91), _row("E", 0.3)],
        [_row("D", 0.91), _row("B", 0.88), _row("A", 0.72), _row("C", 0.55)],
    ),
    # Tüm geçerli, sıralanmış sonuç
    (
        [_row("X", 0.8), _row("Y", 0.9), _row("Z", 0.7)],
        [_row("Y", 0.9), _row("X", 0.8), _row("Z", 0.7)],
    ),
    # None confidence → 1.0 default; None'u geçmeli ve en üste çıkmalı
    (
        [_row("A", 0.85), _row("B")],
        [_row("B"), _row("A", 0.85)],
    ),
    # Tek eleman, filtreli
    ([_row("X", 0.1)], []),
    # Tek eleman, geçerli
    ([_row("X", 0.9)], [_row("X", 0.9)]),
]


# ---------------------------------------------------------------------------
# 3) _append_auth_recovery_gap — 8 vaka
# ---------------------------------------------------------------------------

AUTH_CASES: list[tuple[ParsedDocument, list, int]] = [
    # Gaps doluysa ekleme yapılmamalı
    (
        _doc("kullanıcı giriş yapabilmeli", "Kullanıcı giriş yapabilmeli."),
        [{"missing_area": "Mevcut gap", "suggestion": "S", "severity": "high"}],
        1,
    ),
    # Giriş var, kurtarma yok, gaps boş → eklenmeli
    (
        _doc("kullanıcı sisteme giriş yapabilmeli", "Kullanıcı giriş yapabilmeli."),
        [],
        1,
    ),
    # Giriş yok → eklenmemeli
    (
        _doc("kullanıcı rapor görüntüleyebilmeli", "Kullanıcı rapor görüntüleyebilmeli."),
        [],
        0,
    ),
    # Giriş var + kurtarma var → eklenmemeli
    (
        _doc("kullanıcı giriş yapabilmeli şifre sıfırla"),
        [],
        0,
    ),
    # "login" marker
    (
        _doc("user can login to the system"),
        [],
        1,
    ),
    # "oturum" marker
    (
        _doc("oturum açma ekranı bulunmalıdır"),
        [],
        1,
    ),
    # "mfa" marker (kurtarma var) → eklenmemeli
    (
        _doc("kullanıcı giriş yapabilmeli mfa zorunlu olmalı"),
        [],
        0,
    ),
    # "iki faktör" marker (kurtarma var) → eklenmemeli
    (
        _doc("kullanıcı giriş iki faktör doğrulama"),
        [],
        0,
    ),
]


# ---------------------------------------------------------------------------
# 4) GapAnalyzer mock entegrasyon — 7 vaka
# ---------------------------------------------------------------------------

def _make_analyzer(llm_response: str) -> GapAnalyzer:
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.content = llm_response
    mock_client.chat.return_value = mock_resp
    return GapAnalyzer(llm_client=mock_client)


INTEGRATION_CASES: list[tuple[str, str, int]] = [
    # (LLM JSON, raw_text, beklenen gap sayısı)
    # Yüksek confidence → geçer
    (
        '{"gaps": [{"missing_area": "Parola sıfırlama", "suggestion": "S",'
        '"severity": "high", "confidence": 0.9}], "meta": {"system_type": "web_app"}}',
        "kullanıcı giriş yapabilmeli",
        1,
    ),
    # confidence < 0.5 → filtrelenir, 0 gap
    (
        '{"gaps": [{"missing_area": "UX iyileştirme", "suggestion": "S",'
        '"severity": "low", "confidence": 0.3}], "meta": {"system_type": "web_app"}}',
        "kullanıcı rapor görebilmeli",
        0,
    ),
    # Duplikat gap → 1 kalır
    (
        '{"gaps": ['
        '{"missing_area": "MFA", "suggestion": "S", "severity": "high", "confidence": 0.8},'
        '{"missing_area": "MFA", "suggestion": "S", "severity": "high", "confidence": 0.65}'
        '], "meta": {"system_type": "web_app"}}',
        "kullanıcı rapor görebilmeli",
        1,
    ),
    # Boş gaps + giriş var → auth recovery eklenir
    (
        '{"gaps": [], "meta": {"system_type": "web_app"}}',
        "kullanıcı giriş yapabilmeli",
        1,
    ),
    # Boş requirements → analyze() 0 döner
    ("", "", 0),
    # Markdown fenced JSON
    (
        '```json\n{"gaps": [{"missing_area": "Rate limiting", "suggestion": "S",'
        '"severity": "high", "confidence": 0.85}], "meta": {"system_type": "api"}}\n```',
        "API endpoint token ile korunmalı",
        1,
    ),
    # system_type = "api" → gap geçerli
    (
        '{"gaps": [{"missing_area": "Token iptali", "suggestion": "S",'
        '"severity": "medium", "confidence": 0.75}], "meta": {"system_type": "api"}}',
        "API token ile kimlik doğrulama yapılmalı",
        1,
    ),
]


# ---------------------------------------------------------------------------
# Çalıştırıcı
# ---------------------------------------------------------------------------

def run():
    total = 0
    failures = []

    # --- 1) gaps_payload_to_report_dicts ---
    print("=== gaps_payload_to_report_dicts — 20 vaka ===")
    for i, (payload, expected) in enumerate(PARSING_CASES, 1):
        total += 1
        result = gaps_payload_to_report_dicts(payload)
        ok = result == expected
        mark = "OK" if ok else "XX"
        print(f"{mark} {i:2} gaps={len(payload.get('gaps') or [])} → {len(result)} satır")
        if not ok:
            failures.append(("PARSE", i, payload, result, expected))

    # --- 2) _post_process_gaps ---
    print("\n=== _post_process_gaps — 25 vaka ===")
    for i, (rows, expected) in enumerate(POST_CASES, 1):
        total += 1
        result = _post_process_gaps(rows)
        ok = result == expected
        mark = "OK" if ok else "XX"
        confs = [r.get("confidence", "?") for r in rows]
        print(f"{mark} {i:2} girdi={len(rows)} conf={confs} → {len(result)} kaldı")
        if not ok:
            failures.append(("POST", i, rows, result, expected))

    # --- 3) _append_auth_recovery_gap ---
    print("\n=== _append_auth_recovery_gap_if_needed — 8 vaka ===")
    for i, (doc, gaps, expected_count) in enumerate(AUTH_CASES, 1):
        total += 1
        result = _append_auth_recovery_gap_if_needed(doc, gaps)
        ok = len(result) == expected_count
        mark = "OK" if ok else "XX"
        print(f"{mark} {i:2} raw_text='{doc.raw_text[:40]}' gaps_in={len(gaps)} → {len(result)} gap")
        if not ok:
            failures.append(("AUTH", i, doc.raw_text[:60], len(result), expected_count))

    # --- 4) GapAnalyzer entegrasyon ---
    print("\n=== GapAnalyzer mock entegrasyon — 7 vaka ===")
    for i, (llm_json, raw_text, expected_count) in enumerate(INTEGRATION_CASES, 1):
        total += 1
        try:
            if not raw_text:
                analyzer = GapAnalyzer()
                doc = ParsedDocument(raw_text="", requirements=[])
            else:
                analyzer = _make_analyzer(llm_json)
                doc = _doc(raw_text, raw_text)
            result = analyzer.analyze(doc)
            got_count = len(result)
            ok = got_count == expected_count
        except Exception as e:
            ok = False
            got_count = f"HATA: {e}"
        mark = "OK" if ok else "XX"
        print(f"{mark} {i:2} raw='{raw_text[:35]}' → gaps={got_count} (beklenen={expected_count})")
        if not ok:
            failures.append(("INTEG", i, llm_json[:60], got_count, expected_count))

    # --- Özet ---
    passed = total - len(failures)
    pct = passed / total * 100
    print(f"\nDoğruluk: {passed}/{total} = %{pct:.1f}")
    if failures:
        print(f"\nBaşarısız ({len(failures)}):")
        for group, i, inp, got, exp in failures:
            print(f"  [{group}#{i}]")
            print(f"    got = {got!r}")
            print(f"    exp = {exp!r}")


if __name__ == "__main__":
    run()
