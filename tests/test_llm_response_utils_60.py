"""60 bağımsız vaka ile llm_response_utils doğruluk testi.

extract_json_object  — 40 vaka
filter_valid_requirement_ids — 10 vaka
sort_by_confidence           — 10 vaka
"""

import pytest
from modules.llm_response_utils import (
    extract_json_object,
    filter_valid_requirement_ids,
    sort_by_confidence,
)

# ---------------------------------------------------------------------------
# extract_json_object — 40 vaka
# ---------------------------------------------------------------------------

EJO_CASES: list[tuple[str, object]] = [
    # --- Saf JSON ---
    ('{"key": "value"}',                        {"key": "value"}),
    ('{"a": 1, "b": 2}',                        {"a": 1, "b": 2}),
    ('[1, 2, 3]',                                [1, 2, 3]),
    ('[]',                                       []),
    ('{}',                                       {}),
    ('{"nested": {"x": 1}}',                    {"nested": {"x": 1}}),
    ('[{"id": "R1"}, {"id": "R2"}]',            [{"id": "R1"}, {"id": "R2"}]),
    ('{"arr": [1, 2, 3]}',                      {"arr": [1, 2, 3]}),
    ('{"bool": true, "null": null}',             {"bool": True, "null": None}),
    ('{"unicode": "merhaba dünya"}',            {"unicode": "merhaba dünya"}),

    # --- Markdown code block ---
    ('```json\n{"key": "val"}\n```',            {"key": "val"}),
    ('```\n{"key": "val"}\n```',                {"key": "val"}),
    ('```json\n[1, 2]\n```',                    [1, 2]),
    ('```json\n{"a": {"b": "c"}}\n```',         {"a": {"b": "c"}}),

    # --- JSON etrafında açıklama metni ---
    ('Here is the result: {"status": "ok"}',    {"status": "ok"}),
    ('Analysis done.\n{"score": 0.9}',           {"score": 0.9}),
    ('{"result": "pass"} This is the output.',  {"result": "pass"}),
    ('Note: see below.\n{"x": 1}\nEnd.',        {"x": 1}),
    ('Önce açıklama. {"veri": "sonuç"} Sonra metin.', {"veri": "sonuç"}),

    # --- JSON + sonra açıklama (rfind hatasını tetikler) ---
    ('{"a": 1} Extra text with } brace.',       {"a": 1}),
    ('{"items": [1, 2]} Done. {"meta": {}}',    {"items": [1, 2]}),
    ('[1, 2, 3] extra ] bracket',               [1, 2, 3]),

    # --- İç içe yapılar ---
    ('{"conflicts": [{"id": "C1", "conf": 0.8}]}',
     {"conflicts": [{"id": "C1", "conf": 0.8}]}),
    ('{"meta": {"total": 3, "model": "gpt"}, "items": []}',
     {"meta": {"total": 3, "model": "gpt"}, "items": []}),
    ('{"a": {"b": {"c": {"d": 4}}}}',          {"a": {"b": {"c": {"d": 4}}}}),

    # --- String içinde özel karakterler ---
    (r'{"text": "He said \"hello\""}',          {"text": 'He said "hello"'}),
    ('{"path": "C:\\\\Users\\\\file"}',         {"path": "C:\\Users\\file"}),
    ('{"brace": "{ not a json }"}',             {"brace": "{ not a json }"}),
    ('{"bracket": "[1, 2, 3]"}',                {"bracket": "[1, 2, 3]"}),

    # --- Gerçekçi LLM çıktı kalıpları ---
    (
        'Çelişki analizi tamamlandı:\n```json\n'
        '{"conflicts": [{"req_ids": ["R1", "R2"], "confidence": 0.9}], '
        '"meta": {"total_conflicts": 1}}\n```',
        {"conflicts": [{"req_ids": ["R1", "R2"], "confidence": 0.9}],
         "meta": {"total_conflicts": 1}},
    ),
    (
        'Gap analizi:\n{"gaps": [{"title": "Auth eksik", "confidence": 0.7}]}',
        {"gaps": [{"title": "Auth eksik", "confidence": 0.7}]},
    ),
    (
        '```json\n[{"id": "G1", "severity": "HIGH"}, '
        '{"id": "G2", "severity": "MEDIUM"}]\n```',
        [{"id": "G1", "severity": "HIGH"}, {"id": "G2", "severity": "MEDIUM"}],
    ),

    # --- Boşluk ve satır sonu ---
    ('  {"key": "val"}  ',                      {"key": "val"}),
    ('\n\n{"a": 1}\n\n',                        {"a": 1}),
    ('```json\n\n{"x": 2}\n\n```',             {"x": 2}),

    # --- Array-önce vs object-önce (ikisi aynı anda) ---
    # Brace daha önce geldiğinde object seçilmeli
    ('{"obj": true} [1, 2]',                    {"obj": True}),
    # Bracket daha önce geldiğinde array seçilmeli
    ('[1, 2] {"obj": true}',                    [1, 2]),
]

