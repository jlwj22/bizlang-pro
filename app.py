import streamlit as st
from bizlang.synonyms import normalize
from bizlang.lexer import Lexer, TT
from bizlang.parser import Parser, ParseError
from bizlang.generators.pandas_gen import PandasGenerator
from bizlang.generators.sql_gen import SQLGenerator
from bizlang.generators.chart_gen import ChartGenerator
from bizlang.ast_nodes import LoadNode, ComputeNode, FilterNode


def get_tokens(text):
    return Lexer(normalize(text)).tokenize()


def get_ast(tokens):
    return Parser(tokens).parse()


def token_table(tokens):
    rows = []
    for t in tokens:
        if t.type == TT.EOF:
            break
        rows.append({"Token Type": t.type.name, "Value": str(t.value), "Position": t.pos})
    return rows


def ast_to_dict(node):
    from bizlang.ast_nodes import LoadNode, ComputeNode, ChartNode, PivotNode, FilterNode
    if isinstance(node, LoadNode):
        d = {"type": "LoadNode", "filename": node.filename}
        if node.follow_on:
            d["follow_on"] = ast_to_dict(node.follow_on)
        return d
    elif isinstance(node, ComputeNode):
        d = {
            "type": "ComputeNode",
            "agg_func": node.agg.func,
            "agg_column": node.agg.column,
            "group_by": node.group_by,
            "time_grain": node.time_grain,
        }
        if node.where:
            d["where"] = f"{node.where.column} {node.where.op} {node.where.value!r}"
        return d
    elif isinstance(node, ChartNode):
        return {
            "type": "ChartNode",
            "chart_type": node.chart_type,
            "agg_func": node.agg.func,
            "agg_column": node.agg.column,
            "compare_cols": node.compare_cols,
            "group_by": node.group_by,
        }
    elif isinstance(node, PivotNode):
        return {
            "type": "PivotNode",
            "index_cols": node.index_cols,
            "column_cols": node.column_cols,
            "agg": f"{node.agg.func}({node.agg.column})" if node.agg else "sum (default)",
        }
    elif isinstance(node, FilterNode):
        return {
            "type": "FilterNode",
            "source": node.source,
            "conditions": [f"{c.column} {c.op} {c.value!r}" for c in node.conditions],
        }
    return {"type": "unknown"}


EXAMPLES = [
    "load sales.csv and compute monthly revenue by region",
    "generate a bar chart comparing Q1 and Q2 expenses",
    "create a pivot table by product and region",
    "filter sales where region is North",
    "compute average profit by department where region is not South",
    "compute sum revenue by department",
    "chart line revenue by region",
    "filter df where region is not South",
]


st.set_page_config(page_title="BizLang IDE", page_icon="📊", layout="wide")

st.title("📊 BizLang")
st.caption("Type a plain-English analytics command and get runnable code back.")
st.divider()

with st.sidebar:
    st.header("Settings")
    mode = st.radio("Output mode", ["pandas", "sql", "chart"], index=0)
    st.divider()
    st.subheader("Examples")
    selected_example = st.selectbox("Load an example", ["(pick one)"] + EXAMPLES)
    st.divider()
    st.subheader("About")
    st.markdown(
        "BizLang is a DSL for business analytics. Type a command and it "
        "generates Pandas, SQL, or chart code you can run directly."
    )

default_input = selected_example if selected_example != "(pick one)" else ""

user_input = st.text_input(
    "Enter a BizLang command",
    value=default_input,
    placeholder="e.g. load sales.csv and compute monthly revenue by region",
)

run_btn = st.button("Generate", type="primary")

if run_btn or user_input:
    if not user_input.strip():
        st.warning("Type something first!")
        st.stop()

    normed = normalize(user_input)

    try:
        tokens = get_tokens(user_input)
        ast = get_ast(tokens)
    except ParseError as e:
        st.error(f"Parse error: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.stop()

    ctx = {"df_name": "df"}
    if isinstance(ast, LoadNode):
        ctx["last_file"] = ast.filename

    try:
        if mode == "pandas":
            code = PandasGenerator(ctx).generate(ast)
            lang = "python"
        elif mode == "sql":
            code = SQLGenerator().generate(ast)
            lang = "sql"
        else:
            code = ChartGenerator(ctx).generate(ast)
            lang = "python"
    except Exception as e:
        st.error(f"Code generation error: {e}")
        st.stop()

    col_code, col_tree = st.columns([3, 2])

    with col_code:
        st.subheader("Generated code")
        st.code(code, language=lang)

    with col_tree:
        st.subheader("Parse info")

        with st.expander("Normalized input", expanded=True):
            st.code(normed, language=None)

        with st.expander("Token stream", expanded=True):
            rows = token_table(tokens)
            if rows:
                st.dataframe(rows, use_container_width=True, hide_index=True)

        with st.expander("AST", expanded=True):
            st.json(ast_to_dict(ast))

    if mode == "pandas" and isinstance(ast, (LoadNode, ComputeNode, FilterNode)):
        st.divider()
        st.subheader("Live preview")
        st.caption("Runs the generated code against samples/sales.csv")

        try:
            import pandas as pd
            import io
            import contextlib

            df = pd.read_csv("samples/sales.csv")
            df["date"] = pd.to_datetime(df["date"])

            exec_globals = {"pd": pd, "df": df}
            captured = io.StringIO()

            with contextlib.redirect_stdout(captured):
                exec(code, exec_globals)  # noqa: S102

            output = captured.getvalue()
            if output.strip():
                try:
                    result_df = exec_globals.get("result") or exec_globals.get("filtered") or exec_globals.get("pivot")
                    if result_df is not None and hasattr(result_df, "head"):
                        st.dataframe(result_df, use_container_width=True)
                    else:
                        st.text(output)
                except Exception:
                    st.text(output)

        except Exception as e:
            st.info(f"Live preview skipped: {e}")
