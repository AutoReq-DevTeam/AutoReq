import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add repository path to sys.path
sys.path.insert(0, "/home/knover/Documents/GitHub/AutoReq")

from core.classifier import RequirementClassifier
from core.models import Requirement

# Set up paths
base_path = "/home/knover/Documents/GitHub/AutoReq/data/evaluation"
dev_path = os.path.join(base_path, "dev_corpus.json")
held_path = os.path.join(base_path, "heldout_corpus.json")
conf_path = os.path.join(base_path, "conflict_pairs.json")

# Ground truth mapping for conflict requirements REQ_064 to REQ_153
# (Determined based on requirements engineering standards: security, capacity, performance, reliability, availability, localization, compliance are NFR, others are FR)
CONFLICT_GT_MAPPING = {
    "REQ_064": "FUNCTIONAL",
    "REQ_065": "FUNCTIONAL",
    "REQ_066": "NON_FUNCTIONAL",
    "REQ_067": "NON_FUNCTIONAL",
    "REQ_068": "FUNCTIONAL",
    "REQ_069": "FUNCTIONAL",
    "REQ_070": "NON_FUNCTIONAL",
    "REQ_071": "FUNCTIONAL",
    "REQ_072": "NON_FUNCTIONAL",
    "REQ_073": "NON_FUNCTIONAL",
    "REQ_074": "FUNCTIONAL",
    "REQ_075": "FUNCTIONAL",
    "REQ_076": "NON_FUNCTIONAL",
    "REQ_077": "NON_FUNCTIONAL",
    "REQ_078": "NON_FUNCTIONAL",
    "REQ_079": "NON_FUNCTIONAL",
    "REQ_080": "FUNCTIONAL",
    "REQ_081": "FUNCTIONAL",
    "REQ_082": "FUNCTIONAL",
    "REQ_083": "FUNCTIONAL",
    "REQ_084": "NON_FUNCTIONAL",
    "REQ_085": "FUNCTIONAL",
    "REQ_086": "NON_FUNCTIONAL",
    "REQ_087": "NON_FUNCTIONAL",
    "REQ_088": "FUNCTIONAL",
    "REQ_089": "FUNCTIONAL",
    "REQ_090": "FUNCTIONAL",
    "REQ_091": "FUNCTIONAL",
    "REQ_092": "NON_FUNCTIONAL",
    "REQ_093": "NON_FUNCTIONAL",
    "REQ_094": "NON_FUNCTIONAL",
    "REQ_095": "FUNCTIONAL",
    "REQ_096": "FUNCTIONAL",
    "REQ_097": "FUNCTIONAL",
    "REQ_098": "NON_FUNCTIONAL",
    "REQ_099": "NON_FUNCTIONAL",
    "REQ_100": "NON_FUNCTIONAL",
    "REQ_101": "NON_FUNCTIONAL",
    "REQ_102": "FUNCTIONAL",
    "REQ_103": "FUNCTIONAL",
    "REQ_104": "FUNCTIONAL",
    "REQ_105": "FUNCTIONAL",
    "REQ_106": "NON_FUNCTIONAL",
    "REQ_107": "NON_FUNCTIONAL",
    "REQ_108": "FUNCTIONAL",
    "REQ_109": "FUNCTIONAL",
    "REQ_110": "FUNCTIONAL",
    "REQ_111": "FUNCTIONAL",
    "REQ_112": "NON_FUNCTIONAL",
    "REQ_113": "NON_FUNCTIONAL",
    "REQ_114": "NON_FUNCTIONAL",
    "REQ_115": "NON_FUNCTIONAL",
    "REQ_116": "FUNCTIONAL",
    "REQ_117": "FUNCTIONAL",
    "REQ_118": "NON_FUNCTIONAL",
    "REQ_119": "NON_FUNCTIONAL",
    "REQ_120": "FUNCTIONAL",
    "REQ_121": "FUNCTIONAL",
    "REQ_122": "FUNCTIONAL",
    "REQ_123": "NON_FUNCTIONAL",
    "REQ_124": "FUNCTIONAL",
    "REQ_125": "FUNCTIONAL",
    "REQ_126": "NON_FUNCTIONAL",
    "REQ_127": "NON_FUNCTIONAL",
    "REQ_128": "FUNCTIONAL",
    "REQ_129": "NON_FUNCTIONAL",
    "REQ_130": "FUNCTIONAL",
    "REQ_131": "FUNCTIONAL",
    "REQ_132": "FUNCTIONAL",
    "REQ_133": "FUNCTIONAL",
    "REQ_134": "FUNCTIONAL",
    "REQ_135": "FUNCTIONAL",
    "REQ_136": "FUNCTIONAL",
    "REQ_137": "FUNCTIONAL",
    "REQ_138": "FUNCTIONAL",
    "REQ_139": "NON_FUNCTIONAL",
    "REQ_140": "NON_FUNCTIONAL",
    "REQ_141": "NON_FUNCTIONAL",
    "REQ_142": "FUNCTIONAL",
    "REQ_143": "FUNCTIONAL",
    "REQ_144": "NON_FUNCTIONAL",
    "REQ_145": "NON_FUNCTIONAL",
    "REQ_146": "FUNCTIONAL",
    "REQ_147": "FUNCTIONAL",
    "REQ_148": "FUNCTIONAL",
    "REQ_149": "FUNCTIONAL",
    "REQ_150": "FUNCTIONAL",
    "REQ_151": "FUNCTIONAL",
    "REQ_152": "FUNCTIONAL",
    "REQ_153": "FUNCTIONAL"
}


