from cmath import inf
import os
import random
from flask import Flask, jsonify, send_file, send_from_directory
# Lang
from .lang.compiler import Compiler
from .lang.lexer import PyettyLexer
from .lang.pparser import PyettyParser
from .lang.types import Request
from .splitter import split_php

import json as _json

# Load modules
from .lang.modules import (
    BoolMod,
    ConditionalMod,
    ForEachMod,
    GetIndexMod,
    IncludeMod,
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
    db,
    bcrypt,
    json,
)

# Read wool config
# from sys import argv
import argparse

import yaml
from yaml import Loader

parser = argparse.ArgumentParser(
    prog='NoPHP server',
    description='NoPHP Spindle server',
    epilog='Write Fast. Write More. Write NoPHP.')

parser.add_argument('filename')  
parser.add_argument('-o', '--host', default='localhost')
parser.add_argument('-p', '--port', default=8000)
parser.add_argument('-d', '--debug', action='store_true')

args = parser.parse_args()
host = args.host
port = int(args.port)
debug = args.debug
conf = args.filename

config = yaml.load(open(conf,"r"), Loader)

# Consts
BIGGEST_PAGES = 9_999_999_999

class SpindleApp:
    def __init__(self) -> None:
        self.app = Flask(__name__)
        self.lexer = PyettyLexer()
        self.parser = PyettyParser()

        self.functions = {}



    def build_sp(self, file, _c: Compiler):
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
            **bcrypt.build_funcs(_c),
            **json.build_funcs(_c),
            
            "require_once": {
                "run_func": RequireOnceMod(_c)
            },
            "include": {
                "run_func": IncludeMod(_c)
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
        c: Compiler = _c.new_instance(
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
        global BIGGEST_PAGES
        def _func(*args, **kwargs):
            _c = Compiler([])
            out = self.build_sp(file, _c)
            return out
        
        name = f"_func_" + str(random.randint(0,BIGGEST_PAGES))
        while name in self.functions:
            name = f"_func_" + str(random.randint(0,BIGGEST_PAGES))


        _func.__name__ = _func.__qualname__ = name

        setattr(self, name, _func)
        print("Adding", _func.__name__, route)
        self.app.route(route, methods=['GET', 'POST'])(getattr(self, name))


    def register_static(self, route, file):
        global BIGGEST_PAGES
        def _func(path):
            print(file, path)
            return send_file(
                os.path.join(
                    os.getcwd(),
                    os.path.join(file, path)
                )
            )
        
        name = f"_sfunc_" + str(random.randint(0,BIGGEST_PAGES))
        while name in self.functions:
            name = f"_sfunc_" + str(random.randint(0,BIGGEST_PAGES))

        _func.__name__ = _func.__qualname__ = name

        setattr(self, name, _func)
        print("Adding", _func.__name__, route, file)
        self.app.route(route)(getattr(self, name))

    def register_json(self, route, file):
        global BIGGEST_PAGES
        def _func(*args, **kwargs):
            _c = Compiler([])
            out = self.build_sp(file, _c)
            return jsonify(_json.loads(out))
        
        name = f"_jfunc_" + str(random.randint(0,BIGGEST_PAGES))
        while name in self.functions:
            name = f"_jfunc_" + str(random.randint(0,BIGGEST_PAGES))

        _func.__name__ = _func.__qualname__ = name

        setattr(self, name, _func)
        print("Adding", _func.__name__, route, file)
        self.app.route(route)(getattr(self, name))
        
    def run(self):
        global host, port
        self.app.run(host=host, port=port, debug=debug)
        
app = SpindleApp()
app.app.secret_key = config['secret_key'] if "secret_key" in config else ""
app.app.url_map.strict_slashes = False

for route in config['routes']:
    app.register(
        route,
        config['routes'][route]
    )
    
# if static routes need to be defined, enable them
if 'static' in config:
    for route in config['static']:
        app.register_static(
            route,
            config['static'][route]
        )

if 'json' in config:
    for route in config['json']:
        app.register_json(
            route,
            config['json'][route]
        )

print(app.app.url_map)

if __name__ == "__main__":
    print("Starting on {host}:{port}".format(host=host, port=port))
    app.run(host=host, port=port, debug=debug)