EJO_ERROR_CASES: list[str] = [
    "",
    "   ",
    "Bu tamamen metin, JSON yok.",
    "{ eksik kapanış",
    "[ eksik kapanış",
    "{invalid: json}",
    "```json\n{invalid}\n```",
]

# ---------------------------------------------------------------------------
# filter_valid_requirement_ids — 10 vaka
# ---------------------------------------------------------------------------

FVRI_CASES: list[tuple[list, set, list]] = [
    # (items, valid_ids, expected_output)
    # Tümü geçerli
    (
        [{"requirement_ids": ["R1", "R2"]}, {"requirement_ids": ["R3"]}],
        {"R1", "R2", "R3"},
        [{"requirement_ids": ["R1", "R2"]}, {"requirement_ids": ["R3"]}],
    ),
    # Tümü geçersiz → boş liste
    (
        [{"requirement_ids": ["X99"]}, {"requirement_ids": ["Z1"]}],
        {"R1", "R2"},
        [],
    ),
    # Kısmen geçerli (R1 var, X99 yok) → ilk tutulur
    (
        [{"requirement_ids": ["R1"]}, {"requirement_ids": ["X99"]}],
        {"R1", "R2"},
        [{"requirement_ids": ["R1"]}],
    ),
    # ID alanı yok → kayıt korunur
    (
        [{"description": "no ids here"}],
        {"R1"},
        [{"description": "no ids here"}],
    ),
    # Alternatif anahtar "req_ids"
    (
        [{"req_ids": ["R2"]}, {"req_ids": ["X1"]}],
        {"R2"},
        [{"req_ids": ["R2"]}],
    ),
    # valid_ids boşsa her şey geçer
    (
        [{"requirement_ids": ["R1"]}, {"requirement_ids": ["X99"]}],
        set(),
        [{"requirement_ids": ["R1"]}, {"requirement_ids": ["X99"]}],
    ),
    # items boşsa boş döner
    ([], {"R1"}, []),
    # Karma: bazılarında id yok, bazıları geçerli, bazıları geçersiz
    (
        [
            {"requirement_ids": ["R1"]},
            {"description": "no id"},
            {"requirement_ids": ["X99"]},
        ],
        {"R1"},
        [{"requirement_ids": ["R1"]}, {"description": "no id"}],
    ),
    # ID string olarak verilmiş (liste değil)
    (
        [{"requirement_ids": "R1"}, {"requirement_ids": "X99"}],
        {"R1"},
        [{"requirement_ids": "R1"}],
    ),
    # "ids" anahtarı (üçüncü fallback)
    (
        [{"ids": ["R3", "R4"]}, {"ids": ["X1"]}],
        {"R4"},
        [{"ids": ["R3", "R4"]}],
    ),
]

# ---------------------------------------------------------------------------
# sort_by_confidence — 10 vaka
# ---------------------------------------------------------------------------

