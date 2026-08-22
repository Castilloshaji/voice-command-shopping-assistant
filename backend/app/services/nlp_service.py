import re
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

class NLPService:
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalizes natural language input:
        - Strip leading/trailing whitespace
        - Convert to lower-case
        - Collapse multiple spaces
        - Remove trailing punctuation (!, ?, .) while preserving $ and decimals
        """
        if not text:
            return ""
        s = text.strip().lower()
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
