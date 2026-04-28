from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted

OUT = "BizLang_Submission.pdf"

doc = SimpleDocTemplate(
    OUT,
    pagesize=letter,
    leftMargin=1.0*inch,
    rightMargin=1.0*inch,
    topMargin=1.0*inch,
    bottomMargin=1.0*inch,
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle("t", parent=styles["Title"], fontSize=20, spaceAfter=4)
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=12, spaceAfter=2, spaceBefore=12)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=10, spaceAfter=2, spaceBefore=8)
body = ParagraphStyle("b", parent=styles["Normal"], fontSize=10, leading=15)
code_style = ParagraphStyle(
    "code", parent=styles["Code"], fontSize=8, leading=11,
    leftIndent=16, spaceBefore=2, spaceAfter=4,
)

def h(text, style=h1):  return Paragraph(text, style)
def p(text):            return Paragraph(text, body)
def code(text):         return Preformatted(text, code_style)
def sp(n=6):            return Spacer(1, n)


story = []

# Header
story.append(Paragraph("BizLang", title_style))
story.append(p("Business Analytics Domain-Specific Language"))
story.append(sp(4))
story.append(p("Team Members:  Julius Jones, Derrick Tilford"))
story.append(p("Course:  Programming Languages"))
story.append(p("Project:  Option 3 — BizLang DSL"))
story.append(p("Language:  Python 3"))
story.append(sp(12))


# 1. Domain Description
story.append(h("1. Domain Description"))
story.append(p(
    "BizLang is a domain-specific language for business analysts who need to run data queries "
    "without writing Python or SQL. You type what you want in plain English, and BizLang gives "
    "you back runnable code — either a Pandas script, a SQL query, or Matplotlib chart code."
))
story.append(sp(6))
story.append(p("Example commands:"))
story.append(sp(2))
story.append(code(
    'load sales.csv and compute monthly revenue by region  ->  Pandas groupby script\n'
    'generate a bar chart comparing Q1 and Q2 expenses     ->  Matplotlib bar chart\n'
    'create a pivot table by product and region            ->  df.pivot_table() call\n'
    'filter sales where region is North                    ->  Pandas boolean filter\n'
    'show total earnings by department                     ->  SQL SELECT + GROUP BY'
))
story.append(sp(6))
story.append(p(
    "A synonym dictionary with 40+ mappings normalizes natural variation before the lexer runs. "
    "\"generate\", \"plot\", \"visualize\", and \"draw\" all become the chart command. "
    "\"average\" and \"mean\" become avg. \"grouped by\", \"per\", and \"broken down by\" all become by."
))
story.append(sp(12))


# 2. Grammar
story.append(h("2. Grammar Definition (BNF/EBNF)"))
story.append(p(
    "Context-free grammar. Synonym normalization runs before lexing so the grammar only "
    "handles canonical keyword forms."
))
story.append(sp(4))
story.append(code(
    "<program>       ::= <statement> EOF\n"
    "<statement>     ::= <load_stmt> | <compute_stmt> | <chart_stmt> | <pivot_stmt> | <filter_stmt>\n"
    "\n"
    "<load_stmt>     ::= \"load\" <filename> [ \"and\" <compute_stmt> ]\n"
    "<compute_stmt>  ::= \"compute\" [ <time_grain> ] <agg_expr> [ <time_grain> ]\n"
    "                    \"by\" <column_list> [ \"where\" <condition> ]\n"
    "<chart_stmt>    ::= \"chart\" [ \"a\"|\"an\" ] [ <chart_type> ] [ \"chart\" ]\n"
    "                    ( <agg_expr> | \"comparing\" <column_list> [IDENT] ) [ \"by\" <column_list> ]\n"
    "<pivot_stmt>    ::= \"pivot\" \"by\" <column_list>\n"
    "                    [ \"and\" [\"by\"] <column_list> ] [ \"compute\" <agg_expr> ]\n"
    "<filter_stmt>   ::= \"filter\" [ IDENT ] \"where\" <condition> { \"and\" <condition> }\n"
    "\n"
    "<agg_expr>      ::= [ <agg_func> ] IDENT\n"
    "<agg_func>      ::= \"sum\" | \"avg\" | \"count\" | \"min\" | \"max\"\n"
    "<chart_type>    ::= \"bar\" | \"line\" | \"pie\" | \"scatter\"\n"
    "<time_grain>    ::= \"monthly\" | \"daily\" | \"quarterly\" | \"yearly\"\n"
    "<column_list>   ::= IDENT { \"and\" IDENT }\n"
    "<condition>     ::= IDENT \"is\" [ \"not\" ] ( STRING | NUMBER | IDENT )\n"
    "<filename>      ::= IDENT \".\" ( \"csv\" | \"xlsx\" | \"json\" | \"parquet\" )"
))
story.append(sp(12))


