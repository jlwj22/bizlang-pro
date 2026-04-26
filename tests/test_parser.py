import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from bizlang.synonyms import normalize
from bizlang.lexer import Lexer
from bizlang.parser import Parser, ParseError
from bizlang.ast_nodes import LoadNode, ComputeNode, ChartNode, PivotNode, FilterNode


def parse(text):
    normed = normalize(text)
    toks = Lexer(normed).tokenize()
    return Parser(toks).parse()


def test_load_basic():
    node = parse("load sales.csv")
    assert isinstance(node, LoadNode)
    assert node.filename == "sales.csv"
    assert node.follow_on is None


def test_load_chained_compute():
    node = parse("load sales.csv and compute monthly revenue by region")
    assert isinstance(node, LoadNode)
    assert isinstance(node.follow_on, ComputeNode)
    assert node.follow_on.time_grain == "monthly"
    assert "region" in node.follow_on.group_by


def test_compute_agg_func():
    node = parse("compute average profit by department")
    assert isinstance(node, ComputeNode)
    assert node.agg.func == "avg"
    assert node.agg.column == "profit"


def test_compute_with_where():
    node = parse("compute sum revenue by region where region is North")
    assert node.where is not None
    assert node.where.column == "region"
    assert node.where.value == "North"
    assert node.where.op == "=="


def test_chart_with_comparing():
    node = parse("generate a bar chart comparing Q1 and Q2 marketing expenses")
    # after normalization "generate" → "chart" and "expenses" → "sum"
    assert isinstance(node, ChartNode)
    assert node.chart_type == "bar"
    assert len(node.compare_cols) >= 1


def test_pivot_two_dimensions():
    node = parse("create a pivot table by product and region")
    assert isinstance(node, PivotNode)
    assert "product" in node.index_cols or "product" in node.column_cols


def test_filter_not_negation():
    node = parse("filter df where region is not South")
    assert isinstance(node, FilterNode)
    cond = node.conditions[0]
    assert cond.negate is True
    assert cond.value == "South"


def test_parse_error_on_garbage():
    with pytest.raises(ParseError):
        parse("xyzzy foobar blarg")


def test_filter_quoted_value():
    node = parse('filter sales where region is "North"')
    assert isinstance(node, FilterNode)
    assert node.conditions[0].value == "North"
