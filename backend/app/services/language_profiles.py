import re
from typing import Optional, Tuple, Dict, List, Set

class LanguageProfile:
    def __init__(
        self,
        code: str,
        add_triggers: List[str],
        remove_triggers: List[str],
        update_triggers: List[str],
        number_words: Dict[str, float],
        units_map: Dict[str, str],
        filler_words: Set[str],
        negation_markers: List[str],
        correction_markers: List[str],
        product_aliases: Dict[str, str]
    ):
        self.code = code
        self.add_triggers = add_triggers
        self.remove_triggers = remove_triggers
        self.update_triggers = update_triggers
        self.number_words = number_words
        self.units_map = units_map
        self.filler_words = filler_words
        self.negation_markers = negation_markers
        self.correction_markers = correction_markers
        self.product_aliases = product_aliases


ENGLISH_PROFILE = LanguageProfile(
    code="en",
    add_triggers=[
        "add", "buy", "need", "put", "get", "i need", "i want to buy", "can you add", "please put", "please add"
    ],
    remove_triggers=[
        "remove", "delete", "take off", "dont need", "don't need"
    ],
    update_triggers=[
        "change", "update", "set", "make", "increase"
    ],
    number_words={
        "a": 1.0, "an": 1.0, "one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0,
        "five": 5.0, "six": 6.0, "seven": 7.0, "eight": 8.0, "nine": 9.0, "ten": 10.0,
        "eleven": 11.0, "twelve": 12.0, "half": 0.5, "dozen": 12.0
    },
    units_map={
        "bottle": "bottles", "bottles": "bottles",
        "packet": "packets", "packets": "packets", "pack": "packets", "packs": "packets", "package": "packets", "packages": "packets",
        "kg": "kg", "kilogram": "kg", "kilograms": "kg", "g": "grams", "gram": "grams", "grams": "grams",
        "lb": "lbs", "lbs": "lbs", "pound": "lbs", "pounds": "lbs",
        "liter": "liters", "liters": "liters", "litre": "liters", "litres": "liters",
        "carton": "cartons", "cartons": "cartons", "dozen": "dozen", "dozens": "dozen",
        "box": "boxes", "boxes": "boxes", "can": "cans", "cans": "cans",
        "bag": "bags", "bags": "bags", "jar": "jars", "jars": "jars",
        "bar": "bars", "bars": "bars", "roll": "rolls", "rolls": "rolls"
    },
    filler_words={"please", "can you", "could you", "i need", "i want", "i would like", "to my list", "on my list", "shopping list", "uh", "um", "you know", "okay", "like"},
    negation_markers=[
        "don't add", "do not add", "dont add", "don't buy", "do not buy", "dont buy",
        "don't need", "do not need", "dont need", "don't checkout", "do not checkout",
        "dont checkout", "don't place", "do not place", "dont place", "don't want to checkout",
        "don't want to place", "i don't want to checkout", "i don't want to place"
    ],
    correction_markers=["actually", "no", "sorry", "i mean", "instead"],
    product_aliases={
        "milk": "whole milk",
        "strawberries": "organic strawberries", "strawberry": "organic strawberries",
        "apples": "gala apples", "apple": "gala apples",
        "bananas": "fresh bananas", "banana": "fresh bananas",
        "bread": "whole wheat bread", "loaf": "whole wheat bread",
        "cheese": "cheddar cheese", "butter": "unsalted butter",
        "yogurt": "greek yogurt", "yoghurt": "greek yogurt",
        "chips": "classic potato chips", "toothpaste": "mint toothpaste",
        "soap": "beauty bar soap", "water": "drinking water", "juice": "orange juice",
        "rice": "white rice", "eggs": "eggs", "egg": "eggs",
        "coffee": "dark roast coffee", "nuts": "mixed nuts", "towels": "paper towels", "detergent": "liquid laundry detergent"
    }
)


