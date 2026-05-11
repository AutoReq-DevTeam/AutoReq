"""60 bağımsız gereksinim ile classifier doğruluk testi (LLM dahil)."""
from dotenv import load_dotenv
load_dotenv()

from core.classifier import RequirementClassifier, _FR_VERB_RE
from core.models import Requirement

CASES = [
    # E-TİCARET
    ('Müşteri ürünü sepete ekleyebilmelidir.',                                'FUNCTIONAL'),
    ('Kullanıcı siparişini iptal edebilmeli.',                               'FUNCTIONAL'),
    ('Ödeme sayfası 1.5 saniyede yüklenmelidir.',                            'NON_FUNCTIONAL'),
    ('Sistem anlık 5.000 eşzamanlı alışverişi desteklemelidir.',             'NON_FUNCTIONAL'),
    ('Müşteri iade talebini form üzerinden iletebilmeli.',                   'FUNCTIONAL'),
    ('Ödeme verileri PCI-DSS standartlarına uygun saklanmalıdır.',           'NON_FUNCTIONAL'),
    ('Kullanıcı favori ürünlerini listeleyebilmelidir.',                     'FUNCTIONAL'),
    ('Sepet sayfası mobil cihazlarda hatasız görüntülenmelidir.',            'NON_FUNCTIONAL'),
    ('Admin indirim kuponu oluşturabilmeli.',                                'FUNCTIONAL'),
    ('Ürün görselleri 200ms içinde yüklenmelidir.',                          'NON_FUNCTIONAL'),
    # SAĞLIK
    ('Doktor hasta randevularını onaylayabilmeli.',                           'FUNCTIONAL'),
    ('Hemşire ilaç dozunu kayıt altına alabilmelidir.',                      'FUNCTIONAL'),
    ('Hasta bilgileri KVKK kapsamında şifreli tutulmalıdır.',                'NON_FUNCTIONAL'),
    ('Acil durum bildirimleri 3 saniye içinde iletilmelidir.',               'NON_FUNCTIONAL'),
    ('Eczacı reçete geçmişini görüntüleyebilmeli.',                          'FUNCTIONAL'),
    ('Sistem kesintisiz 7/24 çalışmalıdır.',                                 'NON_FUNCTIONAL'),
    ('Hasta kan tahlili sonuçlarını indirebilmelidir.',                      'FUNCTIONAL'),
    ('Tıbbi kayıtlar yedeklenmiş ortamda saklanmalıdır.',                    'NON_FUNCTIONAL'),
    # EĞİTİM
    ('Öğrenci sınav sonuçlarını görüntüleyebilmeli.',                        'FUNCTIONAL'),
    ('Öğretmen ödev yükleyebilmelidir.',                                     'FUNCTIONAL'),
    ('Platform eşzamanlı 10.000 öğrenciyi desteklemelidir.',                 'NON_FUNCTIONAL'),
    ('Veli öğrencinin devam durumunu takip edebilmeli.',                     'FUNCTIONAL'),
    ('Sistem %99 uptime garantisi sunmalıdır.',                              'NON_FUNCTIONAL'),
    ('Eğitmen canlı ders başlatabilmeli.',                                   'FUNCTIONAL'),
    # FİNANS
    ('Kullanıcı EFT transferi gerçekleştirebilmeli.',                        'FUNCTIONAL'),
    ('İşlem geçmişi son 5 yıl için saklanmalıdır.',                          'NON_FUNCTIONAL'),
    ('Para transferleri SSL/TLS üzerinden iletilmelidir.',                    'NON_FUNCTIONAL'),
    ('Kullanıcı banka hesap özetini PDF olarak indirebilmeli.',              'FUNCTIONAL'),
    ('Sistem şüpheli işlemleri otomatik tespit etmelidir.',                  'NON_FUNCTIONAL'),
    ('Müşteri kredi kartı limitini görüntüleyebilmeli.',                     'FUNCTIONAL'),
    ('Yanıt süresi yoğun saatlerde 500ms geçmemelidir.',                     'NON_FUNCTIONAL'),
    ('Yetkili kullanıcı hesap dondurabilmelidir.',                           'FUNCTIONAL'),
    # LOJİSTİK
    ('Kurye teslimat adresini güncelleyebilmeli.',                           'FUNCTIONAL'),
    ('Sistem günde 50.000 kargo talebini işleyebilmelidir.',                 'NON_FUNCTIONAL'),
    ('Müşteri kargo takip numarasını sorgulayabilmeli.',                     'FUNCTIONAL'),
    ('Rota optimizasyon algoritması 2 saniyede sonuç üretmelidir.',          'NON_FUNCTIONAL'),
    ('Depo sorumlusu stok sayımı başlatabilmeli.',                           'FUNCTIONAL'),
    # IoT
    ('Sensör verileri 100ms aralıklarla iletilmelidir.',                     'NON_FUNCTIONAL'),
    ('Operatör cihaz kalibrasyonu başlatabilmeli.',                          'FUNCTIONAL'),
    ('Sistem düşük bant genişliğinde de çalışmalıdır.',                      'NON_FUNCTIONAL'),
    ('Teknisyen hata loglarını dışa aktarabilmeli.',                         'FUNCTIONAL'),
    ('Cihaz %95 uptime hedefini karşılamalıdır.',                            'NON_FUNCTIONAL'),
    # ZOR SINIR VAKALAR
    ('Admin güvenlik raporlarını dışa aktarabilmeli.',                       'FUNCTIONAL'),
    ('Kullanıcı yedek dosyasını silebilmeli.',                               'FUNCTIONAL'),
    ('Moderatör içerik güvenlik loglarını inceleyebilmeli.',                 'FUNCTIONAL'),
    ('Kullanıcı yükleme işlemi 30 saniye içinde tamamlanabilmelidir.',       'NON_FUNCTIONAL'),
    ('Sistem 10.000 kaydı listeleyebilmeli ancak yanıt 2sn geçmemeli.',      'NON_FUNCTIONAL'),
    ('Uygulama tüm modern tarayıcılarda tutarlı görünmelidir.',              'NON_FUNCTIONAL'),
    ('Sistem çökme sonrası otomatik olarak yeniden başlamalıdır.',           'NON_FUNCTIONAL'),
    ('Sistem ISO 27001 standartlarına uygun olmalıdır.',                     'NON_FUNCTIONAL'),
    ('Kullanıcı standart bir kayıt formu doldurabilmeli.',                   'FUNCTIONAL'),
    ('Yönetici kullanıcıları görüntüleyebilmeli ve silebilmeli.',            'FUNCTIONAL'),
    ('Raporlar hem PDF hem CSV formatında indirilebilmelidir.',              'FUNCTIONAL'),
    ('Kullanıcı parolası en az 8 karakter olmalıdır.',                       'NON_FUNCTIONAL'),
    ('Oturum 30 dakika işlem yapılmadığında otomatik kapatılmalıdır.',       'NON_FUNCTIONAL'),
    ('Koordinatör proje raporunu onaylayabilmeli.',                          'FUNCTIONAL'),
    ('Analist veri setini filtreleyebilmeli.',                               'FUNCTIONAL'),
    ('Sistem hatalı girişlerde kullanıcıyı uyarmalıdır.',                    'FUNCTIONAL'),
    ('Arayüz yüksek kontrast modunu desteklemelidir.',                       'NON_FUNCTIONAL'),
    ('Veriler kullanıcı onayı alınmadan üçüncü taraflarla paylaşılmamalıdır.', 'NON_FUNCTIONAL'),
]


