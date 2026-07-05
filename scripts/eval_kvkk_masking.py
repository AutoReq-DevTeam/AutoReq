import json
import os
import sys
import re

# Add repo to sys.path
sys.path.insert(0, "/home/knover/Documents/GitHub/AutoReq")

from core.preprocessor import TextPreprocessor

TEST_CASES = [
    {
        "text": "Talep formu Ahmet Yılmaz tarafından 12345678901 TC numarası ile onaylanmalıdır.",
        "expected_masked": "Talep formu [KISI_ADI] tarafından [TC_KIMLIK_NO] TC numarası ile onaylanmalıdır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Ahmet Yılmaz"},
            {"type": "TC_KIMLIK_NO", "val": "12345678901"}
        ]
    },
    {
        "text": "Sn. Mehmet Kaya sisteme mehmet.kaya@example.com adresi üzerinden kayıt olabilir.",
        "expected_masked": "Sn. [KISI_ADI] sisteme [EPOSTA] adresi üzerinden kayıt olabilir.",
        "entities": [
            {"type": "KISI_ADI", "val": "Mehmet Kaya"},
            {"type": "EPOSTA", "val": "mehmet.kaya@example.com"}
        ]
    },
    {
        "text": "Kullanıcı destek hattına +905551234567 numarasından ulaşabilmelidir.",
        "expected_masked": "Kullanıcı destek hattına [TELEFON] numarasından ulaşabilmelidir.",
        "entities": [
            {"type": "TELEFON", "val": "+905551234567"}
        ]
    },
    {
        "text": "Dr. Canan Dağdeviren için portal üzerinde yeni randevu oluşturulmalıdır.",
        "expected_masked": "Dr. [KISI_ADI] için portal üzerinde yeni randevu oluşturulmalıdır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Canan Dağdeviren"}
        ]
    },
    {
        "text": "Ayşe Hanım izin talebini ayse.kaya@firma.com.tr e-posta adresinden İK birimine iletti.",
        "expected_masked": "[KISI_ADI] Hanım izin talebini [EPOSTA] e-posta adresinden İK birimine iletti.",
        "entities": [
            {"type": "KISI_ADI", "val": "Ayşe"},
            {"type": "EPOSTA", "val": "ayse.kaya@firma.com.tr"}
        ]
    },
    {
        "text": "Ali Bey yeni parolasını 0542-987-65-43 numaralı telefona gelen SMS kodu ile doğrulamalıdır.",
        "expected_masked": "[KISI_ADI] Bey yeni parolasını [TELEFON] numaralı telefona gelen SMS kodu ile doğrulamalıdır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Ali"},
            {"type": "TELEFON", "val": "0542-987-65-43"}
        ]
    },
    {
        "text": "Sistem, fatura detaylarını avukatımız Av. Burak Demir ile paylaşmalıdır.",
        "expected_masked": "Sistem, fatura detaylarını avukatımız Av. [KISI_ADI] ile paylaşmalıdır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Burak Demir"}
        ]
    },
    {
        "text": "Müşteri temsilcisi Kemal Bey ile 0212 345 67 89 numarasından irtibat kurulabilir.",
        "expected_masked": "Müşteri temsilcisi [KISI_ADI] Bey ile [TELEFON] numarasından irtibat kurulabilir.",
        "entities": [
            {"type": "KISI_ADI", "val": "Kemal"},
            {"type": "TELEFON", "val": "0212 345 67 89"}
        ]
    },
    {
        "text": "Veri tabanında kayıtlı olan 98765432109 kimlik numaralı kullanıcının hesabı askıya alınmalıdır.",
        "expected_masked": "Veri tabanında kayıtlı olan [TC_KIMLIK_NO] kimlik numaralı kullanıcının hesabı askıya alınmalıdır.",
        "entities": [
            {"type": "TC_KIMLIK_NO", "val": "98765432109"}
        ]
    },
    {
        "text": "Ecz. Fatma Kara reçete bilgilerini eczane.sistemi@saglik.gov.tr adresine iletmelidir.",
        "expected_masked": "Ecz. [KISI_ADI] reçete bilgilerini [EPOSTA] adresine iletmelidir.",
        "entities": [
            {"type": "KISI_ADI", "val": "Fatma Kara"},
            {"type": "EPOSTA", "val": "eczane.sistemi@saglik.gov.tr"}
        ]
    },
    {
        "text": "Sistem yöneticisi Mustafa Yılmaz (mustafa.yilmaz@sirket.com) yeni yedeklemeyi tetiklemelidir.",
        "expected_masked": "Sistem yöneticisi [KISI_ADI] ([EPOSTA]) yeni yedeklemeyi tetiklemelidir.",
        "entities": [
            {"type": "KISI_ADI", "val": "Mustafa Yılmaz"},
            {"type": "EPOSTA", "val": "mustafa.yilmaz@sirket.com"}
        ]
    },
    {
        "text": "Müşteri Zeynep Öztürk, zeynep.ozturk@gmail.com ve 05331112233 bilgileriyle kaydoldu.",
        "expected_masked": "Müşteri [KISI_ADI], [EPOSTA] ve [TELEFON] bilgileriyle kaydoldu.",
        "entities": [
            {"type": "KISI_ADI", "val": "Zeynep Öztürk"},
            {"type": "EPOSTA", "val": "zeynep.ozturk@gmail.com"},
            {"type": "TELEFON", "val": "05331112233"}
        ]
    },
    {
        "text": "Lütfen destek için info@firma.com adresi veya 0216-555-44-33 numarası ile iletişime geçiniz.",
        "expected_masked": "Lütfen destek için [EPOSTA] adresi veya [TELEFON] numarası ile iletişime geçiniz.",
        "entities": [
            {"type": "EPOSTA", "val": "info@firma.com"},
            {"type": "TELEFON", "val": "0216-555-44-33"}
        ]
    },
    {
        "text": "Prof. Dr. Hasan Şahin, hastanın durumunu izleme paneline kaydetti.",
        "expected_masked": "Prof. Dr. [KISI_ADI], hastanın durumunu izleme paneline kaydetti.",
        "entities": [
            {"type": "KISI_ADI", "val": "Hasan Şahin"}
        ]
    },
    {
        "text": "Hasta Yakup Yıldız için 55432109876 kimlik numarasıyla kayıt açılmalıdır.",
        "expected_masked": "Hasta [KISI_ADI] için [TC_KIMLIK_NO] kimlik numarasıyla kayıt açılmalıdır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Yakup Yıldız"},
            {"type": "TC_KIMLIK_NO", "val": "55432109876"}
        ]
    },
    {
        "text": "İletişim adresi olarak muhasebe@sirketimiz.com ve telefon 0 (544) 333 22 11 kaydedildi.",
        "expected_masked": "İletişim adresi olarak [EPOSTA] ve telefon [TELEFON] kaydedildi.",
        "entities": [
            {"type": "EPOSTA", "val": "muhasebe@sirketimiz.com"},
            {"type": "TELEFON", "val": "0 (544) 333 22 11"}
        ]
    },
    {
        "text": "Sayın Merve Can, m.can@edu.tr e-posta adresinize doğrulama linki gönderildi.",
        "expected_masked": "Sayın [KISI_ADI], [EPOSTA] e-posta adresinize doğrulama linki gönderildi.",
        "entities": [
            {"type": "KISI_ADI", "val": "Merve Can"},
            {"type": "EPOSTA", "val": "m.can@edu.tr"}
        ]
    },
    {
        "text": "Yönetici Can Bey, yeni yetki tablosunu onayladı.",
        "expected_masked": "Yönetici [KISI_ADI] Bey, yeni yetki tablosunu onayladı.",
        "entities": [
            {"type": "KISI_ADI", "val": "Can"}
        ]
    },
    {
        "text": "Teknisyen Ahmet, sunucu arızasını gidermek için ahmet.teknisyen@gmail.com adresinden bilgilendirildi.",
        "expected_masked": "Teknisyen [KISI_ADI], sunucu arızasını gidermek için [EPOSTA] adresinden bilgilendirildi.",
        "entities": [
            {"type": "KISI_ADI", "val": "Ahmet"},
            {"type": "EPOSTA", "val": "ahmet.teknisyen@gmail.com"}
        ]
    },
    {
        "text": "Sözleşme Dr. Elif Yılmaz ile imzalandı ve tc numarası 45678901234 olarak kaydedildi.",
        "expected_masked": "Sözleşme Dr. [KISI_ADI] ile imzalandı ve tc numarası [TC_KIMLIK_NO] olarak kaydedildi.",
        "entities": [
            {"type": "KISI_ADI", "val": "Elif Yılmaz"},
            {"type": "TC_KIMLIK_NO", "val": "45678901234"}
        ]
    },
    {
        "text": "Sn. Hakan Demirci, 05324445566 numaralı hattınız üzerinden aranacaksınız.",
        "expected_masked": "Sn. [KISI_ADI], [TELEFON] numaralı hattınız üzerinden aranacaksınız.",
        "entities": [
            {"type": "KISI_ADI", "val": "Hakan Demirci"},
            {"type": "TELEFON", "val": "05324445566"}
        ]
    },
    {
        "text": "Müşterimiz Selim Koç (selim@koc.com.tr) siparişini tamamladı.",
        "expected_masked": "Müşterimiz [KISI_ADI] ([EPOSTA]) siparişini tamamladı.",
        "entities": [
            {"type": "KISI_ADI", "val": "Selim Koç"},
            {"type": "EPOSTA", "val": "selim@koc.com.tr"}
        ]
    },
    {
        "text": "Eczacı Murat Bey, murat.eczaci@gmail.com adresine sipariş formunu gönderdi.",
        "expected_masked": "Eczacı [KISI_ADI] Bey, [EPOSTA] adresine sipariş formunu gönderdi.",
        "entities": [
            {"type": "KISI_ADI", "val": "Murat"},
            {"type": "EPOSTA", "val": "murat.eczaci@gmail.com"}
        ]
    },
    {
        "text": "Laborant Gözde Çelik, gozde.celik@hastane.org e-posta adresini kullanmaktadır.",
        "expected_masked": "Laborant [KISI_ADI], [EPOSTA] e-posta adresini kullanmaktadır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Gözde Çelik"},
            {"type": "EPOSTA", "val": "gozde.celik@hastane.org"}
        ]
    },
    {
        "text": "TC kimlik numarası 98765432101 olan Hüseyin Aksoy sistemde aktiftir.",
        "expected_masked": "TC kimlik numarası [TC_KIMLIK_NO] olan [KISI_ADI] sistemde aktiftir.",
        "entities": [
            {"type": "TC_KIMLIK_NO", "val": "98765432101"},
            {"type": "KISI_ADI", "val": "Hüseyin Aksoy"}
        ]
    },
    {
        "text": "Destek elemanı Tarık Bey, 0535-999-88-77 numaralı telefondan çağrıları yanıtlamalıdır.",
        "expected_masked": "Destek elemanı [KISI_ADI] Bey, [TELEFON] numaralı telefondan çağrıları yanıtlamalıdır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Tarık"},
            {"type": "TELEFON", "val": "0535-999-88-77"}
        ]
    },
    {
        "text": "Finans müdürü Sn. Burak Kaya, burak.kaya@sirket.com adresinden bütçe raporunu iletti.",
        "expected_masked": "Finans müdürü Sn. [KISI_ADI], [EPOSTA] adresinden bütçe raporunu iletti.",
        "entities": [
            {"type": "KISI_ADI", "val": "Burak Kaya"},
            {"type": "EPOSTA", "val": "burak.kaya@sirket.com"}
        ]
    },
    {
        "text": "Hemşire Fatma Hanım, fatma@hastane.org e-postasını kontrol etmelidir.",
        "expected_masked": "Hemşire [KISI_ADI] Hanım, [EPOSTA] e-postasını kontrol etmelidir.",
        "entities": [
            {"type": "KISI_ADI", "val": "Fatma"},
            {"type": "EPOSTA", "val": "fatma@hastane.org"}
        ]
    },
    {
        "text": "Geliştirici Ömer Faruk Aksoy, omer.faruk@kod.com adresi üzerinden kod repolarına erişebilir.",
        "expected_masked": "Geliştirici [KISI_ADI], [EPOSTA] adresi üzerinden kod repolarına erişebilir.",
        "entities": [
            {"type": "KISI_ADI", "val": "Ömer Faruk Aksoy"},
            {"type": "EPOSTA", "val": "omer.faruk@kod.com"}
        ]
    },
    {
        "text": "Kurye Ahmet Bey, 0555-888-22-11 numaralı telefondan müşteriyle iletişim kurmalıdır.",
        "expected_masked": "Kurye [KISI_ADI] Bey, [TELEFON] numaralı telefondan müşteriyle iletişim kurmalıdır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Ahmet"},
            {"type": "TELEFON", "val": "0555-888-22-11"}
        ]
    },
    {
        "text": "Müşteri Ayşe Çetin, 12121212121 TC kimlik numarasıyla kayıt yaptırmalıdır.",
        "expected_masked": "Müşteri [KISI_ADI], [TC_KIMLIK_NO] TC kimlik numarasıyla kayıt yaptırmalıdır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Ayşe Çetin"},
            {"type": "TC_KIMLIK_NO", "val": "12121212121"}
        ]
    },
    {
        "text": "Sayın Gökhan Kara, gokhan.kara@gmail.com adresinize yeni teklif formu iletildi.",
        "expected_masked": "Sayın [KISI_ADI], [EPOSTA] adresinize yeni teklif formu iletildi.",
        "entities": [
            {"type": "KISI_ADI", "val": "Gökhan Kara"},
            {"type": "EPOSTA", "val": "gokhan.kara@gmail.com"}
        ]
    },
    {
        "text": "Sistem admini Fatma Hanım, 05412223344 numarasını doğrulama için kullanmalıdır.",
        "expected_masked": "Sistem admini [KISI_ADI] Hanım, [TELEFON] numarasını doğrulama için kullanmalıdır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Fatma"},
            {"type": "TELEFON", "val": "05412223344"}
        ]
    },
    {
        "text": "Av. Mehmet Öztürk, mehmet.ozturk@hukuk.com adresi üzerinden sözleşmeyi paylaştı.",
        "expected_masked": "Av. [KISI_ADI], [EPOSTA] adresi üzerinden sözleşmeyi paylaştı.",
        "entities": [
            {"type": "KISI_ADI", "val": "Mehmet Öztürk"},
            {"type": "EPOSTA", "val": "mehmet.ozturk@hukuk.com"}
        ]
    },
    {
        "text": "Lütfen 22222222222 TC numaralı Selin Kaya için veri maskeleme testi yapınız.",
        "expected_masked": "Lütfen [TC_KIMLIK_NO] TC numaralı [KISI_ADI] için veri maskeleme testi yapınız.",
        "entities": [
            {"type": "TC_KIMLIK_NO", "val": "22222222222"},
            {"type": "KISI_ADI", "val": "Selin Kaya"}
        ]
    },
    {
        "text": "Doktor Ahmet Bey, 0533 999 88 77 numarasından hastayı arayabilmelidir.",
        "expected_masked": "Doktor [KISI_ADI] Bey, [TELEFON] numarasından hastayı arayabilmelidir.",
        "entities": [
            {"type": "KISI_ADI", "val": "Ahmet"},
            {"type": "TELEFON", "val": "0533 999 88 77"}
        ]
    },
    {
        "text": "Sn. Yasemin Yalçın, yasemin.yalcin@outlook.com adresi üzerinden sisteme giriş yaptı.",
        "expected_masked": "Sn. [KISI_ADI], [EPOSTA] adresi üzerinden sisteme giriş yaptı.",
        "entities": [
            {"type": "KISI_ADI", "val": "Yasemin Yalçın"},
            {"type": "EPOSTA", "val": "yasemin.yalcin@outlook.com"}
        ]
    },
    {
        "text": "Analist Kemal Çelik, kemal.celik@analiz.com adresini kullanmaktadır.",
        "expected_masked": "Analist [KISI_ADI], [EPOSTA] adresini kullanmaktadır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Kemal Çelik"},
            {"type": "EPOSTA", "val": "kemal.celik@analiz.com"}
        ]
    },
    {
        "text": "Kullanıcı Meral Hanım, meral.hanim@gmail.com adresinden yeni şifre talep etti.",
        "expected_masked": "Kullanıcı [KISI_ADI] Hanım, [EPOSTA] adresinden yeni şifre talep etti.",
        "entities": [
            {"type": "KISI_ADI", "val": "Meral"},
            {"type": "EPOSTA", "val": "meral.hanim@gmail.com"}
        ]
    },
    {
        "text": "Müşteri Hizmetleri Temsilcisi Ali Bey, 0212 999 88 77 numarasından bilgi verecektir.",
        "expected_masked": "Müşteri Hizmetleri Temsilcisi [KISI_ADI] Bey, [TELEFON] numarasından bilgi verecektir.",
        "entities": [
            {"type": "KISI_ADI", "val": "Ali"},
            {"type": "TELEFON", "val": "0212 999 88 77"}
        ]
    },
    {
        "text": "Lütfen test.user@example.com ve 33333333333 TC numaralı kullanıcının kaydını güncelleyin.",
        "expected_masked": "Lütfen [EPOSTA] ve [TC_KIMLIK_NO] TC numaralı kullanıcının kaydını güncelleyin.",
        "entities": [
            {"type": "EPOSTA", "val": "test.user@example.com"},
            {"type": "TC_KIMLIK_NO", "val": "33333333333"}
        ]
    },
    {
        "text": "Sayın Veli Can, 0532-111-22-33 numaralı telefonunuz sistemde güncellenmiştir.",
        "expected_masked": "Sayın [KISI_ADI], [TELEFON] telefonunuz sistemde güncellenmiştir.",
        "entities": [
            {"type": "KISI_ADI", "val": "Veli Can"},
            {"type": "TELEFON", "val": "0532-111-22-33"}
        ]
    },
    {
        "text": "Teknisyen Canan Hanım, canan.teknik@sirket.com adresinden sunucu durumunu raporladı.",
        "expected_masked": "Teknisyen [KISI_ADI] Hanım, [EPOSTA] adresinden sunucu durumunu raporladı.",
        "entities": [
            {"type": "KISI_ADI", "val": "Canan"},
            {"type": "EPOSTA", "val": "canan.teknik@sirket.com"}
        ]
    },
    {
        "text": "Dr. Halil İbrahim Kaya, halil.kaya@hastane.gov.tr e-posta adresini kaydettirdi.",
        "expected_masked": "Dr. [KISI_ADI], [EPOSTA] e-posta adresini kaydettirdi.",
        "entities": [
            {"type": "KISI_ADI", "val": "Halil İbrahim Kaya"},
            {"type": "EPOSTA", "val": "halil.kaya@hastane.gov.tr"}
        ]
    },
    {
        "text": "Kullanıcı Derya Yılmaz, 44444444444 TC numarasıyla doğrulama işlemini başlattı.",
        "expected_masked": "Kullanıcı [KISI_ADI], [TC_KIMLIK_NO] TC numarasıyla doğrulama işlemini başlattı.",
        "entities": [
            {"type": "KISI_ADI", "val": "Derya Yılmaz"},
            {"type": "TC_KIMLIK_NO", "val": "44444444444"}
        ]
    },
    {
        "text": "Sn. Mehmet Şimşek, 0543 987 65 43 numarasından onay kodu gönderildi.",
        "expected_masked": "Sn. [KISI_ADI], [TELEFON] numarasından onay kodu gönderildi.",
        "entities": [
            {"type": "KISI_ADI", "val": "Mehmet Şimşek"},
            {"type": "TELEFON", "val": "0543 987 65 43"}
        ]
    },
    {
        "text": "Hasta kabul memuru Fatma Beyza, fatma.beyza@saglik.gov.tr e-postasını kullanmaktadır.",
        "expected_masked": "Hasta kabul memuru [KISI_ADI], [EPOSTA] e-postasını kullanmaktadır.",
        "entities": [
            {"type": "KISI_ADI", "val": "Fatma Beyza"},
            {"type": "EPOSTA", "val": "fatma.beyza@saglik.gov.tr"}
        ]
    },
    {
        "text": "Müşterimiz Ahmet Demir (ahmet@demir.com.tr) sipariş durumunu sordu.",
        "expected_masked": "Müşterimiz [KISI_ADI] ([EPOSTA]) sipariş durumunu sordu.",
        "entities": [
            {"type": "KISI_ADI", "val": "Ahmet Demir"},
            {"type": "EPOSTA", "val": "ahmet@demir.com.tr"}
        ]
    },
    {
        "text": "Destek mühendisi Kerem Bey, 0216-999-88-77 numarasından yardım sağladı.",
        "expected_masked": "Destek mühendisi [KISI_ADI] Bey, [TELEFON] numarasından yardım sağladı.",
        "entities": [
            {"type": "KISI_ADI", "val": "Kerem"},
            {"type": "TELEFON", "val": "0216-999-88-77"}
        ]
    },
    {
        "text": "Sözleşme 55555555555 TC numaralı Hülya Öztürk ile tamamlanmıştır.",
        "expected_masked": "Sözleşme [TC_KIMLIK_NO] TC numaralı [KISI_ADI] ile tamamlanmıştır.",
        "entities": [
            {"type": "TC_KIMLIK_NO", "val": "55555555555"},
            {"type": "KISI_ADI", "val": "Hülya Öztürk"}
        ]
    }
]

