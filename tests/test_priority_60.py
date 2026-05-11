"""60 bağımsız gereksinim ile priority_detector doğruluk testi."""
from dotenv import load_dotenv
load_dotenv()

from core.priority_detector import PriorityDetector
from core.models import Requirement

CASES = [
    # === AÇIK HIGH ===
    ('Sistem güvenlik standartlarını karşılamalıdır.',              'HIGH'),
    ('Kullanıcı verileri mutlaka şifrelenmelidir.',                 'HIGH'),
    ('Ödeme altyapısı kritik güvenlik testlerinden geçmelidir.',    'HIGH'),
    ('Oturum yönetimi zorunlu kimlik doğrulama içermelidir.',       'HIGH'),
    ('Sistem asla yetkisiz veri erişimine izin vermemelidir.',      'HIGH'),
    ('Hasta bilgileri mahremiyet kapsamında korunmalıdır.',         'HIGH'),
    ('Şifre politikası mutlaka uygulanmalıdır.',                    'HIGH'),
    ('Kritik sistem bileşenleri yedekli çalışmalıdır.',             'HIGH'),
    ('Veri sızıntısı güvenlik ihlali olarak değerlendirilmelidir.', 'HIGH'),
    ('Admin erişimi zorunlu iki faktörlü doğrulama gerektirmelidir.','HIGH'),
    ('Sistem güvenli iletişim protokolü kullanmalıdır.',            'HIGH'),
    ('Tüm işlemler must audit log içermelidir.',                    'HIGH'),

    # === AÇIK LOW ===
    ('Tercihen koyu tema desteği eklenebilir.',                     'LOW'),
    ('İleride çoklu dil desteği düşünülebilir.',                    'LOW'),
    ('Animasyonlu geçiş efektleri opsiyonel olarak eklenebilir.',   'LOW'),
    ('Nice-to-have: kullanıcı özelleştirme paneli.',                'LOW'),
    ('Gelecek versiyonda sesli bildirim eklenebilir.',              'LOW'),
    ('Tercihen grafik dashboard sunulabilir.',                       'LOW'),
    ('İsteğe bağlı olarak widget desteği sağlanabilir.',            'LOW'),

    # === AÇIK MEDIUM (nötr) ===
    ('Kullanıcı sisteme giriş yapabilmelidir.',                     'MEDIUM'),
    ('Admin kullanıcı listesini görüntüleyebilmeli.',               'MEDIUM'),
    ('Müşteri sipariş takibi yapabilmeli.',                         'MEDIUM'),
    ('Sistem PDF rapor oluşturabilmelidir.',                        'MEDIUM'),
    ('Öğrenci sınav sonuçlarını görebilmeli.',                      'MEDIUM'),
    ('Kullanıcı şifresini sıfırlayabilmelidir.',                    'MEDIUM'),
    ('Doktor randevu takvimini güncelleyebilmeli.',                  'MEDIUM'),
    ('Ürün stok bilgisi sistemde tutulmalıdır.',                    'MEDIUM'),
    ('Kurye teslimat adresini güncelleyebilmeli.',                  'MEDIUM'),
    ('Raporlar Excel formatında indirilebilmelidir.',               'MEDIUM'),

    # === NEGASYON — HIGH kelimesi var ama olumsuz ===
    ('Bu özellik kritik değildir.',                                  'MEDIUM'),
    ('Güvenlik açığı olmaması zorunlu değildir.',                   'MEDIUM'),
    ('Mahremiyet gereksinimi olmayan bir alan.',                     'MEDIUM'),
    ('Sistem yükü altında çökmemeli demek zorunlu değil.',          'MEDIUM'),
    ('Kritik olmayan bir bileşen olarak değerlendirilebilir.',       'MEDIUM'),
    ('Güvenlik logu tutmak şart değildir.',                         'MEDIUM'),
    ('Mutlaka uygulanması gerekmiyor.',                             'MEDIUM'),
    ('Asla hata vermemeli demek abartılı bir beklentidir.',         'MEDIUM'),

    # === NEGASYON — LOW kelimesi var ama olumsuz (LOW kalmalı) ===
    ('İsteğe bağlı değil, tercihen zorunlu olarak eklenebilir.',    'LOW'),

    # === DOMAIN ÇEŞİTLİLİĞİ — HIGH ===
    ('Bankacılık işlemleri kritik güvenlik denetiminden geçmeli.',  'HIGH'),
    ('Tıbbi cihaz yazılımı zorunlu sertifikasyon şartlarını karşılamalı.', 'HIGH'),
    ('Uçuş kontrol sistemi asla hata vermemelidir.',                'HIGH'),
    ('Nükleer tesis kontrol yazılımı mutlaka doğrulanmalıdır.',     'HIGH'),
    ('E-devlet sistemi mahremiyet standartlarına uymalıdır.',       'HIGH'),

    # === DOMAIN ÇEŞİTLİĞİ — MEDIUM ===
    ('IoT sensör verisi buluta yüklenebilmelidir.',                 'MEDIUM'),
    ('Kullanıcı profil fotoğrafı yükleyebilmeli.',                 'MEDIUM'),
    ('Analist veri setini filtreleyebilmeli.',                      'MEDIUM'),
    ('Moderatör içerik kaldırabilmeli.',                            'MEDIUM'),
    ('Koordinatör proje raporu oluşturabilmeli.',                   'MEDIUM'),

    # === ZOR SINIR VAKALAR ===
    # HIGH kelimesi nesne konumunda
    ('Admin güvenlik loglarını görüntüleyebilmeli.',                'MEDIUM'),  # güvenlik nesne, HIGH değil
    ('Kullanıcı kritik bildirimleri silebilmeli.',                  'MEDIUM'),  # kritik nesne, HIGH değil
    # Cümle içi karmaşık yapı
    ('Sistem performansı kritik seviyelere düştüğünde uyarı vermeli.', 'HIGH'), # kritik sistem durumu
    ('Zorunlu alanlar doldurulmadan form gönderilemez.',            'HIGH'),    # zorunlu kural
    ('Güvenlik duvarı yapılandırması mutlaka belgelenmeli.',        'HIGH'),
    # LOW + HIGH birlikte
    ('Tercihen güvenlik sertifikası alınabilir.',                   'LOW'),     # tercihen baskın
    ('İleride kritik altyapı güncellemesi planlanabilir.',          'LOW'),     # ileride baskın
    # Belirsiz
    ('Sistem hata mesajlarını kayıt altına almalıdır.',             'MEDIUM'),
    ('Veriler düzenli olarak temizlenmelidir.',                     'MEDIUM'),
    ('Kullanıcı arayüzü tutarlı olmalıdır.',                       'MEDIUM'),
    # Ek sınır vakalar
    ('Sistem anlık yük altında bile kararlı çalışmalıdır.',        'MEDIUM'),  # no HIGH keyword
    ('Hata ayıklama logları isteğe bağlı tutulabilir.',            'LOW'),   # isteğe bağlı baskın
]

assert len(CASES) == 60, f'Beklenen 60, bulunan {len(CASES)}'


def run():
    det = PriorityDetector()
    failures = []

    for i, (t, e) in enumerate(CASES, 1):
        r = Requirement(id='T', text=t)
        det.detect(r)
        ok = r.priority == e
        mark = 'OK' if ok else 'XX'
        print(f'{mark} {i:2} [{r.priority:6}] beklenen={e:6} | {t[:60]}')
        if not ok:
            failures.append((r.priority, e, t))

    pct = (60 - len(failures)) / 60 * 100
    print(f'\nDogruluk: {60-len(failures)}/60 = %{pct:.1f}')
    if failures:
        print(f'\nBasarisiz ({len(failures)}):')
        for got, exp, t in failures:
            print(f'  got={got:6} exp={exp:6} | {t}')


if __name__ == '__main__':
    run()
