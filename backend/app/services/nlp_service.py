import re
import unicodedata
from typing import Optional, Tuple, Dict, Any, List
from app.schemas.intent import ParsedIntent, IntentEnum, IntentItem
from app.services.language_profiles import (
    parse_multilingual_number,
    parse_multilingual_unit,
    detect_negation,
    apply_corrections,
    ENGLISH_PROFILE,
    MALAYALAM_PROFILE
)

NUMBER_WORDS = {
    "a": 1.0,
    "an": 1.0,
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0,
    "six": 6.0,
    "seven": 7.0,
    "eight": 8.0,
    "nine": 9.0,
    "ten": 10.0,
    "eleven": 11.0,
    "twelve": 12.0,
    "half": 0.5,
    "dozen": 12.0,
}

UNITS_MAP = {
    "bottle": "bottles",
    "bottles": "bottles",
    "packet": "packets",
    "packets": "packets",
    "pack": "packets",
    "packs": "packets",
    "package": "packets",
    "packages": "packets",
    "pkt": "packets",
    "pkts": "packets",
    "kg": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "g": "grams",
    "gram": "grams",
    "grams": "grams",
    "lb": "lbs",
    "lbs": "lbs",
    "pound": "lbs",
    "pounds": "lbs",
    "liter": "liters",
    "liters": "liters",
    "litre": "liters",
    "litres": "liters",
    "carton": "cartons",
    "cartons": "cartons",
    "dozen": "dozen",
    "dozens": "dozen",
    "box": "boxes",
    "boxes": "boxes",
    "can": "cans",
    "cans": "cans",
    "bag": "bags",
    "bags": "bags",
    "jar": "jars",
    "jars": "jars",
    "bar": "bars",
    "bars": "bars",
    "roll": "rolls",
    "rolls": "rolls"
}

KNOWN_BRANDS = [
    "dove", "crest", "tropicana", "lay's", "lays", "dole", "starbucks",
    "bounty", "dawn", "chobani", "tillamook", "land o'lakes", "driscoll's",
    "nature's own", "organic girl", "coke", "cocacola", "pepsi"
]

MALAYALAM_NUMBER_WORDS = {
    "ഒന്ന്": 1.0,
    "ഒരു": 1.0,
    "ഒരേ": 1.0,
    "രണ്ട്": 2.0,
    "രണ്ടു": 2.0,
    "മൂന്ന്": 3.0,
    "മൂന്നു": 3.0,
    "നാല്": 4.0,
    "നാലു": 4.0,
    "അഞ്ച്": 5.0,
    "അഞ്ചു": 5.0,
    "ആറ്": 6.0,
    "ആറു": 6.0,
    "ഏഴ്": 7.0,
    "ഏഴു": 7.0,
    "എട്ട്": 8.0,
    "എട്ടു": 8.0,
    "ഒമ്പത്": 9.0,
    "ഒൻപത്": 9.0,
    "പത്ത്": 10.0,
    "പത്തു": 10.0,
    "പതിനൊന്ന്": 11.0,
    "പന്ത്രണ്ട്": 12.0,
    "അര": 0.5,
    "അര ഡസൻ": 6.0,
    "ഒരു ഡസൻ": 12.0,
}

MALAYALAM_UNITS_MAP = {
    "കുപ്പി": "bottles",
    "കുപ്പികൾ": "bottles",
    "പാക്കറ്റ്": "packets",
    "പാക്കറ്റുകൾ": "packets",
    "പാക്ക്": "pack",
    "കിലോ": "kg",
    "കിലോഗ്രാം": "kg",
    "ഗ്രാം": "g",
    "ഗ്രാമുകൾ": "g",
    "ലിറ്റർ": "liters",
    "ലിറ്റര്": "liters",
    "ലിറ്ററുകൾ": "liters",
    "കാർട്ടൺ": "cartons",
    "കാൻ": "cans",
    "ബാഗ്": "bags",
    "ബോക്സ്": "boxes",
    "ജാർ": "jars",
    "റോൾ": "rolls",
}

