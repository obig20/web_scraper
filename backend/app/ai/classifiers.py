"""Crime and horror classification."""

import re

CRIME_TAXONOMY = {
    "murder": ["murder", "homicide", "killed", "slain", "shot dead"],
    "kidnapping": ["kidnap", "abduct", "missing person", "disappeared"],
    "robbery": ["robbery", "heist", "burglary", "stolen"],
    "assault": ["assault", "attack", "beaten", "stabbed"],
    "fraud": ["fraud", "scam", "embezzle", "forgery"],
    "serial": ["serial killer", "serial murder", "spree"],
    "unsolved": ["unsolved", "cold case", "mystery", "unknown perpetrator"],
    "missing": ["missing", "vanished", "last seen"],
    "terrorism": ["terrorist", "bombing", "extremist"],
    "cybercrime": ["hacking", "ransomware", "data breach"],
}

HORROR_TAXONOMY = {
    "paranormal": ["ghost", "haunted", "poltergeist", "apparition", "spirit"],
    "ufo": ["ufo", "alien", "extraterrestrial", "flying saucer"],
    "cryptid": ["bigfoot", "sasquatch", "mothman", "chupacabra", "cryptid"],
    "folklore": ["folklore", "legend", "myth", "oral tradition"],
    "urban_legend": ["urban legend", "campfire tale", "creepy pasta"],
    "occult": ["occult", "ritual", "satanic", "cult", "sacrifice"],
    "true_crime_horror": ["gruesome", "macabre", "disturbing", "horrific"],
    "supernatural": ["supernatural", "demon", "possession", "exorcism"],
}


def _classify(text: str, taxonomy: dict[str, list[str]], threshold: int = 1) -> list[str]:
    lower = text.lower()
    scores: dict[str, int] = {}
    for category, keywords in taxonomy.items():
        count = sum(len(re.findall(re.escape(kw), lower)) for kw in keywords)
        if count >= threshold:
            scores[category] = count
    return sorted(scores, key=scores.get, reverse=True)


def classify_crime_types(text: str) -> list[str]:
    return _classify(text, CRIME_TAXONOMY)


def classify_horror_categories(text: str) -> list[str]:
    return _classify(text, HORROR_TAXONOMY)
