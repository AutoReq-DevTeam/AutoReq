"""
core/ner.py — Varlık ve Nesne Ayıklayıcı (NER)
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
Cümle içerisinden aktörleri (Kullanıcı, Sistem, vb.) ve temel nesneleri (Kredi Kartı, Sipariş vb.)
tespit eder. Bu bilgiler, gereksinimlerin kapsamını ve etkileşim noktalarını belirlemek için kullanılır.

Mimari Karar (NLP Motoru Seçimi):
Projede spaCy yerine Stanza tercih edilmiştir. spaCy'nin Türkçe dil modelleri açık kaynaklı 
topluluk desteklidir ve Türkçe sondan eklemeli bir dil olduğu için morfolojik analizde (ek-kök bulma) zayıf kalabilmektedir. 
Stanford Üniversitesi yapımı Stanza, metinleri tokenlara bölerken derin öğrenme (Deep Learning) altyapısı sayesinde 
kelimelerin köklerini (lemma) %90'ın üzerinde bir başarıyla tespit edebilir. Bu da yazılım terminolojisinin 
hatasız ayırt edilmesini sağlar.
"""

from modules.logging_utils import get_module_logger

from .models import Requirement
from .nlp_engine import get_shared_stanza_pipeline

_log = get_module_logger("ner")


class EntityRecognizer:
    """Stanza kullanarak metindeki varlıkları tanır."""

    def __init__(self) -> None:
        """EntityRecognizer başlatıcısı.

        Paylaşılan Stanza pipeline'ını kullanır. Pipeline yüklenemezse
        fallback (düz string eşleştirmesi) moduna geçer.
        """
        # Paylaşılan Stanza pipeline'ını kullan (bellek tasarrufu)
        try:
            self.nlp = get_shared_stanza_pipeline()
        except Exception as e:
            _log.warning(
                "Stanza modeli yüklenirken hata oluştu. "
                "'stanza.download(\"tr\")' komutunu çalıştırdınız mı? Hata: {}",
                e,
            )
            self.nlp = None
        
        # Gündelik yazılım gereksinimlerinde sık geçen "Aktör" örüntüleri (köken kelimeler/lemma)
        self.actor_lemmas = {"kullanıcı", "sistem", "yönetici", "admin", "müşteri", "ziyaretçi", "cihaz", "uygulama", "istemci"}
        
        # Sık kullanılan "İş Nesneleri" (Objects)
        self.object_lemmas = {"şifre", "form", "e-posta", "eposta", "sepet", "hesap", "rapor", "buton", "sayfa", "ekran", "veri", "veritabanı", "dosya", "belge", "mesaj", "bildirim", "fatura", "şifremi unuttum", "link"}

    def recognize(self, requirement: Requirement) -> Requirement:
        """
        Gereksinim içindeki tüm kelimelerin köklerine (lemma) bakar ve 
        "kullanıcı", "şifre" gibi bizim sistemimizde kritik olan aktör/nesneleri ayıklar.

        Parametreler:
            requirement: Analiz edilecek gereksinim nesnesi.

        Döndürür:
            Requirement: actors ve objects alanları doldurulmuş gereksinim.
        """
        # Burada list [] yerine set () kullandık. Çünkü eğer müşteri 
        # "Kullanıcı şifresini girer ve kullanıcı onaylar" derse, listeye iki tane
        # 'kullanıcı' eklenirdi. Set veri yapısı matematikteki kümeler gibidir, 
        # aynı elemanı ikinci kez kendi içine eklemez (Duplicate engeller).
        found_actors = set()
        found_objects = set()

        if self.nlp:
            doc = self.nlp(requirement.text)
            for sentence in doc.sentences:
                for word in sentence.words:
                    # word.lemma: Kelimenin köküdür (Örn: "kullanıcının" -> "kullanıcı")
                    lemma = word.lemma.lower() if word.lemma else word.text.lower()
                    
                    if lemma in self.actor_lemmas:
                        found_actors.add(lemma)
                    elif lemma in self.object_lemmas:
                        found_objects.add(lemma)
        else:
            # Fallback Modu: Eğer sunucuda Stanza modeli çökürse kodun patlamaması için (Graceful Degradation)
            # Düz string eşleştirmesi ile hayat kurtaran B planı.
            _log.warning("Stanza pipeline kullanılamıyor, fallback modunda çalışılıyor.")
            text_lower = requirement.text.lower()
            for actor in self.actor_lemmas:
                if actor in text_lower:
                    found_actors.add(actor)
            for obj in self.object_lemmas:
                if obj in text_lower:
                    found_objects.add(obj)

        requirement.actors = list(found_actors)
        requirement.objects = list(found_objects)
        
        return requirement
