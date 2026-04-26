# BizLang — System Assumptions & Language Objectives

## Who is this for?

BizLang is built for business analysts and non-technical stakeholders who need to
run data queries but don't want to write Python or SQL from scratch. The target user
knows what they want from their data — they just don't know the exact syntax to get it.

Think of it like this: instead of Googling "pandas groupby sum reset_index", a user
can just type "compute monthly revenue by region" and get a working script back.

---

## What BizLang is designed to do

- Load tabular data from CSV/Excel files
- Compute aggregations (sum, average, count, min, max) grouped by any column
- Filter rows by a condition
- Build pivot tables across two dimensions
- Generate bar, line, pie, and scatter charts
- Output runnable Pandas code, SQL queries, or Matplotlib chart scripts

The output is always code, not a result. This is intentional — the generated code
can be reviewed, modified, and run independently. BizLang is a translator, not an executor.

---

## Language objectives

**1. Natural English first**
Commands should read like something you'd say to a coworker: "load the sales file
and show me monthly revenue by region." We handle common synonyms automatically
so users don't need to memorize exact keywords.

**2. One command, one intent**
Each BizLang statement maps to exactly one analytics operation. We don't try to
handle multi-step pipelines in a single input — that would make parsing much harder
and the grammar ambiguous. The exception is "load X and compute Y" which chains
two operations because it's such a common pattern.

**3. The output has to actually run**
Generated Pandas/SQL code is meant to be dropped straight into a Jupyter notebook or
a database client. We don't generate pseudocode or descriptions — every output is
syntactically valid Python or SQL.

---

## Design trade-offs and known limitations

**Trade-off: column names vs. business terms**
Some words are both business synonyms and column names. "revenue" could mean the
aggregation function "sum" or it could be a column called `revenue`. We assume column
names are preserved as-is in the input and only substitute known aggregation keywords
(like "total", "average") rather than domain nouns. This means "show total revenue by
region" works, but "show revenue by region" (without an explicit agg word) defaults
to sum on the `revenue` column — which is usually the right behavior anyway.

**Trade-off: fixed schema assumptions**
The time grain features (monthly, quarterly, etc.) assume the DataFrame has a column
called `date` in a format pandas can parse. If the date column is named something
else, the user needs to rename it before running the generated code. We document
this assumption in the generated code as a comment.

**Trade-off: single-table queries only**
BizLang does not support JOINs or multi-table operations. Every command operates on
a single DataFrame loaded from one file. This keeps the grammar simple and avoids
a lot of ambiguity. If someone needs a join they'll have to write that part manually.

**Trade-off: SQL output is generic (ANSI)**
Generated SQL uses standard syntax (DATE_TRUNC, GROUP BY, WHERE) rather than
targeting a specific database. This means it'll work in Postgres and most cloud DBs
but may need minor tweaks for MySQL or SQLite.

**Limitation: no assignment or variables**
BizLang doesn't support saving results to named variables or piping one command into
the next (beyond the load+compute chain). Each command is self-contained.

**Limitation: no math expressions**
You can't say "compute revenue minus expenses by region" — arithmetic on columns isn't
in scope. The aggregation functions work on single columns only.

---

## Error handling approach

When the parser hits something it doesn't recognize, it tries to:
1. Show where in the input the problem occurred
2. Suggest the closest matching keyword using edit distance

For example: "genrate a bar chart..." → `parse error: did you mean 'chart'?`

This makes it easier for users to self-correct without needing to consult documentation.

---

## Synonym dictionary

We maintain a synonym table that normalizes input before tokenizing. This covers
common variations like:
- "generate / plot / draw / visualize" → `chart`
- "calculate / summarize / find / get / show" → `compute`
- "average / mean" → `avg`
- "total" → `sum`
- "grouped by / broken down by / per / split by" → `by`
- "versus / vs / against" → `comparing`
- "by month / each month" → `monthly`
- ...and about 40 more

The normalization happens in a single pre-pass before the lexer runs, using
regex with word boundaries so partial matches don't cause false replacements.