SBC_CASES: list[tuple[list, list]] = [
    # (items, expected_order — ilk elemanın confidence'ı en yüksek)
    # Basit sıralama
    (
        [{"id": "A", "confidence": 0.5}, {"id": "B", "confidence": 0.9}],
        [{"id": "B", "confidence": 0.9}, {"id": "A", "confidence": 0.5}],
    ),
    # Zaten sıralı → değişmez
    (
        [{"confidence": 0.9}, {"confidence": 0.5}],
        [{"confidence": 0.9}, {"confidence": 0.5}],
    ),
    # Confidence eksik → 1.0 kabul (filter ile tutarlı)
    (
        [{"id": "A"}, {"id": "B", "confidence": 0.7}],
        [{"id": "A"}, {"id": "B", "confidence": 0.7}],
    ),
    # Tümü aynı → sıra korunur (stable sort)
    (
        [{"id": "X", "confidence": 0.5}, {"id": "Y", "confidence": 0.5}],
        [{"id": "X", "confidence": 0.5}, {"id": "Y", "confidence": 0.5}],
    ),
    # Tek eleman
    (
        [{"confidence": 0.8}],
        [{"confidence": 0.8}],
    ),
    # Boş liste
    ([], []),
    # Confidence string olarak verilmiş
    (
        [{"confidence": "0.3"}, {"confidence": "0.8"}],
        [{"confidence": "0.8"}, {"confidence": "0.3"}],
    ),
    # None confidence → 0.0
    (
        [{"confidence": None}, {"confidence": 0.6}],
        [{"confidence": 0.6}, {"confidence": None}],
    ),
    # Üç eleman sıralaması
    (
        [{"id": "A", "confidence": 0.4},
         {"id": "B", "confidence": 0.9},
         {"id": "C", "confidence": 0.1}],
        [{"id": "B", "confidence": 0.9},
         {"id": "A", "confidence": 0.4},
         {"id": "C", "confidence": 0.1}],
    ),
    # Özel anahtar adı
    (
        [{"score": 0.2}, {"score": 0.8}],
        [{"score": 0.8}, {"score": 0.2}],
    ),
]


# ---------------------------------------------------------------------------
# Çalıştırıcı
# ---------------------------------------------------------------------------

def run():
    total = 0
    failures = []

    # --- extract_json_object (success) ---
    print("=== extract_json_object — başarı vakaları ===")
    for i, (text, expected) in enumerate(EJO_CASES, 1):
        total += 1
        try:
            result = extract_json_object(text)
            ok = result == expected
        except Exception as e:
            ok = False
            result = f"HATA: {e}"
        mark = "OK" if ok else "XX"
        preview = repr(text)[:55]
        print(f"{mark} {i:2} {preview}")
        if not ok:
            failures.append(("EJO-success", i, repr(text)[:60], result, expected))

    # --- extract_json_object (error) ---
    print("\n=== extract_json_object — hata vakaları (ValueError beklenir) ===")
    for i, text in enumerate(EJO_ERROR_CASES, 1):
        total += 1
        try:
            extract_json_object(text)
            ok = False
            result = "ValueError YÜKSELTİLMEDİ"
        except ValueError:
            ok = True
            result = "ValueError ✓"
        except Exception as e:
            ok = False
            result = f"Yanlış hata: {e}"
        mark = "OK" if ok else "XX"
        print(f"{mark} {i:2} {repr(text)[:55]}")
        if not ok:
            failures.append(("EJO-error", i, repr(text)[:60], result, "ValueError"))

    # --- filter_valid_requirement_ids ---
    print("\n=== filter_valid_requirement_ids ===")
    for i, (items, valid_ids, expected) in enumerate(FVRI_CASES, 1):
        total += 1
        result = filter_valid_requirement_ids(items, valid_ids)
        ok = result == expected
        mark = "OK" if ok else "XX"
        print(f"{mark} {i:2} items={len(items)} valid_ids={valid_ids} → {len(result)} kayıt")
        if not ok:
            failures.append(("FVRI", i, str(items)[:60], result, expected))

    # --- sort_by_confidence ---
    print("\n=== sort_by_confidence ===")
    for i, (items, expected) in enumerate(SBC_CASES, 1):
        total += 1
        # Özel anahtar adı testi (son vaka)
        key = "score" if i == len(SBC_CASES) else "confidence"
        result = sort_by_confidence(items, confidence_key=key)
        ok = result == expected
        mark = "OK" if ok else "XX"
        print(f"{mark} {i:2} {str(items)[:55]}")
        if not ok:
            failures.append(("SBC", i, str(items)[:60], result, expected))

    # --- Özet ---
    passed = total - len(failures)
    pct = passed / total * 100
    print(f"\nDoğruluk: {passed}/{total} = %{pct:.1f}")
    if failures:
        print(f"\nBaşarısız ({len(failures)}):")
        for group, i, text, got, exp in failures:
            print(f"  [{group}#{i}] got={got!r}")
            print(f"            exp={exp!r}")
            print(f"            input={text}")


if __name__ == "__main__":
    run()
