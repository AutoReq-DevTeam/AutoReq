import stanza
from core.nlp_engine import get_shared_stanza_pipeline, turkish_lower
from core.ner import EntityRecognizer
from core.models import Requirement

nlp = get_shared_stanza_pipeline()
rec = EntityRecognizer()

sentences = [
    "İndirim kuponu yalnızca bir kez kullanılabilmelidir.",
    "Yatırım fonu alım satımı mobil uygulama üzerinden gerçekleştirilebilmelidir.",
    "Hesap hareketleri son 1 yıla ait olacak şekilde listelenebilmelidir.",
    "Bildirim tercihleri uygulama içinden yönetilebilmelidir."
]

for s in sentences:
    print("\n" + "="*50)
    print(f"SENTENCE: {s}")
    doc = nlp(s)
    req = Requirement(id="test", text=s)
    rec.recognize(req)
    print(f"-> Extracted actors: {req.actors}")
    print(f"-> Extracted objects: {req.objects}")
    
    # print word details
    for sent in doc.sentences:
        for w in sent.words:
            print(f"  word={w.text} upos={w.upos} lemma={w.lemma} deprel={w.deprel}")
        # check passive voice
        has_passive = False
        for w in sent.words:
            from core.ner import _PASSIVE_VERB_RE
            if _PASSIVE_VERB_RE.search(w.text):
                has_passive = True
                print(f"  Word '{w.text}' matched passive regex!")
        print(f"  has_passive: {has_passive}")
