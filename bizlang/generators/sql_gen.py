from ..ast_nodes import ComputeNode, FilterNode

_AGG_FN = {
    "sum":   "SUM",
    "avg":   "AVG",
    "count": "COUNT",
    "min":   "MIN",
    "max":   "MAX",
}

_DATE_TRUNC = {
    "monthly":   "month",
    "daily":     "day",
    "quarterly": "quarter",
    "yearly":    "year",
}


class SQLGenerator:
    def generate(self, node) -> str:
        if isinstance(node, ComputeNode):
            return self._compute(node)
        if isinstance(node, FilterNode):
            return self._filter(node)
        # LoadNode / ChartNode / PivotNode don't map cleanly to SQL
        return "-- SQL generation not supported for this command type. Use pandas mode instead."

    def _compute(self, node: ComputeNode) -> str:
        fn = _AGG_FN.get(node.agg.func, "SUM")
        col = node.agg.column
        alias = f"{node.agg.func}_{col}"

        select_parts = []
        group_parts = []

        if node.time_grain and node.time_grain in _DATE_TRUNC:
            grain = _DATE_TRUNC[node.time_grain]
            trunc = f"DATE_TRUNC('{grain}', date)"
            select_parts.append(f"    {trunc} AS {grain}")
            group_parts.append(trunc)

        for g in node.group_by:
            select_parts.append(f"    {g}")
            group_parts.append(g)

        select_parts.append(f"    {fn}({col}) AS {alias}")

        lines = ["SELECT"]
        lines.append(",\n".join(select_parts))
        lines.append("FROM data")

        if node.where:
            c = node.where
            val = f"'{c.value}'" if isinstance(c.value, str) else str(c.value)
            lines.append(f"WHERE {c.column} {c.op} {val}")

        if group_parts:
            lines.append(f"GROUP BY {', '.join(group_parts)}")
            lines.append(f"ORDER BY {alias} DESC")

        return "\n".join(lines) + ";"

    def _filter(self, node: FilterNode) -> str:
        source = node.source if node.source != "df" else "data"
        clauses = []
        for c in node.conditions:
            val = f"'{c.value}'" if isinstance(c.value, str) else str(c.value)
            op = "!=" if c.negate else "="
            clauses.append(f"{c.column} {op} {val}")
        where = " AND ".join(clauses)
        return f"SELECT *\nFROM {source}\nWHERE {where};"
