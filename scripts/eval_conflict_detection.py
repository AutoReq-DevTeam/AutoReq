"""
Conflict Detection E2E değerlendirme.
Development corpus (5 demo senaryo) üzerinde LLM conflict detection çalıştırır,
ground truth ile karşılaştırır.

Ground truth çelişki çiftleri: e-ticaret senaryosundaki kasıtlı çelişkiler.
"""
from dotenv import load_dotenv
load_dotenv()

import json, os
from core.preprocessor import TextPreprocessor
from core.classifier import RequirementClassifier
from core.ner import EntityRecognizer
from core.priority_detector import PriorityDetector
from modules.conflict_detector import ConflictDetector

SCENARIO_DIR = "data/demo_scenarios"
SCENARIO_FILES = [
    "01_e_ticaret_celisma.txt",
    "02_bankacilik_eksik.txt",
    "03_egitim_mughrak.txt",
    "04_kurumsal_portal_multi_actor.txt",
    "05_mobil_app_nfr_agirlikli.txt",
]

# === GROUND TRUTH çelişki çiftleri ===
# e-ticaret senaryosundaki kasıtlı çelişkiler (cümle indeksleri, 1-based global):
# Senaryo 01 (satır 1-13):
#   2 vs 3: Misafir ödeme vs kayıtlı kullanıcı zorunlu
#   4 vs 5: Stok yok → engelle vs izin ver+uyarı
#   6 vs 7: Adres zorunlu değil vs adres zorunlu
#   8 vs 9: Kupon tek kullanım vs çoklu kullanım
#   10 vs 11: Kart saklanmamalı vs kart kaydedilebilmeli
#   12 vs 13: Stok anında güncelle vs kargo sonrası güncelle

GROUND_TRUTH_CONFLICTS = [
    # (req_id_1, req_id_2) — REQ_XXX formatında
    ("REQ_002", "REQ_003"),  # misafir vs kayıtlı
    ("REQ_004", "REQ_005"),  # stok engelle vs izin ver
    ("REQ_006", "REQ_007"),  # adres zorunlu değil vs zorunlu
    ("REQ_008", "REQ_009"),  # kupon tek vs çoklu
    ("REQ_010", "REQ_011"),  # kart saklanmamalı vs kaydedilebilmeli
    ("REQ_012", "REQ_013"),  # stok güncelleme zamanlaması
]


def _normalize_pair(a: str, b: str) -> tuple:
    return tuple(sorted([a, b]))


def evaluate():
    # Tüm senaryoları birleştir
    all_text = []
    for f in SCENARIO_FILES:
        path = os.path.join(SCENARIO_DIR, f)
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    all_text.append(line)

    raw = "\n".join(all_text)
    print(f"Toplam cümle: {len(all_text)}")

    # NLP preprocessing
    preprocessor = TextPreprocessor()
    classifier = RequirementClassifier()
    ner = EntityRecognizer()
    priority = PriorityDetector()

    parsed = preprocessor.process(raw)
    for req in parsed.requirements:
        classifier.classify(req)
        ner.recognize(req)
        priority.detect(req)

    print(f"Parse edilen gereksinim: {len(parsed.requirements)}")
    for req in parsed.requirements:
        print(f"  {req.id}: {req.text[:60]}")

    # LLM conflict detection
    print("\nConflict detection çalışıyor...")
    detector = ConflictDetector()
    conflicts = detector.analyze(parsed)
    print(f"Bulunan conflict sayısı: {len(conflicts)}")

    # Bulunan çiftleri çıkar
    found_pairs = set()
    for c in conflicts:
        req_ids = c.get("req_ids", [])
        if len(req_ids) >= 2:
            for i in range(len(req_ids)):
                for j in range(i+1, len(req_ids)):
                    found_pairs.add(_normalize_pair(req_ids[i], req_ids[j]))
        print(f"  Conflict: {req_ids} | type={c.get('conflict_type', '?')} | "
              f"conf={c.get('confidence', '?')}")
        reason = c.get("reason", "")
        if reason:
            print(f"    Reason: {reason[:100]}")

    # Ground truth çiftleri normalize et
    gt_pairs = {_normalize_pair(a, b) for a, b in GROUND_TRUTH_CONFLICTS}

    # Metrikleri hesapla
    tp = len(found_pairs & gt_pairs)
    fp = len(found_pairs - gt_pairs)
    fn = len(gt_pairs - found_pairs)

    detection_rate = tp / len(gt_pairs) * 100 if gt_pairs else 0
    fp_rate = fp / (tp + fp) * 100 if (tp + fp) else 0
    precision = tp / (tp + fp) * 100 if (tp + fp) else 0
    recall = tp / (tp + fn) * 100 if (tp + fn) else 0

    print("\n" + "=" * 60)
    print("CONFLICT DETECTION SONUÇLARI")
    print("=" * 60)
    print(f"Ground truth çifti: {len(gt_pairs)}")
    print(f"Bulunan çift: {len(found_pairs)}")
    print(f"  TP (doğru tespit): {tp}")
    print(f"  FP (yanlış alarm): {fp}")
    print(f"  FN (kaçırılan): {fn}")
    print(f"\nDetection Rate: {detection_rate:.1f}%")
    print(f"False Positive Rate: {fp_rate:.1f}%")
    print(f"Precision: {precision:.1f}%")
    print(f"Recall: {recall:.1f}%")

    # Kaçırılanlar
    missed = gt_pairs - found_pairs
    if missed:
        print(f"\nKaçırılan çelişkiler:")
        for pair in sorted(missed):
            print(f"  {pair}")

    # Yanlış alarmlar
    false_alarms = found_pairs - gt_pairs
    if false_alarms:
        print(f"\nFalse positive çelişkiler:")
        for pair in sorted(false_alarms):
            print(f"  {pair}")

    results = {
        "ground_truth_pairs": len(gt_pairs),
        "found_pairs": len(found_pairs),
        "tp": tp, "fp": fp, "fn": fn,
        "detection_rate": round(detection_rate, 1),
        "false_positive_rate": round(fp_rate, 1),
        "precision": round(precision, 1),
        "recall": round(recall, 1),
    }
    with open("reports/conflict_detection_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSonuçlar reports/conflict_detection_results.json dosyasına kaydedildi.")


if __name__ == "__main__":
    evaluate()
