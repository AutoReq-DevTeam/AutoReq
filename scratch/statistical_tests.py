import json
import math
import os
import sys
from scipy.stats import chi2
from dotenv import load_dotenv
load_dotenv()

# Set PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.classifier import RequirementClassifier
from core.models import Requirement

def wilson_score_interval(successes, total, confidence=0.95):
    """Calculates Wilson score confidence interval."""
    if total == 0:
        return 0.0, 0.0
    p = successes / total
    z = 1.96  # for 95% confidence
    denominator = 1 + z**2 / total
    centre_adj_p = p + z**2 / (2 * total)
    adj_sem = z * math.sqrt((p * (1 - p) + z**2 / (4 * total)) / total)
    lower = (centre_adj_p - adj_sem) / denominator
    upper = (centre_adj_p + adj_sem) / denominator
    return max(0.0, lower), min(1.0, upper)

def load_dev_corpus():
    json_path = os.path.join(os.path.dirname(__file__), "../data/evaluation/dev_corpus.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_mcnemar():
    dev_data = load_dev_corpus()
    clf = RequirementClassifier()
    
    # We will run both the rule-based baseline and the hybrid classifier on all dev sentences
    # Rule-based baseline: Layer 1 + Layer 2. If neither matches, fallback to FUNCTIONAL.
    # Hybrid: Layer 1 + Layer 2 + Layer 3 (LLM fallback)
    
    # Contingency table:
    #             Hybrid Correct    Hybrid Incorrect
    # Rule Correct      n11               n12
    # Rule Incorrect    n21               n22
    n11 = n12 = n21 = n22 = 0
    
    rule_correct_count = 0
    hybrid_correct_count = 0
    total = len(dev_data)
    
    print(f"Evaluating {total} sentences for McNemar test...")
    for i, item in enumerate(dev_data, 1):
        text = item["text"]
        expected_type = item["expected_type"]
        
        # 1. Rule-based baseline prediction
        # (We mimic the classify method but without LLM fallback)
        text_lower = text.lower().replace("\u0307", "") # simplified lowercase
        # Let's use the actual regex and keyword matching from classifier
        has_nfr_num = any(p.search(text_lower) for p in clf.nfr_numeric_patterns)
        has_strong_nfr_kw = clf._has_strong_nfr_kw(text_lower)
        has_nfr_kw = has_strong_nfr_kw or any(kw in text_lower for kw in clf._ambiguous_nfr_keywords)
        
        from core.classifier import _FR_VERB_RE
        if _FR_VERB_RE.search(text_lower) and not has_strong_nfr_kw and not has_nfr_num:
            rule_pred = "FUNCTIONAL"
        elif has_nfr_kw or has_nfr_num:
            rule_pred = "NON_FUNCTIONAL"
        else:
            rule_pred = "FUNCTIONAL" # default fallback
            
        rule_ok = (rule_pred == expected_type)
        if rule_ok:
            rule_correct_count += 1
            
        # 2. Hybrid prediction (calls LLM if needed)
        req = Requirement(id=f"REQ_{i:03d}", text=text)
        clf.classify(req)
        hybrid_pred = req.req_type
        hybrid_ok = (hybrid_pred == expected_type)
        if hybrid_ok:
            hybrid_correct_count += 1
            
        # Populate contingency table
        if rule_ok and hybrid_ok:
            n11 += 1
        elif rule_ok and not hybrid_ok:
            n12 += 1
        elif not rule_ok and hybrid_ok:
            n21 += 1
        else:
            n22 += 1
            
        if i % 20 == 0:
            print(f"Processed {i}/{total}...")
            
    print("\n=== McNEMAR CONTINGENCY TABLE ===")
    print(f"                  Hybrid Correct    Hybrid Incorrect")
    print(f"Rule Correct           {n11:4d}              {n12:4d}")
    print(f"Rule Incorrect         {n21:4d}              {n22:4d}")
    print(f"Rule accuracy: {rule_correct_count}/{total} = {rule_correct_count/total*100:.2f}%")
    print(f"Hybrid accuracy: {hybrid_correct_count}/{total} = {hybrid_correct_count/total*100:.2f}%")
    
    # Calculate McNemar test
    # Chi-squared = (b - c)^2 / (b + c)
    # with continuity correction: (|b - c| - 1)^2 / (b + c)
    b = n12
    c = n21
    if b + c > 0:
        chi2_stat = ((abs(b - c) - 1) ** 2) / (b + c)
        p_val = chi2.sf(chi2_stat, 1)
    else:
        chi2_stat = 0.0
        p_val = 1.0
        
    print(f"\nMcNemar test statistic (with continuity correction): {chi2_stat:.4f}")
    print(f"p-value: {p_val:.4e}")
    
    # Wilson Score Confidence Intervals
    rule_lower, rule_upper = wilson_score_interval(rule_correct_count, total)
    hybrid_lower, hybrid_upper = wilson_score_interval(hybrid_correct_count, total)
    print(f"\nWilson Score 95% Confidence Intervals:")
    print(f"Rule-based Accuracy: {rule_correct_count/total*100:.1f}% | 95% CI: [{rule_lower*100:.1f}%, {rule_upper*100:.1f}%]")
    print(f"Hybrid Accuracy:     {hybrid_correct_count/total*100:.1f}% | 95% CI: [{hybrid_lower*100:.1f}%, {hybrid_upper*100:.1f}%]")

if __name__ == "__main__":
    evaluate_mcnemar()
