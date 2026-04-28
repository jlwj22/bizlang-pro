from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    HRFlowable, PageBreak, Table, TableStyle
)

OUT = "BizLang_Submission.pdf"

doc = SimpleDocTemplate(
    OUT,
    pagesize=letter,
    leftMargin=1*inch,
    rightMargin=1*inch,
    topMargin=1*inch,
    bottomMargin=1*inch,
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "mytitle",
    parent=styles["Title"],
    fontSize=22,
    spaceAfter=6,
)
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=14, spaceAfter=4, spaceBefore=14)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, spaceAfter=4, spaceBefore=10)
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=10, leading=15)
code_style = ParagraphStyle(
    "code",
    parent=styles["Code"],
    fontSize=8,
    leading=11,
    backColor=colors.HexColor("#f4f4f4"),
    leftIndent=12,
    rightIndent=12,
    spaceBefore=4,
    spaceAfter=4,
)
small = ParagraphStyle("small", parent=body, fontSize=9, textColor=colors.grey)

def h(text, style=h1):
    return Paragraph(text, style)

def p(text):
    return Paragraph(text, body)

def code(text):
    return Preformatted(text, code_style)

def sp(n=8):
    return Spacer(1, n)

def rule():
    return HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=6, spaceBefore=6)


story = []

# title block
story.append(sp(20))
story.append(Paragraph("BizLang", title_style))
story.append(Paragraph("Business Analytics Domain-Specific Language", styles["Heading2"]))
story.append(sp(4))
story.append(rule())

info_data = [
    ["Team Members", "Julius Jones, Derrick Tilford"],
    ["Course", "Programming Languages"],
    ["Project", "Option 3 — BizLang DSL"],
    ["Language", "Python 3"],
]
info_table = Table(info_data, colWidths=[1.5*inch, 4.5*inch])
info_table.setStyle(TableStyle([
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
    ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#444444")),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("TOPPADDING", (0,0), (-1,-1), 4),
]))
story.append(info_table)
story.append(sp(16))


# 1. domain description
story.append(h("1. Domain Description"))
story.append(rule())
story.append(p(
    "BizLang is a domain-specific language that allows business analysts to describe "
    "analytics tasks in plain English. Instead of writing Python or SQL from scratch, "
    "a user can type a natural-language command and receive runnable code back."
))
story.append(sp())
story.append(p("Example inputs the language understands:"))
story.append(sp(4))

examples_data = [
    ["Input", "Output type"],
    ["load sales.csv and compute monthly revenue by region", "Pandas script"],
    ["generate a bar chart comparing Q1 and Q2 expenses", "Matplotlib code"],
    ["create a pivot table by product and region", "Pandas pivot_table()"],
    ["filter sales where region is North", "Pandas boolean filter"],
    ["show total earnings by department", "SQL SELECT + GROUP BY"],
]
ex_table = Table(examples_data, colWidths=[3.8*inch, 1.8*inch])
ex_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#333333")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f7f7")]),
    ("GRID", (0,0), (-1,-1), 0.3, colors.lightgrey),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
]))
story.append(ex_table)
story.append(sp(10))

story.append(p(
    "The system outputs one of three formats: <b>Pandas scripts</b>, <b>SQL queries</b>, "
    "or <b>Matplotlib chart code</b>. All output is syntactically valid and can be run "
    "directly without modification."
))
story.append(sp())
story.append(p(
    "A synonym dictionary handles natural variation in how users phrase commands. Words "
    "like \"generate\", \"plot\", and \"visualize\" all map to the same chart command. "
    "\"Average\", \"mean\" map to avg. \"Grouped by\", \"broken down by\", \"per\" all "
    "map to the by keyword. This normalization runs before the lexer so the grammar "
    "stays clean and unambiguous."
))


# 2. grammar
story.append(PageBreak())
story.append(h("2. Grammar Definition (BNF/EBNF)"))
story.append(rule())
story.append(p(
    "BizLang uses a context-free grammar defined in BNF/EBNF. Synonym normalization "
    "happens before lexing, so the grammar only needs to handle canonical keyword forms."
))
story.append(sp(6))
story.append(code("""\
<program>       ::= <statement> EOF

<statement>     ::= <load_stmt> | <compute_stmt> | <chart_stmt>
                  | <pivot_stmt> | <filter_stmt>

<load_stmt>     ::= "load" <filename> [ "and" <compute_stmt> ]

<compute_stmt>  ::= "compute" [ <time_grain> ] <agg_expr> [ <time_grain> ]
                    "by" <column_list> [ "where" <condition> ]

<chart_stmt>    ::= "chart" [ "a" | "an" ] [ <chart_type> ] [ "chart" ]
                    ( <agg_expr> | "comparing" <column_list> [ IDENT ] )
                    [ "by" <column_list> ]

<pivot_stmt>    ::= "pivot" "by" <column_list>
                    [ "and" [ "by" ] <column_list> ]
                    [ "compute" <agg_expr> ]

<filter_stmt>   ::= "filter" [ IDENT ] "where"
                    <condition> { "and" <condition> }

<agg_expr>      ::= [ <agg_func> ] IDENT
<agg_func>      ::= "sum" | "avg" | "count" | "min" | "max"
<chart_type>    ::= "bar" | "line" | "pie" | "scatter"
<time_grain>    ::= "monthly" | "daily" | "quarterly" | "yearly"
<column_list>   ::= IDENT { "and" IDENT }
<condition>     ::= IDENT "is" [ "not" ] ( STRING | NUMBER | IDENT )
<filename>      ::= IDENT "." ( "csv" | "xlsx" | "json" | "parquet" )"""))


