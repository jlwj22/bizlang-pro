from .lexer import Token, TT
from .ast_nodes import (
    AggExpr, Condition,
    LoadNode, ComputeNode, ChartNode, PivotNode, FilterNode,
)

AGG_TYPES = {TT.SUM, TT.AVG, TT.COUNT, TT.MIN, TT.MAX}
CHART_TYPES = {TT.BAR, TT.LINE, TT.PIE, TT.SCATTER}
TIME_GRAINS = {TT.MONTHLY, TT.DAILY, TT.QUARTERLY, TT.YEARLY}


def _levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        return _levenshtein(b, a)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        cur = [i + 1]
        for j, cb in enumerate(b):
            cur.append(min(prev[j + 1] + 1, cur[j] + 1, prev[j] + (ca != cb)))
        prev = cur
    return prev[-1]


def _suggest(word: str) -> str:
    candidates = [
        "load", "compute", "chart", "pivot", "filter",
        "sum", "avg", "count", "min", "max",
        "by", "and", "where", "is", "not", "comparing",
    ]
    best = min(candidates, key=lambda c: _levenshtein(word, c))
    if _levenshtein(word, best) <= 3:
        return best
    return ""


class ParseError(Exception):
    def __init__(self, msg: str, tok: Token, suggestion: str = ""):
        loc = f" (at pos {tok.pos}: {tok.value!r})"
        hint = f" -- did you mean '{suggestion}'?" if suggestion else ""
        super().__init__(msg + loc + hint)


class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0
        self.cur = tokens[0]

    def _advance(self):
        if self.pos + 1 < len(self.tokens):
            self.pos += 1
        self.cur = self.tokens[self.pos]

    def _peek(self, offset=1) -> Token:
        idx = min(self.pos + offset, len(self.tokens) - 1)
        return self.tokens[idx]

    def _match(self, *types) -> bool:
        if self.cur.type in types:
            self._advance()
            return True
        return False

    def _expect(self, tt: TT, context: str = "") -> Token:
        if self.cur.type != tt:
            msg = f"expected {tt.name}"
            if context:
                msg += f" in {context}"
            raise ParseError(msg, self.cur, _suggest(str(self.cur.value or "")))
        tok = self.cur
        self._advance()
        return tok

    def parse(self):
        node = self._parse_statement()
        if self.cur.type != TT.EOF:
            raise ParseError("unexpected token after statement", self.cur)
        return node

    def _parse_statement(self):
        t = self.cur.type
        if t == TT.LOAD:    return self._parse_load()
        if t == TT.COMPUTE: return self._parse_compute()
        if t == TT.CHART:   return self._parse_chart()
        if t == TT.PIVOT:   return self._parse_pivot()
        if t == TT.FILTER:  return self._parse_filter()
        raise ParseError("unrecognized command", self.cur, _suggest(str(self.cur.value or "")))

    def _parse_load(self) -> LoadNode:
        self._advance()
        fn_tok = self._expect(TT.FILENAME, "load command")
        follow = None
        if self.cur.type == TT.AND and self._peek().type == TT.COMPUTE:
            self._advance()
            follow = self._parse_compute()
        return LoadNode(filename=fn_tok.value, follow_on=follow)

    def _parse_compute(self) -> ComputeNode:
        if self.cur.type == TT.COMPUTE:
            self._advance()
        time_grain = None
        if self.cur.type in TIME_GRAINS:
            time_grain = self.cur.value
            self._advance()
        agg = self._parse_agg_expr()
        if self.cur.type in TIME_GRAINS and time_grain is None:
            time_grain = self.cur.value
            self._advance()
        self._expect(TT.BY, "compute command")
        group_by = self._parse_column_list()
        if self.cur.type in TIME_GRAINS and time_grain is None:
            time_grain = self.cur.value
            self._advance()
        where = None
        if self.cur.type == TT.WHERE:
            self._advance()
            where = self._parse_condition()
        return ComputeNode(agg=agg, group_by=group_by, time_grain=time_grain, where=where)

    def _parse_chart(self) -> ChartNode:
        self._advance()

        if self.cur.type == TT.IDENT and self.cur.value.lower() in ("a", "an"):
            self._advance()

        chart_type = "bar"
        if self.cur.type in CHART_TYPES:
            chart_type = self.cur.value
            self._advance()

        if self.cur.type == TT.CHART:
            self._advance()

        agg = AggExpr(func="sum", column="value")
        if self.cur.type not in (TT.COMPARING, TT.BY, TT.EOF):
            agg = self._parse_agg_expr()

        compare_cols = []
        group_by = []

        if self.cur.type == TT.COMPARING:
            self._advance()
            compare_cols = self._parse_column_list()

        if compare_cols and self.cur.type == TT.IDENT:
            agg = AggExpr(func="sum", column=self.cur.value)
            self._advance()

        if self.cur.type == TT.BY:
            self._advance()
            group_by = self._parse_column_list()

        return ChartNode(chart_type=chart_type, agg=agg, compare_cols=compare_cols, group_by=group_by)

    def _parse_pivot(self) -> PivotNode:
        self._advance()
        self._expect(TT.BY, "pivot command")
        index_cols = self._parse_column_list()
        col_cols = []
        if self.cur.type == TT.AND:
            nxt = self._peek()
            if nxt.type in (TT.IDENT, TT.BY):
                self._advance()
                if self.cur.type == TT.BY:
                    self._advance()
                col_cols = self._parse_column_list()
        agg = None
        if self.cur.type == TT.COMPUTE:
            self._advance()
            agg = self._parse_agg_expr()
        return PivotNode(index_cols=index_cols, column_cols=col_cols, agg=agg)

    def _parse_filter(self) -> FilterNode:
        self._advance()
        source = "df"
        if self.cur.type == TT.IDENT and self._peek().type == TT.WHERE:
            source = self.cur.value
            self._advance()
        self._expect(TT.WHERE, "filter command")
        conditions = [self._parse_condition()]
        while self.cur.type == TT.AND:
            self._advance()
            conditions.append(self._parse_condition())
        return FilterNode(source=source, conditions=conditions)

    def _parse_agg_expr(self) -> AggExpr:
        func = "sum"
        if self.cur.type in AGG_TYPES:
            func = self.cur.value
            self._advance()
            if self.cur.type in AGG_TYPES:
                self._advance()
        col_tok = self._expect(TT.IDENT, "aggregation expression")
        return AggExpr(func=func, column=col_tok.value)

    def _parse_column_list(self) -> list:
        cols = []
        col_tok = self._expect(TT.IDENT, "column list")
        cols.append(col_tok.value)
        while self.cur.type == TT.AND and self._peek().type == TT.IDENT:
            self._advance()
            cols.append(self.cur.value)
            self._advance()
        return cols

    def _parse_condition(self) -> Condition:
        col_tok = self._expect(TT.IDENT, "condition")
        self._expect(TT.IS, "condition")
        negate = False
        if self.cur.type == TT.NOT:
            negate = True
            self._advance()
        val_tok = self.cur
        if val_tok.type not in (TT.STRING, TT.NUMBER, TT.IDENT):
            raise ParseError("expected a value after 'is'", val_tok)
        self._advance()
        op = "!=" if negate else "=="
        return Condition(column=col_tok.value, op=op, value=val_tok.value, negate=negate)
