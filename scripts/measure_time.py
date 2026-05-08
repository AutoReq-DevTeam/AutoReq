import os
import sys
import time
import json
import statistics
from pathlib import Path
from unittest.mock import MagicMock
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# --- Streamlit Mocking ---
# We mock streamlit to run the core pipeline outside of the Streamlit UI without errors
mock_st = MagicMock()
mock_st.session_state = {}
def mock_cache_resource(*args, **kwargs):
    def decorator(func):
        return func
    return decorator
mock_st.cache_resource = mock_cache_resource
sys.modules['streamlit'] = mock_st

# Add project root to sys.path so we can import 'core'
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from core.pipeline import process_text
from dotenv import load_dotenv

def measure_nlp_only(text: str) -> float:
    """
    Measures the execution time of the NLP-only pipeline.
    This is done by temporarily hiding the API keys so the LLM part is skipped.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY")
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY") # Check for OpenRouter too
    
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    if "DEEPSEEK_API_KEY" in os.environ:
        del os.environ["DEEPSEEK_API_KEY"]
    if "OPENROUTER_API_KEY" in os.environ:
        del os.environ["OPENROUTER_API_KEY"]
        
    start_time = time.time()
    try:
        # process_text checks _is_llm_available() and skips LLM if keys are missing
        process_text(text)
    except Exception as e:
        print(f"Error during NLP-only execution: {e}")
    finally:
        # Restore keys
        if gemini_key is not None:
            os.environ["GEMINI_API_KEY"] = gemini_key
        if deepseek_key is not None:
            os.environ["DEEPSEEK_API_KEY"] = deepseek_key
        if openrouter_key is not None:
            os.environ["OPENROUTER_API_KEY"] = openrouter_key
            
    end_time = time.time()
    return end_time - start_time

def measure_full_hybrid(text: str) -> float:
    """
    Measures the execution time of the full hybrid pipeline (NLP + LLM).
    Assumes environment variables are loaded and API keys exist.
    """
    start_time = time.time()
    try:
        process_text(text)
    except Exception as e:
        print(f"Error during Full Hybrid execution: {e}")
    end_time = time.time()
    return end_time - start_time

def remove_outliers(data):
    if len(data) < 4:
        return data, 0
    try:
        quantiles = statistics.quantiles(data, n=4)
        q1 = quantiles[0]
        q3 = quantiles[2]
    except AttributeError:
        # Fallback for Python versions without statistics.quantiles
        sorted_data = sorted(data)
        q1_idx = len(sorted_data) // 4
        q3_idx = (len(sorted_data) * 3) // 4
        q1 = sorted_data[q1_idx]
        q3 = sorted_data[q3_idx]
        
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    filtered = [x for x in data if lower_bound <= x <= upper_bound]
    return filtered, len(data) - len(filtered)

def main():
    load_dotenv(project_root / ".env")
    
    data_dir = project_root / "data" / "demo_scenarios"
    if not data_dir.exists():
        print(f"Hata: Test seti dizini bulunamadı ({data_dir})")
        sys.exit(1)

    sentences = []
    # Load all text documents from the demo_scenarios folder and split into sentences
    for file_path in data_dir.glob("*.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    sentences.append(line)
            
    if not sentences:
        print("Hata: Test setinde cümle bulunamadı!")
        sys.exit(1)

    nlp_times = []
    hybrid_times = []
    
    print(f"Test Seti Dizini: {data_dir.relative_to(project_root)}")
    print(f"Test Edilecek Toplam Cümle Sayısı: {len(sentences)}")
    print("--------------------------------------------------")
    
    # Run the tests for each sentence
    for i, sentence in enumerate(sentences, 1):
        print(f"Cümle {i}/{len(sentences)} işleniyor...")
        
        # 1. NLP Only
        t_nlp = measure_nlp_only(sentence)
        nlp_times.append(t_nlp)
        
        # 2. Full Hybrid
        t_hybrid = measure_full_hybrid(sentence)
        hybrid_times.append(t_hybrid)

    # IQR Outlier Removal
    filtered_nlp, removed_nlp = remove_outliers(nlp_times)
    filtered_hybrid, removed_hybrid = remove_outliers(hybrid_times)
    total_outliers = removed_nlp + removed_hybrid
    
    # Calculate statistics
    avg_nlp = statistics.mean(filtered_nlp) if filtered_nlp else 0.0
    std_nlp = statistics.stdev(filtered_nlp) if len(filtered_nlp) > 1 else 0.0
    
    avg_hybrid = statistics.mean(filtered_hybrid) if filtered_hybrid else 0.0
    std_hybrid = statistics.stdev(filtered_hybrid) if len(filtered_hybrid) > 1 else 0.0
    
    results = {
        "avg_nlp_only_per_sentence_seconds": round(avg_nlp, 4),
        "avg_hybrid_per_sentence_seconds": round(avg_hybrid, 4),
        "std_dev_nlp_only": round(std_nlp, 4),
        "std_dev_hybrid": round(std_hybrid, 4),
        "outliers_removed": total_outliers
    }
    
    # Save the results to reports/timing_results.json
    out_dir = project_root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "timing_results.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print("--------------------------------------------------")
    print("Test Tamamlandı!")
    print(f"Temizlenen aykırı değer (outlier) sayısı: {total_outliers}")
    print(f"Sonuçlar {out_file.relative_to(project_root)} dosyasına kaydedildi:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