MALAYALAM_PROFILE = LanguageProfile(
    code="ml",
    add_triggers=["ചേർക്കൂ", "ചേർക്കുക", "വാങ്ങണം", "വാങ്ങൂ", "വേണം", "ഉൾപ്പെടുത്തൂ"],
    remove_triggers=["നീക്കം ചെയ്യൂ", "മൊത്തം കളയൂ", "വേണ്ട"],
    update_triggers=["ആക്കൂ", "മാറ്റൂ"],
    number_words={
        "ഒന്ന്": 1.0, "ഒരു": 1.0, "ഒരേ": 1.0, "രണ്ട്": 2.0, "രണ്ടു": 2.0,
        "മൂന്ന്": 3.0, "മൂന്നു": 3.0, "നാല്": 4.0, "നാലു": 4.0,
        "അഞ്ച്": 5.0, "അഞ്ചു": 5.0, "ആറ്": 6.0, "ആറു": 6.0,
        "ഏഴ്": 7.0, "ഏഴു": 7.0, "എട്ട്": 8.0, "എട്ടു": 8.0,
        "ഒമ്പത്": 9.0, "ഒൻപത്": 9.0, "പത്ത്": 10.0, "പത്തു": 10.0,
        "പതിനൊന്ന്": 11.0, "പന്ത്രണ്ട്": 12.0, "അര": 0.5, "അര ഡസൻ": 6.0, "ഒരു ഡസൻ": 12.0
    },
    units_map={
        "കുപ്പി": "bottles", "കുപ്പികൾ": "bottles",
        "പാക്കറ്റ്": "packets", "പാക്കറ്റുകൾ": "packets", "പാക്ക്": "packets",
        "കിലോ": "kg", "കിലോഗ്രാം": "kg", "ഗ്രാം": "grams", "ഗ്രാമുകൾ": "grams",
        "ലിറ്റർ": "liters", "ലിറ്റര്": "liters", "ലിറ്ററുകൾ": "liters",
        "കാർട്ടൺ": "cartons", "കാൻ": "cans", "ബാഗ്": "bags", "ബോക്സ്": "boxes", "ജാർ": "jars", "റോൾ": "rolls"
    },
    filler_words={"ദയവായി", "എനിക്ക്", "എന്റെ", "ലിസ്റ്റിലേക്ക്", "ഷോപ്പിംഗ് ലിസ്റ്റിലേക്ക്"},
    negation_markers=["വേണ്ട", "ചേർക്കണ്ട", "വാങ്ങണ്ട", "വേണ്ടതില്ല", "ചെക്ക്ഔട്ട് ചെയ്യണ്ട", "ഓർഡർ ചെയ്യണ്ട"],
    correction_markers=["അല്ല", "സോറി", "പകരം"],
    product_aliases={
        "പാൽ": "milk", "പാല്": "milk", "പാലിന്റെ": "milk", "പാലിന്": "milk", "paal": "milk",
        "ആപ്പിൾ": "apples", "ആപ്പിള്": "apples", "ആപ്പിളുകൾ": "apples", "ആപ്പിളിന്റെ": "apples",
        "ഏത്തപ്പഴം": "bananas", "വാഴപ്പഴം": "bananas", "പഴം": "bananas",
        "തൈര്": "curd", "അരി": "rice", "ബ്രെഡ്": "bread", "റൊട്ടി": "bread",
        "ചിപ്സ്": "chips", "ടൂത്ത് പേസ്റ്റ്": "toothpaste", "ടൂത്ത്പേസ്റ്റ്": "toothpaste",
        "സോപ്പ്": "soap", "വെള്ളം": "water", "ജ്യൂസ്": "juice", "ചീസ്": "cheese",
        "വെണ്ണ": "butter", "മുട്ട": "eggs", "മുട്ടകൾ": "eggs", "തക്കാളി": "tomatoes",
        "ഉള്ളി": "onions", "ഉരുളക്കിഴങ്ങ്": "potatoes", "പഞ്ചസാര": "sugar",
        "ഉപ്പ്": "salt", "എണ്ണ": "cooking oil"
    }
)


PROFILES = [ENGLISH_PROFILE, MALAYALAM_PROFILE]


def parse_multilingual_number(token: str) -> Optional[float]:
    """Parse number digit or number word across English and Malayalam profiles."""
    if not token:
        return None
    s = token.strip().lower()
    for profile in PROFILES:
        if s in profile.number_words:
            return profile.number_words[s]
    try:
        return float(s)
    except ValueError:
        return None


def parse_multilingual_unit(token: str) -> Optional[str]:
    """Parse unit token across English and Malayalam profiles."""
    if not token:
        return None
    s = token.strip().lower()
    for profile in PROFILES:
        if s in profile.units_map:
            return profile.units_map[s]
    return None


def detect_negation(text: str) -> bool:
    """
    Checks if text contains explicit negation command markers across profiles
    (e.g., "don't add milk", "do not buy milk", "don't need milk" without "anymore").
    """
    if not text:
        return False
    norm = text.strip().lower()
    for profile in PROFILES:
        for marker in profile.negation_markers:
            if marker in norm:
                if "anymore" in norm:
                    continue
                return True
    return False


def apply_corrections(text: str) -> str:
    """
    Resolves self-corrections deterministically across profiles.
    Example:
    - "add milk, actually bread" -> "add bread"
    - "add milk, no bread" -> "add bread"
    - "add two apples, sorry, three apples" -> "add three apples"
    """
    if not text:
        return ""
    s = text.strip()
    norm = s.lower()

    correction_patterns = [
        r'(.+?),\s*(?:actually|no|sorry|i\s+mean|instead)\s*,?\s*(.+)',
        r'(.+?)\s+(?:actually|no|sorry|i\s+mean|instead)\s+(.+)'
    ]

    for pat in correction_patterns:
        m = re.match(pat, norm, flags=re.IGNORECASE)
        if m:
            first_part = m.group(1).strip()
            second_part = m.group(2).strip()

            verb_match = re.match(r'^(add|buy|need|get|put|i\s+need|can\s+you\s+add|please\s+add)\s+', first_part, flags=re.IGNORECASE)
            if verb_match and not re.match(r'^(add|buy|need|get|put)\s+', second_part, flags=re.IGNORECASE):
                prefix = verb_match.group(0)
                return f"{prefix}{second_part}"
            return second_part

    return s


SUPPORTED_LANGUAGES = {
    "en": "English",
    "ml": "Malayalam"
}