# 3. parser
story.append(sp(10))
story.append(h("3. Parser Implementation"))
story.append(rule())
story.append(p(
    "<b>Strategy: Recursive Descent (top-down, LL(1))</b>"
))
story.append(sp(4))
story.append(p(
    "The parser is hand-written with one method per grammar rule. It consumes a flat "
    "token list produced by the lexer and returns an Abstract Syntax Tree. There is no "
    "external parser library — everything from tokenization to code generation is built "
    "from scratch."
))
story.append(sp())
story.append(p("The full pipeline is:"))
story.append(sp(4))
story.append(code(
    "raw input  →  synonym normalizer  →  Lexer  →  [Token]  →  Parser  →  AST  →  Generator  →  code"
))
story.append(sp(6))
story.append(p("<b>AST Node types:</b>"))
story.append(sp(4))
story.append(code("""\
LoadNode    (filename, follow_on)
ComputeNode (agg: AggExpr, group_by, time_grain, where: Condition)
ChartNode   (chart_type, agg: AggExpr, compare_cols, group_by)
PivotNode   (index_cols, column_cols, agg: AggExpr)
FilterNode  (source, conditions: [Condition])"""))
story.append(sp(6))
story.append(p(
    "<b>Error handling:</b> When the parser hits an unrecognized token it computes "
    "Levenshtein edit distance against the full keyword list and suggests the closest "
    "match. For example, typing \"genrate a bar chart\" produces: "
    "<i>parse error: unrecognized command — did you mean 'chart'?</i>"
))


# 4. example runs
story.append(PageBreak())
story.append(h("4. Example Runs"))
story.append(rule())

runs = [
    (
        "load sales.csv and compute monthly revenue by region",
        "pandas",
        """\
import pandas as pd

df = pd.read_csv("sales.csv")
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.to_period("M")

result = df.groupby(['month', 'region'])["revenue"].sum().reset_index()
result.columns = ['month', 'region', 'sum_revenue']
print(result)"""
    ),
    (
        "filter sales where region is North",
        "pandas",
        'filtered = df[(df["region"] == "North")]\nprint(filtered)'
    ),
    (
        "show total earnings by department",
        "sql",
        """\
SELECT
    department,
    SUM(earnings) AS sum_earnings
FROM data
GROUP BY department
ORDER BY sum_earnings DESC;"""
    ),
    (
        "compute average profit by department where region is not South",
        "sql",
        """\
SELECT
    department,
    AVG(profit) AS avg_profit
FROM data
WHERE region != 'South'
GROUP BY department
ORDER BY avg_profit DESC;"""
    ),
    (
        "generate a bar chart comparing Q1 and Q2 expenses",
        "chart",
        """\
import matplotlib.pyplot as plt

categories = ['Q1', 'Q2']
values = [df["Q1"].sum(), df["Q2"].sum()]

fig, ax = plt.subplots()
ax.bar(categories, values)
ax.set_title("Q1 vs Q2 expenses")
ax.set_ylabel("expenses")
plt.tight_layout()
plt.show()"""
    ),
    (
        "create a pivot table by product and region",
        "pandas",
        """\
pivot = df.pivot_table(
    index=['product', 'region'],
    values="value",
    aggfunc="sum"
)
print(pivot)"""
    ),
]

for cmd, mode, output in runs:
    story.append(Paragraph(f"<b>Input:</b>  <i>{cmd}</i>", body))
    story.append(Paragraph(f"<b>Mode:</b>   {mode}", body))
    story.append(sp(3))
    story.append(code(output))
    story.append(sp(8))


# 5. parse tree + AST
story.append(PageBreak())
story.append(h("5. Parse Tree and AST Visualization"))
story.append(rule())
story.append(p(
    "The following shows the full pipeline for the command "
    "<i>\"load sales.csv and compute monthly revenue by region\"</i>:"
))
story.append(sp(6))
story.append(h("Parse Tree (token stream)", h2))
story.append(code("""\
  Input:      "load sales.csv and compute monthly revenue by region"
  Normalized: "load sales.csv and compute monthly revenue by region"

  <program>
  ├── LOAD          'load'
  ├── FILENAME      'sales.csv'
  ├── AND           'and'
  ├── COMPUTE       'compute'
  ├── MONTHLY       'monthly'
  ├── IDENT         'revenue'
  ├── BY            'by'
  └── IDENT         'region'"""))