# 3. Parser
story.append(h("3. Parser Implementation"))
story.append(p(
    "Strategy: Recursive Descent (top-down, LL(1)). Hand-written with one method per grammar "
    "rule. No external parser library — lexer, parser, and all three code generators are built "
    "from scratch in pure Python."
))
story.append(sp(4))
story.append(code(
    "raw input  ->  synonym normalizer  ->  Lexer  ->  [Token]  ->  Parser  ->  AST  ->  Generator  ->  code"
))
story.append(sp(6))
story.append(p("AST node types:"))
story.append(sp(2))
story.append(code(
    "LoadNode    (filename, follow_on)\n"
    "ComputeNode (agg: AggExpr, group_by, time_grain, where: Condition)\n"
    "ChartNode   (chart_type, agg, compare_cols, group_by)\n"
    "PivotNode   (index_cols, column_cols, agg)\n"
    "FilterNode  (source, conditions: [Condition])"
))
story.append(sp(6))
story.append(p(
    "Error handling: when the parser hits something it doesn't recognize, it computes "
    "Levenshtein edit distance against the keyword list and gives the user a suggestion."
))
story.append(code('Input:  "genrate a bar chart..."\nError:  parse error: unrecognized command -- did you mean \'chart\'?'))
story.append(sp(12))


# 4. Example Runs
story.append(h("4. Example Runs"))

story.append(h("load sales.csv and compute monthly revenue by region  (pandas mode)", h2))
story.append(code(
    'import pandas as pd\n\n'
    'df = pd.read_csv("sales.csv")\n'
    'df["date"] = pd.to_datetime(df["date"])\n'
    'df["month"] = df["date"].dt.to_period("M")\n'
    'result = df.groupby([\'month\', \'region\'])[\'revenue\'].sum().reset_index()\n'
    'result.columns = [\'month\', \'region\', \'sum_revenue\']\n'
    'print(result)'
))

story.append(h("show total earnings by department  (sql mode)", h2))
story.append(code(
    "SELECT\n"
    "    department,\n"
    "    SUM(earnings) AS sum_earnings\n"
    "FROM data\n"
    "GROUP BY department\n"
    "ORDER BY sum_earnings DESC;"
))

story.append(h("compute average profit by department where region is not South  (sql mode)", h2))
story.append(code(
    "SELECT\n"
    "    department,\n"
    "    AVG(profit) AS avg_profit\n"
    "FROM data\n"
    "WHERE region != 'South'\n"
    "GROUP BY department\n"
    "ORDER BY avg_profit DESC;"
))

story.append(h("filter sales where region is North  (pandas mode)", h2))
story.append(code(
    'filtered = df[(df["region"] == "North")]\n'
    'print(filtered)'
))

story.append(h("generate a bar chart comparing Q1 and Q2 expenses  (chart mode)", h2))
story.append(code(
    "import matplotlib.pyplot as plt\n\n"
    "categories = ['Q1', 'Q2']\n"
    "values = [df['Q1'].sum(), df['Q2'].sum()]\n\n"
    "fig, ax = plt.subplots()\n"
    "ax.bar(categories, values)\n"
    "ax.set_title('Q1 vs Q2 expenses')\n"
    "ax.set_ylabel('expenses')\n"
    "plt.tight_layout()\n"
    "plt.show()"
))

