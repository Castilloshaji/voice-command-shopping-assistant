import re
import unicodedata
from typing import Optional, Tuple, Dict, Any, List
from app.schemas.intent import ParsedIntent, IntentEnum

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
    "തൈര്": "yogurt",
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
    '൦': '0', '<ctrl42>': '1', '൨': '2', '൩': '3', '൪': '4',
    '൫': '5', '൬': '6', '൭': '7', '൮': '8', '൯': '9'
}


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
        
        # Strip common filler prefixes
        s = re.sub(r'^(?:add|i need|i want to buy|buy|please put|put|can you add|add to my list|to my list|on my list)\s+', '', s, flags=re.IGNORECASE)
        s = re.sub(r'\s+(?:on|to)\s+(?:my\s+|the\s+)?(?:shopping\s+)?list$', '', s, flags=re.IGNORECASE)
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
        work_text = norm
        work_text = re.sub(r'^(?:എന്റെ\s+)?(?:ലിസ്റ്റിലേക്ക്|ഷോപ്പിംഗ്\s+ലിസ്റ്റിലേക്ക്|എനിക്ക്|ദയവായി)\s+', '', work_text).strip()

        add_verbs = [
            "ചേർക്കൂ", "ചേർക്കുക", "വാങ്ങണം", "വാങ്ങൂ", "വേണം", "ഉൾപ്പെടുത്തൂ"
        ]
        has_add_verb = False
        for v in add_verbs:
            if work_text.endswith(" " + v) or work_text == v:
                work_text = re.sub(rf'\s+{re.escape(v)}$', '', work_text).strip()
                has_add_verb = True
                break

        qty_val: Optional[float] = None
        unit_val: Optional[str] = None
        rem_text = work_text

        for num_phrase, num_num in sorted(MALAYALAM_NUMBER_WORDS.items(), key=lambda x: len(x[0]), reverse=True):
            if rem_text.startswith(num_phrase + " "):
                qty_val = num_num
                rem_text = rem_text[len(num_phrase):].strip()
                break

        tokens = rem_text.split()
        if tokens:
            if qty_val is None:
                parsed_q = parse_malayalam_number(tokens[0])
                if parsed_q is not None:
                    qty_val = parsed_q
                    tokens = tokens[1:]

            if tokens and tokens[0] in MALAYALAM_UNITS_MAP:
                unit_val = MALAYALAM_UNITS_MAP[tokens[0]]
                tokens = tokens[1:]

            item_str = " ".join(tokens).strip()
            clean_item = MALAYALAM_ITEM_MAP.get(item_str, item_str)

            if clean_item in MALAYALAM_ITEM_MAP.values() or item_str in MALAYALAM_ITEM_MAP or has_add_verb or qty_val is not None:
                if item_str or clean_item:
                    return ParsedIntent(
                        intent=IntentEnum.ADD_ITEM,
                        item=clean_item if clean_item else item_str,
                        quantity=qty_val if qty_val is not None else 1.0,
                        unit=unit_val,
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
        normalization -> intent detection -> entity extraction -> ParsedIntent
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

            m_between = re.search(rf'between\s+\$?({num_expr})\s+and\s+\$?({num_expr})(?:\s+dollars?)?', norm_search)
            if m_between:
                val1 = NLPService.parse_number(m_between.group(1))
                val2 = NLPService.parse_number(m_between.group(2))
                if val1 is not None and val2 is not None:
                    min_price = min(val1, val2)
                    max_price = max(val1, val2)
                    norm_search = re.sub(rf'between\s+\$?{num_expr}\s+and\s+\$?{num_expr}(?:\s+dollars?)?', '', norm_search).strip()
            else:
                m_max = re.search(rf'(?:under|below|less\s+than|up\s+to)\s+\$?({num_expr})(?:\s+dollars?)?', norm_search)
                if m_max:
                    val_max = NLPService.parse_number(m_max.group(1))
                    if val_max is not None:
                        max_price = val_max
                        norm_search = re.sub(rf'(?:under|below|less\s+than|up\s+to)\s+\$?{num_expr}(?:\s+dollars?)?', '', norm_search).strip()
                else:
                    m_min = re.search(rf'(?:above|over|more\s+than|at\s+least)\s+\$?({num_expr})(?:\s+dollars?)?', norm_search)
                    if m_min:
                        val_min = NLPService.parse_number(m_min.group(1))
                        if val_min is not None:
                            min_price = val_min
                            norm_search = re.sub(rf'(?:above|over|more\s+than|at\s+least)\s+\$?{num_expr}(?:\s+dollars?)?', '', norm_search).strip()

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
            r'^please\s+put\b', r'^can\s+you\s+add\b'
        ]
        is_add_cmd = any(re.search(pat, norm) for pat in add_triggers)
        
        if is_add_cmd:
            qty, unit, item_name = NLPService.extract_quantity_unit_item(norm)
            if item_name:
                return ParsedIntent(
                    intent=IntentEnum.ADD_ITEM,
                    item=item_name,
                    quantity=qty,
                    unit=unit,
                    confidence=1.0,
                    original_text=raw_text,
                    normalized_text=norm
                )

        # Direct pattern match for quantities without explicit verb (e.g. "2 bottles of milk", "5 oranges")
        num_start = re.match(r'^(?:\d+|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b)', norm)
        if num_start:
            qty, unit, item_name = NLPService.extract_quantity_unit_item(norm)
            if item_name:
                return ParsedIntent(
                    intent=IntentEnum.ADD_ITEM,
                    item=item_name,
                    quantity=qty,
                    unit=unit,
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
