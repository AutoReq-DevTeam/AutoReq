"""
core/ner.py — Varlık ve Nesne Ayıklayıcı (NER)
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
Cümle içerisinden aktörleri ve nesneleri tespit eder. 3 katmanlı mimari:
  Katman 1 — Lemma tablosu: Genel ve domain-spesifik bilinen roller
  Katman 2 — Syntactic pattern: SOV düzeni + POS tag'larıyla domain-agnostic
  Katman 3 — Fallback: Katman 1/2 boş kalırsa generic sistem aktörü
"""

import re
from modules.logging_utils import get_module_logger

from .models import Requirement
from .nlp_engine import get_shared_stanza_pipeline, turkish_lower

_log = get_module_logger("ner")

_PASSIVE_VERB_RE = re.compile(
    r"\b\w*(?:(?<!b)ılmalı|(?<!b)ilmeli|(?<!b)ulmalı|(?<!b)ülmeli|(?<!b)ınmalı|(?<!b)inmeli|(?<!b)unmalı|(?<!b)ünmeli|(?<!b)anmalı|(?<!b)enmeli"
    r"|ılabilmeli|ilebilmeli|ulabilmeli|ülebilmeli|ınabilmeli|inebilmeli|unabilmeli|ünebilmeli|anabilmeli|enebilmeli"
    r"|(?<!b)ılır|(?<!b)ilir|(?<!b)ulur|(?<!b)ülür|(?<!b)ınır|(?<!b)inir|(?<!b)unur|(?<!b)ünür|(?<!b)anır|(?<!b)enir"
    r"|(?<!b)ılmak|(?<!b)ilmek|(?<!b)ulmak|(?<!b)ülmek|(?<!b)ınmak|(?<!b)inmek|(?<!b)unmak|(?<!b)ünmek|(?<!b)anmak|(?<!b)enmek)\w*\b",
    re.IGNORECASE
)

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
            "diyetisyen", "fizyoterapist", "veteriner", "laborant", "radyolog",
            "başhekim",
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
            # Domain-agnostik genel roller (yeni)
            "koordinatör", "yetkili", "sorumlu", "temsilci",
            "operatör", "teknisyen", "analist", "moderatör",
            "editör", "müdür", "direktör", "sekreter",
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
            ("yazılım", "geliştirici"): "yazılım geliştirici",
            ("test", "uzman"):         "test uzmanı",
            ("içerik", "üretici"):     "içerik üreticisi",
            ("proje", "koordinatör"):  "proje koordinatörü",
            ("alan", "uzman"):         "alan uzmanı",
            ("hasta", "yakın"):        "hasta yakını",
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
            # Yeni nesneler (Katman 2 hatalarını önlemek için)
            "kupon", "kart", "özellik", "boyut", "iletim", "geçiş", "tüketim",
            "oran", "değerlendirme", "veri", "veriler", "şikayet", "bakiye",
            "ekstre", "randevular", "sonuçlar", "geçmiş", "durum", "adres",
            "limit", "süre", "hedef", "standart", "gereklilik", "araç",
            "arayüz", "sistem trafik", "trafiği", "doğrulama", "çevrimdışı modda",
            "aktif kullanımda", "crash oranı", "aktif kullanıcı", "oturum",
            "bilgileri", "bilgisi", "süreçleri", "süreci", "mod", "modda",
            "provizyon", "sorgulama", "entegrasyon", "yedekleme", "kayıt",
            "takip", "dikte", "görüşme", "envanter", "geçmiş", "dosyası", "ad"
        }
        
        # De-asciified aramalar için setler
        self.actor_lemmas_de = {self._de_asciify(a) for a in self.actor_lemmas}
        self.actor_bigrams_de = {self._de_asciify(phrase): phrase for phrase in self.actor_bigram_labels.values()}
        self.object_lemmas_de = {self._de_asciify(o) for o in self.object_lemmas}

    # ------------------------------------------------------------------
    # Yardımcı metotlar
    # ------------------------------------------------------------------

    @staticmethod
    def _is_object_case(text_word: str, lemma: str) -> bool:
        """Kelimenin Türkçe belirtme (accusative), yönelme (dative), bulunma (locative) veya 
        ayrılma (ablative) durum eki alıp almadığını kontrol eder.
        """
        tw = text_word.lower()
        lem = lemma.lower()
        
        tw_de = EntityRecognizer._de_asciify(tw)
        lem_de = EntityRecognizer._de_asciify(lem)
        
        if not tw_de.startswith(lem_de):
            return False
            
        suffix = tw_de[len(lem_de):]
        if not suffix:
            return False
            
        # Object/oblique cases suffixes in Turkish (de-asciified):
        forbidden_suffixes = {
            # Accusative / plural oblique
            "lari", "leri", "larini", "lerini", "larina", "lerine", "larinda", "lerinde", "larindan", "lerinden",
            # Dative
            "ya", "ye", "a", "e", "na", "ne", "lara", "lere",
            # Locative
            "da", "de", "ta", "te", "nda", "nde", "larda", "lerde",
            # Ablative
            "dan", "den", "tan", "ten", "ndan", "nden", "lardan", "lerden",
            # Accusative singular
            "yi", "yu", "ni", "nu",
        }
        
        if suffix in forbidden_suffixes:
            return True
        return False

    @staticmethod
    def _is_genitive_case(word) -> bool:
        """Kelimenin tamlayan (genitive) eki alıp almadığını kontrol eder."""
        if hasattr(word, "feats") and word.feats:
            if "Case=Gen" in word.feats:
                return True
        t = word.text.lower()
        for suf in ("ın", "in", "un", "ün", "nın", "nin", "nun", "nün", "ların", "lerin"):
            if t.endswith(suf) and len(t) - len(suf) >= 3:
                return True
        return False

    @staticmethod
    def _de_asciify(s: str) -> str:
        """Türkçe karakterleri İngilizce karşılıklarına haritalandırır (arama hassasiyeti için)."""
        translation = str.maketrans({
            "ı": "i",
            "ğ": "g",
            "ü": "u",
            "ş": "s",
            "ö": "o",
            "ç": "c"
        })
        return s.translate(translation)

    @staticmethod
    def _norm(text: str) -> str:
        """Türkçe-uyumlu küçük harf.

        İ → i dönüşümünde Python'un eklediği U+0307 combining-dot'u temizler
        böylece bigram ve prefix eşleşmeleri doğru çalışır.
        """
        return turkish_lower(text)

    @staticmethod
    def _strip_possessive(text_word: str) -> str:
        """Türkçe tamlayan (iyelik) eklerini soyar: müşterinin → müşteri.

        Yalnızca sonuç en az 3 karakter uzunluğundaysa uygular.
        """
        for suffix in ("nin", "nın", "nün", "nun", "in", "ın", "ün", "un"):
            if text_word.endswith(suffix):
                base = text_word[: -len(suffix)]
                if len(base) >= 3:
                    return base
        return text_word

    def _find_actor_k1(self, lemma: str, text_word: str, upos: str = "NOUN") -> str | None:
        """Katman 1: Lemma tablosu ve Türkçe agglutination prefix-match."""
        lemma_de = self._de_asciify(lemma)
        text_word_de = self._de_asciify(text_word)

        # Tüketim/Tüketici çakışma koruması
        if "tuketim" in text_word_de or "tuketim" in lemma_de:
            return None
        
        # Tam eşleşme (de-asciified)
        for actor in self.actor_lemmas:
            actor_de = self._de_asciify(actor)
            if lemma_de == actor_de or text_word_de == actor_de:
                return actor
                
        # Fiil veya yardımcı fiil ise prefix/ters prefix eşleştirmelerini devre dışı bırak
        if upos in ("VERB", "AUX"):
            return None

        # Tamlayan eki soyma: "müşterinin" -> "müşteri"
        stripped = self._strip_possessive(text_word)
        stripped_de = self._de_asciify(stripped)
        if stripped != text_word:
            for actor in self.actor_lemmas:
                actor_de = self._de_asciify(actor)
                if stripped_de == actor_de:
                    return actor
                    
        # Çekimli form prefix-match: "müşteriye".startswith("müşteri") -> True
        for actor in self.actor_lemmas:
            actor_de = self._de_asciify(actor)
            if len(actor_de) >= 4 and text_word_de.startswith(actor_de) and len(text_word_de) > len(actor_de):
                return actor
                
        # Ters prefix: Stanza MWT bölümü (örn. "Yönet"->"yönetici", "Sorum"->"sorumlu")
        if len(lemma_de) >= 4:
            for actor in self.actor_lemmas:
                actor_de = self._de_asciify(actor)
                if actor_de.startswith(lemma_de) and len(actor_de) > len(lemma_de):
                    return actor
                    
        return None

    def _extract_by_dependency(self, sentence) -> set[str]:
        """Katman 1.5: nsubj bağıyla işaretlenmiş özneyi yakalar.

        Dependency parsing'in belirlediği nominal özne (nsubj / nsubj:pass)
        doğrudan actor_lemmas tablosuna karşı kontrol edilir.
        """
        actors: set[str] = set()
        for word in sentence.words:
            if word.deprel not in ("nsubj", "nsubj:pass"):
                continue
            lemma = self._norm(word.lemma or word.text)
            text_word = self._norm(word.text)
            actor = self._find_actor_k1(lemma, text_word, getattr(word, "upos", "NOUN"))
            if actor:
                actors.add(actor)
        return actors

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
            # Ama ikinci isim doğrudan nesne/tümleç ise bileşik aktör sayılmaz.
            second_deprel = getattr(second_noun, "deprel", None)
            if (
                first_is_base
                and second_has_suf
                and len(first_lemma) >= 3
                and len(second_lemma) >= 3
                and second_lemma not in self.object_lemmas
                and second_deprel not in ("obj", "iobj", "obl")
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
        text_de = self._de_asciify(text_norm)

        # === Katman 1a: Çok-kelimeli bilinen aktörler (text-level substring - de-asciified) ===
        matched_multiword: set[str] = set()
        for de_phrase, phrase in self.actor_bigrams_de.items():
            if de_phrase in text_de:
                found_actors.add(phrase)
                matched_multiword.add(phrase)

        if self.nlp:
            doc = self.nlp(requirement.text)
            for sentence in doc.sentences:
                # --- Stanza MWT split birleştirme adımı ---
                merged_words = []
                idx = 0
                original_words = sentence.words
                while idx < len(original_words):
                    w = original_words[idx]
                    if idx + 1 < len(original_words):
                        w_next = original_words[idx + 1]
                        combined_text = w.text + w_next.text
                        combined_text_norm = self._de_asciify(self._norm(combined_text))
                        is_actor = False
                        for actor in self.actor_lemmas:
                            if combined_text_norm == self._de_asciify(actor):
                                is_actor = True
                                break
                        if is_actor:
                            # w ve w_next birleştirilir
                            w.text = combined_text
                            w.lemma = combined_text_norm
                            w.upos = "NOUN"
                            w.deprel = w.deprel if w.deprel in ("nsubj", "nsubj:pass", "obj", "obl") else w_next.deprel
                            idx += 2
                            merged_words.append(w)
                            continue
                    
                    merged_words.append(w)
                    idx += 1
                sentence.words = merged_words

                # Passive and NFR flags computed at sentence level
                has_passive_verb = bool(_PASSIVE_VERB_RE.search(sentence.text))
                has_agent = any(w.text == "tarafından" for w in sentence.words)
                is_passive = has_passive_verb and not has_agent
                is_nfr = requirement.req_type == "NON_FUNCTIONAL"

                noun_run: list[str] = []
                layer1_sent: set[str] = set()
                candidates = []

                # Türkçe iyelik eki kontrolü
                def is_genitive(text_str: str, lemma_str: str) -> bool:
                    t = text_str.lower()
                    lem = lemma_str.lower()
                    if t == lem:
                        return False
                    for suf in ("ın", "in", "un", "ün", "nın", "nin", "nun", "nün", "ların", "lerin"):
                        if t.endswith(suf) and len(t) - len(suf) >= 3:
                            return True
                    return False

                # Cümle kelimelerini klauzlara böl
                clauses: list[list] = []
                current: list = []
                for w in sentence.words:
                    is_separator = w.upos == "CCONJ" or w.text in (";", "ve", "veya", "yahut", "ama", "fakat", "lakin", "ancak")
                    if is_separator:
                        if current:
                            clauses.append(current)
                        current = []
                    else:
                        current.append(w)
                if current:
                    clauses.append(current)

                # Her klauz için aday çıkarımı ve süzme
                for clause in clauses:
                    clause_candidates = []
                    
                    # === Katman 1b: Kelime bazlı lemma eşleşmesi ===
                    for word in clause:
                        lemma     = self._norm(word.lemma or word.text)
                        text_word = self._norm(word.text)
                        lemma_de  = self._de_asciify(lemma)

                        # Çok-kelimeli aktörün parçası → tekil eşleşmeyi atla.
                        if any(
                            text_word == part or (len(text_word) >= 3 and part.startswith(text_word))
                            for phrase in matched_multiword
                            for part in phrase.split()
                        ):
                            noun_run = []
                            continue

                        actor_match = self._find_actor_k1(lemma, text_word, getattr(word, "upos", "NOUN"))
                        if actor_match:
                            # Check if it has an object case suffix
                            if self._is_object_case(word.text, actor_match):
                                noun_run = []
                                continue

                            # Check if it is a modifier of an object (governor check)
                            is_modifier_of_object = False
                            if word.deprel not in ("nsubj", "nsubj:pass", "obl:agent") and word.head > 0:
                                for w_gov in sentence.words:
                                    if w_gov.id == word.head:
                                        gov_lemma = self._norm(w_gov.lemma or w_gov.text)
                                        gov_lemma_de = self._de_asciify(gov_lemma)
                                        if gov_lemma_de in self.object_lemmas_de:
                                            # If sentence is passive or the governor is genitive (nested modifier)
                                            if is_passive or self._is_genitive_case(w_gov):
                                                is_modifier_of_object = True
                                        break
                            if is_modifier_of_object:
                                noun_run = []
                                continue

                            # 'kullanıcı dostu', 'aktif/eş zamanlı kullanıcı', 'kullanıcı yetki/rol' scale metriklerini ve modifikatörleri ele
                            if actor_match == "kullanıcı":
                                if "kullanıcı dost" in text_norm or "kullanicici dost" in text_de:
                                    noun_run = []
                                    continue
                                if any(phrase in text_norm for phrase in (
                                    "eş zamanlı kullanıcı", "eşzamanlı kullanıcı", 
                                    "aktif kullanıcı", "aktif kullanici",
                                    "kullanıcı yetki", "kullanici yetki",
                                    "kullanıcı rol", "kullanici rol",
                                    "kullanıcı hesap", "kullanici hesap",
                                    "kullanıcı profil", "kullanici profil"
                                )):
                                    noun_run = []
                                    continue

                            is_strong = False
                            if word.deprel in ("nsubj", "nsubj:pass", "obl:agent"):
                                is_strong = True
                            else:
                                for w2 in sentence.words:
                                    if w2.head == word.id and w2.text == "tarafından":
                                        is_strong = True
                                        break
                                        
                            if is_strong and is_genitive(word.text, lemma):
                                is_strong = False

                            clause_candidates.append({
                                "actor": actor_match,
                                "is_strong": is_strong,
                                "is_genitive": is_genitive(word.text, lemma),
                                "word": word
                            })
                            noun_run = []
                        elif lemma_de in self.object_lemmas_de:
                            found_objects.add(lemma)
                            noun_run = []
                        elif word.upos in ("NOUN", "PROPN"):
                            noun_run.append(word.text)
                        else:
                            if 2 <= len(noun_run) <= 3:
                                found_objects.add(turkish_lower(" ".join(noun_run)))
                            noun_run = []

                    if 2 <= len(noun_run) <= 3:
                        found_objects.add(turkish_lower(" ".join(noun_run)))

                    # Çoklu kelimeler için de candidate oluştur (klauz içindeki kelimeleri içeriyorsa)
                    clause_text = " ".join([self._norm(w.text) for w in clause])
                    clause_text_de = self._de_asciify(clause_text)
                    for phrase in matched_multiword:
                        de_phrase = self._de_asciify(phrase)
                        if de_phrase in clause_text_de:
                            # Raw text içinde nerede geçtiğini bulup sonrasında genitive eki var mı kontrol et
                            idx_p = text_norm.find(phrase)
                            is_strong = True
                            is_gen = False
                            if idx_p != -1:
                                after_text = text_norm[idx_p + len(phrase):].strip()
                                for suf in ("nin", "nın", "nün", "nun", "in", "ın", "ün", "un", "lerin", "ların"):
                                    if after_text.startswith(suf) and (len(after_text) == len(suf) or not after_text[len(suf)].isalnum()):
                                        is_gen = True
                                        is_strong = False
                                        break
                            clause_candidates.append({
                                "actor": phrase,
                                "is_strong": is_strong,
                                "is_genitive": is_gen,
                                "word": None
                            })

                    # Strong vs Weak aktör hiyerarşi süzmesi
                    strongs = {c["actor"] for c in clause_candidates if c["is_strong"] and c["actor"] not in self.generic_actors}
                    weaks = {c["actor"] for c in clause_candidates if not c["is_strong"] and c["actor"] not in self.generic_actors}

                    if strongs:
                        layer1_sent.update(strongs)
                    elif weaks:
                        non_genitives = {c["actor"] for c in clause_candidates if not c["is_genitive"] and c["actor"] not in self.generic_actors}
                        if non_genitives:
                            layer1_sent.update(non_genitives)
                        else:
                            layer1_sent.update(weaks)

                # === Katman 1.5: Dependency parsing tabanlı özne tespiti ===
                human_k1 = {a for a in layer1_sent if a not in self.generic_actors}
                dep_actors: set[str] = set()
                if not human_k1:
                    # Alternatif özne çıkarımı
                    for word in sentence.words:
                        if word.deprel not in ("nsubj", "nsubj:pass"):
                            continue
                        lemma = self._norm(word.lemma or word.text)
                        text_word = self._norm(word.text)
                        actor = self._find_actor_k1(lemma, text_word, getattr(word, "upos", "NOUN"))
                        if actor and actor not in self.generic_actors:
                            dep_actors.add(actor)
                    human_k1 |= dep_actors

                # === Katman 2: Syntactic pattern (Bypass mantığı ile) ===
                layer2_sent: set[str] = set()
                
                # (is_passive ve is_nfr değişkenleri cümle bazında yukarıda hesaplandı)

                # Eğer insan aktör bulunamadıysa ve cümle edilgen ya da NFR değilse Katman 2 çalıştır
                if not human_k1 and not is_nfr and not is_passive:
                    layer2_sent = self._extract_layer2_actors(sentence)

                found_actors |= layer1_sent
                found_actors |= dep_actors

                # Katman 2 sonuçlarını ekle — zaten bulunanlarla veya object_lemmas ile çakışma varsa atla
                for a in layer2_sent:
                    head = self._norm(a.split()[-1])
                    head_de = self._de_asciify(head)
                    if a not in found_actors and head_de not in self.object_lemmas_de:
                        found_actors.add(a)

        else:
            # Fallback: Stanza yoksa substring eşleşmesi (Graceful Degradation)
            _log.warning("Stanza pipeline kullanılamıyor, fallback modunda çalışılıyor.")
            for actor in self.actor_lemmas:
                if actor not in self.generic_actors:
                    actor_de = self._de_asciify(actor)
                    if actor_de in text_de:
                        found_actors.add(actor)
            for obj in self.object_lemmas:
                obj_de = self._de_asciify(obj)
                if obj_de in text_de:
                    found_objects.add(obj)

        # === Katman 3 + Öncelik filtresi ===
        # Asla generic sistem aktörlerini (sistem, platform, vb.) listede döndürme
        human_actors = {a for a in found_actors if a not in self.generic_actors}
        requirement.actors  = list(human_actors)
        requirement.objects = list(found_objects)

        return requirement