MALAYALAM_ITEM_MAP = {
    "പാൽ": "milk",
    "പാലിന്റെ": "milk",
    "പാലിന്": "milk",
    "ആപ്പിൾ": "apples",
    "ആപ്പിളുകൾ": "apples",
    "ആപ്പിളിന്റെ": "apples",
    "ഏത്തപ്പഴം": "bananas",
    "വാഴപ്പഴം": "bananas",
    "പഴം": "bananas",
    "തൈര്": "curd",
    "അരി": "rice",
    "ബ്രെഡ്": "bread",
    "റൊട്ടി": "bread",
    "ചിപ്സ്": "chips",
    "ടൂത്ത് പേസ്റ്റ്": "toothpaste",
    "ടൂത്ത്പേസ്റ്റ്": "toothpaste",
    "സോപ്പ്": "soap",
    "വെള്ളം": "water",
    "ജ്യൂസ്": "juice",
    "ചീസ്": "cheese",
    "വെണ്ണ": "butter",
    "മുട്ട": "eggs",
    "മുട്ടകൾ": "eggs",
    "തക്കാളി": "tomatoes",
    "ഉള്ളി": "onions",
    "ഉരുളക്കിഴങ്ങ്": "potatoes",
    "പഞ്ചസാര": "sugar",
    "ചായ": "tea",
    "കാപ്പി": "coffee",
}

MALAYALAM_DIGITS = {
    '൦': '0', '൧': '1', '൨': '2', '൩': '3', '൪': '4',
    '൫': '5', '൬': '6', '൭': '7', '൮': '8', '൯': '9'
}

KNOWN_COMPOUND_PRODUCTS = [
    "half and half", "mac and cheese", "macaroni and cheese",
    "salt and pepper", "pork and beans", "fish and chips"
]


def contains_malayalam(text: str) -> bool:
    """Check if string contains Malayalam Unicode characters (U+0D00 - U+0D7F)."""
    return any('\u0d00' <= char <= '\u0d7f' for char in text)


