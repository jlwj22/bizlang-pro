# BizLang — System Assumptions & Language Objectives

## Who is this for?

Business analysts who need to run data queries but don't want to write Python or SQL
from scratch. The target user knows what they want from their data, just not the exact
syntax to get it. Instead of Googling "pandas groupby sum reset_index", they type
"compute monthly revenue by region" and get a working script back.

---

## What it does

- Load tabular data from CSV/Excel files
- Compute aggregations (sum, avg, count, min, max) grouped by any column
- Filter rows by a condition
- Build pivot tables across two dimensions
- Generate bar, line, pie, and scatter charts
- Output runnable Pandas code, SQL queries, or Matplotlib chart scripts

The output is always code, not a result. This is intentional — the generated code
can be reviewed, modified, and run independently. BizLang is a translator.

---

## Design goals

**Natural English first.** Commands should read like something you'd say to a
coworker: "load the sales file and show me monthly revenue by region." Common
synonyms are handled automatically so users don't need to memorize exact keywords.

**One command, one intent.** Each statement maps to exactly one analytics operation.
The one exception is "load X and compute Y" which chains two ops because it's such
a common pattern it felt wrong not to support it.

**The output actually runs.** Every Pandas/SQL output is syntactically valid and
can be dropped straight into a notebook or database client. No pseudocode.

---

## Limitations and trade-offs

**Column names vs. business terms.** Some words are both synonyms and column names.
We only substitute known aggregation words (like "total", "average") rather than
domain nouns like "revenue" or "profit", which are treated as column names.

**Assumed date column.** Time grain features (monthly, quarterly, etc.) assume the
DataFrame has a column called `date` that pandas can parse. If the date column is
named differently, the user needs to rename it or edit the generated code.

**Single-table only.** No JOINs or multi-table queries. Everything runs on one
DataFrame from one file. Keeps the grammar unambiguous.

**ANSI SQL output.** Generated SQL uses standard syntax (DATE_TRUNC, GROUP BY)
rather than targeting a specific DB. Works in Postgres and most cloud DBs but may
need small tweaks for MySQL or SQLite.

**No variables or assignment.** You can't save a result and reference it later.
Each command is self-contained.

**No math expressions.** "compute revenue minus expenses by region" isn't supported.
Aggregation works on single columns only.

---

## Error handling

When the parser hits something it doesn't understand, it:
1. Shows where in the input the problem is
2. Suggests the closest matching keyword using edit distance

Example: `"genrate a bar chart..."` → `parse error: did you mean 'chart'?`

---

## Synonym dictionary

A pre-pass replaces common variations with canonical keywords before tokenizing:

- "generate / plot / draw / visualize" → `chart`
- "calculate / summarize / find / show" → `compute`
- "average / mean" → `avg`
- "total" → `sum`
- "grouped by / broken down by / per" → `by`
- "versus / vs / against" → `comparing`
- "by month / each month" → `monthly`
- ...40+ total mappings (see synonyms.py)

Matching is case-insensitive and uses word boundaries so partial matches don't
cause false replacements.