story.append(h("create a pivot table by product and region  (pandas mode)", h2))
story.append(code(
    "pivot = df.pivot_table(\n"
    "    index=['product', 'region'],\n"
    "    values='value',\n"
    "    aggfunc='sum'\n"
    ")\n"
    "print(pivot)"
))
story.append(sp(12))


# 5. Parse Tree / AST
story.append(h("5. Parse Tree and AST"))
story.append(p('Input: "load sales.csv and compute monthly revenue by region"'))
story.append(sp(4))
story.append(code(
    "Parse Tree (token stream)          Abstract Syntax Tree\n"
    "  <program>                          LoadNode\n"
    "  |- LOAD        'load'                |- filename: \"sales.csv\"\n"
    "  |- FILENAME    'sales.csv'           '- follow_on:\n"
    "  |- AND         'and'                     ComputeNode\n"
    "  |- COMPUTE     'compute'                   |- agg.func:   sum\n"
    "  |- MONTHLY     'monthly'                   |- agg.column: revenue\n"
    "  |- IDENT       'revenue'                   |- group_by:   ['region']\n"
    "  |- BY          'by'                        |- time_grain: monthly\n"
    "  '- IDENT       'region'                    '- where:      None"
))
story.append(sp(8))
story.append(p('Input: "filter sales where region is North"'))
story.append(sp(4))
story.append(code(
    "Parse Tree                         AST\n"
    "  <program>                          FilterNode\n"
    "  |- FILTER    'filter'                |- source: sales\n"
    "  |- IDENT     'sales'                 '- condition: region == 'North'\n"
    "  |- WHERE     'where'\n"
    "  |- IDENT     'region'\n"
    "  |- IS        'is'\n"
    "  '- IDENT     'North'"
))
story.append(sp(12))


# 6. How to Run
story.append(h("6. How to Run the Project"))
story.append(p("Install dependencies:"))
story.append(code("pip install pandas matplotlib streamlit pytest"))
story.append(sp(4))
story.append(p("Terminal REPL:"))
story.append(code(
    "python main.py\n\n"
    "bizlang> load samples/sales.csv and compute monthly revenue by region\n"
    "bizlang> mode sql\n"
    "bizlang> show total earnings by department\n"
    "bizlang> quit"
))
story.append(sp(4))
story.append(p("Web IDE (Streamlit):"))
story.append(code("streamlit run app.py\n# opens at http://localhost:8501"))
story.append(sp(4))
story.append(p("AST visualizer:"))
story.append(code(
    "python ast_viz.py\n"
    "python ast_viz.py \"compute average profit by department\""
))
story.append(sp(4))
story.append(p("Tests (27 total):"))
story.append(code("pytest tests/ -v"))
story.append(sp(12))


# 7. Assumptions & Trade-offs
story.append(h("7. System Assumptions and Trade-offs"))
story.append(p("Target user: business analysts who know what they want from their data but don't want to write Python or SQL from scratch."))
story.append(sp(6))
story.append(p("Design decisions:"))
story.append(sp(2))
story.append(code(
    "Single-table only        No JOINs. Keeps the grammar unambiguous.\n"
    "Output is code           Generated code can be reviewed before running.\n"
    "ANSI SQL                 Works in Postgres and most cloud DBs.\n"
    "Date column assumed      Time grain features expect a column named 'date'.\n"
    "No variables             Each command is self-contained.\n"
    "No math expressions      Aggregation works on single columns only."
))
story.append(sp(8))
story.append(p("Extra credit implemented:"))
story.append(sp(2))
story.append(code(
    "Synonym dictionary       10 pts  --  synonyms.py, 40+ mappings, regex pre-pass\n"
    "Error detection          10 pts  --  Levenshtein distance in parser.py\n"
    "Web IDE (Streamlit)      15 pts  --  app.py, live code gen + data preview"
))


doc.build(story)
print(f"saved: {OUT}")
