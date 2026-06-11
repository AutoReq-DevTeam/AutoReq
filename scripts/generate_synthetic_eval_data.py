import os
import json
import sys
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.llm_client import LLMClient
from modules.llm_response_utils import extract_json_object

def generate_dev_corpus_data(client: LLMClient):
    print("Generating dev corpus additions...")
    domains = ["iot", "saas", "oyun"]
    new_items = []
    
    for domain in domains:
        print(f"Generating requirements for domain: {domain}...")
        system_prompt = (
            "Sen Türkçe yazılım gereksinim mühendisliği uzmanısın. Görevin, verilen sektöre (domain) ait "
            "yapay zeka analiz testlerinde kullanılacak gerçekçi Türkçe yazılım gereksinim cümleleri üretmektir."
        )
        
        user_prompt = f"""
Lütfen '{domain}' sektörü için tam olarak 60 adet yazılım gereksinimi (requirement) cümlesi üret.
Bu cümleler, bir sistemin doğruluğunu (aktör çıkarma ve FR/NFR sınıflandırması) test etmek için kullanılacaktır.

Gereksinimler şu özelliklere sahip olmalıdır:
1. Yaklaşık yarısı Functional (FR) ve yarısı Non-Functional (NFR) olmalıdır.
2. Bazı cümlelerde belirgin aktörler (örneğin: 'akıllı priz', 'tenant yöneticisi', 'oyuncu', 'sistem yöneticisi', 'sistem', 'kullanıcı') olmalı, bazılarında ise eylemi yapan açık bir aktör olmamalıdır (expected_actors boş liste olmalıdır).
3. Cümleler doğal Türkçe dilinde ve gerçekçi yazılım projelerinden alınmış gibi olmalıdır.

Yanıtını YALNIZCA aşağıdaki JSON formatında ver. Başka hiçbir açıklama, markdown veya metin ekleme. Sadece geçerli bir JSON listesi döndür.

JSON Formatı:
[
  {{
    "text": "Gereksinim cümlesi...",
    "expected_actors": ["aktör1", "aktör2"],
    "expected_type": "FUNCTIONAL" veya "NON_FUNCTIONAL",
    "domain": "{domain}"
  }}
]
"""
        try:
            response = client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                metadata={"action": f"generate_dev_corpus_{domain}"}
            )
            data = extract_json_object(response.content)
            if isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, list):
                        data = val
                        break
            if isinstance(data, list):
                print(f"Successfully generated {len(data)} items for {domain}.")
                new_items.extend(data)
            else:
                print(f"Error: Generated data for {domain} is not a list. Raw content preview: {response.content[:200]}")
        except Exception as e:
            print(f"Failed to generate for {domain}: {e}")
            
    # Load existing dev corpus
    dev_path = "data/evaluation/dev_corpus.json"
    if os.path.exists(dev_path):
        with open(dev_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = []
        
    combined = existing_data + new_items
    with open(dev_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"Dev corpus updated. Total items: {len(combined)} (Added {len(new_items)})")


def generate_heldout_corpus_data(client: LLMClient):
    print("Generating heldout corpus additions...")
    domain = "otomotiv"
    print(f"Generating requirements for heldout domain: {domain}...")
    
    system_prompt = (
        "Sen Türkçe yazılım gereksinim mühendisliği uzmanısın. Görevin, otomotiv/otonom sürüş sistemleri "
        "sektörüne ait testlerde kullanılacak gerçekçi Türkçe yazılım gereksinim cümleleri üretmektir."
    )
    
    user_prompt = """
Lütfen 'otomotiv' (akıllı araçlar, otonom sürüş, gösterge panelleri vb.) sektörü için tam olarak 75 adet yazılım gereksinimi cümlesi üret.
Bu cümleler sistemin hiç görmediği bir held-out veri kümesi olarak kullanılacaktır.

Gereksinimler şu özelliklere sahip olmalıdır:
1. Yaklaşık yarısı Functional (FR) ve yarısı Non-Functional (NFR) olmalıdır.
2. Bazı cümlelerde belirgin otomotiv aktörleri (örneğin: 'sürücü', 'radar sensörü', 'infotainment sistemi', 'şerit takip asistanı', 'fren sistemi', 'kullanıcı') olmalı, bazılarında ise açık bir aktör olmamalıdır (expected_actors boş liste olmalıdır).
3. Cümleler doğal Türkçe dilinde ve gerçekçi otomotiv yazılımlarından alınmış gibi olmalıdır.

Yanıtını YALNIZCA aşağıdaki JSON formatında ver. Başka hiçbir açıklama, markdown veya metin ekleme. Sadece geçerli bir JSON listesi döndür.

JSON Formatı:
[
  {{
    "text": "Gereksinim cümlesi...",
    "expected_actors": ["aktör1", "aktör2"],
    "expected_type": "FUNCTIONAL" veya "NON_FUNCTIONAL"
  }}
]
"""
    try:
        response = client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={"action": "generate_heldout_corpus"}
        )
        data = extract_json_object(response.content)
        if isinstance(data, dict):
            for key, val in data.items():
                if isinstance(val, list):
                    data = val
                    break
        if isinstance(data, list):
            print(f"Successfully generated {len(data)} items for heldout corpus.")
            heldout_path = "data/evaluation/heldout_corpus.json"
            if os.path.exists(heldout_path):
                with open(heldout_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            
            combined = existing_data + data
            with open(heldout_path, "w", encoding="utf-8") as f:
                json.dump(combined, f, ensure_ascii=False, indent=2)
            print(f"Heldout corpus updated. Total items: {len(combined)} (Added {len(data)})")
        else:
            print(f"Error: Generated heldout data is not a list. Raw content preview: {response.content[:200]}")
    except Exception as e:
        print(f"Failed to generate heldout corpus: {e}")


def generate_conflict_pairs_data(client: LLMClient):
    print("Generating conflict pairs additions...")
    system_prompt = (
        "Sen Türkçe yazılım gereksinim mühendisliği uzmanısın. Görevin, çelişki tespiti (conflict detection) "
        "algoritmalarını test etmek amacıyla birbiriyle mantıksal, teknik, yetki veya performans yönünden çelişen "
        "Türkçe yazılım gereksinim cümle çiftleri üretmektir."
    )
    
    user_prompt = """
Lütfen birbiriyle çelişen tam olarak 45 adet gereksinim cümlesi çifti üret.
Her çiftte birbiriyle doğrudan veya dolaylı olarak çelişen iki gereksinim cümlesi bulunmalıdır.

Çelişki türleri şunlar olabilir:
- Mantıksal Zıtlık (Logical Contradiction)
- Yetki Çakışması (Permission Conflict)
- Veri/Zamanlama Uyumsuzluğu (Data/Timing Mismatch)
- Performans/NFR Uyumsuzluğu (Performance/NFR Conflict)

Yanıtını YALNIZCA aşağıdaki JSON formatında ver. Başka hiçbir açıklama, markdown veya metin ekleme. Sadece geçerli bir JSON listesi döndür.

JSON Formatı:
[
  {{
    "req1": "İlk gereksinim cümlesi...",
    "req2": "İlk gereksinim ile çelişen ikinci gereksinim cümlesi...",
    "conflict_type": "logical_contradiction veya timing_conflict veya data_mismatch veya permission_conflict",
    "reason": "Çelişkinin kısa açıklaması"
  }}
]
"""
    try:
        response = client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={"action": "generate_conflict_pairs"}
        )
        data = extract_json_object(response.content)
        if isinstance(data, dict):
            for key, val in data.items():
                if isinstance(val, list):
                    data = val
                    break
        if isinstance(data, list):
            print(f"Successfully generated {len(data)} conflict pairs.")
            
            conflict_path = "data/evaluation/conflict_pairs.json"
            if os.path.exists(conflict_path):
                with open(conflict_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            else:
                existing_data = {"requirements": [], "expected_conflicts": []}
                
            reqs = existing_data.get("requirements", [])
            expected_conflicts = existing_data.get("expected_conflicts", [])
            
            start_index = len(reqs) + 1
            
            for i, pair in enumerate(data):
                id1 = f"REQ_{start_index:03d}"
                start_index += 1
                id2 = f"REQ_{start_index:03d}"
                start_index += 1
                
                reqs.append({"id": id1, "text": pair["req1"]})
                reqs.append({"id": id2, "text": pair["req2"]})
                expected_conflicts.append([id1, id2])
                
            combined = {
                "requirements": reqs,
                "expected_conflicts": expected_conflicts
            }
            
            with open(conflict_path, "w", encoding="utf-8") as f:
                json.dump(combined, f, ensure_ascii=False, indent=2)
            print(f"Conflict pairs updated. Total requirements: {len(reqs)}, Total expected conflicts: {len(expected_conflicts)} (Added {len(data)} pairs)")
        else:
            print(f"Error: Generated conflict pairs is not a list. Raw content preview: {response.content[:200]}")
    except Exception as e:
        print(f"Failed to generate conflict pairs: {e}")


if __name__ == "__main__":
    # Initialize LLMClient with Gemini 2.5 Flash
    client = LLMClient(model_name="google/gemini-2.5-flash", max_output_tokens=8192)
    
    # Check if dev_corpus is already populated
    dev_path = "data/evaluation/dev_corpus.json"
    if os.path.exists(dev_path):
        with open(dev_path, "r", encoding="utf-8") as f:
            dev_data = json.load(f)
        if len(dev_data) < 200:
            generate_dev_corpus_data(client)
        else:
            print(f"dev_corpus already has {len(dev_data)} items. Skipping generation.")
    else:
        generate_dev_corpus_data(client)
        
    # Check if heldout_corpus is already populated
    heldout_path = "data/evaluation/heldout_corpus.json"
    if os.path.exists(heldout_path):
        with open(heldout_path, "r", encoding="utf-8") as f:
            heldout_data = json.load(f)
        if len(heldout_data) < 100:
            generate_heldout_corpus_data(client)
        else:
            print(f"heldout_corpus already has {len(heldout_data)} items. Skipping generation.")
    else:
        generate_heldout_corpus_data(client)
        
    # Check if conflict_pairs is already populated
    conflict_path = "data/evaluation/conflict_pairs.json"
    if os.path.exists(conflict_path):
        with open(conflict_path, "r", encoding="utf-8") as f:
            conflict_data = json.load(f)
        if len(conflict_data.get("expected_conflicts", [])) < 50:
            generate_conflict_pairs_data(client)
        else:
            print(f"conflict_pairs already has {len(conflict_data.get('expected_conflicts', []))} pairs. Skipping generation.")
    else:
        generate_conflict_pairs_data(client)
        
    print("All checks and generations completed successfully!")
