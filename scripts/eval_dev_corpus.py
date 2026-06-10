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

# === GROUND TRUTH ===
# Her tuple: (cümle, beklenen_aktörler, beklenen_tip, domain)
# Aktörler: set — en az biri bulunmalı (recall), fazladan bulunan precision'ı düşürür

GROUND_TRUTH = [
    # ── 01 E-TİCARET (13) ──
    ("Kullanıcı sepetine ürün ekleyebilmeli ve ödeme adımına geçebilmelidir.", {"kullanıcı"}, "FUNCTIONAL", "e-ticaret"),
    ("Ödeme sayfasında kullanıcı oturumu zorunlu olmamalı; misafir kullanıcı da ödeme yapabilmelidir.", {"kullanıcı", "misafir kullanıcı"}, "FUNCTIONAL", "e-ticaret"),
    ("Ödeme sayfasına erişim yalnızca kayıtlı ve giriş yapmış kullanıcılara açık olmalıdır.", {"kullanıcı"}, "FUNCTIONAL", "e-ticaret"),
    ("Sistem, stokta olmayan ürünleri sepete eklenmesine izin vermemelidir.", set(), "FUNCTIONAL", "e-ticaret"),
    ("Sistem, stokta olmayan ürünler sepete eklenebilmeli; ancak ödeme sırasında uyarı gösterilmelidir.", set(), "FUNCTIONAL", "e-ticaret"),
    ("Kullanıcı, siparişini tamamlamadan önce adres bilgisini girmek zorunda olmamalıdır.", {"kullanıcı"}, "FUNCTIONAL", "e-ticaret"),
    ("Her sipariş için geçerli bir teslimat adresi zorunlu tutulmalıdır.", set(), "FUNCTIONAL", "e-ticaret"),
    ("İndirim kuponu yalnızca bir kez kullanılabilmelidir.", set(), "FUNCTIONAL", "e-ticaret"),
    ("Aynı kupon kodu birden fazla siparişe uygulanabilmelidir.", set(), "FUNCTIONAL", "e-ticaret"),
    ("Kredi kartı bilgileri sunucuda saklanmamalı; yalnızca tokenize hali tutulmalıdır.", set(), "NON_FUNCTIONAL", "e-ticaret"),
    ("Hızlı ödeme için kart bilgileri kullanıcı onayıyla kaydedilebilmelidir.", {"kullanıcı"}, "FUNCTIONAL", "e-ticaret"),
    ("Sistem, sipariş tamamlandıktan sonra stok miktarını otomatik güncellenmelidir.", set(), "FUNCTIONAL", "e-ticaret"),
    ("Stok güncellemesi yalnızca kargo firmasi teslimatı onayladıktan sonra yapılmalıdır.", {"kargo firması"}, "FUNCTIONAL", "e-ticaret"),

    # ── 02 BANKACILIK (10) ──
    ("Müşteri mobil uygulama üzerinden hesap bakiyesini görüntüleyebilmelidir.", {"müşteri"}, "FUNCTIONAL", "bankacılık"),
    ("Müşteri EFT ve havale işlemi gerçekleştirebilmelidir.", {"müşteri"}, "FUNCTIONAL", "bankacılık"),
    ("Müşteri kredi kartı ekstresi PDF olarak indirilebilmelidir.", {"müşteri"}, "FUNCTIONAL", "bankacılık"),
    ("Müşteri döviz alım satım işlemi yapabilmelidir.", {"müşteri"}, "FUNCTIONAL", "bankacılık"),
    ("Yatırım fonu alım satımı mobil uygulama üzerinden gerçekleştirilebilmelidir.", set(), "FUNCTIONAL", "bankacılık"),
    ("Müşteri şube randevusu oluşturabilmelidir.", {"müşteri"}, "FUNCTIONAL", "bankacılık"),
    ("Müşteri destek hattını uygulama içinden arayabilmelidir.", {"müşteri"}, "FUNCTIONAL", "bankacılık"),
    ("Hesap hareketleri son 1 yıla ait olacak şekilde listelenebilmelidir.", set(), "FUNCTIONAL", "bankacılık"),
    ("Müşteri IBAN ile para transferi yapabilmelidir.", {"müşteri"}, "FUNCTIONAL", "bankacılık"),
    ("Bildirim tercihleri uygulama içinden yönetilebilmelidir.", set(), "FUNCTIONAL", "bankacılık"),

    # ── 03 EĞİTİM / MUĞLAK (12) ──
    ("Sistem hızlı olmalıdır.", set(), "NON_FUNCTIONAL", "eğitim"),
    ("Öğrenciler sistemi kolayca kullanabilmelidir.", {"öğrenci"}, "NON_FUNCTIONAL", "eğitim"),
    ("Platform güvenli olmalıdır.", set(), "NON_FUNCTIONAL", "eğitim"),
    ("İçerikler kaliteli sunulmalıdır.", set(), "NON_FUNCTIONAL", "eğitim"),
    ("Sistem her zaman erişilebilir olmalıdır.", set(), "NON_FUNCTIONAL", "eğitim"),
    ("Bildirimler zamanında gönderilmelidir.", set(), "NON_FUNCTIONAL", "eğitim"),
    ("Öğretmen raporları düzenli paylaşabilmelidir.", {"öğretmen"}, "FUNCTIONAL", "eğitim"),
    ("Sistem yüksek trafiği kaldırabilmelidir.", set(), "NON_FUNCTIONAL", "eğitim"),
    ("Arayüz kullanıcı dostu tasarlanmalıdır.", set(), "NON_FUNCTIONAL", "eğitim"),
    ("Veri güvenli saklanmalıdır.", set(), "NON_FUNCTIONAL", "eğitim"),
    ("Sistem ölçeklenebilir olmalıdır.", set(), "NON_FUNCTIONAL", "eğitim"),
    ("Uygulama farklı cihazlarda düzgün çalışmalıdır.", set(), "NON_FUNCTIONAL", "eğitim"),

    # ── 04 KURUMSAL PORTAL (13) ──
    ("Çalışan kendi izin taleplerini sisteme girebilmelidir.", {"çalışan"}, "FUNCTIONAL", "kurumsal"),
    ("Yönetici, ekibindeki çalışanların izin taleplerini onaylayabilmeli veya reddedebilmelidir.", {"yönetici"}, "FUNCTIONAL", "kurumsal"),
    ("İK uzmanı, tüm departmanlardaki izin süreçlerini raporlayabilmelidir.", {"ik uzmanı"}, "FUNCTIONAL", "kurumsal"),
    ("Sistem yöneticisi kullanıcı yetki matrisini güncelleyebilmelidir.", {"sistem yöneticisi"}, "FUNCTIONAL", "kurumsal"),
    ("Çalışan bordro bilgilerini görüntüleyebilmeli; yalnızca kendi bilgilerine erişebilmelidir.", {"çalışan"}, "FUNCTIONAL", "kurumsal"),
    ("İK uzmanı, çalışan özlük dosyasına belge ekleyebilmelidir.", {"ik uzmanı"}, "FUNCTIONAL", "kurumsal"),
    ("Yönetici, ekibinin performans değerlendirme formlarını doldurabilmelidir.", {"yönetici"}, "FUNCTIONAL", "kurumsal"),
    ("Çalışan, kendi performans değerlendirme sonuçlarını görüntüleyebilmelidir.", {"çalışan"}, "FUNCTIONAL", "kurumsal"),
    ("Sistem yöneticisi denetim loglarını inceleyebilmelidir.", {"sistem yöneticisi"}, "FUNCTIONAL", "kurumsal"),
    ("Finans müdürü, departman bazlı bütçe raporlarını Excel olarak dışa aktarabilmelidir.", {"finans müdürü"}, "FUNCTIONAL", "kurumsal"),
    ("İK uzmanı, işe alım süreçlerini sistemde takip edebilmelidir.", {"ik uzmanı"}, "FUNCTIONAL", "kurumsal"),
    ("Aday, iş başvurusunu portal üzerinden gerçekleştirebilmelidir.", {"aday"}, "FUNCTIONAL", "kurumsal"),
    ("Yönetici, departmanına yeni çalışan ataması yapabilmelidir.", {"yönetici"}, "FUNCTIONAL", "kurumsal"),

    # ── 05 MOBİL APP / NFR AĞIRLIKLI (15) ──
    ("Uygulama, Android 10 ve üzeri ile iOS 15 ve üzeri sürümlerde çalışmalıdır.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Uygulama açılış süresi soğuk başlatmada 3 saniyeyi geçmemelidir.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Sayfa geçişleri 500 milisaniyenin altında tamamlanmalıdır.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Uygulama, 10.000 eş zamanlı kullanıcıyı desteklemelidir.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Çevrimdışı modda son 7 günlük veri önbellekten erişilebilir olmalıdır.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Uygulama batarya tüketimi günde 2 saat aktif kullanımda %5'i geçmemelidir.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Tüm ağ iletişimi TLS 1.3 protokolüyle şifrelenmelidir.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Kullanıcı oturumu 30 dakika hareketsizlikte otomatik sonlandırılmalıdır.", {"kullanıcı"}, "NON_FUNCTIONAL", "mobil"),
    ("Biyometrik doğrulama (parmak izi, yüz tanıma) desteklenmelidir.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Uygulama %99,9 SLA hedefini karşılamalıdır.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Crash oranı aylık aktif kullanıcı başına %0,1'in altında tutulmalıdır.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Erişilebilirlik standartları (WCAG 2.1 AA) uyumlu olunmalıdır.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Kişisel veriler KVKK ve GDPR gerekliliklerine uygun şekilde işlenmelidir.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Uygulama boyutu 50 MB'ı geçmemelidir.", set(), "NON_FUNCTIONAL", "mobil"),
    ("Push bildirim iletim süresi 5 saniyeyi geçmemelidir.", set(), "NON_FUNCTIONAL", "mobil"),
]

assert len(GROUND_TRUTH) == 63, f"Beklenen 63 cümle, bulunan {len(GROUND_TRUTH)}"


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
        "total_sentences": 63,
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
