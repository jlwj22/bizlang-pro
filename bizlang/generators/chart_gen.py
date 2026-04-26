from ..ast_nodes import ChartNode


class ChartGenerator:
    def __init__(self, ctx: dict):
        self.ctx = ctx

    def generate(self, node) -> str:
        if not isinstance(node, ChartNode):
            return "# chart mode only supports chart commands"
        lines = []
        self._chart(node, lines)
        return "\n".join(lines)

    def _chart(self, node: ChartNode, out: list):
        df = self.ctx.get("df_name", "df")
        col = node.agg.column
        ct = node.chart_type

        out.append("import matplotlib.pyplot as plt")
        out.append("")

        if node.compare_cols:
            # side-by-side comparison of fixed columns
            cats = node.compare_cols
            vals = [f'{df}["{c}"].sum()' for c in cats]
            cats_str = str(cats)
            vals_str = f"[{', '.join(vals)}]"
            title = f"{' vs '.join(cats)} {col}"

            out.append(f"categories = {cats_str}")
            out.append(f"values = {vals_str}")
            out.append("")
            out.append("fig, ax = plt.subplots()")

            if ct == "bar":
                out.append("ax.bar(categories, values)")
            elif ct == "line":
                out.append("ax.plot(categories, values, marker='o')")
            elif ct == "pie":
                out.append("ax.pie(values, labels=categories, autopct='%1.1f%%')")
            elif ct == "scatter":
                out.append("ax.scatter(range(len(categories)), values)")

            out.append(f'ax.set_title("{title}")')
            if ct != "pie":
                out.append(f'ax.set_ylabel("{col}")')

        elif node.group_by:
            # grouped chart — one series per group value
            grp = node.group_by[0]
            title = f"{col} by {grp}"

            out.append("fig, ax = plt.subplots()")
            out.append("")

            if ct in ("line", "scatter"):
                out.append(f'for grp_val, sub in {df}.groupby("{grp}"):')
                out.append(f'    vals = sub["{col}"]')
                if ct == "line":
                    out.append(f"    ax.plot(range(len(vals)), vals.values, label=str(grp_val))")
                else:
                    out.append(f"    ax.scatter(range(len(vals)), vals.values, label=str(grp_val))")
                out.append("ax.legend()")
            else:
                out.append(f'grouped = {df}.groupby("{grp}")["{col}"].sum()')
                if ct == "bar":
                    out.append("ax.bar(grouped.index.astype(str), grouped.values)")
                elif ct == "pie":
                    out.append("ax.pie(grouped.values, labels=grouped.index.astype(str), autopct='%1.1f%%')")

            out.append(f'ax.set_title("{title}")')
            if ct != "pie":
                out.append(f'ax.set_xlabel("{grp}")')
                out.append(f'ax.set_ylabel("{col}")')
        else:
            # fallback — just plot the column
            out.append("fig, ax = plt.subplots()")
            out.append(f'ax.bar({df}.index, {df}["{col}"])')
            out.append(f'ax.set_title("{col}")')

        out.append("plt.tight_layout()")
        out.append("plt.show()")