def extract_bilingual_add_items(norm_text: str) -> List[IntentItem]:
    """
    Unified deterministic parser for English, Malayalam, and Code-Switched ADD_ITEM commands.
    Extracts quantities, units, and product names across languages.
    """
    s = norm_text.strip()
    if not s:
        return []

    # Guard: Ensure command contains at least one shopping indicator (add trigger, digit, number word, unit, or product noun)
    add_indicators = [
        r'\badd\b', r'\bbuy\b', r'\bneed\b', r'\bput\b', r'\bget\b',
        r'ചേർക്കൂ', r'ചേർക്കുക', r'വാങ്ങണം', r'വാങ്ങൂ', r'വേണം', r'ഉൾപ്പെടുത്തൂ', r'എടുക്കൂ',
        r'\band\b', r'\bthen\b'
    ]
    has_indicator = any(re.search(pat, norm_text, flags=re.IGNORECASE) for pat in add_indicators)
    has_num = any(parse_multilingual_number(t) is not None for t in norm_text.split())
    has_unit = any(parse_multilingual_unit(t) is not None for t in norm_text.split())
    has_known_product = any(
        t in MALAYALAM_ITEM_MAP or t in {
            "milk", "bread", "eggs", "apples", "bananas", "rice", "water", "cheese", "butter", "yoghurt", "yogurt",
            "curd", "chips", "toothpaste", "soap", "juice", "tomatoes", "onions", "potatoes", "sugar", "salt", "oil"
        }
        for t in norm_text.lower().split()
    )

    if not (has_indicator or has_num or has_unit or has_known_product):
        return []

    # Step 1: Protect known compound product names from 'and' splitting
    protected_map = {}
    for idx, phrase in enumerate(KNOWN_COMPOUND_PRODUCTS):
        if phrase in s.lower():
            placeholder = f"__PROTECTED_COMPOUND_{idx}__"
            protected_map[placeholder] = phrase
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            s = pattern.sub(placeholder, s)

    # Step 2: Strip leading fillers/triggers across English and Malayalam
    leading_fillers = r'^(?:i\s+want\s+to\s+buy|i\s+need|can\s+you\s+add|please\s+put|please\s+add|add\s+to|add|buy\s+to|buy|need\s+to|need|get\s+to|get|put|ദയവായി|എനിക്ക്|എന്റെ|ലിസ്റ്റിലേക്ക്|ഷോപ്പിംഗ്\s+ലിസ്റ്റിലേക്ക്)\s+'
    s = re.sub(leading_fillers, '', s, flags=re.IGNORECASE).strip()

    # Step 3: Strip trailing fillers/verbs across English and Malayalam
    trailing_fillers = r'\s+(?:on|to)\s+(?:my\s+|the\s+)?(?:shopping\s+)?list$'
    s = re.sub(trailing_fillers, '', s, flags=re.IGNORECASE).strip()
    s = re.sub(r'\s+(?:on\s+my\s+list|to\s+my\s+list|ഷോപ്പിംഗ്\s+ലിസ്റ്റിലേക്ക്|ലിസ്റ്റിലേക്ക്)$', '', s, flags=re.IGNORECASE).strip()

    ml_add_verbs = ["ചേർക്കൂ", "ചേർക്കുക", "വാങ്ങണം", "വാങ്ങൂ", "വേണം", "ഉൾപ്പെടുത്തൂ", "എടുക്കൂ"]
    for v in ml_add_verbs:
        if s.endswith(" " + v) or s == v:
            s = re.sub(rf'\s+{re.escape(v)}$', '', s).strip()

    # Step 4: Replace clause boundary connectors with standard comma delimiter ', '
    s = re.sub(r'[\s,]+(?:and\s+)?then(?:\s+(?:add|buy|need|get|put)(?:\s+to)?)?', ', ', s, flags=re.IGNORECASE)
    for v in ml_add_verbs:
        s = s.replace(f" {v} ", " , ")
    s = re.sub(r'(?<=\w)\s+(?:add|buy|need|get|put)(?:\s+to)?\s+', ', ', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+and\s+', ', ', s, flags=re.IGNORECASE)

    # Step 5: Split into clauses by comma
    clauses = [c.strip() for c in s.split(',') if c.strip()]

    items: List[IntentItem] = []
    for clause in clauses:
        # Restore protected placeholders
        for ph, orig in protected_map.items():
            if ph in clause:
                clause = clause.replace(ph, orig)

        # Clean filler words from clause start/end
        clause = re.sub(r'^(?:please|add|buy|need|get|put|i\s+need|can\s+you\s+add|to|the|then|ദയവായി)\s+', '', clause, flags=re.IGNORECASE).strip()
        clause = re.sub(r'\s+(?:then|please|to|ചേർക്കൂ|ചേർക്കുക|വാങ്ങണം|വാങ്ങൂ|വേണം)$', '', clause, flags=re.IGNORECASE).strip()

        for v in ml_add_verbs:
            if clause.endswith(" " + v) or clause == v:
                clause = re.sub(rf'\s+{re.escape(v)}$', '', clause).strip()

        if not clause:
            continue

        # Check if clause tokens are Malayalam conjunction items (e.g. "പാലും ബ്രെഡും")
        toks_check = clause.split()
        is_ml_conj = (
            len(toks_check) > 1 and
            all(t.endswith(("ഉം", "യും", "വും")) for t in toks_check) and
            not any(parse_multilingual_number(t) is not None for t in toks_check)
        )
        if is_ml_conj:
            for t in toks_check:
                stem = re.sub(r'(?:ഉം|യും|വും)$', '', t).strip()
                clean_name = MALAYALAM_ITEM_MAP.get(stem, stem)
                if clean_name:
                    items.append(IntentItem(item=clean_name, quantity=1.0, unit=None))
            continue

        # Extract Quantity, Unit, and Item from clause deterministically across languages
        qty_val: Optional[float] = None
        unit_val: Optional[str] = None
        rem_text = clause

        # Try parsing quantity (English or Malayalam number words or digits)
        tokens = rem_text.split()
        if tokens:
            for num_phrase, num_num in sorted({**NUMBER_WORDS, **MALAYALAM_NUMBER_WORDS}.items(), key=lambda x: len(x[0]), reverse=True):
                if rem_text.lower().startswith(num_phrase + " "):
                    qty_val = num_num
                    rem_text = rem_text[len(num_phrase):].strip()
                    tokens = rem_text.split()
                    break

            if qty_val is None and tokens:
                first_num = parse_multilingual_number(tokens[0])
                if first_num is not None:
                    qty_val = first_num
                    tokens = tokens[1:]

            if tokens:
                u_cand = tokens[0].lower()
                parsed_u = parse_multilingual_unit(u_cand)
                if parsed_u is not None:
                    unit_val = parsed_u
                    tokens = tokens[1:]
                elif u_cand == "of" and len(tokens) > 1:
                    tokens = tokens[1:]

            item_str = " ".join(tokens).strip()
            item_str = re.sub(r'^of\s+', '', item_str, flags=re.IGNORECASE).strip()
            item_stem = re.sub(r'(?:ഉം|യും|വും|ന്റെ|ഇന്റെ)$', '', item_str).strip()

            clean_item = (
                MALAYALAM_ITEM_MAP.get(item_stem) or
                MALAYALAM_ITEM_MAP.get(item_str) or
                item_str
            )

            # Restore protected placeholders if present
            for ph, orig in protected_map.items():
                if ph in clean_item:
                    clean_item = clean_item.replace(ph, orig)

            clean_item = clean_item.strip()
            if clean_item:
                items.append(IntentItem(
                    item=clean_item,
                    quantity=qty_val if qty_val is not None else 1.0,
                    unit=unit_val
                ))

    return items


def extract_compound_add_items(norm_text: str) -> List[IntentItem]:
    return extract_bilingual_add_items(norm_text)


def extract_malayalam_compound_add_items(norm_text: str) -> List[IntentItem]:
    return extract_bilingual_add_items(norm_text)


class NLPService:
    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        s = unicodedata.normalize("NFC", text)
        s = s.strip()
        if not contains_malayalam(s):
            s = s.lower()
        s = re.sub(r'\s+', ' ', s)
        s = re.sub(r'[!?.,]+$', '', s)
        s = s.strip()
        return s

    @staticmethod
    def parse_number(val_str: str) -> Optional[float]:
        return parse_multilingual_number(val_str)

    @staticmethod
    def extract_quantity_unit_item(text: str) -> Tuple[Optional[float], Optional[str], str]:
        s = text.strip()
        s = re.sub(r'^(?:please|add|i need|i want to buy|buy|please put|put|can you add|add to my list|to my list|on my list|get|to|the|ദയവായി)\s+', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\s+(?:on|to)\s+(?:my\s+|the\s+)?(?:shopping\s+)?list$', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\s+(?:then|please|to|ചേർക്കൂ|ചേർക്കുക|വാങ്ങണം|വാങ്ങൂ|വേണം)$', '', s, flags=re.IGNORECASE)
        s = s.strip()

        parsed_items = extract_bilingual_add_items(s)
        if parsed_items:
            first = parsed_items[0]
            return first.quantity, first.unit, first.item

        return 1.0, None, s

    @staticmethod
    def parse_malayalam_transcript(raw_text: str, norm: Optional[str] = None) -> ParsedIntent:
        return NLPService.parse_transcript(raw_text)

    @staticmethod
    def parse_transcript(transcript: str, language: str = "en-US") -> ParsedIntent:
        """
        Main deterministic entrypoint for converting voice transcript to ParsedIntent.
        Supports English, Malayalam, and Bilingual Code-Switching commands.
        """
        raw_text = transcript
        norm = NLPService.normalize_text(raw_text)

        if not norm:
            return ParsedIntent(
                intent=IntentEnum.UNKNOWN,
                confidence=0.0,
                original_text=raw_text,
                normalized_text="",
                message="Empty input command"
            )

        # Apply self-corrections (e.g. "add milk, actually bread" -> "add bread", "milk വേണ്ട, bread വേണം")
        norm = apply_corrections(norm)

        # Negation safety gate: Block negated addition / checkout commands
        if detect_negation(norm):
            if any(k in norm.lower() for k in ["checkout", "order", "place", "ചെക്ക്ഔട്ട്", "ഓർഡർ"]):
                return ParsedIntent(
                    intent=IntentEnum.CANCEL_ORDER,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm,
                    message="Order placement cancelled."
                )
            return ParsedIntent(
                intent=IntentEnum.UNKNOWN,
                confidence=0.0,
                original_text=raw_text,
                normalized_text=norm,
                message="Negated command. No items were added."
            )

        # 0. CHECKOUT / CANCEL / CONFIRM (Multilingual / Code-Switching)
        checkout_patterns = [
            r'\b(?:place|complete|finish|submit)\s+(?:the|my|an|a)?\s*order\b',
            r'\b(?:check\s*out|checkout)\b',
            r'\b(?:buy|order)\s+(?:everything|all|my\s+groceries)(?:\s+(?:in|on)\s+(?:my|the)\s+(?:cart|list))?\b',
            r'(?:order|ഓർഡർ|ഓര്ഡര്)\s*(?:place|പ്ലേസ്|ചെയ്യൂ|ചെയ്യണം|ചെയ്യുക|ഇടൂ|ആക്കൂ)',
            r'(?:cart|groceries)\s*(?:checkout|order)',
            r'cart\s*(?:total\s*)?(?:എത്രയാണ്|കാണിക്കൂ|കാണിക്കുക|മൊത്തം|total)',
            r'മൊത്തം\s+എത്രയാണ്',
            r'ചെക്ക്\s*ഔട്ട്',
            r'^(?:how\s+much\s+is|what\s*\'?s)\s+(?:my\s+)?cart(?:\s+total)?$',
            r'^(?:how\s+much\s+is|what\s*\'?s)\s+my\s+total$',
            r'^what\s+is\s+(?:the\s+|my\s+)?total\??$',
            r'^how\s+much\s+will\s+everything\s+cost\??$'
        ]
        for pat in checkout_patterns:
            if re.search(pat, norm, flags=re.IGNORECASE):
                return ParsedIntent(
                    intent=IntentEnum.CHECKOUT,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        cancel_patterns = [
            r'^(?:no|cancel|stop|don\'t\s+checkout|do\s+not\s+checkout|do\s+not\s+place\s+my\s+order|don\'t\s+place\s+my\s+order|don\'t\s+place\s+the\s+order|do\s+not\s+place\s+the\s+order|i\s+don\'t\s+want\s+to\s+checkout|i\s+don\'t\s+want\s+to\s+place\s+my\s+order|i\s+don\'t\s+want\s+to\s+buy\s+these|വേണ്ട|ഇല്ല|വേണ്ടതില്ല|നിർത്തൂ)$'
        ]
        for pat in cancel_patterns:
            if re.search(pat, norm, flags=re.IGNORECASE):
                return ParsedIntent(
                    intent=IntentEnum.CANCEL_ORDER,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        confirm_patterns = [
            r'^(?:yes|yes\s+please|confirm|confirm\s+it|place\s+it|go\s+ahead|do\s+it|yeah|sure|ok|okay|ആതെ|അതെ|ശരി|തീർച്ചയായും|ഉവ്വ്|confirm\s*ചെയ്യൂ)$'
        ]
        confirm_patterns = [
            r'^(?:yes|yeah|yep|ok|okay|confirm|confirmed|proceed|go\s+ahead|do\s+it|place\s+it|place\s+the\s+order|ആതെ|അതെ|ശരി|തീർച്ചയായും|ഉവ്വ്|വേണം|ചെയ്യ്യൂ|സ്ഥിരീകരിക്കൂ|ആക്കൂ|മുന്നോട്ട്\s+പോകൂ)(?:[\s,]+(?:please|confirm|confirmed|place\s+it|place\s+the\s+order|do\s+it|proceed|ചെയ്യൂ|ചെയ്യണം|ആക്കൂ|ഇടൂ|place|it))*$',
            r'\b(?:yes|ok|okay|അതെ|ശരി)\b.*?\b(?:confirm|place|order)\b',
            r'\b(?:confirm|സ്ഥിരീകരിക്കൂ)\s*(?:order|ചെയ്യൂ|ചെയ്യുക)?\b',
            r'^(?:yes\s+please|yes\s+confirm|okay\s+confirm|confirm\s+order|അതെ\s+confirm|ശരി\s+confirm\s*ചെയ്യൂ|yes\s*ചെയ്യൂ|yes\s*place\s*ചെയ്യൂ|അതെ\s*place\s*ചെയ്യൂ|ശരി\s*order\s*place\s*ചെയ്യൂ)$'
        ]
        for pat in confirm_patterns:
            if re.search(pat, norm, flags=re.IGNORECASE):
                return ParsedIntent(
                    intent=IntentEnum.CONFIRM_ORDER,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 1. CLEAR_LIST (Explicit match)
        clear_patterns = [
            r'^(?:clear|empty|delete)\s+(?:all\s+)?(?:my\s+|the\s+)?(?:items|shopping\s+list|list)$',
            r'^remove\s+everything(?:\s+from\s+(?:my\s+|the\s+)?list)?$',
            r'^delete\s+all(?:\s+items)?$',
            r'^(?:ലിസ്റ്റ്\s+)?ക്ലിയർ\s+ചെയ്യൂ$',
            r'^എല്ലാം\s+നീക്കം\s+ചെയ്യൂ$',
            r'^(?:ലിസ്റ്റ്\s+)?മൊത്തം\s+കളയൂ$',
            r'^എല്ലാ\s+ഉൽപ്പന്നങ്ങളും\s+നീക്കം\s+ചെയ്യൂ$',
            r'^ലിസ്റ്റ്\s+ക്ലിയർ\s+ചെയ്യുക$'
        ]
        for pat in clear_patterns:
            if re.search(pat, norm, flags=re.IGNORECASE):
                return ParsedIntent(
                    intent=IntentEnum.CLEAR_LIST,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 2. SHOW_LIST
        show_patterns = [
            r'^(?:show|view|read|display|see)\s+(?:my\s+|the\s+)?(?:shopping\s+)?list$',
            r'^what(?:\s*\'?s|\s+is)\s+on\s+(?:my\s+|the\s+)?(?:shopping\s+)?list$',
            r'^(?:എന്റെ\s+)?(?:ഷോപ്പിംഗ്\s+)?ലിസ്റ്റ്\s+കാണിക്കൂ$',
            r'^ലിസ്റ്റിൽ\s+എന്തൊക്കെയുണ്ട്$',
            r'^(?:എന്റെ\s+)?ലിസ്റ്റ്\s+വായിക്കൂ$',
            r'^ഷോപ്പിംഗ്\s+ലിസ്റ്റ്\s+കാണിക്കൂ$'
        ]
        for pat in show_patterns:
            if re.search(pat, norm, flags=re.IGNORECASE):
                return ParsedIntent(
                    intent=IntentEnum.SHOW_LIST,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 3. GET_SUGGESTIONS
        suggestion_patterns = [
            r'^what\s+should\s+i\s+buy$',
            r'^what\s+am\s+i\s+missing$',
            r'^(?:give\s+me\s+|get\s+)?(?:shopping\s+)?suggestions$',
            r'^what\s+do\s+i\s+usually\s+buy$',
            r'^suggest\s+(?:some\s+)?items$',
            r'^എന്തൊക്കെ\s+വാങ്ങണം\??$',
            r'^(?:എനിക്ക്\s+)?നിർദ്ദേശങ്ങൾ\s+നൽകൂ$',
            r'^ഞാൻ\s+എന്താണ്\s+വാങ്ങേണ്ടത്$'
        ]
        for pat in suggestion_patterns:
            if re.search(pat, norm, flags=re.IGNORECASE):
                return ParsedIntent(
                    intent=IntentEnum.GET_SUGGESTIONS,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 4. UPDATE_QUANTITY
        update_patterns = [
            r'^(?:change|update|set)\s+(?:the\s+)?(?:quantity\s+of\s+)?(?P<item>.+?)\s+(?:quantity\s+)?to\s+(?P<qty>\d+(?:\.\d+)?|\b[a-z]+\b)$',
            r'^make\s+(?:the\s+)?(?P<item>.+?)\s+quantity\s+(?P<qty>\d+(?:\.\d+)?|\b[a-z]+\b)$',
            r'^i\s+need\s+(?P<qty>\d+(?:\.\d+)?|\b[a-z]+\b)\s+(?P<item>.+?)\s+instead$',
            r'^(?P<item>.+?)(?:\s+(?:ന്റെ|ഇന്റെ|അളവ്|എണ്ണം))*\s+(?P<qty>\d+|[^\s]+)\s+(?:ആക്കൂ|ആക്കുക|മാറ്റൂ|ആക്ക്)$'
        ]
        for pat in update_patterns:
            m = re.match(pat, norm, flags=re.IGNORECASE)
            if m:
                item_str = m.group("item").strip()
                item_str = re.sub(r'\s+(?:ന്റെ|ഇന്റെ|അളവ്|എണ്ണം)$', '', item_str).strip()
                qty_str = m.group("qty").strip()
                qty = parse_multilingual_number(qty_str)

                qty_val, unit, clean_item = NLPService.extract_quantity_unit_item(item_str)
                final_qty = qty if qty is not None else qty_val

                clean_item = (
                    MALAYALAM_ITEM_MAP.get(clean_item) or
                    clean_item
                )

                return ParsedIntent(
                    intent=IntentEnum.UPDATE_QUANTITY,
                    item=clean_item,
                    quantity=final_qty,
                    unit=unit,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 5. SEARCH_PRODUCT
        search_triggers = [r'^find\b', r'^search\s+for\b', r'^search\b', r'^look\s+for\b', r'^show\s+me\b']
        if any(re.search(pat, norm, flags=re.IGNORECASE) for pat in search_triggers):
            norm_search = re.sub(r'^(?:find|search\s+for|search|look\s+for|show\s+me)\s+', '', norm, flags=re.IGNORECASE).strip()

            max_price: Optional[float] = None
            min_price: Optional[float] = None
            num_expr = r'(?:\d+(?:\.\d+)?|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|fifty)\b)'
            curr_sym = r'[\$₹]?'
            curr_unit = r'(?:\s+(?:dollars?|rupees?|rs\.?))?'

            m_between = re.search(rf'between\s+{curr_sym}({num_expr})\s+and\s+{curr_sym}({num_expr}){curr_unit}', norm_search, flags=re.IGNORECASE)
            if m_between:
                val1 = NLPService.parse_number(m_between.group(1))
                val2 = NLPService.parse_number(m_between.group(2))
                if val1 is not None and val2 is not None:
                    min_price = min(val1, val2)
                    max_price = max(val1, val2)
                    norm_search = re.sub(rf'between\s+{curr_sym}{num_expr}\s+and\s+{curr_sym}{num_expr}{curr_unit}', '', norm_search, flags=re.IGNORECASE).strip()
            else:
                m_max = re.search(rf'(?:under|below|less\s+than|up\s+to)\s+{curr_sym}({num_expr}){curr_unit}', norm_search, flags=re.IGNORECASE)
                if m_max:
                    val_max = NLPService.parse_number(m_max.group(1))
                    if val_max is not None:
                        max_price = val_max
                        norm_search = re.sub(rf'(?:under|below|less\s+than|up\s+to)\s+{curr_sym}{num_expr}{curr_unit}', '', norm_search, flags=re.IGNORECASE).strip()
                else:
                    m_min = re.search(rf'(?:above|over|more\s+than|at\s+least)\s+{curr_sym}({num_expr}){curr_unit}', norm_search, flags=re.IGNORECASE)
                    if m_min:
                        val_min = NLPService.parse_number(m_min.group(1))
                        if val_min is not None:
                            min_price = val_min
                            norm_search = re.sub(rf'(?:above|over|more\s+than|at\s+least)\s+{curr_sym}{num_expr}{curr_unit}', '', norm_search, flags=re.IGNORECASE).strip()

            brand: Optional[str] = None
            m_brand = re.search(r'\b(?:from|by|brand)\s+([a-zA-Z0-9\'\s]+)$', norm_search, flags=re.IGNORECASE)
            if m_brand:
                brand = m_brand.group(1).strip()
                norm_search = re.sub(r'\b(?:from|by|brand)\s+[a-zA-Z0-9\'\s]+$', '', norm_search, flags=re.IGNORECASE).strip()
            else:
                for b in KNOWN_BRANDS:
                    if norm_search.lower().startswith(b + " "):
                        brand = b.capitalize()
                        norm_search = norm_search[len(b):].strip()
                        break

            search_query = norm_search.strip()
            if search_query.lower() in {"product", "products", "item", "items", "anything", "all", "grocery", "groceries"}:
                search_query = None

            return ParsedIntent(
                intent=IntentEnum.SEARCH_PRODUCT,
                item=search_query if search_query else None,
                max_price=max_price,
                min_price=min_price,
                brand=brand.capitalize() if brand else None,
                confidence=1.0,
                original_text=raw_text,
                normalized_text=norm
            )

        # 6. REMOVE_ITEM
        remove_patterns = [
            r'^(?:remove|delete)\s+(?P<target>.+?)\s+from\s+(?:my\s+|the\s+)?list$',
            r'^take\s+(?P<target>.+?)\s+off\s+(?:the\s+|my\s+)?list$',
            r'^i\s+(?:don\'t|dont)\s+need\s+(?P<target>.+?)\s+anymore$',
            r'^(?:remove|delete)\s+(?P<target>.+)$',
            r'^(?:ലിസ്റ്റിൽ\s+നിന്ന്\s+)?(?P<target>.+?)\s+(?:നീക്കം\s+ചെയ്യൂ|നീക്കം\s+ചെയ്യുക|കളയൂ|ഒഴിവാക്കൂ|എടുത്തു\s+മാറ്റൂ)$'
        ]
        for pat in remove_patterns:
            m = re.match(pat, norm, flags=re.IGNORECASE)
            if m:
                target = m.group("target").strip()
                qty, unit, item_name = NLPService.extract_quantity_unit_item(target)
                clean_item = (
                    MALAYALAM_ITEM_MAP.get(item_name) or
                    item_name
                )
                return ParsedIntent(
                    intent=IntentEnum.REMOVE_ITEM,
                    item=clean_item if clean_item else target,
                    quantity=qty if unit else None,
                    unit=unit,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 7. ADD_ITEM (Bilingual Code-Switching)
        extracted_items = extract_bilingual_add_items(norm)
        if extracted_items:
            first = extracted_items[0]
            return ParsedIntent(
                intent=IntentEnum.ADD_ITEM,
                item=first.item,
                quantity=first.quantity,
                unit=first.unit,
                items=extracted_items,
                confidence=1.0,
                original_text=raw_text,
                normalized_text=norm
            )

        # 8. UNKNOWN / AMBIGUOUS
        return ParsedIntent(
            intent=IntentEnum.UNKNOWN,
            confidence=0.0,
            original_text=raw_text,
            normalized_text=norm,
            message="Command not recognized"
        )
