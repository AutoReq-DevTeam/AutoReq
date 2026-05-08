"""
core/ner.py — Varlık ve Nesne Ayıklayıcı (NER)
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
Cümle içerisinden aktörleri ve nesneleri tespit eder. 3 katmanlı mimari:
  Katman 1 — Lemma tablosu: Genel ve domain-spesifik bilinen roller
  Katman 2 — Syntactic pattern: SOV düzeni + POS tag'larıyla domain-agnostic
  Katman 3 — Fallback: Katman 1/2 boş kalırsa generic sistem aktörü
"""

from modules.logging_utils import get_module_logger

from .models import Requirement
from .nlp_engine import get_shared_stanza_pipeline

_log = get_module_logger("ner")

# Katman 2 için klauz sınırı — CCONJ upos yeterli ama bazı Stanza sürümlerinde
# "ya"/"da" ayrı token olarak PART/ADV gelebilir; bunları da yakala.
_CCONJ_TEXTS = frozenset({"ve", "ile", "ya", "veya", "yahut", "ama", "fakat", "lakin", "ancak"})


class EntityRecognizer:
    """Stanza kullanarak metindeki varlıkları tanır (3 katmanlı mimari)."""

    def __init__(self) -> None:
        """EntityRecognizer başlatıcısı.

        Paylaşılan Stanza pipeline'ını kullanır. Pipeline yüklenemezse
        fallback (düz string eşleştirmesi) moduna geçer.
        """
        try:
            self.nlp = get_shared_stanza_pipeline()
        except Exception as e:
            _log.warning(
                "Stanza modeli yüklenirken hata oluştu. "
                "'stanza.download(\"tr\")' komutunu çalıştırdınız mı? Hata: {}",
                e,
            )
            self.nlp = None

        # --- Katman 1: Lemma tablosu ---
        # Çok sayıda domain'de geçerli olacak şekilde genişletilmiştir.
        # Stanza'nın yanlış POS verebileceği veya çekimli formlarından prefix-match
        # ile yakalanması gereken roller buraya eklenir.
        self.actor_lemmas: set[str] = {
            # Genel dijital roller
            "kullanıcı", "müşteri", "yönetici", "admin", "ziyaretçi",
            "çalışan", "aday", "üye", "abone", "vatandaş",
            # Sağlık
            "hasta", "doktor", "hemşire", "hekim", "eczacı", "cerrah",
            "diyetisyen", "fizyoterapist", "veteriner",
            # Eğitim
            "öğrenci", "öğretmen", "eğitmen", "veli", "hoca",
            # Hukuk / kamu
            "avukat", "hakim", "savcı", "noter", "müvekkil",
            # Ulaşım / operasyon
            "pilot", "sürücü", "kurye", "kaptan", "makinist",
            # Ticaret / tedarik
            "satıcı", "alıcı", "tedarikçi", "bayi", "tüketici",
            # Genel profesyonel
            "danışman", "stajyer", "mühendis",
            # Sistem / teknik — generic, düşük öncelik (Katman 3'te fallback)
            "sistem", "uygulama", "cihaz", "platform", "sunucu", "istemci",
        }

        # Bilinen çok-kelimeli aktörler: normalized text düzeyi substring eşleşmesi.
        # Anahtar: (lemma1, lemma2) — yalnızca dokümantasyon amaçlı.
        # Değer: metinde aranacak kanonik form.
        self.actor_bigram_labels: dict[tuple[str, str], str] = {
            ("ik", "uzman"):           "ik uzmanı",
            ("finans", "müdür"):       "finans müdürü",
            ("sistem", "yönetici"):    "sistem yöneticisi",
            ("misafir", "kullanıcı"):  "misafir kullanıcı",
            ("kayıtlı", "kullanıcı"):  "kayıtlı kullanıcı",
            ("kargo", "firma"):        "kargo firması",
            ("idari", "personel"):     "idari personel",
            ("son", "kullanıcı"):      "son kullanıcı",
            ("proje", "yönetici"):     "proje yöneticisi",
            ("ürün", "yönetici"):      "ürün yöneticisi",
            ("teknik", "destek"):      "teknik destek",
            ("kalite", "güvence"):     "kalite güvence",
            ("veri", "bilim"):         "veri bilimci",
        }

        # Generic (sistem/platform) aktörler — insan aktör bulunamazsa Katman 3 devreye girer.
        self.generic_actors: frozenset[str] = frozenset({
            "sistem", "uygulama", "cihaz", "platform", "sunucu", "istemci",
        })

        # İş nesneleri
        self.object_lemmas: set[str] = {
            "şifre", "form", "e-posta", "eposta", "sepet", "hesap", "rapor",
            "buton", "sayfa", "ekran", "veri", "veritabanı", "dosya", "belge",
            "mesaj", "bildirim", "fatura", "link", "liste",
            "sipariş", "ödeme", "ürün", "kategori", "profil", "randevu",
        }

    # ------------------------------------------------------------------
    # Yardımcı metotlar
    # ------------------------------------------------------------------

    @staticmethod
    def _norm(text: str) -> str:
        """Türkçe-uyumlu küçük harf.

        İ → i dönüşümünde Python'un eklediği U+0307 combining-dot'u temizler
        böylece bigram ve prefix eşleşmeleri doğru çalışır.
        """
        return text.lower().replace("̇", "")

    def _find_actor_k1(self, lemma: str, text_word: str) -> str | None:
        """Katman 1: Lemma tablosu ve Türkçe agglutination prefix-match."""
        if lemma in self.actor_lemmas:
            return lemma
        # Stanza POS/lemma hatası (örn. "Çalışan" → lemma="çalış")
        if text_word in self.actor_lemmas:
            return text_word
        # Çekimli form: "müşterinin".startswith("müşteri") → True
        for actor in self.actor_lemmas:
            if len(actor) >= 4 and text_word.startswith(actor) and len(text_word) > len(actor):
                return actor
        return None

    def _has_morph_suffix(self, word) -> bool:
        """Kelimenin morfolojik suffix aldığını tespit eder (text ≠ lemma)."""
        return self._norm(word.text) != self._norm(word.lemma or word.text)

    # ------------------------------------------------------------------
    # Katman 2: Syntactic pattern tabanlı (domain-agnostic)
    # ------------------------------------------------------------------

    def _extract_layer2_actors(self, sentence) -> set[str]:
        """Katman 2: SOV düzeni + POS tag'larıyla actor çıkarımı.

        Türkçe'nin SOV yapısından yararlanır: cümlenin başındaki isim öbeği
        büyük olasılıkla actor'dür. CCONJ noktalarında "X ve Y yap" gibi
        koordinasyonlar ayrı klauzlar olarak işlenir.
        """
        words = sentence.words
        actors: set[str] = set()

        # CCONJ'da klauzlara böl
        clauses: list[list] = []
        current: list = []
        for w in words:
            is_cconj = w.upos == "CCONJ" or self._norm(w.text) in _CCONJ_TEXTS
            if is_cconj:
                if current:
                    clauses.append(current)
                current = []
            else:
                current.append(w)
        if current:
            clauses.append(current)

        for clause in clauses:
            actor = self._clause_actor(clause)
            if actor:
                actors.add(actor)

        return actors

    def _clause_actor(self, words: list) -> str | None:
        """Tek bir klauz için SOV kalıbına göre actor adını döndürür."""
        # İlk VERB pozisyonunu bul
        verb_pos = next(
            (i for i, w in enumerate(words) if w.upos in ("VERB", "AUX")),
            len(words),
        )
        if verb_pos == 0:
            return None

        # Fiilden önceki başlangıç isim öbeği: (ADJ | NOUN | PROPN)*
        initial_np: list = []
        for w in words[:verb_pos]:
            if w.upos in ("NOUN", "PROPN", "ADJ"):
                initial_np.append(w)
            else:
                break  # Zarf, edat vb. gelince öbek bitti

        if not initial_np:
            return None

        return self._np_to_actor(initial_np)

    def _np_to_actor(self, np_words: list) -> str | None:
        """Başlangıç isim öbeğinden kanonik actor adını türetir.

        Desteklenen kalıplar:
          [NOUN_suffix+]           → tek actor (çoğul ya da başka suffix)
          [NOUN_base + NOUN_suffix] → bileşik actor (örn. "laboratuvar teknisyen")
          [ADJ + NOUN_base]         → modifier+baş (örn. "idari personel")
          [ADJ] (NOUN yok/acc.)    → Stanza yanlış ADJ etiketledi (örn. "hasta")
        """
        nouns = [w for w in np_words if w.upos in ("NOUN", "PROPN")]
        adjs  = [w for w in np_words if w.upos == "ADJ"]

        if not nouns and not adjs:
            return None

        # Başta ADJ var mı?
        leading_adj = adjs[0] if adjs and np_words[0].upos == "ADJ" else None
        adj_lemma   = self._norm(leading_adj.lemma or leading_adj.text) if leading_adj else None

        # ---------- NOUN yok: Stanza ADJ olarak etiketledi, aslında actor ----------
        if not nouns:
            if adj_lemma and len(adj_lemma) >= 3 and adj_lemma not in self.object_lemmas:
                return adj_lemma
            return None

        first_noun   = nouns[0]
        first_lemma  = self._norm(first_noun.lemma or first_noun.text)
        first_is_base = not self._has_morph_suffix(first_noun)

        # ---------- Başta ADJ + takip eden NOUN ----------
        if leading_adj and adj_lemma:
            if self._has_morph_suffix(first_noun):
                # NOUN accusative/dative → ADJ tek başına actor (örn. "Hasta randevusunu…")
                if len(adj_lemma) >= 3 and adj_lemma not in self.object_lemmas:
                    return adj_lemma
            else:
                # NOUN nominative → bileşik actor (örn. "idari personel")
                if first_lemma not in self.object_lemmas:
                    return f"{adj_lemma} {first_lemma}"
            return None

        # ---------- Çoklu NOUN: bileşik actor tespiti ----------
        if len(nouns) >= 2:
            second_noun   = nouns[1]
            second_lemma  = self._norm(second_noun.lemma or second_noun.text)
            second_has_suf = self._has_morph_suffix(second_noun)

            # NOUN_base + NOUN_suffix → bileşik (örn. "Laboratuvar teknisyeni")
            if (
                first_is_base
                and second_has_suf
                and len(first_lemma) >= 3
                and len(second_lemma) >= 3
                and second_lemma not in self.object_lemmas
            ):
                return f"{first_lemma} {second_lemma}"
            # İkisi de base form ya da başka durum → tek actor (ilk NOUN)

        # ---------- Tek NOUN veya bileşik koşul sağlanmadı ----------
        if len(first_lemma) >= 3 and first_lemma not in self.object_lemmas:
            return first_lemma

        return None

    # ------------------------------------------------------------------
    # Ana metot
    # ------------------------------------------------------------------

    def recognize(self, requirement: Requirement) -> Requirement:
        """Gereksinim içindeki aktör ve nesneleri tanır, requirement.actors/objects'i doldurur.

        Katman 1 → Katman 2 → Katman 3 öncelik sırasıyla çalışır.
        Metin boşsa erken döner.
        """
        if not requirement.text.strip():
            return requirement

        found_actors: set[str] = set()
        found_objects: set[str] = set()
        text_norm = self._norm(requirement.text)

        # === Katman 1a: Çok-kelimeli bilinen aktörler (text-level substring) ===
        matched_multiword: set[str] = set()
        for phrase in self.actor_bigram_labels.values():
            if phrase in text_norm:
                found_actors.add(phrase)
                matched_multiword.add(phrase)

        if self.nlp:
            doc = self.nlp(requirement.text)
            for sentence in doc.sentences:
                noun_run: list[str] = []
                layer1_sent: set[str] = set()

                # === Katman 1b: Kelime bazlı lemma eşleşmesi ===
                for word in sentence.words:
                    lemma     = self._norm(word.lemma or word.text)
                    text_word = self._norm(word.text)

                    # Çok-kelimeli aktörün parçası → tekil eşleşmeyi atla.
                    # Stanza MWT bölmesi (ör. "Kayıtlı" → "Kayıt"+"lı") için prefix-check de yapılır.
                    if any(
                        text_word == part or (len(text_word) >= 3 and part.startswith(text_word))
                        for phrase in matched_multiword
                        for part in phrase.split()
                    ):
                        noun_run = []
                        continue

                    actor_match = self._find_actor_k1(lemma, text_word)
                    if actor_match:
                        layer1_sent.add(actor_match)
                        noun_run = []
                    elif lemma in self.object_lemmas:
                        found_objects.add(lemma)
                        noun_run = []
                    elif word.upos in ("NOUN", "PROPN"):
                        noun_run.append(word.text)
                    else:
                        if 2 <= len(noun_run) <= 3:
                            found_objects.add(" ".join(noun_run).lower())
                        noun_run = []

                if 2 <= len(noun_run) <= 3:
                    found_objects.add(" ".join(noun_run).lower())

                # === Katman 2: Syntactic pattern (yalnızca K1 insan actor bulamazsa) ===
                # matched_multiword'deki insan aktörler de K1 sayılır — K2 tetiklenmez.
                human_k1 = {a for a in layer1_sent if a not in self.generic_actors}
                human_k1 |= {a for a in matched_multiword if a not in self.generic_actors}
                layer2_sent: set[str] = set()
                if not human_k1:
                    layer2_sent = self._extract_layer2_actors(sentence)

                found_actors |= layer1_sent

                # Katman 2 sonuçlarını ekle — zaten bulunanlarla veya object_lemmas ile çakışma varsa atla
                for a in layer2_sent:
                    head = self._norm(a.split()[-1])
                    if a not in found_actors and head not in self.object_lemmas:
                        found_actors.add(a)

        else:
            # Fallback: Stanza yoksa substring eşleşmesi (Graceful Degradation)
            _log.warning("Stanza pipeline kullanılamıyor, fallback modunda çalışılıyor.")
            for actor in self.actor_lemmas:
                if actor in text_norm:
                    found_actors.add(actor)
            for obj in self.object_lemmas:
                if obj in text_norm:
                    found_objects.add(obj)

        # === Katman 3 + Öncelik filtresi ===
        # İnsan/rol aktörü varsa generic sistem aktörlerini listeden çıkar.
        human_actors = {a for a in found_actors if a not in self.generic_actors}
        requirement.actors  = list(human_actors if human_actors else found_actors)
        requirement.objects = list(found_objects)

        return requirement
