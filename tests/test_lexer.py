import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bizlang.lexer import Lexer, TT
from bizlang.synonyms import normalize


def lex(text):
    return Lexer(normalize(text)).tokenize()


def test_load_token():
    toks = lex("load sales.csv")
    assert toks[0].type == TT.LOAD


def test_filename_token():
    toks = lex("load sales.csv")
    assert toks[1].type == TT.FILENAME
    assert toks[1].value == "sales.csv"


def test_quoted_string_strips_quotes():
    toks = lex('filter df where region is "North"')
    str_toks = [t for t in toks if t.type == TT.STRING]
    assert len(str_toks) == 1
    assert str_toks[0].value == "North"


def test_number_token():
    toks = lex("filter df where revenue is 500")
    num_toks = [t for t in toks if t.type == TT.NUMBER]
    assert len(num_toks) == 1
    assert num_toks[0].value == 500


def test_unknown_word_is_ident():
    toks = lex("compute revenue by department")
    idents = [t for t in toks if t.type == TT.IDENT]
    assert any(t.value == "department" for t in idents)


def test_eof_always_appended():
    toks = lex("pivot by product")
    assert toks[-1].type == TT.EOF


def test_consecutive_idents_merge():
    # "profit margin" should merge into "profit_margin"
    toks = lex("pivot by profit margin")
    idents = [t for t in toks if t.type == TT.IDENT]
    assert any("profit_margin" in t.value for t in idents)
