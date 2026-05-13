"""
Zamanlama ölçümü: NLP-only vs Hybrid (NLP + LLM) per-sentence süre.
Development corpus (63 cümle) üzerinde çalışır.
IQR yöntemiyle outlier temizleme uygulanır.
"""
from dotenv import load_dotenv
load_dotenv()

import json, time, os, statistics
from core.preprocessor import TextPreprocessor
from core.classifier import RequirementClassifier
from core.ner import EntityRecognizer
from core.priority_detector import PriorityDetector
from core.models import Requirement

# Demo senaryolarından tüm cümleleri oku
SCENARIO_DIR = "data/demo_scenarios"
SCENARIO_FILES = [
    "01_e_ticaret_celisma.txt",
    "02_bankacilik_eksik.txt",
    "03_egitim_mughrak.txt",
    "04_kurumsal_portal_multi_actor.txt",
    "05_mobil_app_nfr_agirlikli.txt",
]


def load_sentences() -> list[str]:
    sentences = []
    for f in SCENARIO_FILES:
        path = os.path.join(SCENARIO_DIR, f)
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    sentences.append(line)
    return sentences


def iqr_filter(data: list[float]) -> list[float]:
    """IQR yöntemiyle outlier temizleme."""
    if len(data) < 4:
        return data
    sorted_d = sorted(data)
    q1 = sorted_d[len(sorted_d) // 4]
    q3 = sorted_d[3 * len(sorted_d) // 4]
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return [x for x in data if lower <= x <= upper]


def measure():
    sentences = load_sentences()
    print(f"Toplam cümle: {len(sentences)}")

    # NLP bileşenlerini yükle
    preprocessor = TextPreprocessor()
    classifier = RequirementClassifier()
    ner = EntityRecognizer()
    priority = PriorityDetector()

    # === NLP-only zamanlama ===
    print("\n--- NLP-only zamanlama ---")
    nlp_times = []
    for i, sent in enumerate(sentences, 1):
        t0 = time.perf_counter()
        parsed = preprocessor.process(sent)
        for req in parsed.requirements:
            classifier.classify(req)
            ner.recognize(req)
            priority.detect(req)
        elapsed = time.perf_counter() - t0
        nlp_times.append(elapsed)
        print(f"  {i:2}/{len(sentences)} NLP: {elapsed:.3f}s")

    nlp_filtered = iqr_filter(nlp_times)
    nlp_mean = statistics.mean(nlp_filtered)
    nlp_std = statistics.stdev(nlp_filtered) if len(nlp_filtered) > 1 else 0

    print(f"\nNLP-only: mean={nlp_mean:.3f}s  std={nlp_std:.3f}s  "
          f"(IQR filtered: {len(nlp_filtered)}/{len(nlp_times)})")

    # === Hybrid zamanlama (NLP + LLM) ===
    has_llm = bool(os.getenv("GEMINI_API_KEY") or os.getenv("DEEPSEEK_API_KEY"))
    hybrid_mean = hybrid_std = 0.0
    hybrid_times = []

    if has_llm:
        from modules.conflict_detector import ConflictDetector
        from modules.gap_analyzer import GapAnalyzer
        import concurrent.futures

        print("\n--- Hybrid (NLP + LLM) zamanlama ---")
        for i, sent in enumerate(sentences, 1):
            t0 = time.perf_counter()
            parsed = preprocessor.process(sent)
            for req in parsed.requirements:
                classifier.classify(req)
                ner.recognize(req)
                priority.detect(req)

            # LLM analizi
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
                f1 = ex.submit(lambda: ConflictDetector().analyze(parsed))
                f2 = ex.submit(lambda: GapAnalyzer().analyze(parsed))
                try:
                    f1.result(timeout=30)
                except Exception:
                    pass
                try:
                    f2.result(timeout=30)
                except Exception:
                    pass

            elapsed = time.perf_counter() - t0
            hybrid_times.append(elapsed)
            print(f"  {i:2}/{len(sentences)} Hybrid: {elapsed:.3f}s")

        hybrid_filtered = iqr_filter(hybrid_times)
        hybrid_mean = statistics.mean(hybrid_filtered)
        hybrid_std = statistics.stdev(hybrid_filtered) if len(hybrid_filtered) > 1 else 0
        print(f"\nHybrid: mean={hybrid_mean:.3f}s  std={hybrid_std:.3f}s  "
              f"(IQR filtered: {len(hybrid_filtered)}/{len(hybrid_times)})")
    else:
        print("\nLLM API key yok — hybrid zamanlama atlanıyor.")

    # === Sonuç ===
    results = {
        "total_sentences": len(sentences),
        "nlp_only": {
            "mean_seconds": round(nlp_mean, 3),
            "std_seconds": round(nlp_std, 3),
            "raw_count": len(nlp_times),
            "filtered_count": len(nlp_filtered),
        },
        "hybrid": {
            "mean_seconds": round(hybrid_mean, 3),
            "std_seconds": round(hybrid_std, 3),
            "raw_count": len(hybrid_times),
            "filtered_count": len(iqr_filter(hybrid_times)) if hybrid_times else 0,
        },
        "added_latency": round(hybrid_mean - nlp_mean, 3) if hybrid_times else None,
    }

    print("\n" + "=" * 60)
    print("ZAMANLAMA SONUÇLARI")
    print("=" * 60)
    print(f"NLP-only  : {nlp_mean:.3f}s ± {nlp_std:.3f}s per sentence")
    if hybrid_times:
        print(f"Hybrid    : {hybrid_mean:.3f}s ± {hybrid_std:.3f}s per sentence")
        print(f"LLM eklenen: ~{hybrid_mean - nlp_mean:.1f}s per sentence")

    with open("reports/timing_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSonuçlar reports/timing_results.json dosyasına kaydedildi.")


if __name__ == "__main__":
    measure()
