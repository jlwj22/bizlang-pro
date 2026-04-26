# BizLang

A domain-specific language that turns plain English business commands into runnable Pandas scripts, SQL queries, and Matplotlib charts.

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

## Example commands

```
bizlang> load samples/sales.csv and compute monthly revenue by region
bizlang> generate a bar chart comparing Q1 and Q2 expenses
bizlang> create a pivot table by product and region
bizlang> mode sql
bizlang> show total earnings by department
bizlang> filter sales where region is North
```

## Output modes

Switch with `mode [pandas|sql|chart]`. Default is `pandas`.

## Running tests

```bash
pytest tests/ -v
```

## Project structure

```
bizlang/
  synonyms.py      synonym normalization
  lexer.py         tokenizer
  ast_nodes.py     AST node classes
  parser.py        recursive descent parser
  generators/
    pandas_gen.py  Pandas code generator
    sql_gen.py     SQL query generator
    chart_gen.py   Matplotlib chart generator
main.py            interactive REPL
samples/           sample CSV data
tests/             pytest test suite
```
