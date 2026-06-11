"""
Healthcare Held-out Corpus (30 cümle) üzerinde NLP metriklerini ölçer.
Sistem bu veriyi hiç görmemiştir — generalization testi.
"""
from dotenv import load_dotenv
load_dotenv()

import json
from core.ner import EntityRecognizer
from core.classifier import RequirementClassifier
from core.models import Requirement

# === LOAD GROUND TRUTH ===
def load_ground_truth():
    import os
    json_path = os.path.join(os.path.dirname(__file__), "../data/evaluation/heldout_corpus.json")
    if not os.path.exists(json_path):
        json_path = "data/evaluation/heldout_corpus.json"
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return [
        (item["text"], set(item["expected_actors"]), item["expected_type"])
        for item in data
    ]

GROUND_TRUTH = load_ground_truth()

assert len(GROUND_TRUTH) >= 30, f"Beklenen en az 30 cümle, bulunan {len(GROUND_TRUTH)}"


def _norm(s: str) -> str:
    return s.lower().replace("\u0307", "")


def evaluate():
    ner = EntityRecognizer()
    clf = RequirementClassifier()

    actor_tp = actor_fp = actor_fn = 0
    clf_correct = clf_total = 0

    print("=" * 80)
    print(f"HEALTHCARE HELD-OUT CORPUS — {len(GROUND_TRUTH)} cümle (generalization)")
    print("=" * 80)

    for i, (text, expected_actors, expected_type) in enumerate(GROUND_TRUTH, 1):
        req = Requirement(id=f"HLD_{i:03d}", text=text)
        clf.classify(req)
        ner.recognize(req)

        found_actors = {_norm(a) for a in (req.actors or [])}
        exp_actors = {_norm(a) for a in expected_actors}

        if exp_actors:
            matched = found_actors & exp_actors
            actor_tp += len(matched)
            actor_fp += len(found_actors - exp_actors)
            actor_fn += len(exp_actors - matched)
        else:
            actor_fp += len(found_actors)

        clf_total += 1
        clf_ok = req.req_type == expected_type
        if clf_ok:
            clf_correct += 1

        actor_mark = "✓" if (not exp_actors and not found_actors) or (exp_actors and found_actors & exp_actors) else "✗"
        clf_mark = "✓" if clf_ok else "✗"
        print(f"{i:2} Actor{actor_mark} Clf{clf_mark} "
              f"found={sorted(found_actors)} exp={sorted(exp_actors)} "
              f"type={req.req_type}/{expected_type} | {text[:55]}")

    precision = actor_tp / (actor_tp + actor_fp) * 100 if (actor_tp + actor_fp) else 0
    recall = actor_tp / (actor_tp + actor_fn) * 100 if (actor_tp + actor_fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    clf_acc = clf_correct / clf_total * 100

    print("\n" + "=" * 80)
    print("HEALTHCARE HELD-OUT SONUÇLARI")
    print("=" * 80)
    print(f"Actor Extraction:  TP={actor_tp}  FP={actor_fp}  FN={actor_fn}")
    print(f"  Precision = {precision:.1f}%")
    print(f"  Recall    = {recall:.1f}%")
    print(f"  F1        = {f1:.1f}%")
    print(f"\nFR/NFR Classification: {clf_correct}/{clf_total} = {clf_acc:.1f}%")

    results = {
        "corpus": "healthcare_heldout",
        "total_sentences": len(GROUND_TRUTH),
        "actor_precision": round(precision, 1),
        "actor_recall": round(recall, 1),
        "actor_f1": round(f1, 1),
        "classification_accuracy": round(clf_acc, 1),
    }
    with open("reports/heldout_corpus_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSonuçlar reports/heldout_corpus_results.json dosyasına kaydedildi.")


if __name__ == "__main__":
    evaluate()