story.append(sp(8))
story.append(h("Abstract Syntax Tree", h2))
story.append(code("""\
  └── LoadNode
      ├── filename: "sales.csv"
      └── follow_on:
          └── ComputeNode
              ├── agg.func:    sum
              ├── agg.column:  revenue
              ├── group_by:    ['region']
              ├── time_grain:  monthly
              └── where:       None"""))
story.append(sp(12))

story.append(p(
    "A second example — <i>\"filter sales where region is North\"</i>:"
))
story.append(sp(6))
story.append(h("Parse Tree", h2))
story.append(code("""\
  <program>
  ├── FILTER        'filter'
  ├── IDENT         'sales'
  ├── WHERE         'where'
  ├── IDENT         'region'
  ├── IS            'is'
  └── IDENT         'North'"""))
story.append(sp(8))
story.append(h("AST", h2))
story.append(code("""\
  └── FilterNode
      ├── source: sales
      └── condition: region == 'North'"""))


# 6. how to run
story.append(PageBreak())
story.append(h("6. How to Run the Project"))
story.append(rule())

story.append(h("Requirements", h2))
story.append(code("pip install pandas matplotlib streamlit pytest"))
story.append(sp(8))

story.append(h("Terminal REPL", h2))
story.append(code("""\
cd bizlang-pro
python main.py

bizlang> load sales.csv and compute monthly revenue by region
bizlang> mode sql
bizlang> show total earnings by department
bizlang> quit"""))
story.append(sp(8))

story.append(h("Web IDE (Streamlit)", h2))
story.append(code("""\
streamlit run app.py
# opens at http://localhost:8501"""))
story.append(sp(4))
story.append(p(
    "The web interface shows the generated code, token stream, and AST side by side. "
    "Selecting pandas mode also runs the code live against samples/sales.csv and "
    "displays the result as a table."
))
story.append(sp(8))

story.append(h("AST Visualizer", h2))
story.append(code("""\
python ast_viz.py
# runs all demo examples

python ast_viz.py "compute average profit by department"
# run a specific command"""))
story.append(sp(8))

story.append(h("Tests", h2))
story.append(code("pytest tests/ -v   # 27 tests across lexer, parser, and generators"))
story.append(sp(12))

story.append(h("Project File Structure", h2))
story.append(code("""\
bizlang-pro/
  main.py                    REPL entry point
  app.py                     Streamlit web IDE
  ast_viz.py                 parse tree / AST printer
  grammar.bnf                full BNF/EBNF grammar
  ASSUMPTIONS.md             design decisions and objectives
  bizlang/
    synonyms.py              synonym normalization
    lexer.py                 tokenizer
    ast_nodes.py             AST node dataclasses
    parser.py                recursive descent parser
    generators/
      pandas_gen.py          Pandas code generator
      sql_gen.py             SQL query generator
      chart_gen.py           Matplotlib chart generator
  tests/                     pytest test suite (27 tests)
  samples/sales.csv          sample dataset"""))


# 7. assumptions (condensed)
story.append(PageBreak())
story.append(h("7. System Assumptions & Language Objectives"))
story.append(rule())

story.append(h("Target User", h2))
story.append(p(
    "Business analysts who know what they want from their data but don't want to write "
    "Python or SQL from scratch. The language is designed so that a command reads like "
    "something you'd say to a coworker."
))
story.append(sp(6))

story.append(h("Design Trade-offs", h2))
trade_data = [
    ["Decision", "Reasoning"],
    ["Single-table queries only", "Keeps grammar unambiguous. No JOIN support."],
    ["Output is code, not results", "Generated code can be reviewed and modified before running."],
    ["ANSI SQL output", "Works across Postgres, most cloud DBs. Minor tweaks needed for MySQL/SQLite."],
    ["Date column assumed to be 'date'", "Avoids schema-detection complexity. Documented in generated code."],
    ["No variables or assignment", "Each command is self-contained. Keeps parsing simple."],
]
td_table = Table(trade_data, colWidths=[2.2*inch, 3.6*inch])
td_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#333333")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f7f7")]),
    ("GRID", (0,0), (-1,-1), 0.3, colors.lightgrey),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
]))
story.append(td_table)
story.append(sp(8))

story.append(h("Extra Credit Features Implemented", h2))
ec_data = [
    ["Feature", "Points", "Implementation"],
    ["Synonym dictionary", "10 pts", "synonyms.py — 40+ mappings, regex pre-pass"],
    ["Error detection / self-correction", "10 pts", "Levenshtein distance in parser.py"],
    ["Web IDE (Streamlit)", "15 pts", "app.py — live code gen + preview"],
]
ec_table = Table(ec_data, colWidths=[2.0*inch, 0.8*inch, 3.0*inch])
ec_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#333333")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f7f7")]),
    ("GRID", (0,0), (-1,-1), 0.3, colors.lightgrey),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
]))
story.append(ec_table)


doc.build(story)
print(f"saved: {OUT}")
