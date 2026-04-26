import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bizlang.synonyms import normalize
from bizlang.lexer import Lexer
from bizlang.parser import Parser
from bizlang.generators.pandas_gen import PandasGenerator
from bizlang.generators.sql_gen import SQLGenerator
from bizlang.generators.chart_gen import ChartGenerator


def _ast(text):
    normed = normalize(text)
    toks = Lexer(normed).tokenize()
    return Parser(toks).parse()


def pandas_code(text, ctx=None):
    return PandasGenerator(ctx or {}).generate(_ast(text))


def sql_code(text):
    return SQLGenerator().generate(_ast(text))


def chart_code(text, ctx=None):
    return ChartGenerator(ctx or {}).generate(_ast(text))


# ---- pandas tests ----

def test_pandas_groupby_present():
    code = pandas_code("compute sum revenue by region")
    assert "groupby" in code
    assert '"revenue"' in code
    assert '"region"' in code


def test_pandas_read_csv():
    code = pandas_code("load sales.csv")
    assert "pd.read_csv" in code
    assert '"sales.csv"' in code


def test_pandas_filter_boolean_index():
    code = pandas_code("filter df where region is North")
    assert '["region"]' in code
    assert "==" in code
    assert '"North"' in code


def test_pandas_pivot_table():
    code = pandas_code("create a pivot table by product and region")
    assert "pivot_table" in code


def test_pandas_time_grain():
    code = pandas_code("compute monthly revenue by region")
    assert "to_period" in code or "dt.to_period" in code


# ---- sql tests ----

def test_sql_select_and_group_by():
    code = sql_code("compute sum revenue by department")
    assert "SELECT" in code.upper()
    assert "GROUP BY" in code.upper()
    assert "SUM(revenue)" in code


def test_sql_where_clause():
    code = sql_code("filter sales where region is North")
    assert "WHERE" in code.upper()
    assert "region" in code
    assert "North" in code


def test_sql_not_supported_for_chart():
    code = sql_code("generate a bar chart comparing Q1 and Q2 expenses")
    assert "not supported" in code.lower() or "SQL" in code


# ---- chart tests ----

def test_chart_has_plt_show():
    code = chart_code("generate a bar chart comparing Q1 and Q2 expenses")
    assert "plt.show()" in code


def test_chart_bar_uses_ax_bar():
    code = chart_code("generate a bar chart comparing Q1 and Q2 expenses")
    assert "ax.bar" in code


def test_chart_line_uses_ax_plot():
    code = chart_code("chart line revenue by region")
    assert "ax.plot" in code or "plot" in code
