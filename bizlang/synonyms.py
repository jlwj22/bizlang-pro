import re

SYNONYMS = {
    "bring in":              "load",
    "import":                "load",
    "ingest":                "load",
    "open":                  "load",
    "read":                  "load",

    "calculate":             "compute",
    "summarize":             "compute",
    "aggregate":             "compute",
    "find":                  "compute",
    "get":                   "compute",
    "show":                  "compute",

    "number of":             "count",
    "how many":              "count",
    "average":               "avg",
    "mean":                  "avg",
    "median":                "avg",
    "total":                 "sum",
    "highest":               "max",
    "maximum":               "max",
    "lowest":                "min",
    "minimum":               "min",

    "create a chart":        "chart",
    "generate":              "chart",
    "visualize":             "chart",
    "display":               "chart",
    "plot":                  "chart",
    "draw":                  "chart",

    "create a pivot table":  "pivot",
    "build a pivot table":   "pivot",
    "make a pivot table":    "pivot",
    "create pivot table":    "pivot",
    "create pivot":          "pivot",

    "keep only":             "filter",
    "restrict to":           "filter",
    "only where":            "filter",
    "select where":          "filter",

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

_DEDUP = ["sum", "avg", "count", "min", "max", "compute", "chart", "load"]


def normalize(text: str) -> str:
    text = text.strip()
    for phrase in sorted(SYNONYMS, key=len, reverse=True):
        pattern = r"\b" + re.escape(phrase) + r"\b"
        text = re.sub(pattern, SYNONYMS[phrase], text, flags=re.IGNORECASE)
    for word in _DEDUP:
        text = re.sub(rf"\b{word}(\s+{word})+\b", word, text, flags=re.IGNORECASE)
    return text
