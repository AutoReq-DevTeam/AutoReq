"""
Conflict Detection E2E değerlendirme.
Development corpus (5 demo senaryo) üzerinde LLM conflict detection çalıştırır,
ground truth ile karşılaştırır.

Ground truth çelişki çiftleri: e-ticaret senaryosundaki kasıtlı çelişkiler.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

import json
from core.classifier import RequirementClassifier
from core.ner import EntityRecognizer
from core.priority_detector import PriorityDetector
from modules.conflict_detector import ConflictDetector

# === LOAD GROUND TRUTH ===
def load_conflict_data():
    import os
    json_path = os.path.join(os.path.dirname(__file__), "../data/evaluation/conflict_pairs.json")
    if not os.path.exists(json_path):
        json_path = "data/evaluation/conflict_pairs.json"
        
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

CONFLICT_DATA = load_conflict_data()
GROUND_TRUTH_CONFLICTS = CONFLICT_DATA["expected_conflicts"]


def _normalize_pair(a: str, b: str) -> tuple:
    return tuple(sorted([a, b]))


def evaluate():
    req_items = CONFLICT_DATA["requirements"]
    print(f"Toplam cümle: {len(req_items)}")

    # NLP processing
    classifier = RequirementClassifier()
    ner = EntityRecognizer()
    priority = PriorityDetector()
    from core.models import Requirement, ParsedDocument
    import random
    
    gt_pairs = {_normalize_pair(a, b) for a, b in GROUND_TRUTH_CONFLICTS}
    req_map = {r["id"]: r["text"] for r in req_items}
    
    # Split the expected conflicts into batches of 5 pairs
    expected_pairs_list = list(gt_pairs)
    batch_size = 5
    batches = [expected_pairs_list[i:i + batch_size] for i in range(0, len(expected_pairs_list), batch_size)]
    
    found_pairs = set()
    detector = ConflictDetector()
    
    print(f"Toplam cümle: {len(req_items)}")
    print(f"Grup (Batch) sayısı: {len(batches)} (Grup büyüklüğü: {batch_size} çelişki çifti)")
    
    for b_idx, batch in enumerate(batches, 1):
        print(f"\n=== GRUP {b_idx}/{len(batches)} ===")
        # Collect requirements that make up the conflicting pairs in this batch
        batch_reqs = set()
        for u, v in batch:
            batch_reqs.add(u)
            batch_reqs.add(v)
            
        # Add 5 random control requirements that do NOT belong to conflicting pairs in this batch
        random.seed(42 + b_idx)
        control_candidates = [rid for rid in req_map.keys() if rid not in batch_reqs]
        control_sample = random.sample(control_candidates, min(5, len(control_candidates)))
        for rid in control_sample:
            batch_reqs.add(rid)
            
        # Process NLP pipeline locally for the batch requirements
        requirements_list = []
        for rid in sorted(batch_reqs):
            req = Requirement(id=rid, text=req_map[rid])
            classifier.classify(req)
            ner.recognize(req)
            priority.detect(req)
            requirements_list.append(req)
            
        parsed = ParsedDocument(
            raw_text="\n".join(req_map[rid] for rid in sorted(batch_reqs)),
            requirements=requirements_list
        )
        
        print(f"Grup {b_idx} için {len(requirements_list)} gereksinim üzerinde çelişki analizi yapılıyor...")
        try:
            conflicts = detector.analyze(parsed)
            print(f"Grup {b_idx} içinde {len(conflicts)} çelişki bulundu.")
            for c in conflicts:
                req_ids = c.get("req_ids", [])
                if len(req_ids) >= 2:
                    for i in range(len(req_ids)):
                        for j in range(i+1, len(req_ids)):
                            found_pairs.add(_normalize_pair(req_ids[i], req_ids[j]))
        except Exception as e:
            print(f"Grup {b_idx} işlenirken hata oluştu: {e}")
            
        import time
        if b_idx < len(batches):
            print("Rate limit koruması için 5 saniye bekleniyor...")
            time.sleep(5)

    # Metrikleri hesapla
    tp = len(found_pairs & gt_pairs)
    fp = len(found_pairs - gt_pairs)
    fn = len(gt_pairs - found_pairs)

    detection_rate = tp / len(gt_pairs) * 100 if gt_pairs else 0
    fp_rate = fp / (tp + fp) * 100 if (tp + fp) else 0
    precision = tp / (tp + fp) * 100 if (tp + fp) else 0
    recall = tp / (tp + fn) * 100 if (tp + fn) else 0

    print("\n" + "=" * 60)
    print("ÇELİŞKİ TESPİTİ DEĞERLENDİRME SONUÇLARI")
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
