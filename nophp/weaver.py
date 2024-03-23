# Pretty-print
from rich import print
from rich.console import Console

from .lang.compiler import Compiler
from .lang.std.htmlspecialchars import HTMLSpecialCharMod
from .lang.std.rand import RandMod
from .lang.std.string import *
from .splitter import split_php
console = Console()
from rich.syntax import Syntax
from rich.progress import Progress

# Parser and lexer
from .lang.lexer import PyettyLexer
from .lang.pparser import PyettyParser
# from rich.traceback import install
# install()

# Load modules
from .lang.modules import (
    ConditionalMod,
    ForEachMod,
    GetIndexMod,
    InternalMod,
    MathMod,
    Module,
    NamespaceMemberMod,
    NamespaceMod,
    NewObjectMod,
    PhpMod,
    HTMLMod,
    ConcatMod,
    PublicMod,
    RequireOnceMod,
    ReturnMod,
    TarrowMod,
    UseMod,
    VariableAssignMod,
    ResolutionMod,
    FunctionCallMod,
    ClassDeclarationMod,
    FunctionDecMod,
    WhileMod
)
# Language builtins
from .lang.std.echo import EchoMod

### Args proc ###
from sys import argv
flags = ''
if len(argv) < 2: 
    raise Exception("Usage: python3 p <input>")
#################
### Read file ###
text = open(argv[1],"r").read()
text, html = split_php(text)
#################

### Construct tree ###
lexer = PyettyLexer()
parser = PyettyParser()
######################
def prettify_and_write(data, indentation=0, file=None):
    if isinstance(data, tuple):
        if len(data) == 2:
            label, content = data
            if isinstance(content, dict):
                file.write(f"{' ' * indentation}('{label}', {{\n")
                for key, value in content.items():
                    file.write(f"{' ' * (indentation + 4)}'{key}': ")
                    prettify_and_write(value, indentation + 4, file)
                file.write(f"{' ' * indentation}}},\n")
            elif isinstance(content, tuple):
                file.write(f"{' ' * indentation}('{label}', (\n")
                for item in content:
                    prettify_and_write(item, indentation + 4, file)
                file.write(f"{' ' * indentation})),\n")
            else:
                file.write(f"{' ' * indentation}('{label}', {content}),\n")
        elif len(data) == 1:
            prettify_and_write(data[0], indentation, file)
        else:
            for item in data:
                prettify_and_write(item, indentation + 4, file)
            
    elif isinstance(data, dict):
        file.write(f"{' ' * indentation}{{\n")
        for key, value in data.items():
            file.write(f"{' ' * (indentation + 4)}'{key}': ")
            prettify_and_write(value, 1, file)
        file.write(f"{' ' * indentation}}},\n")
    else:
        file.write(f"{' ' * indentation}{data},\n")




### Tasks ###

# Works only on functions that support tasks
def construct_task(
    progress, 
    task,
    target,
    *args,
    tasklen = 100
):
    def _run_task():
        return target(
            *args,
            task = task,
            progress = progress,
            tasklen = tasklen
        )
    return _run_task

with Progress(
    refresh_per_second = 100
) as total_progress:
    # Lex 
    lex = total_progress.add_task("Lex...", total=100)
    lexed_tokens = lexer.tokenize(text)

    # Increases time it takes, but makes it possible to track tree building
    lexed_len    = len(list(lexer.tokenize(text)))
    total_progress.update(lex, advance=100)

    # print(list(lexer.tokenize(text)))

    new_arr = []
    for tok in lexer.tokenize(text):
        new_arr.append(tok)
    


    # print(new_arr)

    # Build tree task
    build_tree = total_progress.add_task("Building tree...", total=1000)
    build_tree_task = construct_task(
        total_progress,
        build_tree,
        parser.parse,
        iter(new_arr),
        tasklen = len(new_arr)
    )

    tree = build_tree_task()
    with open("tree", "w+") as f:
        prettify_and_write(tree, 1, f)
    
    # Force finish
    total_progress.update(build_tree, advance=1000)

print(f"\n[bold green]Tree complete, translating...[/bold green]")

compiler = Compiler(tree)
compiler.populate_modules_actions(
    [
        PhpMod,
        HTMLMod,
        VariableAssignMod,
        ResolutionMod,
        NamespaceMod,
        FunctionCallMod,
        ConcatMod,
        ClassDeclarationMod,
        FunctionDecMod,
        ReturnMod,
        NewObjectMod,
        ConditionalMod,
        WhileMod,
        MathMod,
        NamespaceMemberMod,
        GetIndexMod,
        ForEachMod,
        InternalMod,
        TarrowMod
    ]
)
compiler.builtin_functions = {
    # Fake internals as functions
    "echo": {
        "run_func": EchoMod(compiler)
    },
    "require_once": {
        "run_func": RequireOnceMod(compiler)
    },
    "use": {
        "run_func": UseMod(compiler)
    },
    "public": {
        "run_func": PublicMod(compiler)
    },
    "rand": {
        "run_func": RandMod(compiler)
    },
    "htmlspecialchars": {
        "run_func": HTMLSpecialCharMod(compiler)
    },
    "strlen": {
        "run_func": StrLenMod(compiler)
    },
    "str_replace": {
        "run_func": StrReplaceMod(compiler)
    },
}

def main():
    compiler.run()

    pyetty_out_pretty = Syntax(
                        '\n'.join([str(el) for el in compiler.finished]) + "\n" + html,
                        "v",
                        padding=1, 
                        line_numbers=True
                    )
    # print(pyetty_out_pretty)

    print("[green]Complete serving...[/green]")

    with open('out.html', "w+") as f:
        f.write(''.join([str(el) for el in compiler.finished]))
        f.write(html)

if __name__ == '__main__':
    main()

# webbrowser.open('file://' + os.path.realpath("out.html"))

# print(f"\n[bold green]Source complete, compiling...[/bold green]")
# with open("out.v", "w+") as out:
#     out.write('\n'.join(compiler.finished))
# os.system(f"v crun out.v")