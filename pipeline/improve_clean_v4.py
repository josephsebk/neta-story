import json, re

data = json.load(open("holdings_v2.json"))

QTY_PATTERNS=[
    r",?\s*([\d,]*\d[\d,]*)\s*shares?\b",            # "..., 900 Shares"
    r"\beq\.?\s*shares?\s*[-:]?\s*([\d,]*\d[\d,]*)", # "Eq. Share-28"
    r"\bunits?\s*[-:]?\s*([\d,]*\d[\d]*)",          # "Unit-296" / "Units-1515"
    r"\bshares?\s*[-:]?\s*([\d,]*\d[\d]*)",         # "Share-48"
    r"\bq\.?\s*([\d,]*\d[\d]*)\b",                  # "Q. 200"
]

def extract_qty_clean(name):
    cleaned = name
    for pat in QTY_PATTERNS:
        m = re.search(pat, cleaned, re.I)
        if m:
            cleaned = cleaned[:m.start()] + cleaned[m.end():]
            break
    return cleaned

def clean_holding_name(raw):
    n = raw
    # 1. Strip quantity patterns
    n = extract_qty_clean(n)
    
    # 2. Strip leading metadata/date prefixes
    n = re.sub(r"^(?:date\s+)?(?:as\s+)?(?:on|of|at)?\s*\d{2}[-./]\d{2}[-./]\d{4}\b,?\s*", "", n, flags=re.I)
    n = re.sub(r"^(?:investment\s+in\s+)?mutual\s*funds?\s*(?:as\s+on\s+[^:]+|namely)?\s*[:\-]\s*", "", n, flags=re.I)
    n = re.sub(r"^equity\s+shares?\s+holdings?\s*[:\-]\s*", "", n, flags=re.I)
    n = re.sub(r"^(?:investment\s+in\s+|mutual\s+funds?\s+of\s+|mutual\s+funds?\s+)", "", n, flags=re.I)
    n = re.sub(r"^(?:of|in|at|under|with)\s+", "", n, flags=re.I)

    # 3. Strip safe folio/demat/ac details
    n = re.sub(r"\bfolio\s*(?:no\.?|number)?\s*[:\-]?\s*[\dxX/]+\b", "", n, flags=re.I)
    n = re.sub(r"\bdemat\s*(?:a/?c|account)?\s*(?:no\.?|number)?\s*[:\-]?\s*[\dxX/a-zA-Z0-9\-]+\b", "", n, flags=re.I)
    n = re.sub(r"\ba/?c\s*(?:no\.?|number)?\s*[:\-]?\s*[\dxX/0-9\-]+\b", "", n, flags=re.I)
    n = re.sub(r"\bin[3e]\d{6,}\b", "", n, flags=re.I)
    n = re.sub(r"\b\d{8,}\b", "", n) # only very long numbers

    # 4. Strip trailing date/value noise safely
    # Trailing date: as on 31.03.2024
    n = re.sub(r"\b(?:as\s+on|as\s+of|date|dated)\s*[-:]?\s*(?:\d{2}[-./]\d{2}[-./]\d{4}|\d{4}|[a-zA-Z]+\s+\d{4})\b.*$", "", n, flags=re.I)
    # Trailing noise keywords
    TRAIL = re.compile(r"\b(?:market\s+value|book\s+value|per\s+share|cost\s+price|face\s+value|value\s+of|joint\s+with|invested|approx|till\s+date|no\s+of\s+shares|number\s+of\s+shares|purchase\s+value|qty|rate)\b.*$", re.I)
    n = TRAIL.sub("", n)
    
    # 5. Clean up prepositions left behind at the end
    n = re.sub(r"\b(?:of|in|at|under|with|cost|price|share|shares|unit|units|value)\s*$", "", n, flags=re.I)
    n = re.sub(r"@.*$", "", n)
    n = re.sub(r"\(\s*\)", "", n)
    n = re.sub(r"[,;:@\-]+\s*$", "", n)
    n = re.sub(r"^\s*[,;:@\-]+", "", n)
    
    return re.sub(r"\s+", " ", n).strip(" ,.;:-@()")

test_cases = [
    "Date as On 15.03.2024, Alkyl Amines Chemical Ltd , Share 373",
    "Demat No 2651xxxxx The Tata Power Company Ltd INE 245 A01021 Order No 130000000020xxxxx Trade Date-06/02/2019 Quantity 10",
    "Equity Share Holding: [As On. 31.03.20231 1)Hdfc Bank Ltd Units 10,630 Cost Price 1,51,87,837",
    "HDFC Bank 1500 Shares",
    "State Bank of India Units 1000",
    "SBI Magnum TX Gain, Units 1195",
    "SBI, New Delhi 69 A/c384903080",
    "HDFC Retirement Savings Fund 40027.480",
    "HDFC Scheme Type- KIdcap opportunities Fund-Regular Plan Growth Folio-9481178",
]

print("Test results:")
for tc in test_cases:
    print(f"Raw: {tc}")
    print(f"Cleaned: {clean_holding_name(tc)}")
    print("-" * 50)
