import os
import json
import sys

# Add project root and scripts directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Create data/evaluation directory
os.makedirs("data/evaluation", exist_ok=True)

# 1. Convert dev_corpus
try:
    from scripts.eval_dev_corpus import GROUND_TRUTH as dev_gt
    dev_data = []
    for text, actors, req_type, domain in dev_gt:
        dev_data.append({
            "text": text,
            "expected_actors": list(actors),
            "expected_type": req_type,
            "domain": domain
        })
    with open("data/evaluation/dev_corpus.json", "w", encoding="utf-8") as f:
        json.dump(dev_data, f, ensure_ascii=False, indent=2)
    print("Successfully converted dev_corpus.json")
except Exception as e:
    print(f"Error converting dev_corpus: {e}")

# 2. Convert heldout_corpus
try:
    from scripts.eval_heldout_corpus import GROUND_TRUTH as heldout_gt
    heldout_data = []
    for text, actors, req_type in heldout_gt:
        heldout_data.append({
            "text": text,
            "expected_actors": list(actors),
            "expected_type": req_type
        })
    with open("data/evaluation/heldout_corpus.json", "w", encoding="utf-8") as f:
        json.dump(heldout_data, f, ensure_ascii=False, indent=2)
    print("Successfully converted heldout_corpus.json")
except Exception as e:
    print(f"Error converting heldout_corpus: {e}")

# 3. Convert conflict_corpus
try:
    from scripts.eval_conflict_detection import GROUND_TRUTH_CONFLICTS as conflicts_gt
    # We also want to load the requirements texts that map to REQ_001, REQ_002, etc.
    from scripts.eval_dev_corpus import GROUND_TRUTH as dev_gt
    reqs = []
    for i, (text, _, _, _) in enumerate(dev_gt, 1):
        reqs.append({
            "id": f"REQ_{i:03d}",
            "text": text
        })
    
    conflict_data = {
        "requirements": reqs,
        "expected_conflicts": conflicts_gt
    }
    with open("data/evaluation/conflict_pairs.json", "w", encoding="utf-8") as f:
        json.dump(conflict_data, f, ensure_ascii=False, indent=2)
    print("Successfully converted conflict_pairs.json")
except Exception as e:
    print(f"Error converting conflict_pairs: {e}")
