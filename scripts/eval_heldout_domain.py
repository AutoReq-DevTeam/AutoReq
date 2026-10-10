"""
Held-out Corpus — Domain Bazlı Değerlendirme (Sağlık + Otomotiv)

Hocanın talebine göre:
  - Healthcare (sağlık): İlk 30 cümle (index 0-29)
  - Automotive (otomotiv): Kalan 83 cümle (index 30-112)

Her domain için ayrı ayrı:
  - Actor Extraction: Precision, Recall, F1
  - FR/NFR Classification: Accuracy

Çıktı: reports/heldout_domain_results.json
"""
from dotenv import load_dotenv
load_dotenv()

import json, os
from core.ner import EntityRecognizer
from core.classifier import RequirementClassifier
from core.models import Requirement


# === VERİ YÜKLEME ===
def load_corpus():
    json_path = os.path.join(os.path.dirname(__file__), "../data/evaluation/heldout_corpus.json")
    if not os.path.exists(json_path):
        json_path = "data/evaluation/heldout_corpus.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def _norm(s: str) -> str:
    return s.lower().replace("\u0307", "")


def evaluate_subset(items: list, domain_label: str, ner, clf, id_prefix: str):
    """Bir alt küme üzerinde metrikleri hesaplar ve sonucu döndürür."""
    actor_tp = actor_fp = actor_fn = 0
    clf_correct = clf_total = 0

    print("\n" + "=" * 80)
    print(f"DOMAIN: {domain_label.upper()} — {len(items)} cümle")
    print("=" * 80)

    for i, item in enumerate(items, 1):
        text = item["text"]
        expected_actors = set(item["expected_actors"])
        expected_type = item["expected_type"]

        req = Requirement(id=f"{id_prefix}_{i:03d}", text=text)
        clf.classify(req)
        ner.recognize(req)

        found_actors = {_norm(a) for a in (req.actors or [])}
        exp_actors = {_norm(a) for a in expected_actors}

        # Actor metrikleri
        if exp_actors:
            matched = found_actors & exp_actors
            actor_tp += len(matched)
            actor_fp += len(found_actors - exp_actors)
            actor_fn += len(exp_actors - matched)
        else:
            actor_fp += len(found_actors)

        # Classification
        clf_total += 1
        clf_ok = req.req_type == expected_type
        if clf_ok:
            clf_correct += 1

        actor_mark = "✓" if (not exp_actors and not found_actors) or (exp_actors and found_actors & exp_actors) else "✗"
        clf_mark = "✓" if clf_ok else "✗"
        print(f"  {i:3}. Actor{actor_mark} Clf{clf_mark}  "
              f"found={sorted(found_actors)}  exp={sorted(exp_actors)}  "
              f"type={req.req_type}/{expected_type}  |  {text[:55]}")

    # Metrik hesaplama
    precision = actor_tp / (actor_tp + actor_fp) * 100 if (actor_tp + actor_fp) else 0.0
    recall    = actor_tp / (actor_tp + actor_fn) * 100 if (actor_tp + actor_fn) else 0.0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    clf_acc   = clf_correct / clf_total * 100

    print(f"\n  --- {domain_label} Sonuçları ---")
    print(f"  Actor Extraction:  TP={actor_tp}  FP={actor_fp}  FN={actor_fn}")
    print(f"    Precision = {precision:.1f}%")
    print(f"    Recall    = {recall:.1f}%")
    print(f"    F1        = {f1:.1f}%")
    print(f"  FR/NFR Classification: {clf_correct}/{clf_total} = {clf_acc:.1f}%")

    return {
        "domain": domain_label,
        "total_sentences": clf_total,
        "actor_tp": actor_tp,
        "actor_fp": actor_fp,
        "actor_fn": actor_fn,
        "actor_precision": round(precision, 1),
        "actor_recall": round(recall, 1),
        "actor_f1": round(f1, 1),
        "classification_accuracy": round(clf_acc, 1),
    }


