from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TT(Enum):
    LOAD      = auto()
    COMPUTE   = auto()
    CHART     = auto()
    PIVOT     = auto()
    FILTER    = auto()
    SUM       = auto()
    AVG       = auto()
    COUNT     = auto()
    MIN       = auto()
    MAX       = auto()
    BAR       = auto()
    LINE      = auto()
    PIE       = auto()
    SCATTER   = auto()
    MONTHLY   = auto()
    DAILY     = auto()
    QUARTERLY = auto()
    YEARLY    = auto()
    BY        = auto()
    AND       = auto()
    WHERE     = auto()
    IS        = auto()
    NOT       = auto()
    COMPARING = auto()
    IDENT     = auto()
    STRING    = auto()
    NUMBER    = auto()
    FILENAME  = auto()
    EOF       = auto()


TokenType = TT

KEYWORDS = {
    "load":       TT.LOAD,
    "compute":    TT.COMPUTE,
    "chart":      TT.CHART,
    "pivot":      TT.PIVOT,
    "filter":     TT.FILTER,
    "sum":        TT.SUM,
    "avg":        TT.AVG,
    "count":      TT.COUNT,
    "min":        TT.MIN,
    "max":        TT.MAX,
    "bar":        TT.BAR,
    "line":       TT.LINE,
    "pie":        TT.PIE,
    "scatter":    TT.SCATTER,
    "monthly":    TT.MONTHLY,
    "daily":      TT.DAILY,
    "quarterly":  TT.QUARTERLY,
    "yearly":     TT.YEARLY,
    "by":         TT.BY,
    "and":        TT.AND,
    "where":      TT.WHERE,
    "is":         TT.IS,
    "not":        TT.NOT,
    "comparing":  TT.COMPARING,
}

FILE_EXTS = {".csv", ".xlsx", ".json", ".parquet"}


@dataclass
class Token:
    type: TT
    value: Any
    pos: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r})"


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def tokenize(self) -> list:
        toks = []
        while self.pos < len(self.text):
            self._skip_ws()
            if self.pos >= len(self.text):
                break
            tok = self._next_token()
            if tok:
                toks.append(tok)

        toks = self._merge_idents(toks)
        toks.append(Token(TT.EOF, None, self.pos))
        return toks

    def _skip_ws(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def _next_token(self) -> Token:
        start = self.pos
        ch = self.text[self.pos]

        if ch in ('"', "'"):
            return self._read_string(start)

        if ch.isdigit() or (ch == "-" and self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit()):
            return self._read_number(start)

        if ch.isalpha() or ch == "_":
            return self._read_word(start)

        self.pos += 1
        return None

    def _read_string(self, start) -> Token:
        quote = self.text[self.pos]
        self.pos += 1
        buf = []
        while self.pos < len(self.text) and self.text[self.pos] != quote:
            buf.append(self.text[self.pos])
            self.pos += 1
        self.pos += 1
        return Token(TT.STRING, "".join(buf), start)

    def _read_number(self, start) -> Token:
        buf = []
        if self.text[self.pos] == "-":
            buf.append("-")
            self.pos += 1
        while self.pos < len(self.text) and (self.text[self.pos].isdigit() or self.text[self.pos] == "."):
            buf.append(self.text[self.pos])
            self.pos += 1
        raw = "".join(buf)
        val = float(raw) if "." in raw else int(raw)
        return Token(TT.NUMBER, val, start)

    def _read_word(self, start) -> Token:
        buf = []
        while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] in ("_", "-", ".")):
            buf.append(self.text[self.pos])
            self.pos += 1
        word = "".join(buf)

        for ext in FILE_EXTS:
            if word.endswith(ext):
                return Token(TT.FILENAME, word, start)

        lower = word.lower()
        if lower in KEYWORDS:
            return Token(KEYWORDS[lower], lower, start)

        return Token(TT.IDENT, word, start)

    def _merge_idents(self, toks: list) -> list:
        # join adjacent alpha-only IDENTs: "profit margin" -> "profit_margin"
        # skip if either token has digits (e.g. Q2) so we don't mangle column refs
        out = []
        i = 0
        while i < len(toks):
            a = toks[i]
            if (a.type == TT.IDENT
                    and i + 1 < len(toks)
                    and toks[i + 1].type == TT.IDENT
                    and str(a.value).isalpha()
                    and str(toks[i + 1].value).isalpha()):
                merged = a.value + "_" + toks[i + 1].value
                out.append(Token(TT.IDENT, merged, a.pos))
                i += 2
            else:
                out.append(a)
                i += 1
        return out
