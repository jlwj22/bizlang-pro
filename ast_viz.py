import sys
from bizlang.synonyms import normalize
from bizlang.lexer import Lexer, TT
from bizlang.parser import Parser, ParseError
from bizlang.ast_nodes import LoadNode, ComputeNode, ChartNode, PivotNode, FilterNode


def print_parse_tree(tokens: list, input_text: str):
    print(f"  Input:  \"{input_text}\"")
    print(f"  Normalized: \"{normalize(input_text)}\"")
    print()
    print("  Parse Tree (token stream)")
    print("  " + "-" * 40)
    print("  <program>")
    for i, tok in enumerate(tokens):
        if tok.type == TT.EOF:
            break
        is_last = all(t.type == TT.EOF for t in tokens[i+1:])
        branch = "└──" if is_last else "├──"
        print(f"  {branch} {tok.type.name:<12}  '{tok.value}'")
    print()


def _node_lines(node, prefix="", is_last=True) -> list:
    connector = "└── " if is_last else "├── "
    lines = []

    if isinstance(node, LoadNode):
        lines.append(prefix + connector + "LoadNode")
        cp = prefix + ("    " if is_last else "│   ")
        lines.append(cp + f"├── filename: \"{node.filename}\"")
        if node.follow_on:
            lines.append(cp + "└── follow_on:")
            lines += _node_lines(node.follow_on, cp + "    ", is_last=True)
        else:
            lines.append(cp + "└── follow_on: None")

    elif isinstance(node, ComputeNode):
        lines.append(prefix + connector + "ComputeNode")
        cp = prefix + ("    " if is_last else "│   ")
        lines.append(cp + f"├── agg.func:    {node.agg.func}")
        lines.append(cp + f"├── agg.column:  {node.agg.column}")
        lines.append(cp + f"├── group_by:    {node.group_by}")
        lines.append(cp + f"├── time_grain:  {node.time_grain}")
        if node.where:
            c = node.where
            lines.append(cp + f"└── where:       {c.column} {c.op} {c.value!r}")
        else:
            lines.append(cp + "└── where:       None")

    elif isinstance(node, ChartNode):
        lines.append(prefix + connector + "ChartNode")
        cp = prefix + ("    " if is_last else "│   ")
        lines.append(cp + f"├── chart_type:    {node.chart_type}")
        lines.append(cp + f"├── agg.func:      {node.agg.func}")
        lines.append(cp + f"├── agg.column:    {node.agg.column}")
        lines.append(cp + f"├── compare_cols:  {node.compare_cols}")
        lines.append(cp + f"└── group_by:      {node.group_by}")

    elif isinstance(node, PivotNode):
        lines.append(prefix + connector + "PivotNode")
        cp = prefix + ("    " if is_last else "│   ")
        lines.append(cp + f"├── index_cols:   {node.index_cols}")
        lines.append(cp + f"├── column_cols:  {node.column_cols}")
        agg_str = f"{node.agg.func}({node.agg.column})" if node.agg else "sum (default)"
        lines.append(cp + f"└── agg:          {agg_str}")

    elif isinstance(node, FilterNode):
        lines.append(prefix + connector + "FilterNode")
        cp = prefix + ("    " if is_last else "│   ")
        lines.append(cp + f"├── source: {node.source}")
        for i, c in enumerate(node.conditions):
            last = (i == len(node.conditions) - 1)
            br = "└──" if last else "├──"
            lines.append(cp + f"{br} condition: {c.column} {c.op} {c.value!r}")
    else:
        lines.append(prefix + connector + repr(node))

    return lines


def print_ast(ast):
    print("  AST")
    print("  " + "-" * 40)
    for line in _node_lines(ast, prefix="  ", is_last=True):
        print(line)
    print()


DEMO_INPUTS = [
    "load sales.csv and compute monthly revenue by region",
    "generate a bar chart comparing Q1 and Q2 expenses",
    "create a pivot table by product and region",
    "filter sales where region is North",
    "compute average profit by department where region is not South",
]


def run(text: str):
    print("=" * 56)
    print()
    normed = normalize(text)
    tokens = Lexer(normed).tokenize()
    print_parse_tree(tokens, text)
    try:
        ast = Parser(tokens).parse()
        print_ast(ast)
    except ParseError as e:
        print(f"  Parse error: {e}")
        print()


def main():
    if len(sys.argv) > 1:
        run(" ".join(sys.argv[1:]))
    else:
        print("\nBizLang — AST & Parse Tree Visualizer")
        print("Running demo examples...\n")
        for ex in DEMO_INPUTS:
            run(ex)


if __name__ == "__main__":
    main()
