from ..ast_nodes import LoadNode, ComputeNode, ChartNode, PivotNode, FilterNode, AggExpr

_PERIOD = {
    "monthly":   ("M",       "month"),
    "daily":     ("D",       "date"),
    "quarterly": ("Q",       "quarter"),
    "yearly":    ("Y",       "year"),
}

_AGG_METHOD = {
    "sum":   "sum",
    "avg":   "mean",
    "count": "count",
    "min":   "min",
    "max":   "max",
}


class PandasGenerator:
    def __init__(self, ctx: dict):
        self.ctx = ctx   # carries last loaded filename / df name across REPL turns

    def generate(self, node) -> str:
        lines = []
        self._visit(node, lines)
        return "\n".join(lines)

    def _visit(self, node, out: list):
        if isinstance(node, LoadNode):
            self._load(node, out)
        elif isinstance(node, ComputeNode):
            self._compute(node, out)
        elif isinstance(node, FilterNode):
            self._filter(node, out)
        elif isinstance(node, PivotNode):
            self._pivot(node, out)
        elif isinstance(node, ChartNode):
            out.append("# use 'chart' mode for chart commands")
        else:
            out.append("# unsupported node type")

    def _load(self, node: LoadNode, out: list):
        out.append("import pandas as pd")
        out.append("")
        out.append(f'df = pd.read_csv("{node.filename}")')
        self.ctx["df_name"] = "df"
        self.ctx["last_file"] = node.filename
        if node.follow_on:
            out.append("")
            self._visit(node.follow_on, out)

    def _compute(self, node: ComputeNode, out: list):
        df = self.ctx.get("df_name", "df")
        method = _AGG_METHOD.get(node.agg.func, "sum")
        col = node.agg.column

        group_cols = list(node.group_by)

        # apply pre-filter if present
        if node.where:
            cond = node.where
            val = f'"{cond.value}"' if isinstance(cond.value, str) else cond.value
            out.append(f'{df} = {df}[{df}["{cond.column}"] {cond.op} {val}]')

        # time grain: add a derived column then group by it
        if node.time_grain and node.time_grain in _PERIOD:
            freq, grain_col = _PERIOD[node.time_grain]
            out.append(f'{df}["date"] = pd.to_datetime({df}["date"])')
            if freq in ("M", "Q", "Y"):
                out.append(f'{df}["{grain_col}"] = {df}["date"].dt.to_period("{freq}")')
            else:
                out.append(f'{df}["{grain_col}"] = {df}["date"].dt.date')
            group_cols = [grain_col] + group_cols

        group_str = str(group_cols) if len(group_cols) > 1 else f'"{group_cols[0]}"'
        alias = f"{method}_{col}"
        out.append("")
        out.append(f'result = {df}.groupby({group_str})["{col}"].{method}().reset_index()')
        out.append(f'result.columns = {group_cols + [alias]}')
        out.append("print(result)")

    def _filter(self, node: FilterNode, out: list):
        df = self.ctx.get("df_name", "df")
        parts = []
        for c in node.conditions:
            val = f'"{c.value}"' if isinstance(c.value, str) else c.value
            parts.append(f'{df}["{c.column}"] {c.op} {val}')
        mask = " & ".join(f"({p})" for p in parts)
        out.append(f"filtered = {df}[{mask}]")
        out.append("print(filtered)")

    def _pivot(self, node: PivotNode, out: list):
        df = self.ctx.get("df_name", "df")
        agg = node.agg or AggExpr(func="sum", column="value")
        method = _AGG_METHOD.get(agg.func, "sum")

        idx = node.index_cols[0] if len(node.index_cols) == 1 else node.index_cols
        idx_str = f'"{idx}"' if isinstance(idx, str) else str(idx)
        cols_str = f'"{node.column_cols[0]}"' if len(node.column_cols) == 1 else str(node.column_cols)

        if node.column_cols:
            out.append(f"pivot = {df}.pivot_table(")
            out.append(f'    index={idx_str},')
            out.append(f'    columns={cols_str},')
            out.append(f'    values="{agg.column}",')
            out.append(f'    aggfunc="{method}"')
            out.append(")")
        else:
            out.append(f"pivot = {df}.pivot_table(")
            out.append(f'    index={idx_str},')
            out.append(f'    values="{agg.column}",')
            out.append(f'    aggfunc="{method}"')
            out.append(")")
        out.append("print(pivot)")
