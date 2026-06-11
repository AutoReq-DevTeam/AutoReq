from dotenv import load_dotenv
load_dotenv()

from core.ner import EntityRecognizer
from core.classifier import RequirementClassifier
from core.models import Requirement
from scripts.eval_dev_corpus import GROUND_TRUTH, _norm

rec = EntityRecognizer()
clf = RequirementClassifier()

print("FAILURES DETAILS:\n")
for i, (text, expected_actors, expected_type, domain) in enumerate(GROUND_TRUTH, 1):
    req = Requirement(id=f"REQ_{i:03d}", text=text)
    clf.classify(req)
    rec.recognize(req)

    found_actors = {_norm(a) for a in (req.actors or [])}
    exp_actors = {_norm(a) for a in expected_actors}

    is_ok = False
    if exp_actors:
        matched = found_actors & exp_actors
        if len(matched) == len(exp_actors) and len(found_actors - exp_actors) == 0:
            is_ok = True
    else:
        if len(found_actors) == 0:
            is_ok = True

    if not is_ok:
        print(f"REQ_{i:03d} [{domain}] | Type={req.req_type} (exp={expected_type})")
        print(f"  Text: {text}")
        print(f"  Found:    {sorted(found_actors)}")
        print(f"  Expected: {sorted(exp_actors)}")
        # Print stanza parse tree
        if rec.nlp:
            doc = rec.nlp(text)
            for sent in doc.sentences:
                for w in sent.words:
                    print(f"    id={w.id:2d} text={w.text:15} lemma={w.lemma:15} upos={w.upos:6} deprel={w.deprel:12} head={w.head}")
        print("-" * 80)
