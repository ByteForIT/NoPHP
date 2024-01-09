import random
from flask import Flask
# Lang
from .lang.compiler import Compiler
from .lang.lexer import PyettyLexer
from .lang.pparser import PyettyParser
from .lang.types import Request
from .splitter import split_php

# Load modules
from .lang.modules import (
    BoolMod,
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
    PrivateMod,
    ProtectedMod,
    PublicMod,
    RequireOnceMod,
    ReturnMod,
    SetIndexMod,
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
from .lang.std import (
    echo,
    rand,
    htmlspecialchars,
    string,
    session,
    redirect,
    primitives,
    db
)

# Read wool config
from sys import argv

import yaml
from yaml import Loader
flags = ''
if len(argv) < 2: 
    raise Exception("Usage: python3 p <input>")

config = yaml.load(open(argv[1],"r"), Loader)

class SpindleApp:
    def __init__(self) -> None:
        self.app = Flask(__name__)
        self.lexer = PyettyLexer()
        self.parser = PyettyParser()

        self.functions = {}



    def build_sp(self, file, _c):
        text = open(file,"r").read()
        php, html = split_php(text)
        toks = self.lexer.tokenize(
            php
        )
        ast = self.parser.parse(toks)



        _c.populate_modules_actions(
            [
                ConditionalMod,
                ForEachMod,
                GetIndexMod,
                InternalMod,
                MathMod,
                NamespaceMemberMod,
                NamespaceMod,
                NewObjectMod,
                PhpMod,
                HTMLMod,
                ConcatMod,
                PrivateMod,
                ProtectedMod,
                PublicMod,
                RequireOnceMod,
                ReturnMod,
                SetIndexMod,
                TarrowMod,
                UseMod,
                VariableAssignMod,
                ResolutionMod,
                FunctionCallMod,
                ClassDeclarationMod,
                FunctionDecMod,
                WhileMod,
                BoolMod,
            ]
        )
        _c.add_builtin_functions({
            # Fake internals as functions
            "echo": {
                "run_func": echo.EchoMod(_c)
            },
            "rand": {
                "run_func": rand.RandMod(_c)
            },
            "htmlspecialchars": {
                "run_func": htmlspecialchars.HTMLSpecialCharMod(_c)
            },
            "strlen": {
                "run_func": string.StrLenMod(_c)
            },
            "str_replace": {
                "run_func": string.StrReplaceMod(_c)
            },
            "substr": {
                "run_func": string.SubstrMod(_c)
            },
            "nl2br": {
                "run_func": string.Nl2BrMod(_c)
            },
            "session_start": {
                "run_func": session.SessionStartMod(_c)
            },
            "session_destroy": {
                "run_func": session.SessionDestroyMod(_c)
            },
            "redirect": {
                "run_func": redirect.RedirectMod(_c)
            },

            **db.build_funcs(_c),
            **primitives.build_funcs(_c),

            
            "require_once": {
                "run_func": RequireOnceMod(_c)
            },
            "use": {
                "run_func": UseMod(_c)
            },
            "public": {
                "run_func": PublicMod(_c)
            },
            "private": {
                "run_func": PrivateMod(_c)
            },
            "protected": {
                "run_func": ProtectedMod(_c)
            }
        })
        c = _c.new_instance(
            namespace='main',
            sync="b"
        )
        c.create_variable(
            "_SERVER",
            Request,
            Request()
        )
        c.run(ast)
        return '\n'.join([str(el) for el in c.finished]) + "\n" + html
        
    
    def register(self, route, file):
        def _func(*args, **kwargs):
            _c = Compiler([])
            out = self.build_sp(file, _c)
            return out
        
        name = f"_func_" + str(random.randint(0,9999))
        while name in self.functions:
            name = f"_func_" + str(random.randint(0,9999))


        _func.__name__ = _func.__qualname__ = name

        setattr(self, name, _func)
        print("Adding", _func.__name__, route)
        self.app.route(route, methods=['GET', 'POST'])(getattr(self, name))
        
        
app = SpindleApp()
app.app.secret_key = config['secret_key'] if "secret_key" in config else ""
app.app.url_map.strict_slashes = False

for route in config['routes']:
    app.register(
        route,
        config['routes'][route]
    )

if __name__ == "__main__":
    app.app.run(host='127.0.0.1', port=8000, debug=True)