import re
import unicodedata
from typing import Optional, Tuple, Dict, Any, List
from app.schemas.intent import ParsedIntent, IntentEnum, IntentItem
from app.services.language_profiles import (
    parse_multilingual_number,
    parse_multilingual_unit,
    detect_negation,
    apply_corrections
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


def parse_malayalam_number(val_str: str) -> Optional[float]:
    """Parse digit string or Malayalam number word into float."""
    if not val_str:
        return None
    s = val_str.strip()
    for ml_d, ascii_d in MALAYALAM_DIGITS.items():
        s = s.replace(ml_d, ascii_d)
    if s in MALAYALAM_NUMBER_WORDS:
        return MALAYALAM_NUMBER_WORDS[s]
    try:
        return float(s)
    except ValueError:
        return None


def extract_compound_add_items(norm_text: str) -> List[IntentItem]:
    """
    Parses compound ADD_ITEM text into a list of IntentItem objects.
    Handles conversational speech, 'then', 'and then', 'add to', repeated verbs, commas, and 'and'.
    Protects known compound products like 'half and half'.
    """
    s = norm_text.strip()

    # Step 1: Protect known compound product names from 'and' splitting
    protected_map = {}
    for idx, phrase in enumerate(KNOWN_COMPOUND_PRODUCTS):
        if phrase in s:
            placeholder = f"__PROTECTED_COMPOUND_{idx}__"
            protected_map[placeholder] = phrase
            s = s.replace(phrase, placeholder)

    # Step 2: Strip initial add command triggers at the very beginning of the full command
    s = re.sub(
        r'^(?:i\s+want\s+to\s+buy|i\s+need|can\s+you\s+add|please\s+put|please\s+add|add\s+to|add|buy\s+to|buy|need\s+to|need|get\s+to|get|put)\s+',
        '', s, flags=re.IGNORECASE
    )
    s = re.sub(r'\s+(?:on|to)\s+(?:my\s+|the\s+)?(?:shopping\s+)?list$', '', s, flags=re.IGNORECASE)
    s = s.strip()

    # Step 3: Normalize remaining conversational 'add to' / 'buy to'
    s = re.sub(r'\b(?:please\s+)?(?:add|buy|need|get|put)\s+to\b', 'add', s, flags=re.IGNORECASE)

    # Step 4: Replace clause boundary connectors with standard comma delimiter ', '
    # Handle 'and then', 'then', ', then', ', and then'
    s = re.sub(r'[\s,]+(?:and\s+)?then(?:\s+(?:add|buy|need|get|put)(?:\s+to)?)?', ', ', s, flags=re.IGNORECASE)

    # Handle repeated verb triggers e.g., "milk add strawberries" -> "milk, strawberries"
    s = re.sub(r'(?<=\w)\s+(?:add|buy|need|get|put)(?:\s+to)?\s+', ', ', s, flags=re.IGNORECASE)

    # Handle 'and' separators e.g., "strawberries and yoghurt" -> "strawberries, yoghurt"
    s = re.sub(r'\s+and\s+', ', ', s, flags=re.IGNORECASE)

    # Step 5: Split into individual raw clauses by comma
    clauses = [c.strip() for c in s.split(',') if c.strip()]

    items: List[IntentItem] = []
    for clause in clauses:
        # Restore protected placeholders
        for ph, orig in protected_map.items():
            if ph in clause:
                clause = clause.replace(ph, orig)

        # Strip filler prefixes from clause
        clause = re.sub(
            r'^(?:please|add|buy|need|get|put|i\s+need|i\s+want\s+to\s+buy|can\s+you\s+add|to|the|then)\s+',
            '', clause, flags=re.IGNORECASE
        ).strip()

        # Strip trailing filler words from clause
        clause = re.sub(r'\s+(?:then|please|to)$', '', clause, flags=re.IGNORECASE).strip()

        if not clause:
            continue

        qty, unit, clean_item = NLPService.extract_quantity_unit_item(clause)

        # Clean item of any remaining filler words at start/end
        clean_item = re.sub(
            r'^(?:please|add|buy|need|get|put|to|the|then)\s+',
            '', clean_item, flags=re.IGNORECASE
        ).strip()
        clean_item = re.sub(r'\s+(?:then|please|to)$', '', clean_item, flags=re.IGNORECASE).strip()

        # Restore protected placeholders if inside clean_item
        for ph, orig in protected_map.items():
            if ph in clean_item:
                clean_item = clean_item.replace(ph, orig)

        if clean_item:
            items.append(IntentItem(item=clean_item, quantity=qty, unit=unit))

    return items


def extract_malayalam_compound_add_items(norm_text: str) -> List[IntentItem]:
    """
    Parses compound Malayalam ADD_ITEM text into a list of IntentItem objects.
    """
    work_text = norm_text
    work_text = re.sub(r'^(?:എന്റെ\s+)?(?:ലിസ്റ്റിലേക്ക്|ഷോപ്പിംഗ്\s+ലിസ്റ്റിലേക്ക്|എനിക്ക്|ദയവായി)\s+', '', work_text).strip()

    add_verbs = ["ചേർക്കൂ", "ചേർക്കുക", "വാങ്ങണം", "വാങ്ങൂ", "വേണം", "ഉൾപ്പെടുത്തൂ"]

    clauses_raw = []
    if "," in work_text:
        clauses_raw = [c.strip() for c in work_text.split(",") if c.strip()]
    elif any(f" {v} " in work_text for v in add_verbs):
        for v in add_verbs:
            work_text = work_text.replace(f" {v} ", " , ")
        clauses_raw = [c.strip() for c in work_text.split(",") if c.strip()]
    else:
        clauses_raw = [work_text]

    items: List[IntentItem] = []

    for clause_str in clauses_raw:
        c_text = clause_str.strip()
        has_clause_add_verb = False
        for v in add_verbs:
            if c_text.endswith(" " + v) or c_text == v:
                c_text = re.sub(rf'\s+{re.escape(v)}$', '', c_text).strip()
                has_clause_add_verb = True
                break

        tokens = c_text.split()
        is_conj_tokens = (
            len(tokens) > 1 and
            all(t.endswith(("ഉം", "യും", "വും")) for t in tokens) and
            not any(parse_malayalam_number(t) is not None for t in tokens)
        )

        if is_conj_tokens:
            for t in tokens:
                stem = re.sub(r'(?:ഉം|യും|വും)$', '', t).strip()
                clean_name = MALAYALAM_ITEM_MAP.get(stem, stem)
                if clean_name:
                    items.append(IntentItem(item=clean_name, quantity=1.0, unit=None))
        else:
            qty_val: Optional[float] = None
            unit_val: Optional[str] = None
            rem_text = c_text

            for num_phrase, num_num in sorted(MALAYALAM_NUMBER_WORDS.items(), key=lambda x: len(x[0]), reverse=True):
                if rem_text.startswith(num_phrase + " "):
                    qty_val = num_num
                    rem_text = rem_text[len(num_phrase):].strip()
                    break

            toks = rem_text.split()
            if toks:
                if qty_val is None:
                    pq = parse_malayalam_number(toks[0])
                    if pq is not None:
                        qty_val = pq
                        toks = toks[1:]

                if toks:
                    u_cand = toks[0].lower()
                    if u_cand in MALAYALAM_UNITS_MAP:
                        unit_val = MALAYALAM_UNITS_MAP[u_cand]
                        toks = toks[1:]
                    elif u_cand in UNITS_MAP:
                        unit_val = UNITS_MAP[u_cand]
                        toks = toks[1:]

                item_str = " ".join(toks).strip()
                item_stem = re.sub(r'(?:ഉം|യും|വും)$', '', item_str).strip()
                clean_item = MALAYALAM_ITEM_MAP.get(item_stem, MALAYALAM_ITEM_MAP.get(item_str))
                if clean_item is not None or has_clause_add_verb or qty_val is not None or unit_val is not None:
                    final_item = clean_item if clean_item is not None else item_str
                    if final_item:
                        items.append(IntentItem(
                            item=final_item,
                            quantity=qty_val if qty_val is not None else 1.0,
                            unit=unit_val
                        ))

    return items


class NLPService:
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalizes natural language input:
        - Unicode NFC normalization
        - Strip leading/trailing whitespace
        - Convert to lower-case for non-Malayalam text
        - Collapse multiple spaces
        - Remove trailing punctuation (!, ?, .) while preserving $ and decimals
        """
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
        """Converts digit string or number word to float."""
        if not val_str:
            return None
        val_str = val_str.strip().lower()
        if val_str in NUMBER_WORDS:
            return NUMBER_WORDS[val_str]
        try:
            return float(val_str)
        except ValueError:
            return None

    @staticmethod
    def extract_quantity_unit_item(text: str) -> Tuple[Optional[float], Optional[str], str]:
        """
        Extracts (quantity, unit, clean_item_name) from text.
        Supports patterns:
        - "2 bottles of milk" -> (2.0, "bottles", "milk")
        - "3 cartons orange juice" -> (3.0, "cartons", "orange juice")
        - "5 oranges" -> (5.0, None, "oranges")
        - "milk" -> (1.0, None, "milk")
        """
        s = text.strip()
        
        # Strip common filler prefixes and suffixes
        s = re.sub(r'^(?:please|add|i need|i want to buy|buy|please put|put|can you add|add to my list|to my list|on my list|get|to|the)\s+', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\s+(?:on|to)\s+(?:my\s+|the\s+)?(?:shopping\s+)?list$', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\s+(?:then|please|to)$', '', s, flags=re.IGNORECASE)
        s = s.strip()

        units_pattern = r'|'.join(re.escape(u) for u in sorted(UNITS_MAP.keys(), key=len, reverse=True))
        num_pattern = r'\d+(?:\.\d+)?|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|half|a dozen|a|an)\b'

        # Match "2 bottles of milk" or "three cartons milk"
        match_unit = re.match(
            rf'^(?P<qty>{num_pattern})\s+(?P<unit>{units_pattern})\s+(?:of\s+)?(?P<item>.+)$',
            s,
            flags=re.IGNORECASE
        )
        if match_unit:
            qty_raw = match_unit.group("qty")
            unit_raw = match_unit.group("unit").lower()
            item_raw = match_unit.group("item").strip()
            
            qty = NLPService.parse_number(qty_raw)
            unit = UNITS_MAP.get(unit_raw, unit_raw)
            return qty if qty is not None else 1.0, unit, item_raw

        # Match "5 oranges" or "two apples"
        match_qty = re.match(
            rf'^(?P<qty>{num_pattern})\s+(?P<item>.+)$',
            s,
            flags=re.IGNORECASE
        )
        if match_qty:
            qty_raw = match_qty.group("qty")
            item_raw = match_qty.group("item").strip()
            qty = NLPService.parse_number(qty_raw)
            return qty if qty is not None else 1.0, None, item_raw

        # Default fallback: item with default quantity 1.0
        return 1.0, None, s

    @staticmethod
    def parse_malayalam_transcript(raw_text: str, norm: str) -> ParsedIntent:
        """
        Deterministic parser pipeline for Malayalam voice commands.
        """
        # 0. CHECKOUT / CONFIRM / CANCEL
        ml_checkout_patterns = [
            r'checkout\s*(?:ചെയ്യൂ|ചെയ്യുക|ആക്കൂ)?',
            r'order\s*place\s*(?:ചെയ്യൂ|ചെയ്യുക)?',
            r'cart\s*(?:കാണിക്കൂ|കാണിക്കുക|മൊത്തം|total)',
            r'മൊത്തം\s+എത്രയാണ്',
            r'എത്രയാ(?:ണ്|കും)',
            r'ചെക്ക്\s*ഔട്ട്'
        ]
        for pat in ml_checkout_patterns:
            if re.search(pat, norm, flags=re.IGNORECASE):
                return ParsedIntent(
                    intent=IntentEnum.CHECKOUT,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        ml_confirm_patterns = [
            r'^(?:ആതെ|അതെ|ശരി|തീർച്ചയായും|ഉവ്വ്|confirm\s*ചെയ്യൂ)$'
        ]
        for pat in ml_confirm_patterns:
            if re.search(pat, norm, flags=re.IGNORECASE):
                return ParsedIntent(
                    intent=IntentEnum.CONFIRM_ORDER,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        ml_cancel_patterns = [
            r'^(?:വേണ്ട|ഇല്ല|cancel\s*ചെയ്യൂ|വേണ്ടതില്ല|നിർത്തൂ)$'
        ]
        for pat in ml_cancel_patterns:
            if re.search(pat, norm, flags=re.IGNORECASE):
                return ParsedIntent(
                    intent=IntentEnum.CANCEL_ORDER,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 1. CLEAR_LIST (Explicit strict matching)
        clear_patterns = [
            r'^(?:ലിസ്റ്റ്\s+)?ക്ലിയർ\s+ചെയ്യൂ$',
            r'^എല്ലാം\s+നീക്കം\s+ചെയ്യൂ$',
            r'^(?:ലിസ്റ്റ്\s+)?മൊത്തം\s+കളയൂ$',
            r'^എല്ലാ\s+ഉൽപ്പന്നങ്ങളും\s+നീക്കം\s+ചെയ്യൂ$',
            r'^ലിസ്റ്റ്\s+ക്ലിയർ\s+ചെയ്യുക$'
        ]
        for pat in clear_patterns:
            if re.search(pat, norm):
                return ParsedIntent(
                    intent=IntentEnum.CLEAR_LIST,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 2. SHOW_LIST
        show_patterns = [
            r'^(?:എന്റെ\s+)?(?:ഷോപ്പിംഗ്\s+)?ലിസ്റ്റ്\s+കാണിക്കൂ$',
            r'^ലിസ്റ്റിൽ\s+എന്തൊക്കെയുണ്ട്$',
            r'^(?:എന്റെ\s+)?ലിസ്റ്റ്\s+വായിക്കൂ$',
            r'^ഷോപ്പിംഗ്\s+ലിസ്റ്റ്\s+കാണിക്കൂ$'
        ]
        for pat in show_patterns:
            if re.search(pat, norm):
                return ParsedIntent(
                    intent=IntentEnum.SHOW_LIST,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 3. GET_SUGGESTIONS
        suggestion_patterns = [
            r'^എന്തൊക്കെ\s+വാങ്ങണം\??$',
            r'^(?:എനിക്ക്\s+)?നിർദ്ദേശങ്ങൾ\s+നൽകൂ$',
            r'^ഞാൻ\s+എന്താണ്\s+വാങ്ങേണ്ടത്$'
        ]
        for pat in suggestion_patterns:
            if re.search(pat, norm):
                return ParsedIntent(
                    intent=IntentEnum.GET_SUGGESTIONS,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 4. UPDATE_QUANTITY
        update_match = re.match(
            r'^(?P<item>.+?)(?:\s+(?:ന്റെ|ഇന്റെ|അളവ്|എണ്ണം))*\s+(?P<qty>\d+|[^\s]+)\s+(?:ആക്കൂ|ആക്കുക|മാറ്റൂ|ആക്ക്)$',
            norm
        )
        if update_match:
            item_raw = update_match.group("item").strip()
            item_raw = re.sub(r'\s+(?:ന്റെ|ഇന്റെ|അളവ്|എണ്ണം)$', '', item_raw).strip()
            qty_raw = update_match.group("qty").strip()
            qty_val = parse_malayalam_number(qty_raw)
            if qty_val is not None:
                clean_item = MALAYALAM_ITEM_MAP.get(item_raw, item_raw)
                return ParsedIntent(
                    intent=IntentEnum.UPDATE_QUANTITY,
                    item=clean_item,
                    quantity=qty_val,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 5. REMOVE_ITEM
        remove_match = re.match(
            r'^(?:ലിസ്റ്റിൽ\s+നിന്ന്\s+)?(?P<item>.+?)\s+(?:നീക്കം\s+ചെയ്യൂ|നീക്കം\s+ചെയ്യുക|കളയൂ|ഒഴിവാക്കൂ|എടുത്തു\s+മാറ്റൂ)$',
            norm
        )
        if remove_match:
            item_raw = remove_match.group("item").strip()
            clean_item = MALAYALAM_ITEM_MAP.get(item_raw, item_raw)
            return ParsedIntent(
                intent=IntentEnum.REMOVE_ITEM,
                item=clean_item,
                confidence=1.0,
                original_text=raw_text,
                normalized_text=norm
            )

        # 6. ADD_ITEM
        ml_items = extract_malayalam_compound_add_items(norm)
        if ml_items:
            first = ml_items[0]
            return ParsedIntent(
                intent=IntentEnum.ADD_ITEM,
                item=first.item,
                quantity=first.quantity,
                unit=first.unit,
                items=ml_items,
                confidence=1.0,
                original_text=raw_text,
                normalized_text=norm
            )

        # Fallback to UNKNOWN
        return ParsedIntent(
            intent=IntentEnum.UNKNOWN,
            confidence=0.0,
            original_text=raw_text,
            normalized_text=norm,
            message="Command not recognized"
        )

    @staticmethod
    def parse_transcript(transcript: str, language: str = "en-US") -> ParsedIntent:
        """
        Main deterministic parser pipeline:
        normalization -> self-repair -> negation check -> intent detection -> entity extraction -> ParsedIntent
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

        # Apply self-corrections (e.g. "add milk, actually bread" -> "add bread")
        norm = apply_corrections(norm)

        # Negation safety gate: Block negated addition commands (e.g. "don't add milk", "do not buy milk")
        if detect_negation(norm):
            return ParsedIntent(
                intent=IntentEnum.UNKNOWN,
                confidence=0.0,
                original_text=raw_text,
                normalized_text=norm,
                message="Negated command. No items were added."
            )

        # 0. CHECKOUT / CANCEL / CONFIRM (Top-level check for English, Malayalam, and Code-Switching)
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
        for pat in confirm_patterns:
            if re.search(pat, norm, flags=re.IGNORECASE):
                return ParsedIntent(
                    intent=IntentEnum.CONFIRM_ORDER,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        if contains_malayalam(norm) or contains_malayalam(raw_text):
            return NLPService.parse_malayalam_transcript(raw_text, norm)

        # 1. CLEAR_LIST (Explicit match)
        clear_patterns = [
            r'^(?:clear|empty|delete)\s+(?:all\s+)?(?:my\s+|the\s+)?(?:items|shopping\s+list|list)$',
            r'^remove\s+everything(?:\s+from\s+(?:my\s+|the\s+)?list)?$',
            r'^delete\s+all(?:\s+items)?$'
        ]
        for pat in clear_patterns:
            if re.search(pat, norm):
                return ParsedIntent(
                    intent=IntentEnum.CLEAR_LIST,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 2. SHOW_LIST
        show_patterns = [
            r'^(?:show|view|read|display|see)\s+(?:my\s+|the\s+)?(?:shopping\s+)?list$',
            r'^what(?:\s*\'?s|\s+is)\s+on\s+(?:my\s+|the\s+)?(?:shopping\s+)?list$'
        ]
        for pat in show_patterns:
            if re.search(pat, norm):
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
            r'^suggest\s+(?:some\s+)?items$'
        ]
        for pat in suggestion_patterns:
            if re.search(pat, norm):
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
            r'^i\s+need\s+(?P<qty>\d+(?:\.\d+)?|\b[a-z]+\b)\s+(?P<item>.+?)\s+instead$'
        ]
        for pat in update_patterns:
            m = re.match(pat, norm)
            if m:
                item_str = m.group("item").strip()
                qty_str = m.group("qty").strip()
                qty = NLPService.parse_number(qty_str)
                
                # Check if item contains unit
                qty_val, unit, clean_item = NLPService.extract_quantity_unit_item(item_str)
                final_qty = qty if qty is not None else qty_val
                
                return ParsedIntent(
                    intent=IntentEnum.UPDATE_QUANTITY,
                    item=clean_item if clean_item else item_str,
                    quantity=final_qty,
                    unit=unit,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 5. SEARCH_PRODUCT
        search_triggers = [r'^find\b', r'^search\s+for\b', r'^search\b', r'^look\s+for\b', r'^show\s+me\b']
        if any(re.search(pat, norm) for pat in search_triggers):
            # Step A: Strip search trigger verb prefix first
            norm_search = re.sub(r'^(?:find|search\s+for|search|look\s+for|show\s+me)\s+', '', norm).strip()

            # Step B: Extract price filters (digits or number words)
            max_price: Optional[float] = None
            min_price: Optional[float] = None

            num_expr = r'(?:\d+(?:\.\d+)?|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|fifty)\b)'

            curr_sym = r'[\$₹]?'
            curr_unit = r'(?:\s+(?:dollars?|rupees?|rs\.?))?'

            m_between = re.search(rf'between\s+{curr_sym}({num_expr})\s+and\s+{curr_sym}({num_expr}){curr_unit}', norm_search)
            if m_between:
                val1 = NLPService.parse_number(m_between.group(1))
                val2 = NLPService.parse_number(m_between.group(2))
                if val1 is not None and val2 is not None:
                    min_price = min(val1, val2)
                    max_price = max(val1, val2)
                    norm_search = re.sub(rf'between\s+{curr_sym}{num_expr}\s+and\s+{curr_sym}{num_expr}{curr_unit}', '', norm_search).strip()
            else:
                m_max = re.search(rf'(?:under|below|less\s+than|up\s+to)\s+{curr_sym}({num_expr}){curr_unit}', norm_search)
                if m_max:
                    val_max = NLPService.parse_number(m_max.group(1))
                    if val_max is not None:
                        max_price = val_max
                        norm_search = re.sub(rf'(?:under|below|less\s+than|up\s+to)\s+{curr_sym}{num_expr}{curr_unit}', '', norm_search).strip()
                else:
                    m_min = re.search(rf'(?:above|over|more\s+than|at\s+least)\s+{curr_sym}({num_expr}){curr_unit}', norm_search)
                    if m_min:
                        val_min = NLPService.parse_number(m_min.group(1))
                        if val_min is not None:
                            min_price = val_min
                            norm_search = re.sub(rf'(?:above|over|more\s+than|at\s+least)\s+{curr_sym}{num_expr}{curr_unit}', '', norm_search).strip()

            # Step C: Extract brand filter
            brand: Optional[str] = None
            m_brand = re.search(r'\b(?:from|by|brand)\s+([a-zA-Z0-9\'\s]+)$', norm_search)
            if m_brand:
                brand = m_brand.group(1).strip()
                norm_search = re.sub(r'\b(?:from|by|brand)\s+[a-zA-Z0-9\'\s]+$', '', norm_search).strip()
            else:
                for b in KNOWN_BRANDS:
                    if norm_search.startswith(b + " "):
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
            r'^(?:remove|delete)\s+(?P<target>.+)$'
        ]
        for pat in remove_patterns:
            m = re.match(pat, norm)
            if m:
                target = m.group("target").strip()
                qty, unit, item_name = NLPService.extract_quantity_unit_item(target)
                return ParsedIntent(
                    intent=IntentEnum.REMOVE_ITEM,
                    item=item_name if item_name else target,
                    quantity=qty if unit else None,
                    unit=unit,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # 7. ADD_ITEM
        add_triggers = [
            r'^add\b', r'^i\s+need\b', r'^i\s+want\s+to\s+buy\b', r'^put\b', r'^buy\b',
            r'^please\s+put\b', r'^can\s+you\s+add\b', r'^get\b'
        ]
        is_add_cmd = any(re.search(pat, norm) for pat in add_triggers)
        num_start = re.match(r'^(?:\d+|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b)', norm)

        if is_add_cmd or num_start:
            extracted_items = extract_compound_add_items(norm)
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
