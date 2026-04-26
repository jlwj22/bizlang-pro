from bizlang.synonyms import normalize
from bizlang.lexer import Lexer
from bizlang.parser import Parser, ParseError
from bizlang.generators.pandas_gen import PandasGenerator
from bizlang.generators.sql_gen import SQLGenerator
from bizlang.generators.chart_gen import ChartGenerator

BANNER = """\
  ____  _     _
 | __ )(_)___| |    __ _ _ __   __ _
 |  _ \\| |_  / |   / _` | '_ \\ / _` |
 | |_) | |/ /| |__| (_| | | | | (_| |
 |____/|_/___|_____\\__,_|_| |_|\\__, |
                                |___/

Type a command. 'mode [pandas|sql|chart]' to switch output. 'quit' to exit.
"""

MODES = ("pandas", "sql", "chart")


def _run(raw: str, mode: str, ctx: dict) -> str:
    normed = normalize(raw)
    tokens = Lexer(normed).tokenize()
    ast = Parser(tokens).parse()

    if mode == "pandas":
        return PandasGenerator(ctx).generate(ast)
    elif mode == "sql":
        return SQLGenerator().generate(ast)
    else:
        return ChartGenerator(ctx).generate(ast)


def _update_ctx(ast, ctx: dict):
    from bizlang.ast_nodes import LoadNode
    if isinstance(ast, LoadNode):
        ctx["last_file"] = ast.filename
        ctx["df_name"] = "df"


def repl():
    print(BANNER)
    mode = "pandas"
    ctx = {}

    while True:
        try:
            raw = input("bizlang> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break

        if not raw:
            continue

        if raw.lower() in ("quit", "exit", "q"):
            print("Bye.")
            break

        if raw.lower().startswith("mode "):
            parts = raw.split()
            if len(parts) >= 2 and parts[1].lower() in MODES:
                mode = parts[1].lower()
                print(f"[mode: {mode}]")
            else:
                print(f"Unknown mode. Use: {', '.join(MODES)}")
            continue

        if raw.lower() in ("help", "?"):
            print("Commands:  load  compute  chart  pivot  filter")
            print("Modes:     mode pandas | mode sql | mode chart")
            continue

        try:
            code = _run(raw, mode, ctx)
            normed = normalize(raw)
            toks = Lexer(normed).tokenize()
            ast = Parser(toks).parse()
            _update_ctx(ast, ctx)

            print()
            print("--- generated code ---")
            print(code)
            print("----------------------")
            print()
        except ParseError as e:
            print(f"  parse error: {e}")
        except Exception as e:
            print(f"  error: {e}")


if __name__ == "__main__":
    repl()
