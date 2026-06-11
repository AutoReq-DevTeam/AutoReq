import re

_PASSIVE_VERB_RE = re.compile(
    r"\b\w*(?:(?<!b)ılmalı|(?<!b)ilmeli|(?<!b)ulmalı|(?<!b)ülmeli|(?<!b)ınmalı|(?<!b)inmeli|(?<!b)unmalı|(?<!b)ünmeli|(?<!b)anmalı|(?<!b)enmeli"
    r"|ılabilmeli|ilebilmeli|ulabilmeli|ülebilmeli|ınabilmeli|inebilmeli|unabilmeli|ünebilmeli|anabilmeli|enebilmeli"
    r"|(?<!b)ılır|(?<!b)ilir|(?<!b)ulur|(?<!b)ülur|(?<!b)ınır|(?<!b)inir|(?<!b)unur|(?<!b)ünür|(?<!b)anır|(?<!b)enir"
    r"|(?<!b)ılmak|(?<!b)ilmek|(?<!b)ulmak|(?<!b)ülmek|(?<!b)ınmak|(?<!b)inmek|(?<!b)unmak|(?<!b)ünmek|(?<!b)anmak|(?<!b)enmek)\w*\b",
    re.IGNORECASE
)

test_cases = {
    # Active (should be False)
    "onaylayabilmeli": False,
    "yapabilmeli": False,
    "görebilmeli": False,
    "onaylayabilir": False,
    "yapabilir": False,
    "görebilir": False,
    
    # Passive (should be True)
    "onaylanmalıdır": True,
    "kaydedilebilmelidir": True,
    "yapılabilmelidir": True,
    "şifrelenmelidir": True,
    "gönderilmelidir": True,
    "yapılır": True,
    "gönderilir": True,
    "onaylanmalı": True,
    "onaylanır": True,
    "belirlenebilmeli": True,
}

print("Testing regex:")
failed = 0
for word, expected in test_cases.items():
    match = bool(_PASSIVE_VERB_RE.search(word))
    if match != expected:
        print(f"FAIL: '{word}' -> match={match} (expected {expected})")
        failed += 1
    else:
        print(f"OK:   '{word}' -> match={match}")

print(f"\nFailed: {failed}/{len(test_cases)}")
