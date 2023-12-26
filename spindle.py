from flask import Flask
# Lang
from lang.compiler import Compiler
from lang.lexer import PyettyLexer
from lang.pparser import PyettyParser
from splitter import split_php

# Load modules
from lang.modules import (
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
    PublicModMod,
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
from lang.std import (
    echo,
    rand
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



    def build_sp(self, file, _c):
        text = open(file,"r").read()
        php, html = split_php(text)
        toks = self.lexer.tokenize(
            php
        )
        ast = self.parser.parse(toks)



        _c.populate_modules_actions(
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
        _c.builtin_functions = {
            # Fake internals as functions
            "echo": {
                "run_func": echo.EchoMod(_c)
            },
            "rand": {
                "run_func": rand.RandMod(_c)
            },
            "require_once": {
                "run_func": RequireOnceMod(_c)
            },
            "use": {
                "run_func": UseMod(_c)
            },
            "public": {
                "run_func": PublicModMod(_c)
            },
        }
        c = _c.new_instance(
            namespace='main',
            sync="b"
        )
        c.run(ast)
        return '\n'.join([str(el) for el in c.finished]) + "\n" + html
        
    
    def register(self, route, file):
        @self.app.route(route)
        def _func():
            _c = Compiler([])
            out = self.build_sp(file, _c)
            
            return out
        


app = SpindleApp()



for route in config['routes']:
    app.register(
        route,
        config['routes'][route]
    )

if __name__ == "__main__":
    app.app.run(host='127.0.0.1', port=8000, debug=True)