def evaluate():
    all_data = load_corpus()
    total = len(all_data)
    print(f"\nToplam held-out cümle sayısı: {total}")

    # Domain sınırlarını belirle
    HEALTHCARE_COUNT = 30
    assert total >= HEALTHCARE_COUNT, f"Yetersiz veri: {total} cümle var, en az {HEALTHCARE_COUNT} bekleniyor."

    healthcare_items = all_data[:HEALTHCARE_COUNT]
    automotive_items = all_data[HEALTHCARE_COUNT:]

    print(f"  Sağlık (healthcare): {len(healthcare_items)} cümle (index 0–{HEALTHCARE_COUNT-1})")
    print(f"  Otomotiv (automotive): {len(automotive_items)} cümle (index {HEALTHCARE_COUNT}–{total-1})")

    ner = EntityRecognizer()
    clf = RequirementClassifier()

    # Her domain'i ayrı değerlendir
    health_result = evaluate_subset(healthcare_items, "healthcare", ner, clf, "HLT")
    auto_result   = evaluate_subset(automotive_items, "automotive",  ner, clf, "AUT")

    # Genel birleşik sonuçlar
    total_tp = health_result["actor_tp"] + auto_result["actor_tp"]
    total_fp = health_result["actor_fp"] + auto_result["actor_fp"]
    total_fn = health_result["actor_fn"] + auto_result["actor_fn"]
    total_clf_correct = (
        round(health_result["classification_accuracy"] / 100 * health_result["total_sentences"]) +
        round(auto_result["classification_accuracy"]   / 100 * auto_result["total_sentences"])
    )
    total_sentences = health_result["total_sentences"] + auto_result["total_sentences"]

    overall_precision = total_tp / (total_tp + total_fp) * 100 if (total_tp + total_fp) else 0.0
    overall_recall    = total_tp / (total_tp + total_fn) * 100 if (total_tp + total_fn) else 0.0
    overall_f1        = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) else 0.0
    overall_clf_acc   = total_clf_correct / total_sentences * 100

    print("\n" + "=" * 80)
    print("GENEL BİRLEŞİK SONUÇLAR (Healthcare + Automotive)")
    print("=" * 80)
    print(f"Toplam cümle: {total_sentences}")
    print(f"Actor Extraction:  TP={total_tp}  FP={total_fp}  FN={total_fn}")
    print(f"  Precision = {overall_precision:.1f}%")
    print(f"  Recall    = {overall_recall:.1f}%")
    print(f"  F1        = {overall_f1:.1f}%")
    print(f"FR/NFR Classification: {total_clf_correct}/{total_sentences} = {overall_clf_acc:.1f}%")

    # JSON çıktısı (dev_corpus_results.json formatına uygun)
    output = {
        "corpus": "heldout_domain_breakdown",
        "total_sentences": total_sentences,
        "actor_precision": round(overall_precision, 1),
        "actor_recall": round(overall_recall, 1),
        "actor_f1": round(overall_f1, 1),
        "classification_accuracy": round(overall_clf_acc, 1),
        "domain_breakdown": {
            "healthcare": {
                "sentences": health_result["total_sentences"],
                "actor_tp": health_result["actor_tp"],
                "actor_fp": health_result["actor_fp"],
                "actor_fn": health_result["actor_fn"],
                "precision": health_result["actor_precision"],
                "recall": health_result["actor_recall"],
                "f1": health_result["actor_f1"],
                "clf_accuracy": health_result["classification_accuracy"],
            },
            "automotive": {
                "sentences": auto_result["total_sentences"],
                "actor_tp": auto_result["actor_tp"],
                "actor_fp": auto_result["actor_fp"],
                "actor_fn": auto_result["actor_fn"],
                "precision": auto_result["actor_precision"],
                "recall": auto_result["actor_recall"],
                "f1": auto_result["actor_f1"],
                "clf_accuracy": auto_result["classification_accuracy"],
            },
        },
    }

    out_path = "reports/heldout_domain_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nSonuçlar {out_path} dosyasına kaydedildi.")
    return output


if __name__ == "__main__":
    evaluate()
