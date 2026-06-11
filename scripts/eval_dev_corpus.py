"""
Development Corpus (63 cümle, 5 domain) üzerinde NLP metriklerini ölçer.

Ölçülen metrikler:
  - Actor Extraction: Precision, Recall, F1
  - FR/NFR Classification: Accuracy
  - Domain bazlı kırılım
"""
from dotenv import load_dotenv
load_dotenv()

import json, time
from core.ner import EntityRecognizer
from core.classifier import RequirementClassifier
from core.models import Requirement

# === LOAD GROUND TRUTH ===
def load_ground_truth():
    import os
    json_path = os.path.join(os.path.dirname(__file__), "../data/evaluation/dev_corpus.json")
    if not os.path.exists(json_path):
        json_path = "data/evaluation/dev_corpus.json"
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return [
        (item["text"], set(item["expected_actors"]), item["expected_type"], item["domain"])
        for item in data
    ]

GROUND_TRUTH = load_ground_truth()

assert len(GROUND_TRUTH) >= 63, f"Beklenen en az 63 cümle, bulunan {len(GROUND_TRUTH)}"


def _norm(s: str) -> str:
    return s.lower().replace("\u0307", "")


def evaluate():
    ner = EntityRecognizer()
    clf = RequirementClassifier()

    # Sayaçlar
    actor_tp = actor_fp = actor_fn = 0
    clf_correct = clf_total = 0
    domain_stats: dict[str, dict] = {}

    print("=" * 80)
    print(f"DEVELOPMENT CORPUS DEĞERLENDİRME — 63 cümle, 5 domain")
    print("=" * 80)

    for i, (text, expected_actors, expected_type, domain) in enumerate(GROUND_TRUTH, 1):
        req = Requirement(id=f"REQ_{i:03d}", text=text)
        clf.classify(req)
        ner.recognize(req)

        found_actors = {_norm(a) for a in (req.actors or [])}
        exp_actors = {_norm(a) for a in expected_actors}

        # --- Actor metrikleri ---
        if exp_actors:
            matched = found_actors & exp_actors
            actor_tp += len(matched)
            actor_fp += len(found_actors - exp_actors)
            actor_fn += len(exp_actors - matched)
        else:
            # Beklenen aktör yok — bulunan her şey FP
            actor_fp += len(found_actors)

        # --- Classification metrikleri ---
        clf_total += 1
        clf_ok = req.req_type == expected_type
        if clf_ok:
            clf_correct += 1

        # --- Domain kırılım ---
        if domain not in domain_stats:
            domain_stats[domain] = {"actor_tp": 0, "actor_fp": 0, "actor_fn": 0,
                                     "clf_ok": 0, "clf_total": 0}
        ds = domain_stats[domain]
        if exp_actors:
            matched = found_actors & exp_actors
            ds["actor_tp"] += len(matched)
            ds["actor_fp"] += len(found_actors - exp_actors)
            ds["actor_fn"] += len(exp_actors - matched)
        else:
            ds["actor_fp"] += len(found_actors)
        ds["clf_total"] += 1
        if clf_ok:
            ds["clf_ok"] += 1

        # Satır çıktısı
        actor_mark = "✓" if (not exp_actors and not found_actors) or (exp_actors and found_actors & exp_actors) else "✗"
        clf_mark = "✓" if clf_ok else "✗"
        print(f"{i:2} [{domain[:6]:>6}] Actor{actor_mark} Clf{clf_mark} "
              f"found={sorted(found_actors)} exp={sorted(exp_actors)} "
              f"type={req.req_type}/{expected_type} | {text[:50]}")

    # === GENEL SONUÇLAR ===
    precision = actor_tp / (actor_tp + actor_fp) * 100 if (actor_tp + actor_fp) else 0
    recall = actor_tp / (actor_tp + actor_fn) * 100 if (actor_tp + actor_fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    clf_acc = clf_correct / clf_total * 100

    print("\n" + "=" * 80)
    print("GENEL SONUÇLAR")
    print("=" * 80)
    print(f"Actor Extraction:  TP={actor_tp}  FP={actor_fp}  FN={actor_fn}")
    print(f"  Precision = {precision:.1f}%")
    print(f"  Recall    = {recall:.1f}%")
    print(f"  F1        = {f1:.1f}%")
    print(f"\nFR/NFR Classification: {clf_correct}/{clf_total} = {clf_acc:.1f}%")

    # === DOMAIN KIRILIM ===
    print("\n" + "-" * 60)
    print("DOMAIN BAZLI KIRILIM")
    print("-" * 60)
    for d, s in domain_stats.items():
        dp = s["actor_tp"] / (s["actor_tp"] + s["actor_fp"]) * 100 if (s["actor_tp"] + s["actor_fp"]) else 0
        dr = s["actor_tp"] / (s["actor_tp"] + s["actor_fn"]) * 100 if (s["actor_tp"] + s["actor_fn"]) else 0
        da = s["clf_ok"] / s["clf_total"] * 100
        print(f"  {d:12} | ActorP={dp:5.1f}%  ActorR={dr:5.1f}%  ClfAcc={da:5.1f}%  ({s['clf_total']} cümle)")

    # === JSON export ===
    results = {
        "corpus": "development",
        "total_sentences": len(GROUND_TRUTH),
        "actor_precision": round(precision, 1),
        "actor_recall": round(recall, 1),
        "actor_f1": round(f1, 1),
        "classification_accuracy": round(clf_acc, 1),
        "domain_breakdown": {
            d: {
                "precision": round(s["actor_tp"] / (s["actor_tp"] + s["actor_fp"]) * 100, 1) if (s["actor_tp"] + s["actor_fp"]) else 0,
                "recall": round(s["actor_tp"] / (s["actor_tp"] + s["actor_fn"]) * 100, 1) if (s["actor_tp"] + s["actor_fn"]) else 0,
                "clf_accuracy": round(s["clf_ok"] / s["clf_total"] * 100, 1),
                "sentences": s["clf_total"],
            }
            for d, s in domain_stats.items()
        },
    }
    with open("reports/dev_corpus_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSonuçlar reports/dev_corpus_results.json dosyasına kaydedildi.")


if __name__ == "__main__":
    evaluate()