def run_kvkk_evaluation():
    preprocessor = TextPreprocessor()
    
    results = []
    
    tp_count = 0
    fn_count = 0
    fp_count = 0  # To evaluate false positives (normal words masked as entities)
    
    entity_stats = {
        "KISI_ADI": {"tp": 0, "fn": 0, "fp": 0},
        "TC_KIMLIK_NO": {"tp": 0, "fn": 0, "fp": 0},
        "EPOSTA": {"tp": 0, "fn": 0, "fp": 0},
        "TELEFON": {"tp": 0, "fn": 0, "fp": 0}
    }
    
    print(f"Running KVKK masking validation on {len(TEST_CASES)} sentences...")
    
    for idx, case in enumerate(TEST_CASES, 1):
        text = case["text"]
        expected = case["expected_masked"]
        entities = case["entities"]
        
        actual = preprocessor.mask_kvkk(text)
        
        # Check matching of expected masked vs actual masked
        matched = (actual == expected)
        
        # Calculate entity level matches
        for ent in entities:
            ent_type = ent["type"]
            val = ent["val"]
            placeholder = f"[{ent_type}]"
            
            # If the entity placeholder exists in actual but the original value doesn't
            if placeholder in actual and val not in actual:
                entity_stats[ent_type]["tp"] += 1
                tp_count += 1
            else:
                entity_stats[ent_type]["fn"] += 1
                fn_count += 1
                
        # Count false positives
        # A false positive is a placeholder in actual that was not in expected
        for ent_type in ["KISI_ADI", "TC_KIMLIK_NO", "EPOSTA", "TELEFON"]:
            placeholder = f"[{ent_type}]"
            actual_count = actual.count(placeholder)
            expected_count = expected.count(placeholder)
            if actual_count > expected_count:
                diff = actual_count - expected_count
                entity_stats[ent_type]["fp"] += diff
                fp_count += diff
                
        results.append({
            "id": f"KVKK_{idx:03d}",
            "original": text,
            "expected": expected,
            "actual": actual,
            "match": matched
        })
        
    print("\n=== KVKK EVALUATION ENTITY STATS ===")
    overall_tp = 0
    overall_fp = 0
    overall_fn = 0
    
    for ent_type, stats in entity_stats.items():
        tp = stats["tp"]
        fn = stats["fn"]
        fp = stats["fp"]
        
        overall_tp += tp
        overall_fp += fp
        overall_fn += fn
        
        precision = tp / (tp + fp) * 100 if (tp + fp) > 0 else 100.0
        recall = tp / (tp + fn) * 100 if (tp + fn) > 0 else 100.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 100.0
        
        print(f"{ent_type:15} | TP={tp:2d}  FP={fp:2d}  FN={fn:2d} | Precision={precision:5.1f}%  Recall={recall:5.1f}%  F1={f1:5.1f}%")
        
    overall_precision = overall_tp / (overall_tp + overall_fp) * 100 if (overall_tp + overall_fp) > 0 else 100.0
    overall_recall = overall_tp / (overall_tp + overall_fn) * 100 if (overall_tp + overall_fn) > 0 else 100.0
    overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 100.0
    
    print("-" * 80)
    print(f"{'OVERALL':15} | TP={overall_tp:2d}  FP={overall_fp:2d}  FN={overall_fn:2d} | Precision={overall_precision:5.1f}%  Recall={overall_recall:5.1f}%  F1={overall_f1:5.1f}%")
    print("-" * 80)
    
    output_report = {
        "overall_precision": round(overall_precision, 2),
        "overall_recall": round(overall_recall, 2),
        "overall_f1": round(overall_f1, 2),
        "entity_stats": entity_stats,
        "results": results
    }
    
    artifact_dir = "/home/knover/.gemini/antigravity/brain/a10b89f1-3ed6-4ebb-9370-43c5ec74f343"
    
    # Save JSON report in repo and artifacts
    os.makedirs("/home/knover/Documents/GitHub/AutoReq/reports", exist_ok=True)
    with open("/home/knover/Documents/GitHub/AutoReq/reports/kvkk_masking_results.json", "w", encoding="utf-8") as f:
        json.dump(output_report, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(artifact_dir, "kvkk_masking_results.json"), "w", encoding="utf-8") as f:
        json.dump(output_report, f, ensure_ascii=False, indent=2)
        
    # Save CSV in artifacts
    import csv
    csv_path = os.path.join(artifact_dir, "kvkk_masking_results.csv")
    headers = ["id", "original", "expected", "actual", "match"]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"KVKK Masking results saved to {csv_path}")

if __name__ == "__main__":
    run_kvkk_evaluation()
