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
    leftMargin=0.75*inch,
    rightMargin=0.75*inch,
    topMargin=0.75*inch,
    bottomMargin=0.75*inch,
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle("mytitle", parent=styles["Title"], fontSize=18, spaceAfter=2)
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=12, spaceAfter=2, spaceBefore=8)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=10, spaceAfter=2, spaceBefore=6)
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9, leading=13)
code_style = ParagraphStyle(
    "code",
    parent=styles["Code"],
    fontSize=7.5,
    leading=10,
    backColor=colors.HexColor("#f4f4f4"),
    leftIndent=8,
    rightIndent=8,
    spaceBefore=2,
    spaceAfter=2,
)

def h(text, style=h1):
    return Paragraph(text, style)

def p(text):
    return Paragraph(text, body)

def code(text):
    return Preformatted(text, code_style)

def sp(n=4):
    return Spacer(1, n)

def rule():
    return HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=3, spaceBefore=2)


story = []

# title block
story.append(Paragraph("BizLang", title_style))
story.append(Paragraph("Business Analytics Domain-Specific Language", styles["Heading2"]))
story.append(sp(2))
story.append(rule())

info_data = [
    ["Team Members", "Julius Jones, Derrick Tilford"],
    ["Course", "Programming Languages"],
    ["Project", "Option 3 — BizLang DSL"],
    ["Language", "Python 3"],
]
info_table = Table(info_data, colWidths=[1.4*inch, 4.5*inch])
info_table.setStyle(TableStyle([
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
    ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#444444")),
    ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ("TOPPADDING", (0,0), (-1,-1), 2),
]))
story.append(info_table)
story.append(sp(6))


# 1. domain description
story.append(h("1. Domain Description"))
story.append(rule())
story.append(p(
    "BizLang is a domain-specific language that lets business analysts describe analytics "
    "tasks in plain English and receive runnable code back — Pandas scripts, SQL queries, "
    "or Matplotlib chart code."
))
story.append(sp(3))

examples_data = [
    ["Input", "Output"],
    ["load sales.csv and compute monthly revenue by region", "Pandas script"],
    ["generate a bar chart comparing Q1 and Q2 expenses", "Matplotlib code"],
    ["create a pivot table by product and region", "Pandas pivot_table()"],
    ["filter sales where region is North", "Pandas boolean filter"],
    ["show total earnings by department", "SQL SELECT + GROUP BY"],
]
ex_table = Table(examples_data, colWidths=[4.0*inch, 1.6*inch])
ex_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#333333")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f7f7")]),
    ("GRID", (0,0), (-1,-1), 0.3, colors.lightgrey),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ("TOPPADDING", (0,0), (-1,-1), 3),
    ("LEFTPADDING", (0,0), (-1,-1), 5),
]))
story.append(ex_table)
story.append(sp(4))
story.append(p(
    "A synonym dictionary (40+ mappings) normalizes natural variation before the lexer runs — "
    "\"generate\", \"plot\", \"visualize\" all map to the chart command; \"average\"/\"mean\" map "
    "to avg; \"grouped by\"/\"per\"/\"broken down by\" all map to by."
))


# 2. grammar
story.append(sp(2))
story.append(h("2. Grammar Definition (BNF/EBNF)"))
story.append(rule())
story.append(p(
    "Context-free grammar. Synonym normalization runs before lexing so the grammar only handles canonical forms."
))
story.append(sp(3))
story.append(code("""\
<program>       ::= <statement> EOF
<statement>     ::= <load_stmt> | <compute_stmt> | <chart_stmt> | <pivot_stmt> | <filter_stmt>

<load_stmt>     ::= "load" <filename> [ "and" <compute_stmt> ]
<compute_stmt>  ::= "compute" [ <time_grain> ] <agg_expr> [ <time_grain> ] "by" <column_list> [ "where" <condition> ]
<chart_stmt>    ::= "chart" [ "a"|"an" ] [ <chart_type> ] [ "chart" ] ( <agg_expr> | "comparing" <column_list> [IDENT] ) [ "by" <column_list> ]
<pivot_stmt>    ::= "pivot" "by" <column_list> [ "and" ["by"] <column_list> ] [ "compute" <agg_expr> ]
<filter_stmt>   ::= "filter" [ IDENT ] "where" <condition> { "and" <condition> }

<agg_expr>      ::= [ <agg_func> ] IDENT
<agg_func>      ::= "sum" | "avg" | "count" | "min" | "max"
<chart_type>    ::= "bar" | "line" | "pie" | "scatter"
<time_grain>    ::= "monthly" | "daily" | "quarterly" | "yearly"
<column_list>   ::= IDENT { "and" IDENT }
<condition>     ::= IDENT "is" [ "not" ] ( STRING | NUMBER | IDENT )
<filename>      ::= IDENT "." ( "csv" | "xlsx" | "json" | "parquet" )"""))