def load_data():
    with open(dev_path, "r", encoding="utf-8") as f:
        dev_data = json.load(f)
    with open(held_path, "r", encoding="utf-8") as f:
        held_data = json.load(f)
    with open(conf_path, "r", encoding="utf-8") as f:
        conf_data = json.load(f)

    return dev_data, held_data, conf_data


def run_rule_based(clf, text):
    text_lower = text.lower().replace("\u0307", "")
    has_nfr_num = any(p.search(text_lower) for p in clf.nfr_numeric_patterns)
    has_strong_nfr_kw = clf._has_strong_nfr_kw(text_lower)
    has_nfr_kw = has_strong_nfr_kw or any(
        kw in text_lower for kw in clf._ambiguous_nfr_keywords
    )

    from core.classifier import _FR_VERB_RE

    if _FR_VERB_RE.search(text_lower) and not has_strong_nfr_kw and not has_nfr_num:
        return "FUNCTIONAL"
    elif has_nfr_kw or has_nfr_num:
        return "NON_FUNCTIONAL"
    else:
        return "FUNCTIONAL"  # default fallback


def evaluate_all():
    dev_data, held_data, conf_data = load_data()
    clf = RequirementClassifier()

    dev_texts_map = {item["text"]: item["expected_type"] for item in dev_data}

    # Combined output list
    output_records = []

    datasets = [
        ("development", dev_data),
        ("held-out", held_data),
        ("conflict", conf_data["requirements"]),
    ]

    print("Running evaluation on dev, held-out, and conflict datasets...")

    for ds_name, items in datasets:
        print(f"Processing dataset: {ds_name} ({len(items)} items)")
        for idx, item in enumerate(items, 1):
            if ds_name == "conflict":
                text = item["text"]
                req_id = item["id"]
                # Determine expected type
                if text in dev_texts_map:
                    expected_type = dev_texts_map[text]
                else:
                    expected_type = CONFLICT_GT_MAPPING.get(req_id, "FUNCTIONAL")
            else:
                text = item["text"]
                expected_type = item["expected_type"]
                prefix = "DEV" if ds_name == "development" else "HLD"
                req_id = f"{prefix}_{idx:03d}"

            # 1. Rule-based prediction
            rule_pred = run_rule_based(clf, text)
            rule_correct = rule_pred == expected_type

            # 2. Hybrid prediction
            req = Requirement(id=req_id, text=text)
            clf.classify(req)
            hybrid_pred = req.req_type
            hybrid_correct = hybrid_pred == expected_type

            # Matched pair category:
            # n11: both correct
            # n12: rule correct, hybrid incorrect
            # n21: rule incorrect, hybrid correct
            # n22: both incorrect
            if rule_correct and hybrid_correct:
                category = "n11"
            elif rule_correct and not hybrid_correct:
                category = "n12"
            elif not rule_correct and hybrid_correct:
                category = "n21"
            else:
                category = "n22"

            record = {
                "id": req_id,
                "dataset": ds_name,
                "text": text,
                "expected_type": expected_type,
                "rule_based_pred": rule_pred,
                "hybrid_pred": hybrid_pred,
                "rule_correct": rule_correct,
                "hybrid_correct": hybrid_correct,
                "matched_pair_category": category,
            }
            output_records.append(record)

    # Save outputs
    # 1. Save to repo reports/matched_pairs_results.json
    os.makedirs("/home/knover/Documents/GitHub/AutoReq/reports", exist_ok=True)
    report_path = "/home/knover/Documents/GitHub/AutoReq/reports/matched_pairs_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(output_records, f, ensure_ascii=False, indent=2)
    print(f"Matched-pair results saved to {report_path}")

    # 2. Save to artifacts folder
    artifact_dir = (
        "/home/knover/.gemini/antigravity/brain/a10b89f1-3ed6-4ebb-9370-43c5ec74f343"
    )
    artifact_path = os.path.join(artifact_dir, "matched_pairs_results.json")
    with open(artifact_path, "w", encoding="utf-8") as f:
        json.dump(output_records, f, ensure_ascii=False, indent=2)
    print(f"Matched-pair results saved to artifact path {artifact_path}")

    # Also save as CSV in artifacts for convenience
    csv_path = os.path.join(artifact_dir, "matched_pairs_results.csv")
    import csv

    headers = [
        "id",
        "dataset",
        "text",
        "expected_type",
        "rule_based_pred",
        "hybrid_pred",
        "rule_correct",
        "hybrid_correct",
        "matched_pair_category",
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output_records)
    print(f"Matched-pair results saved to CSV artifact {csv_path}")


if __name__ == "__main__":
    evaluate_all()
