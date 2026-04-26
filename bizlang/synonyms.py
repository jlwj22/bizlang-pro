import re

# Multi-word phrases must come before their component words so the
# longest-match pass replaces them first.
SYNONYMS = {
    # --- load ---
    "bring in":              "load",
    "import":                "load",
    "ingest":                "load",
    "open":                  "load",
    "read":                  "load",

    # --- compute ---
    "calculate":             "compute",
    "summarize":             "compute",
    "aggregate":             "compute",
    "find":                  "compute",
    "get":                   "compute",
    "show":                  "compute",

    # --- agg functions ---
    "number of":             "count",
    "how many":              "count",
    "average":               "avg",
    "mean":                  "avg",
    "median":                "avg",   # close enough for our purposes
    "total":                 "sum",
    "highest":               "max",
    "maximum":               "max",
    "lowest":                "min",
    "minimum":               "min",

    # --- chart ---
    "create a chart":        "chart",
    "generate":              "chart",
    "visualize":             "chart",
    "display":               "chart",
    "plot":                  "chart",
    "draw":                  "chart",

    # --- pivot ---
    "create a pivot table":  "pivot",
    "build a pivot table":   "pivot",
    "make a pivot table":    "pivot",
    "create pivot table":    "pivot",
    "create pivot":          "pivot",

    # --- filter ---
    "keep only":             "filter",
    "restrict to":           "filter",
    "only where":            "filter",
    "select where":          "filter",

    # --- structural ---
    "broken down by":        "by",
    "grouped by":            "by",
    "split by":              "by",
    "across":                "by",
    "per":                   "by",
    "equal to":              "is",
    "equals":                "is",
    "in which":              "where",
    "when":                  "where",
    "versus":                "comparing",
    "against":               "comparing",
    "isn't":                 "not is",
    "vs.":                   "comparing",
    "vs":                    "comparing",
    "excluding":             "not",
    "except":                "not",

    # --- time ---
    "each month":            "monthly",
    "by month":              "monthly",
    "each day":              "daily",
    "by day":                "daily",
    "each year":             "yearly",
    "by year":               "yearly",
    "annually":              "yearly",
    "annual":                "yearly",
    "by quarter":            "quarterly",
    "each quarter":          "quarterly",
    "quarter":               "quarterly",
}

# canonical words that may get duplicated after synonym expansion
_DEDUP = ["sum", "avg", "count", "min", "max", "compute", "chart", "load"]


def normalize(text: str) -> str:
    # Don't lowercase the whole string — we want to preserve case for column
    # values like "North" or "Marketing". Only do case-insensitive matching.
    text = text.strip()
    for phrase in sorted(SYNONYMS, key=len, reverse=True):
        pattern = r"\b" + re.escape(phrase) + r"\b"
        text = re.sub(pattern, SYNONYMS[phrase], text, flags=re.IGNORECASE)
    # collapse accidental duplicates: "sum sum" → "sum"
    for word in _DEDUP:
        text = re.sub(rf"\b{word}(\s+{word})+\b", word, text, flags=re.IGNORECASE)
    return text