# 3. parser
story.append(sp(2))
story.append(h("3. Parser Implementation"))
story.append(rule())
story.append(p(
    "<b>Strategy: Recursive Descent (top-down, LL(1)).</b> Hand-written with one method per grammar rule. "
    "No external parser library — lexer, parser, and code generators are all built from scratch."
))
story.append(sp(3))
story.append(code("raw input  →  synonym normalizer  →  Lexer  →  [Token]  →  Parser  →  AST  →  Generator  →  code"))
story.append(sp(3))
story.append(p("<b>AST node types:</b>"))
story.append(sp(2))
story.append(code("""\
LoadNode    (filename, follow_on)          ComputeNode (agg: AggExpr, group_by, time_grain, where: Condition)
ChartNode   (chart_type, agg, compare_cols, group_by)  PivotNode (index_cols, column_cols, agg)
FilterNode  (source, conditions: [Condition])"""))
story.append(sp(3))
story.append(p(
    "<b>Error handling:</b> Levenshtein edit distance against the keyword list gives the user a suggestion. "
    "e.g. \"genrate a bar chart\" → <i>parse error: unrecognized command — did you mean 'chart'?</i>"
))


# 4. example runs
story.append(PageBreak())
story.append(h("4. Example Runs"))
story.append(rule())

runs = [
    (
        "load sales.csv and compute monthly revenue by region", "pandas",
        'import pandas as pd\n\ndf = pd.read_csv("sales.csv")\ndf["date"] = pd.to_datetime(df["date"])\ndf["month"] = df["date"].dt.to_period("M")\n\nresult = df.groupby([\'month\', \'region\'])[\"revenue\"].sum().reset_index()\nresult.columns = [\'month\', \'region\', \'sum_revenue\']\nprint(result)'
    ),
    (
        "filter sales where region is North", "pandas",
        'filtered = df[(df["region"] == "North")]\nprint(filtered)'
    ),
    (
        "show total earnings by department", "sql",
        "SELECT\n    department,\n    SUM(earnings) AS sum_earnings\nFROM data\nGROUP BY department\nORDER BY sum_earnings DESC;"
    ),
    (
        "compute average profit by department where region is not South", "sql",
        "SELECT\n    department,\n    AVG(profit) AS avg_profit\nFROM data\nWHERE region != 'South'\nGROUP BY department\nORDER BY avg_profit DESC;"
    ),
    (
        "generate a bar chart comparing Q1 and Q2 expenses", "chart",
        "import matplotlib.pyplot as plt\n\ncategories = ['Q1', 'Q2']\nvalues = [df[\"Q1\"].sum(), df[\"Q2\"].sum()]\n\nfig, ax = plt.subplots()\nax.bar(categories, values)\nax.set_title(\"Q1 vs Q2 expenses\")\nax.set_ylabel(\"expenses\")\nplt.tight_layout()\nplt.show()"
    ),
    (
        "create a pivot table by product and region", "pandas",
        "pivot = df.pivot_table(\n    index=['product', 'region'],\n    values=\"value\",\n    aggfunc=\"sum\"\n)\nprint(pivot)"
    ),
]

for cmd, mode, output in runs:
    story.append(Paragraph(f"<b>Input:</b> <i>{cmd}</i>  |  <b>mode:</b> {mode}", body))
    story.append(sp(2))
    story.append(code(output))
    story.append(sp(5))


# 5. parse tree + AST
story.append(h("5. Parse Tree and AST Visualization"))
story.append(rule())
story.append(p("<i>\"load sales.csv and compute monthly revenue by region\"</i>"))
story.append(sp(2))

col_w = 2.95*inch
tree_data = [[
    Preformatted("""\
Parse Tree (token stream)
  <program>
  ├── LOAD          'load'
  ├── FILENAME      'sales.csv'
  ├── AND           'and'
  ├── COMPUTE       'compute'
  ├── MONTHLY       'monthly'
  ├── IDENT         'revenue'
  ├── BY            'by'
  └── IDENT         'region'""", code_style),
    Preformatted("""\
Abstract Syntax Tree
  └── LoadNode
      ├── filename: "sales.csv"
      └── follow_on:
          └── ComputeNode
              ├── agg.func:   sum
              ├── agg.column: revenue
              ├── group_by:   ['region']
              ├── time_grain: monthly
              └── where:      None""", code_style),
]]
side_table = Table(tree_data, colWidths=[col_w, col_w])
side_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 4)]))
story.append(side_table)
story.append(sp(4))

