import json
import os
import sys
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Add repository to sys.path
sys.path.insert(0, "/home/knover/Documents/GitHub/AutoReq")

from modules.llm_client import LLMClient
from sklearn.metrics import cohen_kappa_score

AGREEMENT_SYSTEM_PROMPT = """\
Sen bağımsız bir yazılım gereksinim analizcisisin. 
Sana verilen Türkçe gereksinim cümlesini analiz ederek şu iki bilgiyi çıkarman gerekiyor:

1. Gereksinim Türü (req_type):
- FUNCTIONAL: Sistemin yapması gereken eylemler, kullanıcı işlemleri, iş özellikleri.
- NON_FUNCTIONAL: Performans, güvenlik, kullanılabilirlik, güvenilirlik, uyumluluk, ölçeklenebilirlik, kapasite gibi kalite özellikleri veya kısıtlar.

2. Aktörler (actors):
- Eylemi gerçekleştiren kişi, harici sistem veya donanım (örn: "kullanıcı", "yönetici", "müşteri"). 
- Cümledeki lemma (yalın) halleriyle liste olarak çıkar. Aktör yoksa boş liste döndür.

Yanıtını MUTLAKA aşağıdaki JSON formatında ver. JSON dışında hiçbir açıklama veya metin ekleme:
{
  "req_type": "FUNCTIONAL" veya "NON_FUNCTIONAL",
  "actors": ["aktör1", "aktör2", ...]
}
"""

def run_labeling():
    artifact_dir = "/home/knover/.gemini/antigravity/brain/a10b89f1-3ed6-4ebb-9370-43c5ec74f343"
    agreement_input_path = "/home/knover/Documents/GitHub/AutoReq/scratch/selected_agreement_sentences.json"
    
    with open(agreement_input_path, "r", encoding="utf-8") as f:
        sentences = json.load(f)
        
    client = LLMClient(model_name="google/gemini-2.5-flash", max_output_tokens=500)
    
    annotator1_types = []
    annotator2_types = []
    
    records = []
    
    print(f"Starting independent annotation on {len(sentences)} sentences...")
    
    for idx, item in enumerate(sentences, start=1):
        text = item["text"]
        id_str = item.get("id", f"REQ_{idx:03d}")
        exp_type = item["expected_type"]
        exp_actors = item["expected_actors"]
        
        # Call LLM for independent annotation
        prompt = f"Gereksinim Cümlesi:\n\"{text}\""
        try:
            response = client.chat(system_prompt=AGREEMENT_SYSTEM_PROMPT, user_prompt=prompt)
            content = response.content.strip()
            
            # Simple JSON parse
            # Extract JSON block if LLM added markdown formatting
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            res = json.loads(content)
            pred_type = res.get("req_type", "FUNCTIONAL")
            pred_actors = res.get("actors", [])
        except Exception as e:
            print(f"Error labeling sentence {id_str}: {e}")
            pred_type = "FUNCTIONAL"  # fallback
            pred_actors = []
            
        annotator1_types.append(exp_type)
        annotator2_types.append(pred_type)
        
        records.append({
            "id": id_str,
            "text": text,
            "annotator1_req_type": exp_type,
            "annotator2_req_type": pred_type,
            "annotator1_actors": exp_actors,
            "annotator2_actors": pred_actors,
            "type_agreement": exp_type == pred_type,
            "actor_agreement": sorted([a.lower() for a in exp_actors]) == sorted([a.lower() for a in pred_actors])
        })
        
        if idx % 10 == 0:
            print(f"Labeled {idx}/{len(sentences)} sentences...")
            
    # Calculate Cohen's Kappa
    kappa = cohen_kappa_score(annotator1_types, annotator2_types)
    agreement_accuracy = sum(1 for r in records if r["type_agreement"]) / len(records) * 100
    
    print("\n=== INTER-ANNOTATOR AGREEMENT RESULTS ===")
    print(f"Agreement Accuracy: {agreement_accuracy:.2f}%")
    print(f"Cohen's Kappa (Classification): {kappa:.4f}")
    
    output_data = {
        "agreement_accuracy_percent": round(agreement_accuracy, 2),
        "cohens_kappa": round(kappa, 4),
        "total_sentences": len(sentences),
        "annotations": records
    }
    
    # Save to reports/
    os.makedirs("/home/knover/Documents/GitHub/AutoReq/reports", exist_ok=True)
    report_path = "/home/knover/Documents/GitHub/AutoReq/reports/agreement_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Agreement results saved to {report_path}")
    
    # Save to artifacts/
    artifact_path = os.path.join(artifact_dir, "agreement_results.json")
    with open(artifact_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Agreement results saved to artifact path {artifact_path}")
    
    # Save CSV
    csv_path = os.path.join(artifact_dir, "agreement_results.csv")
    import csv
    headers = [
        "id", "text", "annotator1_req_type", "annotator2_req_type", 
        "annotator1_actors", "annotator2_actors", "type_agreement", "actor_agreement"
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        # format list fields as strings for CSV representation
        csv_records = []
        for r in records:
            cr = r.copy()
            cr["annotator1_actors"] = ", ".join(cr["annotator1_actors"])
            cr["annotator2_actors"] = ", ".join(cr["annotator2_actors"])
            csv_records.append(cr)
        writer.writerows(csv_records)
    print(f"Agreement CSV saved to {csv_path}")

if __name__ == "__main__":
    run_labeling()
