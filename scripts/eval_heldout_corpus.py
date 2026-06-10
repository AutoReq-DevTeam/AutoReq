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

# === GROUND TRUTH — HEALTHCARE HELD-OUT (30 cümle) ===
GROUND_TRUTH = [
    ("Hasta randevu almadan önce TC kimlik numarasını doğrulatmalıdır.", {"hasta"}, "FUNCTIONAL"),
    ("Doktor, hastanın tıbbi geçmişini görüntüleyebilmelidir.", {"doktor"}, "FUNCTIONAL"),
    ("Hemşire, hasta yatak başı gözlem formunu doldurabilmelidir.", {"hemşire"}, "FUNCTIONAL"),
    ("Eczacı, reçetedeki ilaçları hasta adına karşılayabilmelidir.", {"eczacı"}, "FUNCTIONAL"),
    ("Laborant, test sonuçlarını sisteme girebilmelidir.", {"laborant"}, "FUNCTIONAL"),
    ("Diyetisyen, hastaya özel beslenme planı oluşturabilmelidir.", {"diyetisyen"}, "FUNCTIONAL"),
    ("Fizyoterapist, tedavi seanslarını planlayabilmelidir.", {"fizyoterapist"}, "FUNCTIONAL"),
    ("Hasta yakını, hastanın durumunu çevrimiçi takip edebilmelidir.", {"hasta yakını"}, "FUNCTIONAL"),
    ("Acil servis triaj hemşiresi hastaları önceliklendirmelidir.", {"hemşire"}, "FUNCTIONAL"),
    ("Radyolog, görüntüleme sonuçlarını PACS sistemine yükleyebilmelidir.", {"radyolog"}, "FUNCTIONAL"),
    ("Başhekim, klinik bazlı doluluk oranlarını raporlayabilmelidir.", {"başhekim"}, "FUNCTIONAL"),
    ("Hastane yöneticisi, personel nöbet çizelgesini düzenleyebilmelidir.", {"yönetici"}, "FUNCTIONAL"),
    ("Tıbbi sekreter, hasta dosyasını arşivleyebilmelidir.", {"sekreter"}, "FUNCTIONAL"),
    ("Hasta, faturasını online ödeyebilmelidir.", {"hasta"}, "FUNCTIONAL"),
    ("Doktor, e-reçete yazabilmeli ve eczaneye iletebilmelidir.", {"doktor"}, "FUNCTIONAL"),
    ("Hasta verilerinin yedeklenmesi günde en az iki kez yapılmalıdır.", set(), "NON_FUNCTIONAL"),
    ("Sistem, eş zamanlı 500 poliklinik kaydını işleyebilmelidir.", set(), "NON_FUNCTIONAL"),
    ("Tıbbi kayıtlar KVKK kapsamında şifrelenmiş olarak saklanmalıdır.", set(), "NON_FUNCTIONAL"),
    ("Acil çağrı bildirimleri 2 saniye içinde ilgili ekibe ulaşmalıdır.", set(), "NON_FUNCTIONAL"),
    ("Laboratuvar sonuçları otomatik olarak doktorun ekranına düşmelidir.", {"doktor"}, "FUNCTIONAL"),
    ("Sistem %99,5 uptime hedefini sağlamalıdır.", set(), "NON_FUNCTIONAL"),
    ("Hasta taburcu işlemi ortalama 15 dakikayı geçmemelidir.", {"hasta"}, "NON_FUNCTIONAL"),
    ("Ameliyathane doluluk oranı anlık olarak izlenebilmelidir.", set(), "FUNCTIONAL"),
    ("Eczane stok seviyesi kritik eşiğin altına düştüğünde otomatik uyarı verilmelidir.", set(), "FUNCTIONAL"),
    ("İlaç etkileşim kontrolü reçete yazılmadan önce otomatik gerçekleştirilmelidir.", set(), "FUNCTIONAL"),
    ("Hasta memnuniyet anketi taburculuk sonrası 24 saat içinde gönderilmelidir.", {"hasta"}, "FUNCTIONAL"),
    ("Doktor, ameliyat notlarını sesli komutla dikte edebilmelidir.", {"doktor"}, "FUNCTIONAL"),
    ("Sigorta şirketi entegrasyonu üzerinden hasta provizyon sorgulama yapılabilmelidir.", set(), "FUNCTIONAL"),
    ("Teletıp görüşmeleri uçtan uca şifrelenmiş video altyapısı üzerinden gerçekleştirilmelidir.", set(), "NON_FUNCTIONAL"),
    ("Kan bankası envanter takibi FIFO prensibiyle yönetilmelidir.", set(), "FUNCTIONAL"),
]

assert len(GROUND_TRUTH) == 30, f"Beklenen 30, bulunan {len(GROUND_TRUTH)}"


def _norm(s: str) -> str:
    return s.lower().replace("\u0307", "")


def evaluate():
    ner = EntityRecognizer()
    clf = RequirementClassifier()

    actor_tp = actor_fp = actor_fn = 0
    clf_correct = clf_total = 0

    print("=" * 80)
    print("HEALTHCARE HELD-OUT CORPUS — 30 cümle (generalization)")
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
        "total_sentences": 30,
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
