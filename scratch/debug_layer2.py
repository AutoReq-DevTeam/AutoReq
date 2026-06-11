import stanza
from core.nlp_engine import get_shared_stanza_pipeline, turkish_lower
from core.ner import EntityRecognizer
from core.models import Requirement

nlp = get_shared_stanza_pipeline()
rec = EntityRecognizer()

s = "Veznedar nakit işlemlerini onaylayabilmeli."
doc = nlp(s)
for sent in doc.sentences:
    print(f"\nAnalyzing sentence: {s}")
    for w in sent.words:
        print(f"  word={w.text} upos={w.upos} lemma={w.lemma} deprel={w.deprel}")
    
    # Let's run Katman 2 logic manually
    words = sent.words
    clauses = [words] # single clause
    for clause in clauses:
        verb_pos = next(
            (i for i, w in enumerate(clause) if w.upos in ("VERB", "AUX")),
            len(clause),
        )
        print(f"  verb_pos: {verb_pos}")
        initial_np = []
        for w in clause[:verb_pos]:
            if w.upos in ("NOUN", "PROPN", "ADJ"):
                initial_np.append(w)
            else:
                break
        print(f"  initial_np: {[w.text for w in initial_np]}")
        
        nouns = [w for w in initial_np if w.upos in ("NOUN", "PROPN")]
        adjs  = [w for w in initial_np if w.upos == "ADJ"]
        print(f"  nouns: {[w.text for w in nouns]}")
        print(f"  adjs: {[w.text for w in adjs]}")
        
        first_noun   = nouns[0]
        first_lemma  = rec._norm(first_noun.lemma or first_noun.text)
        first_is_base = not rec._has_morph_suffix(first_noun)
        print(f"  first_lemma: {first_lemma}, first_is_base: {first_is_base}")
        
        if len(nouns) >= 2:
            second_noun   = nouns[1]
            second_lemma  = rec._norm(second_noun.lemma or second_noun.text)
            second_has_suf = rec._has_morph_suffix(second_noun)
            second_deprel = getattr(second_noun, "deprel", None)
            print(f"  second_lemma: {second_lemma}, second_has_suf: {second_has_suf}, second_deprel: {second_deprel}")
            
            # check the condition
            cond1 = first_is_base
            cond2 = second_has_suf
            cond3 = len(first_lemma) >= 3
            cond4 = len(second_lemma) >= 3
            cond5 = second_lemma not in rec.object_lemmas
            cond6 = second_deprel not in ("obj", "iobj", "obl")
            print(f"  conds: {cond1} {cond2} {cond3} {cond4} {cond5} {cond6}")
            if cond1 and cond2 and cond3 and cond4 and cond5 and cond6:
                print(f"  matches compound actor!")
        
        # let's see why it would return None
        # is first_lemma in object_lemmas?
        print(f"  first_lemma in object_lemmas: {first_lemma in rec.object_lemmas}")
        print(f"  first_lemma de-asciified: {rec._de_asciify(first_lemma)}")
        print(f"  first_lemma de-asciified in object_lemmas_de: {rec._de_asciify(first_lemma) in rec.object_lemmas_de}")