story.append(p("<i>\"filter sales where region is North\"</i>"))
story.append(sp(2))
tree_data2 = [[
    Preformatted("""\
Parse Tree
  <program>
  ├── FILTER   'filter'
  ├── IDENT    'sales'
  ├── WHERE    'where'
  ├── IDENT    'region'
  ├── IS       'is'
  └── IDENT    'North'""", code_style),
    Preformatted("""\
AST
  └── FilterNode
      ├── source: sales
      └── condition: region == 'North'""", code_style),
]]
side_table2 = Table(tree_data2, colWidths=[col_w, col_w])
side_table2.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 4)]))
story.append(side_table2)


# 6. how to run
story.append(sp(2))
story.append(h("6. How to Run the Project"))
story.append(rule())

run_data = [[
    [
        Paragraph("<b>Terminal REPL</b>", body),
        sp(2),
        code("python main.py\n\nbizlang> load sales.csv and compute monthly revenue by region\nbizlang> mode sql\nbizlang> show total earnings by department\nbizlang> quit"),
        sp(4),
        Paragraph("<b>AST Visualizer</b>", body),
        sp(2),
        code('python ast_viz.py\npython ast_viz.py "compute average profit by department"'),
        sp(4),
        Paragraph("<b>Tests</b>", body),
        sp(2),
        code("pytest tests/ -v   # 27 tests"),
    ],
    [
        Paragraph("<b>Web IDE (Streamlit)</b>", body),
        sp(2),
        code("pip install pandas matplotlib streamlit pytest\nstreamlit run app.py\n# opens at http://localhost:8501"),
        sp(4),
        Paragraph("<b>Project structure</b>", body),
        sp(2),
        code("bizlang-pro/\n  main.py          REPL\n  app.py           Streamlit web IDE\n  ast_viz.py       parse tree printer\n  grammar.bnf      BNF/EBNF grammar\n  bizlang/\n    synonyms.py    normalizer\n    lexer.py       tokenizer\n    ast_nodes.py   AST nodes\n    parser.py      recursive descent\n    generators/    pandas / sql / chart\n  tests/           27 pytest tests\n  samples/sales.csv"),
    ],
]]
run_table = Table(run_data, colWidths=[col_w, col_w])
run_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 6)]))
story.append(run_table)


# 7. assumptions
story.append(sp(2))
story.append(h("7. System Assumptions & Language Objectives"))
story.append(rule())
story.append(p(
    "<b>Target user:</b> Business analysts who know what they want from their data but don't want "
    "to write Python or SQL from scratch. Commands are designed to read like something you'd say to a coworker."
))
story.append(sp(4))

trade_data = [
    ["Decision", "Reasoning"],
    ["Single-table queries only", "Keeps grammar unambiguous. No JOIN support."],
    ["Output is code, not results", "Generated code can be reviewed and modified before running."],
    ["ANSI SQL output", "Works across Postgres and most cloud DBs."],
    ["Date column assumed 'date'", "Avoids schema-detection complexity."],
    ["No variables or assignment", "Each command is self-contained. Keeps parsing simple."],
]
td_table = Table(trade_data, colWidths=[2.1*inch, 3.7*inch])
td_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#333333")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f7f7")]),
    ("GRID", (0,0), (-1,-1), 0.3, colors.lightgrey),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ("TOPPADDING", (0,0), (-1,-1), 3),
    ("LEFTPADDING", (0,0), (-1,-1), 5),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
]))
story.append(td_table)
story.append(sp(4))

ec_data = [
    ["Extra Credit Feature", "Points", "Implementation"],
    ["Synonym dictionary", "10 pts", "synonyms.py — 40+ mappings, regex pre-pass"],
    ["Error detection / self-correction", "10 pts", "Levenshtein distance in parser.py"],
    ["Web IDE (Streamlit)", "15 pts", "app.py — live code gen + data preview"],
]
ec_table = Table(ec_data, colWidths=[2.1*inch, 0.7*inch, 3.0*inch])
ec_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#333333")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f7f7f7")]),
    ("GRID", (0,0), (-1,-1), 0.3, colors.lightgrey),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ("TOPPADDING", (0,0), (-1,-1), 3),
    ("LEFTPADDING", (0,0), (-1,-1), 5),
]))
story.append(ec_table)


doc.build(story)
print(f"saved: {OUT}")
