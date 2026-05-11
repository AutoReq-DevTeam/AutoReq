"""
tests/test_improver_60.py — RequirementImprover 60 Vaka Testi
LLM çağrısı yapılmaz; tüm LLM etkileşimi mock LLMClient ile simüle edilir.

Bölümler:
  A (20 vaka) — _text_has_vague_keyword / _detected_vague_terms (kelime sınırı, İngilizce, Türkçe)
  B (20 vaka) — improve() tek gereksinim (payload ayrıştırma, alan çıkarma, fallback)
  C (12 vaka) — improve_batch() toplu işlem (ID eşleme, eksik ID, hata yönetimi)
  D (8 vaka)  — Kenar durumlar (boş metin, muğlak kelime yok, LLM hatası, vb.)
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

from core.models import Requirement
from modules.improver import (
    RequirementImprover,
    _detected_vague_terms,
    _text_has_vague_keyword,
    vague_keywords,
)
from modules.llm_client import LLMClientError


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------

def _req(text: str, req_id: str = "R1") -> Requirement:
    return Requirement(id=req_id, text=text, req_type="FUNCTIONAL")


def _mock_client(content: str) -> MagicMock:
    """LLMClient.chat() her çağrıda verilen içeriği döndürür."""
    client = MagicMock()
    resp = MagicMock()
    resp.content = content
    client.chat.return_value = resp
    return client


def _mock_client_error() -> MagicMock:
    """LLMClient.chat() her çağrıda LLMClientError fırlatır."""
    client = MagicMock()
    client.chat.side_effect = LLMClientError("test error")
    return client


def _single_payload(improved: str, reason: str, feasibility: str = "", vague_terms: list | None = None) -> str:
    d: dict[str, Any] = {"improved": improved, "reason": reason}
    if feasibility:
        d["feasibility"] = feasibility
    if vague_terms is not None:
        d["vague_terms"] = vague_terms
    return json.dumps(d)


def _batch_payload(items: list[dict]) -> str:
    return json.dumps(items)


# ---------------------------------------------------------------------------
# BÖLÜM A — _text_has_vague_keyword / _detected_vague_terms (20 vaka)
# ---------------------------------------------------------------------------

KEYWORD_CASES: list[tuple[str, bool, str]] = [
    # (metin, beklenen_has_vague, açıklama)
    # Temel Türkçe eşleşmeler
    ("Sistem hızlı çalışmalıdır.", True, "hızlı"),
    ("Arayüz kolay olmalı.", True, "kolay"),
    ("Uygulama güvenli olmalı.", True, "güvenli"),
    ("Platform modern görünmeli.", True, "modern"),
    ("Yazılım esnek tasarlanmalı.", True, "esnek"),
    ("Sistem ölçeklenebilir olmalıdır.", True, "ölçeklenebilir"),
    ("Kod verimli yazılmalıdır.", True, "verimli"),
    ("Kullanıcı dostu bir arayüz sunulmalı.", True, "kullanıcı dostu"),
    # İngilizce eşleşmeler
    ("The system must be fast.", True, "fast (English)"),
    ("API should be secure.", True, "secure (English)"),
    ("Platform must be scalable.", True, "scalable (English)"),
    ("UI must be responsive.", True, "responsive (English)"),
    ("System must be efficient.", True, "efficient (English)"),
    ("Service must be robust.", True, "robust (English)"),
    # Kelime sınırı — false positive önleme
    ("Ekip iyileştirme çalışması yaptı.", False, "'iyi' → 'iyileştirme' içinde olmamalı"),
    ("Kolaylaştırma süreci başladı.", False, "'kolay' → 'kolaylaştırma' içinde olmamalı"),
    ("Büyüklük önemlidir.", False, "'büyük' → 'büyüklük' içinde olmamalı"),
    # Gerçek negatifler (muğlak kelime yok)
    ("Kullanıcı sisteme kayıt olabilmelidir.", False, "kayıt akışı — vague yok"),
    ("Rapor PDF formatında dışa aktarılabilmeli.", False, "format belirtilmiş — vague yok"),
    ("API, JWT ile kimlik doğrulaması yapmalıdır.", False, "teknik ifade — vague yok"),
]


def run_keyword_tests() -> tuple[int, int, list]:
    passed = total = 0
    failures = []
    print("=== _text_has_vague_keyword — 20 vaka ===")
    for i, (text, expected, note) in enumerate(KEYWORD_CASES, 1):
        total += 1
        got = _text_has_vague_keyword(text)
        ok = got == expected
        if ok:
            passed += 1
            print(f"OK {i:2d} {note!r}")
        else:
            print(f"XX {i:2d} {note!r}")
            print(f"       metin={text!r}")
            print(f"       got={got} beklenen={expected}")
            failures.append(("KW", i, note, got, expected))
    return passed, total, failures


# ---------------------------------------------------------------------------
# BÖLÜM B — improve() tek gereksinim (20 vaka)
# ---------------------------------------------------------------------------

def run_improve_single_tests() -> tuple[int, int, list]:
    passed = total = 0
    failures = []
    print("\n=== improve() tek gereksinim — 20 vaka ===")

    cases: list[tuple[str, dict, dict, str]] = []

    # B1 — Temel iyileştirme, tüm alanlar mevcut
    cases.append((
        "Sistem hızlı çalışmalı.",
        _mock_client(_single_payload(
            "Sistem p95 yanıt süresi 200 ms altında olmalı.",
            "Hız belirsizliği yanıt süresiyle somutlaştırıldı.",
            "200 ms standart CDN altyapısında gerçekçidir.",
            ["hızlı"],
        )),
        {"improved": "Sistem p95 yanıt süresi 200 ms altında olmalı.",
         "reason": "Hız belirsizliği yanıt süresiyle somutlaştırıldı.",
         "feasibility": "200 ms standart CDN altyapısında gerçekçidir.",
         "vague_terms": ["hızlı"]},
        "tam payload",
    ))

    # B2 — feasibility alanı yok → sonuçta feasibility anahtarı olmamalı
    cases.append((
        "Arayüz kolay olmalı.",
        _mock_client(_single_payload(
            "Temel akış 120 sn içinde tamamlanabilmeli.",
            "Kolaylık, süreye indirgendi.",
            vague_terms=["kolay"],
        )),
        {"improved": "Temel akış 120 sn içinde tamamlanabilmeli.",
         "reason": "Kolaylık, süreye indirgendi.",
         "vague_terms": ["kolay"]},
        "feasibility yok",
    ))

    # B3 — vague_terms LLM tarafından döndürülmemiş → modül kendi tespit eder
    cases.append((
        "Sistem güvenli olmalı.",
        _mock_client(_single_payload(
            "Tüm veri TLS 1.2+ ile iletilmeli.",
            "Güvenlik, protokol sürümüyle netleştirildi.",
        )),
        {"improved": "Tüm veri TLS 1.2+ ile iletilmeli.",
         "vague_terms": ["güvenli"]},
        "vague_terms LLM'den gelmiyor, modül tespit ediyor",
    ))

    # B4 — improved boş string → original ile doldurulmalı
    cases.append((
        "Sistem hızlı olmalı.",
        _mock_client(json.dumps({"improved": "", "reason": "test"})),
        {"improved": "Sistem hızlı olmalı.", "vague_terms": ["hızlı"]},
        "improved boş → original fallback",
    ))

    # B5 — reason boş string → fallback mesajı
    cases.append((
        "Uygulama kolay kullanılmalı.",
        _mock_client(json.dumps({"improved": "Görev 2 denemede tamamlanmalı.", "reason": ""})),
        {"reason": "(Açıklama yok.)"},
        "reason boş → fallback",
    ))

    # B6 — JSON etrafında markdown code block
    cases.append((
        "API hızlı yanıt vermeli.",
        _mock_client("```json\n" + _single_payload(
            "API p99 yanıt süresi 500 ms altında olmalı.",
            "Hız somutlaştırıldı.",
            vague_terms=["hızlı"],
        ) + "\n```"),
        {"improved": "API p99 yanıt süresi 500 ms altında olmalı."},
        "markdown code block",
    ))

    # B7 — vague_terms listede birden fazla kelime
    cases.append((
        "Sistem hızlı ve kolay olmalı.",
        _mock_client(_single_payload(
            "Sistem p95 200 ms; görev 60 sn tamamlanmalı.",
            "İkisi de somutlaştırıldı.",
            vague_terms=["hızlı", "kolay"],
        )),
        {"vague_terms": ["hızlı", "kolay"]},
        "birden fazla vague_term",
    ))

    # B8 — LLM JSON olmayan çıktı → ValueError → fallback (original döner, reason hata içerir)
    cases.append((
        "Sistem hızlı olmalı.",
        _mock_client("Bu JSON değil."),
        {"improved": "Sistem hızlı olmalı."},
        "geçersiz JSON → fallback original",
    ))

    # B9 — feasibility dolu → sonuçta yer almalı
    cases.append((
        "Yazılım esnek olmalı.",
        _mock_client(_single_payload(
            "Yazılım plugin mimarisi ile genişletilebilmeli.",
            "Esneklik, plugin API ile somutlaştırıldı.",
            "Plugin API tasarımı 2 sprint içinde tamamlanabilir.",
            ["esnek"],
        )),
        {"feasibility": "Plugin API tasarımı 2 sprint içinde tamamlanabilir."},
        "feasibility dolu",
    ))

    # B10 — İngilizce muğlak kelime
    cases.append((
        "The API must be fast.",
        _mock_client(_single_payload(
            "API p95 response time must stay under 300 ms.",
            "'fast' replaced with numeric latency target.",
            vague_terms=["fast"],
        )),
        {"vague_terms": ["fast"]},
        "İngilizce 'fast' tespiti",
    ))

    # B11 — vague_terms LLM string döndürdü (list değil) → yok sayılmalı, modül tespit eder
    cases.append((
        "Sistem güvenli ve hızlı olmalı.",
        _mock_client(json.dumps({
            "improved": "TLS + p95 200 ms.",
            "reason": "İkisi somutlaştırıldı.",
            "vague_terms": "güvenli, hızlı",  # list değil → geçersiz
        })),
        {"vague_terms": ["güvenli", "hızlı"]},
        "vague_terms string → geçersiz → modül tespit eder",
    ))

    # B12 — scalable (İngilizce) tespit
    cases.append((
        "Platform must be scalable.",
        _mock_client(_single_payload(
            "Platform must handle 10,000 concurrent users without degradation.",
            "'scalable' quantified with concurrent user target.",
            vague_terms=["scalable"],
        )),
        {"vague_terms": ["scalable"]},
        "İngilizce 'scalable' tespiti",
    ))

    # B13 — original metinde muğlak kelime → vague_terms modül tarafından doldurulur
    cases.append((
        "Kullanıcı dostu bir arayüz sunulmalı.",
        _mock_client(_single_payload(
            "Temel görev akışı, ilk kez kullanan kullanıcı tarafından 90 sn içinde tamamlanabilmeli.",
            "Kullanıcı dostu ifadesi, ölçülebilir görev süresine indirgendi.",
        )),
        {"vague_terms": ["kullanıcı dostu"]},
        "çok kelimeli vague term tespiti",
    ))

    # B14 — "iyi" → false positive yok: "iyileştirme" metni
    cases.append((
        "Sistem iyileştirme süreci yönetilmeli.",
        None,  # LLM çağrılmamalı
        {"improved": "Sistem iyileştirme süreci yönetilmeli.", "reason": None},
        "'iyi' kelime sınırı — iyileştirme'yi eşleştirmemeli",
    ))

    # B15 — "kolay" → false positive yok: "kolaylaştırma"
    cases.append((
        "Kolaylaştırma adımları belgelenmeli.",
        None,
        {"improved": "Kolaylaştırma adımları belgelenmeli."},
        "'kolay' kelime sınırı — kolaylaştırma'yı eşleştirmemeli",
    ))

    # B16 — "verimli" tespiti
    cases.append((
        "Algoritma verimli çalışmalıdır.",
        _mock_client(_single_payload(
            "Algoritma 10.000 kayıt için CPU kullanımı %20 altında kalmalıdır.",
            "Verimlilik, CPU kullanım yüzdesiyle somutlaştırıldı.",
            vague_terms=["verimli"],
        )),
        {"vague_terms": ["verimli"]},
        "verimli tespiti",
    ))

    # B17 — "stabil" tespiti
    cases.append((
        "Sistem stabil çalışmalıdır.",
        _mock_client(_single_payload(
            "Sistem 99.9% uptime SLA ile çalışmalıdır.",
            "Stabilite, uptime SLA ile somutlaştırıldı.",
            vague_terms=["stabil"],
        )),
        {"vague_terms": ["stabil"]},
        "stabil tespiti",
    ))

    # B18 — "robust" (İngilizce) tespiti
    cases.append((
        "System must be robust.",
        _mock_client(_single_payload(
            "System must recover from failures within 30 seconds.",
            "'robust' replaced with recovery time target.",
            vague_terms=["robust"],
        )),
        {"vague_terms": ["robust"]},
        "İngilizce robust tespiti",
    ))

    # B19 — user-friendly (çizgili) tespiti
    cases.append((
        "The UI must be user-friendly.",
        _mock_client(_single_payload(
            "Core task must be completable by a new user in under 90 seconds.",
            "'user-friendly' replaced with task completion metric.",
            vague_terms=["user-friendly"],
        )),
        {"vague_terms": ["user-friendly"]},
        "user-friendly tespiti",
    ))

    # B20 — muğlak kelime yok → LLM çağrılmaz, orijinal döner
    cases.append((
        "Kullanıcı e-posta ile kayıt olabilmeli.",
        None,
        {"improved": "Kullanıcı e-posta ile kayıt olabilmeli."},
        "muğlak kelime yok → LLM çağrılmaz",
    ))

    for i, (text, client, expected_subset, note) in enumerate(cases, 1):
        total += 1
        req = _req(text)
        if client is None:
            improver = RequirementImprover(llm_client=_mock_client("{}"))
        else:
            improver = RequirementImprover(llm_client=client)
        result = improver.improve(req)

        ok = True
        fail_details = []
        for key, exp_val in expected_subset.items():
            if key == "reason" and exp_val is None:
                # LLM çağrılmadıysa reason = _NO_VAGUE_REASON içermelidir
                if "muğlak anahtar" not in result.get("reason", ""):
                    ok = False
                    fail_details.append(f"reason should indicate no vague keyword, got={result.get('reason')!r}")
            elif key == "vague_terms":
                got_terms = set(result.get("vague_terms") or [])
                exp_terms = set(exp_val)
                if not exp_terms.issubset(got_terms):
                    ok = False
                    fail_details.append(f"vague_terms: got={got_terms} exp_subset={exp_terms}")
            elif key in result:
                if result[key] != exp_val:
                    ok = False
                    fail_details.append(f"{key}: got={result[key]!r} exp={exp_val!r}")
            else:
                if exp_val is not None:
                    ok = False
                    fail_details.append(f"key '{key}' missing from result")

        if ok:
            passed += 1
            print(f"OK {i:2d} {note!r}")
        else:
            print(f"XX {i:2d} {note!r}")
            for d in fail_details:
                print(f"       {d}")
            failures.append(("SINGLE", i, note, fail_details))

    return passed, total, failures


# ---------------------------------------------------------------------------
# BÖLÜM C — improve_batch() (12 vaka)
# ---------------------------------------------------------------------------

def run_improve_batch_tests() -> tuple[int, int, list]:
    passed = total = 0
    failures = []
    print("\n=== improve_batch() — 12 vaka ===")

    # C1 — Tek muğlak gereksinim
    def c1():
        reqs = [_req("Sistem hızlı olmalı.", "R1")]
        payload = _batch_payload([{"req_id": "R1", "improved": "p95 200 ms.", "reason": "Hız somutlaştırıldı.", "vague_terms": ["hızlı"]}])
        improver = RequirementImprover(llm_client=_mock_client(payload))
        res = improver.improve_batch(reqs)
        return len(res) == 1 and res[0]["improved"] == "p95 200 ms." and "hızlı" in (res[0].get("vague_terms") or [])

    # C2 — Muğlak olmayan gereksinim → LLM çağrılmaz, orijinal döner
    def c2():
        reqs = [_req("Kullanıcı kayıt olabilmeli.", "R1")]
        improver = RequirementImprover(llm_client=_mock_client("[]"))
        res = improver.improve_batch(reqs)
        return len(res) == 1 and res[0]["improved"] == "Kullanıcı kayıt olabilmeli."

    # C3 — Karışık liste: 1 muğlak, 1 muğlak değil
    def c3():
        reqs = [_req("Sistem hızlı olmalı.", "R1"), _req("Kullanıcı giriş yapabilmeli.", "R2")]
        payload = _batch_payload([{"req_id": "R1", "improved": "p95 200 ms.", "reason": "Hız.", "vague_terms": ["hızlı"]}])
        improver = RequirementImprover(llm_client=_mock_client(payload))
        res = improver.improve_batch(reqs)
        return (len(res) == 2
                and res[0]["improved"] == "p95 200 ms."
                and res[1]["improved"] == "Kullanıcı giriş yapabilmeli.")

    # C4 — LLM yanıtında bir req_id eksik → eksik için original döner
    def c4():
        reqs = [_req("Sistem hızlı olmalı.", "R1"), _req("API kolay entegre olmalı.", "R2")]
        payload = _batch_payload([{"req_id": "R1", "improved": "p95 200 ms.", "reason": "Hız.", "vague_terms": ["hızlı"]}])
        improver = RequirementImprover(llm_client=_mock_client(payload))
        res = improver.improve_batch(reqs)
        return len(res) == 2 and res[1]["improved"] == "API kolay entegre olmalı."

    # C5 — Boş liste → boş sonuç
    def c5():
        improver = RequirementImprover(llm_client=_mock_client("[]"))
        res = improver.improve_batch([])
        return res == []

    # C6 — LLM geçersiz JSON döndürür → ValueError → her muğlak req için original döner
    def c6():
        reqs = [_req("Sistem hızlı olmalı.", "R1")]
        improver = RequirementImprover(llm_client=_mock_client("Bu JSON değil."))
        res = improver.improve_batch(reqs)
        return len(res) == 1 and res[0]["improved"] == "Sistem hızlı olmalı."

    # C7 — LLM hatası (exception) → fallback
    def c7():
        reqs = [_req("Sistem kolay kullanılmalı.", "R1")]
        improver = RequirementImprover(llm_client=_mock_client_error())
        res = improver.improve_batch(reqs)
        return len(res) == 1 and res[0]["improved"] == "Sistem kolay kullanılmalı."

    # C8 — feasibility alanı batch yanıtta mevcut → aktarılır
    def c8():
        reqs = [_req("Sistem hızlı olmalı.", "R1")]
        payload = _batch_payload([{
            "req_id": "R1",
            "improved": "p95 200 ms.",
            "reason": "Hız.",
            "feasibility": "Gerçekçi eşik.",
            "vague_terms": ["hızlı"],
        }])
        improver = RequirementImprover(llm_client=_mock_client(payload))
        res = improver.improve_batch(reqs)
        return len(res) == 1 and res[0].get("feasibility") == "Gerçekçi eşik."

    # C9 — Sıralama korunur: LLM farklı sırada döndürmüş olsa bile
    def c9():
        reqs = [_req("Sistem hızlı olmalı.", "R1"), _req("API kolay olmalı.", "R2")]
        payload = _batch_payload([
            {"req_id": "R2", "improved": "Görev 60 sn.", "reason": "Kolay.", "vague_terms": ["kolay"]},
            {"req_id": "R1", "improved": "p95 200 ms.", "reason": "Hız.", "vague_terms": ["hızlı"]},
        ])
        improver = RequirementImprover(llm_client=_mock_client(payload))
        res = improver.improve_batch(reqs)
        return res[0]["improved"] == "p95 200 ms." and res[1]["improved"] == "Görev 60 sn."

    # C10 — İngilizce muğlak kelime batch'te tanınır
    def c10():
        reqs = [_req("API must be fast.", "R1")]
        payload = _batch_payload([{"req_id": "R1", "improved": "API p95 < 300 ms.", "reason": "fast → latency.", "vague_terms": ["fast"]}])
        improver = RequirementImprover(llm_client=_mock_client(payload))
        res = improver.improve_batch(reqs)
        return len(res) == 1 and res[0]["improved"] == "API p95 < 300 ms."

    # C11 — Tümü muğlak değil → LLM hiç çağrılmaz (mock çağrılmasa da OK)
    def c11():
        reqs = [
            _req("Kullanıcı giriş yapabilmeli.", "R1"),
            _req("Rapor PDF olarak dışa aktarılabilmeli.", "R2"),
        ]
        improver = RequirementImprover(llm_client=_mock_client("[]"))
        res = improver.improve_batch(reqs)
        return (len(res) == 2
                and res[0]["improved"] == "Kullanıcı giriş yapabilmeli."
                and res[1]["improved"] == "Rapor PDF olarak dışa aktarılabilmeli.")

    # C12 — vague_terms eksik LLM yanıtında → modül tespit eder (missing req fallback)
    def c12():
        reqs = [_req("Sistem hızlı olmalı.", "R1"), _req("API kolay olmalı.", "R2")]
        # LLM yalnızca R1'i döndürür; R2 eksik → modül fallback üretir
        payload = _batch_payload([{"req_id": "R1", "improved": "p95 200 ms.", "reason": "Hız."}])
        improver = RequirementImprover(llm_client=_mock_client(payload))
        res = improver.improve_batch(reqs)
        # R2 fallback'te vague_terms modül tarafından doldurulmalı
        r2 = res[1]
        return "kolay" in (r2.get("vague_terms") or [])

    batch_cases = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]
    for i, fn in enumerate(batch_cases, 1):
        total += 1
        try:
            ok = fn()
        except Exception as exc:
            ok = False
            print(f"XX {i:2d} exception: {exc}")
            failures.append(("BATCH", i, str(exc)))
            continue
        if ok:
            passed += 1
            print(f"OK {i:2d} {fn.__doc__ or fn.__name__}")
        else:
            print(f"XX {i:2d} {fn.__doc__ or fn.__name__} → BAŞARISIZ")
            failures.append(("BATCH", i, fn.__name__))

    return passed, total, failures


# ---------------------------------------------------------------------------
# BÖLÜM D — Kenar durumlar (8 vaka)
# ---------------------------------------------------------------------------

def run_edge_tests() -> tuple[int, int, list]:
    passed = total = 0
    failures = []
    print("\n=== Kenar durumlar — 8 vaka ===")

    cases: list[tuple[str, Any, dict, str]] = []

    # D1 — Boş metin → orijinal döner
    cases.append((
        "",
        _mock_client("{}"),
        {"improved": "", "original": ""},
        "boş gereksinim metni",
    ))

    # D2 — Sadece boşluk → orijinal döner
    cases.append((
        "   ",
        _mock_client("{}"),
        {"improved": ""},
        "sadece boşluk",
    ))

    # D3 — Muğlak kelime yok → LLM çağrılmaz, reason _NO_VAGUE_REASON
    cases.append((
        "Kullanıcı sisteme JWT ile kimlik doğrulamalıdır.",
        None,
        {"reason": None},  # None → _NO_VAGUE_REASON içermeli kontrolü
        "muğlak kelime yok",
    ))

    # D4 — LLM hatası → original döner
    cases.append((
        "Sistem hızlı olmalı.",
        "error",
        {"improved": "Sistem hızlı olmalı."},
        "LLM hatası → original fallback",
    ))

    # D5 — _detected_vague_terms: "iyi" tek başına geçmeli
    cases.append((
        "Sistem iyi çalışmalıdır.",
        _mock_client(_single_payload("Sistem %99.9 uptime SLA ile çalışmalı.", "İyi → uptime.", vague_terms=["iyi"])),
        {"vague_terms": ["iyi"]},
        "_detected_vague_terms 'iyi' tek kelime",
    ))

    # D6 — _detected_vague_terms: "kötü" tespiti
    cases.append((
        "Kötü performanslı sorgular optimize edilmeli.",
        _mock_client(_single_payload("Sorgu süresi 1 sn üzerindeyse optimize edilmeli.", "Kötü somutlaştırıldı.", vague_terms=["kötü"])),
        {"vague_terms": ["kötü"]},
        "_detected_vague_terms 'kötü'",
    ))

    # D7 — Hem Türkçe hem İngilizce muğlak kelime aynı cümlede
    cases.append((
        "Sistem fast ve güvenli olmalıdır.",
        _mock_client(_single_payload("p95 200 ms, TLS 1.2+.", "İkisi somutlaştırıldı.", vague_terms=["fast", "güvenli"])),
        {"vague_terms": ["fast", "güvenli"]},
        "karma dil muğlak kelime",
    ))

    # D8 — vague_keywords seti beklenen terimleri içermeli
    cases.append((
        "__meta__",  # Özel: doğrudan vague_keywords'e bakıyoruz
        None,
        {},
        "vague_keywords genişletildi: esnek, ölçeklenebilir, verimli, scalable",
    ))

    for i, (text, client_or_flag, expected_subset, note) in enumerate(cases, 1):
        total += 1

        if note == "vague_keywords genişletildi: esnek, ölçeklenebilir, verimli, scalable":
            # Doğrudan set kontrolü
            required = {"esnek", "ölçeklenebilir", "verimli", "scalable", "efficient", "robust"}
            missing = required - vague_keywords
            ok = len(missing) == 0
            if ok:
                passed += 1
                print(f"OK {i:2d} {note!r}")
            else:
                print(f"XX {i:2d} {note!r} → eksik: {missing}")
                failures.append(("EDGE", i, note, missing))
            continue

        if client_or_flag == "error":
            improver = RequirementImprover(llm_client=_mock_client_error())
        elif client_or_flag is None:
            improver = RequirementImprover(llm_client=_mock_client("{}"))
        else:
            improver = RequirementImprover(llm_client=client_or_flag)

        req = _req(text.strip())
        result = improver.improve(req)

        ok = True
        fail_details = []
        for key, exp_val in expected_subset.items():
            if key == "reason" and exp_val is None:
                if "muğlak anahtar" not in result.get("reason", ""):
                    ok = False
                    fail_details.append(f"reason should contain 'muğlak anahtar', got={result.get('reason')!r}")
            elif key == "vague_terms":
                got_terms = set(result.get("vague_terms") or [])
                exp_terms = set(exp_val)
                if not exp_terms.issubset(got_terms):
                    ok = False
                    fail_details.append(f"vague_terms: got={got_terms} exp_subset={exp_terms}")
            elif key in result:
                if result[key] != exp_val:
                    ok = False
                    fail_details.append(f"{key}: got={result[key]!r} exp={exp_val!r}")
            else:
                if exp_val is not None:
                    ok = False
                    fail_details.append(f"key '{key}' missing from result")

        if ok:
            passed += 1
            print(f"OK {i:2d} {note!r}")
        else:
            print(f"XX {i:2d} {note!r}")
            for d in fail_details:
                print(f"       {d}")
            failures.append(("EDGE", i, note, fail_details))

    return passed, total, failures


# ---------------------------------------------------------------------------
# Ana çalıştırıcı
# ---------------------------------------------------------------------------

def main() -> None:
    all_passed = all_total = 0
    all_failures: list = []

    for runner in [run_keyword_tests, run_improve_single_tests, run_improve_batch_tests, run_edge_tests]:
        p, t, f = runner()
        all_passed += p
        all_total += t
        all_failures.extend(f)

    pct = 100.0 * all_passed / all_total if all_total else 0
    print(f"\nDoğruluk: {all_passed}/{all_total} = %{pct:.1f}")

    if all_failures:
        print(f"\nBaşarısız ({len(all_failures)}):")
        for f in all_failures:
            print(f"  {f}")


if __name__ == "__main__":
    main()
