"""60 bağımsız gereksinim ile NER aktör çıkarımı doğruluk testi."""
from dotenv import load_dotenv
load_dotenv()

from core.ner import EntityRecognizer
from core.models import Requirement

# Her tuple: (gereksinim metni, beklenen aktör seti)
# Beklenen set: recognize() çıktısındaki actors listesinde en az bir eleman bu seti kapsamalı.
# None = hiçbir insan aktör beklenmez (sistem/generic kabul)
CASES = [
    # === AÇIK TEKİL AKTÖRLER ===
    ('Kullanıcı sisteme giriş yapabilmelidir.',                        {'kullanıcı'}),
    ('Müşteri siparişini iptal edebilmeli.',                           {'müşteri'}),
    ('Admin kullanıcı listesini görüntüleyebilmeli.',                  {'admin'}),
    ('Doktor hasta randevularını onaylayabilmeli.',                    {'doktor'}),
    ('Hemşire ilaç dozunu kayıt altına alabilmelidir.',               {'hemşire'}),
    ('Öğrenci sınav sonuçlarını görüntüleyebilmeli.',                 {'öğrenci'}),
    ('Öğretmen ödev yükleyebilmeli.',                                  {'öğretmen'}),
    ('Eczacı reçete geçmişini görüntüleyebilmeli.',                   {'eczacı'}),
    ('Veli öğrencinin devam durumunu takip edebilmeli.',              {'veli'}),
    ('Kurye teslimat adresini güncelleyebilmeli.',                     {'kurye'}),
    ('Yönetici raporları dışa aktarabilmeli.',                        {'yönetici'}),
    ('Eğitmen canlı ders başlatabilmeli.',                            {'eğitmen'}),
    ('Pilot uçuş planını onaylayabilmelidir.',                        {'pilot'}),
    ('Sürücü güzergah bilgisini güncelleyebilmeli.',                  {'sürücü'}),
    ('Hakim davayı sonuçlandırabilmelidir.',                          {'hakim'}),
    ('Avukat dava dosyasına erişebilmeli.',                           {'avukat'}),

    # === DOMAIN-AGNOSTİK GENEL ROLLER ===
    ('Koordinatör proje raporunu onaylayabilmeli.',                    {'koordinatör'}),
    ('Analist veri setini filtreleyebilmeli.',                        {'analist'}),
    ('Moderatör içeriği kaldırabilmeli.',                             {'moderatör'}),
    ('Teknisyen hata loglarını dışa aktarabilmeli.',                  {'teknisyen'}),
    ('Operatör cihaz kalibrasyonu başlatabilmeli.',                   {'operatör'}),
    ('Sorumlu raporu onaylayabilmelidir.',                            {'sorumlu'}),
    ('Yetkili sisteme müdahale edebilmelidir.',                       {'yetkili'}),
    ('Editör içeriği yayınlayabilmelidir.',                           {'editör'}),

    # === ÇOK-KELİMELİ (BİGRAM) AKTÖRLER ===
    ('Sistem yöneticisi yetki tanımlarını yapılandırabilmeli.',       {'sistem yöneticisi'}),
    ('Son kullanıcı arayüzü özelleştirebilmelidir.',                  {'son kullanıcı'}),
    ('Proje yöneticisi kaynak planlaması yapabilmeli.',               {'proje yöneticisi'}),
    ('Teknik destek bilet oluşturabilmeli.',                          {'teknik destek'}),
    ('Kayıtlı kullanıcı geçmiş siparişlere bakabilmelidir.',         {'kayıtlı kullanıcı'}),

    # === İYELİK EKİ (POSSESSIVE) STRIPPING ===
    ("Müşterinin şikayeti sisteme kaydedilmelidir.",                  {'müşteri'}),
    ("Kullanıcının profilini görüntüleyebilmeli.",                    {'kullanıcı'}),
    ("Doktorun randevu takvimi güncellenmeli.",                       {'doktor'}),
    ("Öğrencinin sınav sonuçlarına erişilebilmeli.",                  {'öğrenci'}),

    # === STANZA LEMMA HATASI — PREFIX-MATCH ===
    ("Çalışan maaş bilgisini görüntüleyebilmelidir.",                 {'çalışan'}),
    ("Yöneticiler log kayıtlarını silebilmelidir.",                   {'yönetici'}),
    ("Müşteriler sepete ürün ekleyebilmeli.",                        {'müşteri'}),
    ("Kullanıcılar şifre sıfırlayabilmeli.",                         {'kullanıcı'}),

    # === BİRDEN FAZLA AKTÖR ===
    ("Doktor veya hemşire hasta dosyasını açabilmeli.",               {'doktor', 'hemşire'}),
    ("Öğretmen ve öğrenci ortak çalışma belgesi oluşturabilmeli.",    {'öğretmen', 'öğrenci'}),
    ("Admin ve yönetici sistem ayarlarını değiştirebilmeli.",         {'admin', 'yönetici'}),

    # === SİSTEM AKTÖRÜ (GENERİK FALLBACK) ===
    ("Sistem kritik hatayı otomatik kayıt altına almalıdır.",         set()),
    ("Platform anlık bildirim göndermelidir.",                        set()),
    ("Uygulama kullanıcı oturumunu sonlandırmalıdır.",               {'kullanıcı'}),

    # === DOMAIN ÇEŞİTLİLİĞİ ===
    # Finans
    ("Muhasebeci fatura kesebilmelidir.",                             {'muhasebeci'}),
    ("Veznedar nakit işlemlerini onaylayabilmeli.",                   {'veznedar'}),
    # Lojistik
    ("Depo sorumlusu stok sayımı başlatabilmeli.",                    {'sorumlu'}),
    ("Tedarikçi ürün fiyatını güncelleyebilmelidir.",                 {'tedarikçi'}),
    # Sağlık
    ("Veteriner aşı takvimini görüntüleyebilmeli.",                  {'veteriner'}),
    ("Diyetisyen diyet planı oluşturabilmeli.",                       {'diyetisyen'}),
    # Eğitim
    ("Öğrenci ödeve yorum yapabilmeli.",                             {'öğrenci'}),
    ("Hoca sınav notu girebilmelidir.",                               {'hoca'}),

    # === ZOR SINIR VAKALAR ===
    # Aktör cümle ortasında
    ("Ödeme tamamlandığında müşteriye bildirim gönderilmelidir.",     {'müşteri'}),
    # Aktör nesne konumunda da geçiyor
    ("Admin, kullanıcı hesabını dondurabilmelidir.",                  {'admin', 'kullanıcı'}),
    # Pasif yapı
    ("Raporlar yönetici tarafından onaylanmalıdır.",                  {'yönetici'}),
    # Birleşik cümle, iki aktör
    ("Koordinatör raporu hazırlar, müdür onaylar.",                   {'koordinatör', 'müdür'}),
    # Aktör sonunda gelen
    ("Sistem kayıtları düzenli olarak analist tarafından incelenmelidir.", {'analist'}),
    # Sahiplik yapısı
    ("Öğretmenin not defteri sisteme aktarılmalıdır.",                {'öğretmen'}),
    # Meslek rol
    ("Mühendis teknik dokümanı sisteme yükleyebilmelidir.",          {'mühendis'}),
    ("Stajyer proje görevlerini görüntüleyebilmeli.",                 {'stajyer'}),
    ("Danışman müşteri raporunu hazırlayabilmelidir.",                {'danışman'}),
]

assert len(CASES) == 60, f'Beklenen 60, bulunan {len(CASES)}'


def _actors_found(req_actors: list, expected: set) -> bool:
    if not expected:
        return len(req_actors) == 0
    found = {a.lower() for a in req_actors}
    return bool(found & expected)


def run():
    rec = EntityRecognizer()
    failures = []

    for i, (text, expected) in enumerate(CASES, 1):
        r = Requirement(id='T', text=text)
        rec.recognize(r)
        actors = list(r.actors) if r.actors else []
        ok = _actors_found(actors, expected)
        mark = 'OK' if ok else 'XX'
        actors_str = ', '.join(actors) if actors else '—'
        print(f'{mark} {i:2} actors=[{actors_str}] beklenen={expected} | {text[:55]}')
        if not ok:
            failures.append((actors, expected, text))

    pct = (60 - len(failures)) / 60 * 100
    print(f'\nDogruluk: {60-len(failures)}/60 = %{pct:.1f}')
    if failures:
        print(f'\nBasarisiz ({len(failures)}):')
        for actors, expected, text in failures:
            print(f'  actors={actors}  beklenen={expected}')
            print(f'  {text}')


if __name__ == '__main__':
    run()