def run():
    clf = RequirementClassifier()
    failures = []
    layer_counts = {'K1': 0, 'K2': 0, 'K3': 0}

    for i, (t, e) in enumerate(CASES, 1):
        r = Requirement(id='T', text=t)
        tl = t.lower()
        has_strong = clf._has_strong_nfr_kw(tl)
        has_num    = any(p.search(tl) for p in clf.nfr_numeric_patterns)
        has_fr     = bool(_FR_VERB_RE.search(tl))
        has_amb    = any(kw in tl for kw in clf._ambiguous_nfr_keywords)
        layer = 'K1' if (has_fr and not has_strong and not has_num) else \
                ('K2' if (has_strong or has_num or has_amb) else 'K3')

        clf.classify(r)
        ok = r.req_type == e
        layer_counts[layer] += 1
        mark = 'OK' if ok else 'XX'
        llm_tag = '*' if layer == 'K3' else ' '
        print(f'{mark} {i:2} {layer}{llm_tag} {r.req_type:14} {e:14} {t[:52]}')
        if not ok:
            failures.append((layer, r.req_type, e, t))

    pct = (60 - len(failures)) / 60 * 100
    print(f'\nDogruluk: {60-len(failures)}/60 = %{pct:.1f}')
    print(f'K1={layer_counts["K1"]}  K2={layer_counts["K2"]}  K3/LLM={layer_counts["K3"]}')
    if failures:
        print(f'\nBasarisiz ({len(failures)}):')
        for layer, got, exp, t in failures:
            print(f'  [{layer}] got={got} exp={exp}')
            print(f'       {t}')


if __name__ == '__main__':
    run()
