from copy import deepcopy
import inspect
import pprint
import re

from .exceptions import ModuleExceptions, TranspilerExceptions, RuntimeExceptions, Warn
from .module import Module
from nophp.splitter import split_php

from .lexer import PyettyLexer
from .pparser import PyettyParser
from .types import *
pprint = pprint.PrettyPrinter(indent=2).pprint
from rich.console import Console
from rich.syntax import Syntax
console = Console()

def rprint(data):
    console.print(
        Syntax(
            str(data),
            "Python", 
            padding=1, 
            line_numbers=True
        )
    )

class ConcatMod(Module):
    name="CONCAT"
    type = Module.MODULE_TYPES.ACTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        first, second = tree['0'], tree['1']

        supported_types = {
            ID,
            String,
            Int32,
            Bool,
            Auto,
            Nil
        }

        print(self.compiler_instance.namespace)

        first_resolved = resolution_module(first)
        second_resolved = resolution_module(second)


        # Todo: Legacy, remove as it's not used and may cause issues
        if type(first_resolved) == str: first_resolved = String(first_resolved)
        if type(second_resolved) == str: second_resolved = String(second_resolved)

        if type(first_resolved) not in supported_types or\
              type(second_resolved) not in supported_types:
            # Invalid type
            raise TranspilerExceptions.Generic(f"Not Implemented: {first_resolved} {second_resolved} Only supports: {supported_types}")
        
        first_value = ""
        if type(first_resolved) == ID:
            first_var: BasicType  = self.compiler_instance.get_variable(first_resolved.value)

            if first_var["type"] not in [String, Int32, Bool, Auto, Nil]:
                # Invalid type
                raise TranspilerExceptions.Generic(f"Expected an ID() of String() type, got {first_var['type'].__name__}()")
            
            first_value = first_var["object"].value
        elif type(first_resolved) == String:
            first_value = first_resolved.value
        elif type(first_resolved) ==  Int32:
            first_value = f"\"{first_resolved.value}\""
        elif type(first_resolved) == Auto:
            first_value = first_resolved.value


        second_value = ""
        if type(second_resolved) == ID:
            second_var: BasicType  = self.compiler_instance.get_variable(second_resolved.value)

            if second_var["type"] not in [String, Int32, Bool, Auto, Nil]:
                # Invalid type
                raise TranspilerExceptions.Generic(f"Expected an ID() of String() type, got {second_var['type'].__name__}()")
        
            second_value = second_var["object"].value
        elif type(second_resolved) == String:
            second_value = second_resolved.value
        elif type(second_resolved) ==  Int32:
            second_value = f"\"{second_resolved.value}\""
        elif type(second_resolved) == Auto:
            second_value = second_resolved.value

        return String(self.remove_quotes(first_value) + self.remove_quotes(second_value))

class PhpMod(Module):
    name="PHP"
    type = Module.MODULE_TYPES.NON_WRITEABLE

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        console.log("[PHP] triggered SP (single page) build.")

        # Match actions through local scope
        self.compiler_instance.run(
            tree['PROGRAM']
        )

class HTMLMod(Module):
    name="HTML"
    type = Module.MODULE_TYPES.SPECIAL_ACTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

        self.tag = ""
        self.attrs = {}

        from html.parser import HTMLParser
        from html.entities import name2codepoint

        class MyHTMLParser(HTMLParser):
            def __init__(self, host, convert_charrefs: bool = True) -> None:
                super().__init__(convert_charrefs=convert_charrefs)
                self.host = host
            def handle_starttag(self, tag, attrs):
                # print("Start tag:", tag)
                self.host.tag = tag
                for attr in attrs:
                    # print("     attr:", attr)
                    self.host.attrs[attr[0]] = attr[1]
        

        self.parser = MyHTMLParser(self)

    def proc_tree(self, tree):
        # pprint("[HTML] triggered simplified HTML build.")

        self.tag = ""
        self.attrs = {}

        if len(tree['PROGRAM']) == 0:
            value = ""
        elif tree['PROGRAM'][0] == 'HTML':
            
            value = self.__class__(self.compiler_instance)(tree['PROGRAM'][1])
        # Not sure if ths should be deleted,
        # it used to handle the ID's and etc, but shouldn't be viable anymore
        # as we can just use the RESOLUT for this
        #
        # elif tree['PROGRAM'][0] == 'ID':
        #     # Get value
        #     value = self.compiler_instance.get_variable(tree['PROGRAM'][1]['VALUE'])['object'].value
        # else:
        #     value = tree['PROGRAM'][1]['VALUE']
        else:
            obj = self.compiler_instance.get_action("RESOLUT")(tree['PROGRAM'])

            if type(obj) == String:
                # format string
                value = self.remove_quotes(obj.value)
            elif type(obj) == ID:
                value = self.remove_quotes(self.compiler_instance.get_variable(obj.value)['object'].value)
            elif obj is None:
                # Resolution returned None?
                raise TranspilerExceptions.Generic("Failed to parse")
            elif type(obj) == str: # TODO: Legacy
                value = obj
            else: value = obj.value


        # Check if it's a php call
        start = tree['LABEL']['START'] if tree['LABEL']['START'] is not None else ""
        end = tree['LABEL']['END'] if tree['LABEL']['END'] is not None else ""

        # Test parse of the start
        self.tag = ""
        self.attrs = {}
        self.parser.feed(start)
        # print(self.tag)
        # print(self.attrs)
        
        if self.attrs != {}:
            final = []
            # parse content of the attribute
            for attr in self.attrs:
                if self.attrs[attr] is None:
                    raise TranspilerExceptions.Generic(f"Invalid HTML at tag {self.tag}")
                if self.attrs[attr].startswith('$'):
                    code = f"echo {self.attrs[attr]}"
                    lexer = PyettyLexer()
                    parser = PyettyParser()
                    ast = parser.parse(lexer.tokenize(code))

                    instance = self.compiler_instance.new_instance(
                        tree=ast,
                        sync="advanced"
                    )
                    instance.run()
                    out = ''.join(instance.finished)
                    final.append(f"{attr}=\"{out}\"")
                else:
                    final.append(f"{attr}=\"{self.attrs[attr]}\"")
            start = f"<{self.tag} {' '.join(final)}>"

        # Todo: Legacy
        if type(value) == String:
            value = self.remove_quotes(value.value)

        return String(start + str(value) + end)
    
class NamespaceMod(Module):
    name="NAMESPACE"
    type = Module.MODULE_TYPES.SPECIAL_ACTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        # print(tree)
        name = tree['ID']

        if name in self.compiler_instance.namespaces:
            # Continue using the namespace
            pass
        else:
            self.compiler_instance.namespace = name

            self.compiler_instance.namespaces[name] = self.compiler_instance


class NamespaceMemberMod(Module):
    name="NAMESPACE_MEMBER"
    type = Module.MODULE_TYPES.SPECIAL_ACTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        # TODO: This will at some point need to loop over every namespace entry
        namespace = tree["NAMESPACE"]
        member = tree["MEMBER"]

        if namespace in self.compiler_instance.namespaces:
            ns = self.compiler_instance.namespaces[namespace]
        else:
            raise TranspilerExceptions.NamespaceNotFound(namespace, self.compiler_instance.namespaces)
        
        # TODO: Add Classes, other namespaces
        if member in ns.functions:
            return sInnerMut("namespace_member_func", member, ns.functions[member])
        if member in ns.classes:
            return sInnerMut("namespace_member_class", member, ns.classes[member])
        else:
            raise TranspilerExceptions.UnkownMethodReference(member, list(ns.functions.keys()))


class UseMod(Module):
    name="USE_FUNC"
    type = Module.MODULE_TYPES.NON_WRITEABLE

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, _):
        Warn("Use is obsolete in NoPHP, the namespace was autoloaded, skipping.")

class RequireOnceMod(Module):
    name="REQUIRE_ONCE"
    type = Module.MODULE_TYPES.NON_WRITEABLE

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        values = []

        console.log("[red]<===>[/red] Require Once")

        if len(tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS']) > 1:
            raise TranspilerExceptions.TooManyValues(values, "require_once($_path)")
        

        for var in tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS']:
            resolved = resolution_module(var)
            value: BasicType = None
            
            if type(resolved) == ID:
                value = resolved.value
                v = self.compiler_instance.get_variable(value)
                if v["type"] == String:
                    value = self.remove_quotes(v['object'].value)
                elif v["type"] == type(None):
                    value = ""
                else:
                    value = v['object'].value
            elif type(resolved) == String:
                value = self.remove_quotes(resolved.value)
            

            values.append(value) 

        # Load file then lex and parse it
        tokens = None
        with open(value, "r") as f:
            text = f.read()
            php, html = split_php(text)

            lexer = PyettyLexer()
            parser = PyettyParser()

            tokens = parser.parse(
                lexer.tokenize(php)
            )


        old_nm = self.compiler_instance.namespace

        instance = self.compiler_instance.new_instance(
            namespace= value+"_sub",# Set namespace
            tree=tokens, # Load file here with lexer & parser
            sync="advanced"
        )

        instance.run()

        self.compiler_instance.namespace = old_nm

        self.compiler_instance.namespaces[
            instance.namespace
        ] = instance

        self.compiler_instance.write_back(
            instance
        )
        # self.compiler_instance.sync_variables(
        #     instance
        # )

        # Sync functions to own instance
        self.compiler_instance.sync_functions(
            instance
        )

        

class GetIndexMod(Module):
    name="GET_INDEX"
    type = Module.MODULE_TYPES.SPECIAL_ACTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        # pprint(tree)
        line = tree['LINE']
        name = resolution_module(tree['EXPRESSION'])
        index = resolution_module(tree['INDEX'])

        if type(index) == String:
            index_value = self.remove_quotes(index.value)
        else: index_value = index.value

        if type(name) == ID:
            var = self.compiler_instance.get_variable(name.value)
            if var['type'] == DynArray:
                if 0 <= index_value < var['object'].length:
                    return var['object'].value[index_value]
                else:
                    print(var['object'])
                    raise TranspilerExceptions.OutOfBounds(index_value, var['object'].length)
            # TODO: Session and Request types need to be compatible with printing out in echo
            elif var['type'] == Session:
                if index_value in var['object'].value:
                    # print("Session contains:",var['object'].value[index_value], type(var['object'].value[index_value]), var['object'].value)
                    return Auto(var['object'].value[index_value], "basic")
                else:
                    # print(f"Session does not contain {index_value}, it only contains: {list(var['object'].value.keys())}")
                    return Nil()
            elif var['type'] == Request:
                if index_value.lower() in var['object'].value.__dir__():
                    # print("Request contains:", getattr(var['object'].value, index_value.lower()), index_value.lower(), list(var['object'].value.__dir__()))
                    return Auto(getattr(var['object'].value, index_value.lower()), type="basic")
                else:
                    # print("Request contains:",list(var['object'].value.__dir__()))
                    return Nil()
            else:
                raise TranspilerExceptions.TypeMissmatch("Get ID Index Actor", var['type'], [ID, DynArray, Session, Request], line)
        elif type(name) == DynArray:
            if 0 <= index_value < name.length:
                return Auto(name.value[index_value], "basic")
            else:
                raise TranspilerExceptions.OutOfBounds(index_value, name.length)
            # raise TranspilerExceptions.Generic(f"{name.value}")
        elif type(name) == Auto:
            # This is dumb but assume we got passed some internal object right?
            from werkzeug.datastructures import ImmutableMultiDict
            if type(name.value) == ImmutableMultiDict:
                if index_value in name.value.to_dict():
                    return Auto(name.value.to_dict()[index_value], "basic")
                else:
                    # Not present
                    return Nil()
            elif type(name.value) == dict:
                if index_value in name.value:
                    return Auto(name.value[index_value], "basic")
                else:
                    return Nil()
            elif type(name.value) == Map:
                if index_value in name.value.value:
                    return Auto(name.value.value[index_value], "basic")
                else:
                    return Nil()
            elif type(name.value) == DynArray:
                if 0 <= index_value < name.value.length:
                    return Auto(name.value.value[index_value], "basic")
                else:
                    raise TranspilerExceptions.OutOfBounds(index_value, name.value.length)
            raise TranspilerExceptions.Generic(f"{name.value}")
        elif type(name) == Nil:
            return Nil()
        else:
            raise TranspilerExceptions.TypeMissmatch(f"Get Index Actor: {name}", type(name), [ID, DynArray], line)
        return Nil()

class SetIndexMod(Module):
    name="SET_INDEX"
    type = Module.MODULE_TYPES.SPECIAL_ACTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        # pprint(tree)
        # exit()
        line = tree['ID'][-1]
        name = resolution_module(tree['ID'][1]['EXPRESSION'])
        index = resolution_module(tree['ID'][1]['INDEX'])
        value = resolution_module(tree['EXPRESSION'])

        if type(index) == String:
            index_value = self.remove_quotes(index.value)
        else: index_value = index.value

        if type(value) == String:
            value = self.remove_quotes(value.value)
        

        if type(name) == ID:
            var = self.compiler_instance.get_variable(name.value)
            if var['type'] == DynArray:
                if 0 <= index_value < var['object'].length:
                    var['object'].value[index_value] = value
                else:
                    raise TranspilerExceptions.OutOfBounds(index_value, var['object'].length)
            elif var['type'] == Session:
                # print("Session contains:",var['object'].value[index_value], type(var['object'].value[index_value]))
                var['object'].value[index_value] = value.value
            else:
                raise TranspilerExceptions.TypeMissmatch("Get ID Index Actor", var['type'], [ID, DynArray], line)
        elif type(name) == DynArray:
            raise TranspilerExceptions.NotImplemented
        elif type(name) == Auto:
            if type(name.value) == dict:
                name.value[index_value] = value
            elif type(name.value) == Map:
                name.value.value[index_value] = value
            else:
                raise TranspilerExceptions.Generic(f"{name.value} is not a map.")
        else:
            raise TranspilerExceptions.TypeMissmatch(f"Get Index Actor '{name}'", type(name), [ID, DynArray], line)
        
class ResolutionMod(Module):
    name="RESOLUT"
    type = Module.MODULE_TYPES.ACTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance
    
    def proc_tree(self, tree):
        #pprint(tree)
        
        if tree[0] == 'STRING':
            return String(tree[1]['VALUE'])

        if tree[0] == 'FORMATTED_STRING':
            pattern = re.compile(r":\$(\w+):")
            text = tree[1]['VALUE']

            def replace(match):
                variable_name = match.group(1)
                value = self.compiler_instance.get_variable(variable_name)['object']
                
                return self.safely_resolve(value.value)

            result = pattern.sub(replace, text)
            return String(result)

        elif tree[0] == 'INT':
            return Int32(tree[1]['VALUE'])
        
        elif tree[0] == 'NEG':
            return Int32(-(self(tree[1]).value))

        elif tree[0] == 'FLOAT':
            return Float(tree[1]['VALUE'])
        
        elif tree[0] == 'BOOL':
            return Bool(tree[1]['VALUE'])

        elif tree[0] == 'HEX':
            return HexInt32(tree[1]['VALUE'])
        
        elif tree[0] == 'Nil':
            return Nil(0)
        
        elif tree[0] == 'NULL':
            return Nil(0)

        elif tree[0] == 'CHAR':
            # if the actual type is string, there will be an array in place of the value
            if type(tree[1]['VALUE']) == tuple:
                return Char(tree[1]['VALUE'][0])
            else:
                return Char(tree[1]['VALUE'])
            
        elif tree[0] == 'ARRAY':
            return DynArray(tree[1]['ITEMS'], type=List.BONE)
        
        elif tree[0] == 'ARRAY_FILLED':
            items = [self.proc_tree(item) for item in tree[1]['ITEMS']]
            return DynArray(items, type=List.GUESS)
        
        elif tree[0] == 'MAP':
            if len(tree[1]['ITEMS']) == 0:
                items = dict()
            else:
                raise TranspilerExceptions.NotImplemented
            return Map(items)

        elif tree[0] == 'ID':
            return ID(tree[1]['VALUE'])
        
        elif tree[0] == 'CONCAT':
            concat_module: Module = self.compiler_instance.get_action('CONCAT')
            return concat_module(tree[1])
        
        elif tree[0] == 'HTML':
            html_module: Module = self.compiler_instance.get_action("HTML")
            return html_module(tree[1])
        
        elif tree[0] == 'FUNCTION_CALL':
            stack = inspect.stack()

            # print("Resolution on", tree[1]['ID'], "by", f"{stack[2].filename}:{stack[2].lineno}")
            func_call_mod: Module = self.compiler_instance.get_action("FUNCTION_CALL")
            return func_call_mod(tree[1])
        
        elif tree[0] == 'NEW_OBJECT':
            new_object_mod: Module = self.compiler_instance.get_action("NEW_OBJECT")
            return new_object_mod(tree[1])
        
        elif tree[0] == 'GET_INDEX':
            get_index_mod: Module = self.compiler_instance.get_action("GET_INDEX")
            return get_index_mod(tree[1])
        
        elif tree[0] in {
            "ADD", "SUB", "MUL", "DIV"
        }:
            math_mod: Module = self.compiler_instance.get_action("MATH")
            return math_mod(tree)
        
        elif tree[0] == "NAMESPACE_MEMBER":
            NamespaceMemberMod: Module = self.compiler_instance.get_action("NAMESPACE_MEMBER")
            return NamespaceMemberMod(tree[1])
        
        elif tree[0] == "TARROW":
            TarrowMod: Module = self.compiler_instance.get_action("TARROW")
            return TarrowMod(tree[1])
        
        elif tree[0] == "FOREACH":
            ForeachMod: Module = self.compiler_instance.get_action("FOREACH")
            return ForeachMod(tree[1], no_construct=True)
        
        elif tree[0] in ["OR", "AND"]:
            BoolMod: Module = self.compiler_instance.get_action("BOOLMOD")
            return BoolMod(tree)

        raise Exception(f"[RESOLUT] Failed to match {tree} is '{tree[0]}' supported?")


class ClassDeclarationMod(Module):
    name="CLASS_DECLARATION"
    type = Module.MODULE_TYPES.ACTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # pprint(tree)
        extends = None
        source: list = []

        if "EXTENDS" in tree:
            # Check if the class exists
            extends = tree["EXTENDS"]

            if extends in self.compiler_instance.classes:
                # Get tree of the class, then we copy its code
                instance = self.compiler_instance.new_instance(
                    namespace=tree['ID']
                )
                source = list(self.compiler_instance.classes[extends]["source"])
                source.extend(tree['PROGRAM'])
                instance.run(source)
                extends = self.compiler_instance.classes[extends]['object']
            else:
                raise TranspilerExceptions.ClassNotFound(extends)

        else:

            # Create a new instance, it will track the functions and variables in its namespace
            instance = self.compiler_instance.new_instance(
                namespace=tree['ID'],
                tree=tree['PROGRAM']
            )
            source = tree['PROGRAM']
            instance.run()

        # Then Add this instance as a class template object, we can duplicate it later
        self.compiler_instance.create_class(
            name=tree['ID'],
            obj=instance,
            source=source,
            parent=extends
        )

        # print(
        #     instance.variables.keys()
        # )
        # input('c')

        console.log("[ClassMod] New class & scope created for \"{}\" ({})".format(tree['ID'], instance))

class NewObjectMod(Module):
    name="NEW_OBJECT"
    type = Module.MODULE_TYPES.ACTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # pprint(tree)
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        name = resolution_module(tree['ID'])
        arguments = tree['FUNCTION_ARGUMENTS']

        if type(name) == sInnerMut:
            clas = name.value[2]
            obj = self.compiler_instance.new_instance(
                    namespace=name.value[1] + "_obj",
                    sync="b"
                )
            obj.run(clas['source'])
        elif name.value in self.compiler_instance.classes:
            obj = self.compiler_instance.new_instance(
                    namespace=name.value + "_obj",
                    sync="b"
                )
            obj.run(self.compiler_instance.classes[name.value]["source"])
        else:
            raise TranspilerExceptions.ClassNotFound(name)

        # Call it's constructor
        if "__construct" in obj.functions:
            if 'POSITIONAL_ARGS' in arguments:
                parsed_args = [
                    resolution_module(arg)
                    for arg in arguments['POSITIONAL_ARGS']
                ]

                for i, arg in enumerate(obj.functions["__construct"]["arguments"]):
                    try:
                        v = parsed_args[i]
                    except IndexError as e:
                        print(parsed_args)
                        # raise TranspilerExceptions.OutOfBounds(i, len(parsed_args))
                        raise TranspilerExceptions.Generic(f"Too few arguments provided for constructor.\n\tGot:{parsed_args}\n\tExpected:{obj.functions["__construct"]["arguments"]}")

                    if type(v) == ID:
                        n = v.value
                        v = self.compiler_instance.get_variable(v.value)['object']
                    else: n = None

                    # print(n, v, self.compiler_instance.namespace)


                    obj.functions["__construct"]["object"].create_variable(
                        arg.value, 
                        type(v),
                        v,
                        force=True
                    )

            if obj.functions["__construct"]['level'] != "public" \
                and self.compiler_instance.namespace != obj.functions["__construct"]['object'].parent.namespace:
                raise TranspilerExceptions.Generic(f"Invalid access level on constructor of {obj.namespace}")

            func = obj.functions["__construct"]["run_func"]
            func()

            # pprint(obj.functions["__construct"]['object'].variables)

            self.compiler_instance.write_back(
                obj.functions["__construct"]['object']
            )
            # print(obj.variables)
            # print(obj.functions["__construct"]['object'].variables)
            # console.log("Ran constructor for \"{}\"\n{}".format(name, 
            #             self.compiler_instance.classes[name]["source"]))

        console.log("New object created for \"{}\"(...)".format(name))

        return obj



class FunctionDecMod(Module):
    name="FUNCTION_DECLARATION"
    type = Module.MODULE_TYPES.SPECIAL_ACTION_FUNC

    def __init__(self, compiler_instance):
        super().__init__()

        self.compiler_instance = compiler_instance
    
    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        line = tree['ID'][-1]

        funcname = tree['ID']
        arguments = tree['FUNCTION_ARGUMENTS']
        program  = tree['PROGRAM']
        returns  = tree['RETURNS_TYPE'][1]['VALUE'] if "RETURNS_TYPE" in tree else "any"

        types = {
            'int': Int32,
            'hex': HexInt32,
            'char': Char,
            'float': Float,
            'string': String,
            'void': Nil,
            'any': Any
        }

        # pprint(program)
        # exit()

        if arguments:
            arguments = [resolution_module(arg) for arg in arguments['POSITIONAL_ARGS']]
        
        console.log(f"[FunctionDecMod] {funcname}({arguments}) -> {returns} in {self.compiler_instance.namespace}")

        # Create a new instance, it will be filled with the function's tree
        instance = self.compiler_instance.new_instance(
            namespace=self.compiler_instance.namespace+"_"+funcname+"_ns",
            tree=program,
            sync = "object"
        )

        instance.parent = self.compiler_instance

        if 'LEVEL' in tree:
            if self.compiler_instance.namespace != 'main':
                level = tree['LEVEL']
            else:
                raise TranspilerExceptions.IncompleteDeclaration(f"Access levels are only allowed in classes, not {self.compiler_instance.namespace}")
        else: level = "public"

        # On call run the instance 
        # with injected locals for arguments
        #
        # instance.run()

        console.log(f"{funcname}(...) is built in '{self.compiler_instance.namespace}'")

        self.compiler_instance.create_function(
            funcname,
            instance,
            tree,
            types[returns],
            arguments=arguments,
            level = level 
        )


class FunctionCallMod(Module):
    name="FUNCTION_CALL"
    type = Module.MODULE_TYPES.SPECIAL_ACTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def run_sInnerMut(self, funcobj, arguments):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        if 'POSITIONAL_ARGS' in arguments:
            parsed_args = [
                resolution_module(arg)
                for arg in arguments['POSITIONAL_ARGS']
            ]
        else: parsed_args = []
        if funcobj.value[0] == "namespace_member_func":
            for i, arg in enumerate(funcobj.value[2]["arguments"]):
                try:
                    v = parsed_args[i]
                except IndexError as e:
                    raise TranspilerExceptions.OutOfBounds(f"{i}, {arg}, {parsed_args}", len(funcobj.value[2]["arguments"]))
        
                funcobj.value[2]['object'].create_variable(
                    arg.value, 
                    type(v),
                    v,
                    force=True
                )
                # print(v.value)
            # We are executing something from a different namespace
            # ("namespace_member_func", member, ns.functions[member])
            func = funcobj.value[2]["run_func"]
            # funcobj.value[2]['object'].stop = False
            func()
            self.compiler_instance.write_back(
                funcobj.value[2]['object']
            )
            ret = funcobj.value[2]['object'].returns
            exp = funcobj.value[2]['returns']

            if ret != Nil:
                if type(ret) == ID:
                    ret = funcobj.value[2]['object'].get_variable(ret.value)['object']
                if type(ret) != exp and exp != Any:
                    raise TranspilerExceptions.TypeMissmatchNL(f"{funcobj.value[1]}(...) return value", ret, exp)
                # print(ret.value)
                # input()
                return ret
        else:
            raise TranspilerExceptions.NotImplemented()

    def proc_tree(self, tree):
        # TODO: Simplify this
        #           - Move all expected return validation into a separate function
        #           - Parse args here instead of inside the function
        #           - Raise proper error when a parent doesnt exist
        

        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        done = None
        
        supported_types = {
            String,
            Nil,
            Int32,
            Float,
            Char,
            List,
            ID
        }

        if 'CLASS' in tree:
            # We assume it's part of a class
            #    {"FUNCTION_ARGUMENTS": p.function_arguments, "ID": p.ID1, "CLASS": p.ID0},
            cls = tree['CLASS']
            arguments = tree['FUNCTION_ARGUMENTS']
            funcname = tree['ID']
            funcobj = None
        else:
            # pprint(tree['ID'])
            # input()
            funcobj = resolution_module(tree['ID'])
            funcname = funcobj.value
            arguments = tree['FUNCTION_ARGUMENTS']
            cls = None

        if type(funcobj) != sInnerMut and funcname not in self.compiler_instance.builtin_functions:
            if 'POSITIONAL_ARGS' in arguments:
                parsed_args = [
                    resolution_module(arg)
                    for arg in arguments['POSITIONAL_ARGS']
                ]
            else: parsed_args = []

        console.log(f"[FunctionCallMod] {funcname}(...) from {cls}")

        if type(funcobj) == sInnerMut:
            return self.run_sInnerMut(funcobj, arguments)
        elif cls is not None:
            if cls == 'parent':
                function_parent = self.compiler_instance.parent
                class_parent    = function_parent.parent # grandad
                if class_parent is None:
                    raise TranspilerExceptions.ClassNotFound(f"None. This class does not contain a parent: {function_parent.namespace}")
                if funcname in class_parent.functions:
                    class_parent.functions[funcname]['run_func']()
                    # Sync back

                    self.compiler_instance.write_back(
                        class_parent.functions[funcname]['object']
                    )
                    ret = class_parent.functions[funcname]['object'].returns
                    exp = class_parent.functions[funcname]["returns"]
                    if ret != Nil:
                        if type(ret) != exp and exp != Any:
                            raise TranspilerExceptions.TypeMissmatch(f"{funcname}(...) return value", ret, exp, tree['ID'][-1])
                        done = ret
                else:
                    raise TranspilerExceptions.UnkownMethodReference(funcname, class_parent.functions)
                
            elif cls == 'this':
                function_parent = self.compiler_instance.parent

                if function_parent is None:
                    raise TranspilerExceptions.ClassNotFound(cls)
                
                if funcname in function_parent.functions:
                    function_parent.functions[funcname]['run_func']()
                    # Sync back

                    self.compiler_instance.write_back(
                        function_parent.functions[funcname]['object']
                    )
                    ret = function_parent.functions[funcname]['object'].returns
                    exp = function_parent.functions[funcname]["returns"]
                    if ret != Nil:
                        if type(ret) != exp and exp != Any:
                            raise TranspilerExceptions.TypeMissmatch(f"{funcname}(...) return value", ret, exp, tree['ID'][-1])
                        done = ret
                else:
                    raise TranspilerExceptions.UnkownMethodReference(funcname, function_parent.functions)

            elif cls in self.compiler_instance.variables:
                if funcname in self.compiler_instance.variables[cls]['object'].functions:
                    funcobj = self.compiler_instance.variables[cls]['object'].functions[funcname]

                    for i, arg in enumerate(self.compiler_instance.variables[cls]['object'].functions[funcname]["arguments"]):
                        try:
                            v = parsed_args[i]
                        except IndexError as e:
                            raise TranspilerExceptions.OutOfBounds(i, len(self.compiler_instance.variables[cls]['object'].functions[funcname]["arguments"]))

                        self.compiler_instance.variables[cls]['object'].functions[funcname]["object"].create_variable(
                            arg.value, 
                            type(v),
                            v,
                            force=True
                        )
                    # TODO: REMOVE
                    # print(self.compiler_instance.variables[cls]['object'].functions[funcname]["object"].namespace ,self.compiler_instance.variables[cls]['object'].functions[funcname]["object"].variables)
                    func = self.compiler_instance.variables[cls]['object'].functions[funcname]["run_func"]
                    # TODO: Check permission level
                    func()
                    self.compiler_instance.write_back(
                        self.compiler_instance.variables[cls]['object'].functions[funcname]['object']
                    )
                    ret = self.compiler_instance.variables[cls]['object'].functions[funcname]['object'].returns
                    exp = self.compiler_instance.variables[cls]['object'].functions[funcname]['returns']
                    # TODO: REMOVE
                    # print(funcname, ret)
                    if ret != Nil:
                        if type(ret) == ID:
                            # print(list(self.compiler_instance.variables[cls]['object'].functions[funcname]['object'].variables.keys()))
                            # input("vars.")
                            ret = self.compiler_instance.variables[cls]['object'].functions[funcname]['object'].get_variable(ret.value)['object']
                        if type(ret) != exp and exp != Any:
                            raise TranspilerExceptions.TypeMissmatchNL(f"{funcname}(...) return value", ret, exp)
                        done = ret
                else:
                    raise TranspilerExceptions.UnkownMethodReference(funcname, list(self.compiler_instance.variables[cls]['object'].functions.keys()), ns=self.compiler_instance.variables[cls]['object'].namespace)
            else:
                raise TranspilerExceptions.ClassNotFound(cls)
            
        elif funcname in self.compiler_instance.builtin_functions:
            done = self.compiler_instance.builtin_functions[funcname]["run_func"](tree)

        elif funcname in self.compiler_instance.functions:
            for i, arg in enumerate(self.compiler_instance.functions[funcname]["arguments"]):
                try:
                    v = parsed_args[i]
                except IndexError as e:
                    raise TranspilerExceptions.OutOfBounds(i, len(self.compiler_instance.functions[funcname]["arguments"]))

                self.compiler_instance.functions[funcname]["object"].create_variable(
                    arg.value, 
                    type(v),
                    v,
                    force=True
                )

            self.compiler_instance.functions[funcname]["run_func"]()
            # Sync back
            self.compiler_instance.write_back(
                self.compiler_instance.functions[funcname]["object"]
            )
            ret = self.compiler_instance.functions[funcname]["object"].returns
            exp = self.compiler_instance.functions[funcname]["returns"]
            if ret != Nil:
                if type(ret) != exp and exp != Any:
                    raise TranspilerExceptions.TypeMissmatch(f"{funcname}(...) return value", ret, exp, tree['ID'][-1])
                done = ret
        else:
            raise TranspilerExceptions.UnkownMethodReference(funcname, list(self.compiler_instance.functions.keys()), self.compiler_instance.namespace)
        
        return done


class ReturnMod(Module):
    name="RETURN"
    type = Module.MODULE_TYPES.ACTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance
    
    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        v = resolution_module(tree["EXPRESSION"])

        self.compiler_instance.returns = v
        self.compiler_instance.stop = True
        


class TarrowMod(Module):
    name="TARROW"
    type = Module.MODULE_TYPES.NON_WRITEABLE

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance
    
    def proc_tree(self, tree):
        # TODO: Add sometihng idk
        # TODO: Add parent
        if tree["FROM"] == "this":
            # print(self.compiler_instance.get_variable(tree["TO"])['object'])
            return self.compiler_instance.get_variable(tree["TO"])['object']
        elif tree["FROM"] in self.compiler_instance.variables:
            o = self.compiler_instance.get_variable(tree["FROM"])['object']
            # print(tree["TO"], o.get_variable(tree["TO"]), self.compiler_instance.namespace)
            return Auto(o.get_variable(tree["TO"])['object'], 'basic').value
        else:
            raise TranspilerExceptions.NotImplemented
        
class ClassAttrMod(Module):
    name="CLASS_ATTR"
    type = Module.MODULE_TYPES.NON_WRITEABLE

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        raise TranspilerExceptions.NotImplemented
    

### ACCESS LEVELS ###
# TODO: ACTUALLY IMPLEMENT THEM
class PublicMod(Module):
    name="public"
    type = Module.MODULE_TYPES.NON_WRITEABLE

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        varas_module: Module = self.compiler_instance.get_action('VARIABLE_ASSIGNMENT')

        # Create var :)))
        ntree = {}
        ntree['EXPRESSION'] = ["Nil"]
        ntree['ID'] = tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS'][0][1]['VALUE']

        varas_module(ntree)

class ProtectedMod(Module):
    name="protected"
    type = Module.MODULE_TYPES.NON_WRITEABLE

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        varas_module: Module = self.compiler_instance.get_action('VARIABLE_ASSIGNMENT')

        # Create var :)))
        ntree = {}
        ntree['EXPRESSION'] = ["Nil"]
        ntree['ID'] = tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS'][0][1]['VALUE']

        varas_module(ntree)


class PrivateMod(Module):
    name="private"
    type = Module.MODULE_TYPES.NON_WRITEABLE

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        varas_module: Module = self.compiler_instance.get_action('VARIABLE_ASSIGNMENT')

        # Create var :)))
        ntree = {}
        ntree['EXPRESSION'] = ["Nil"]
        ntree['ID'] = tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS'][0][1]['VALUE']

        varas_module(ntree)

###############################################################################################


class VariableAssignMod(Module):
    name="VARIABLE_ASSIGNMENT"
    type = Module.MODULE_TYPES.NON_WRITEABLE

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        expr = tree['EXPRESSION']
        var  = tree['ID']
        parent = tree['PARENT'] if 'PARENT' in tree else ""
        # We will need to guess the type from the expression we are given
        # vartype = tree['TYPE'] 


        resolved = resolution_module(expr)

        console.log(f"[VariableAssignMod] '{var}': guess -> {expr} to {resolved} in {self.compiler_instance.namespace}")

        while type(resolved) == ID:
            resolved = self.compiler_instance.get_variable(resolved.value)['object']

        if var not in self.compiler_instance.variables:
            # We create a new variable
            self.compiler_instance.create_variable(var, type(resolved), resolved)
        else:
            self.compiler_instance.create_variable(var, type(resolved), resolved, force=True)
        
        # No need to return anything here
        # The module is of type Non-Writeable



class MathMod(Module):
    name="MATH"
    type = Module.MODULE_TYPES.ACTION

    def __init__(self, compiler_instance):
        super().__init__()

        self.compiler_instance = compiler_instance

    def add(self, val1, val2):
        return val1.value + val2.value

    def sub(self, val1, val2):
        return val1.value - val2.value
    
    def mult(self, val1, val2): 
        return val1.value * val2.value

    def div(self, val1, val2): 
        return val1.value / val2.value
    
    def proc_tree(self, tree):
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        ops = {
            'ADD': self.add,
            'SUB': self.sub,
            'MUL': self.mult,
            'DIV': self.div
        }

        op = ops[tree[0]]

        # Process first and second value
        first = resolution_module(tree[1])
        second = resolution_module(tree[2])
        
        def atomize(val):
            if type(val) == ID:
                val = self.compiler_instance.get_variable(val.value)['object']
            return val
        
        first = atomize(first)
        second = atomize(second)

        return Int32(op(first, second))

class ConditionalMod(Module):
    name="CONDITIONAL"
    type = Module.MODULE_TYPES.SPECIAL_ACTION

    def __init__(self, compiler_instance):
        super().__init__()

        self.compiler_instance = compiler_instance

    def equal(self, val1, val2):
        return self.remove_quotes(val1) == self.remove_quotes(val2)

    def nequal(self, val1, val2):
        return not self.equal(val1, val2)
    
    def less(self, val1, val2): 
        return self.remove_quotes(val1) < self.remove_quotes(val2)

    def greater(self, val1, val2): 
        return self.remove_quotes(val1) > self.remove_quotes(val2)
    
    def function_call(self, tree):
        func_module: Module = self.compiler_instance.get_action('FUNCTION_CALL')
        res = func_module(tree)
        return res.value
    
    def or_adv_bool(self, val1, val2):
        return val1 or val2
    
    def and_adv_bool(self, val1, val2):
        return val1 and val2
    
    def proc_tree(self, tree):
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        if_condition = tree['IF'][1]['CONDITION']
        if_program = tree['IF'][1]['CODE']
        else_pr = None if tree["ELSE"][0] is None else tree["ELSE"]

        conditionals = {
            'EQEQ': self.equal,
            'NOT_EQEQ': self.nequal,
            'LESS': self.less,
            'GREATER': self.greater,
            'FUNCTION_CALL': self.function_call,
            'OR': self.or_adv_bool,
            'AND': self.and_adv_bool
        }


        # Resolve condition
        condition = conditionals[if_condition[0]]


        if if_condition[0] != 'FUNCTION_CALL':
            # Process first and second value
            first = resolution_module(if_condition[1])
            second = resolution_module(if_condition[2])

            def atomize(val):
                if type(val) == ID:
                    val = atomize(self.compiler_instance.get_variable(val.value)['object'])
                elif type(val) in [Int32, String, Bool, Float] :
                    val = val.value
                elif type(val) == Auto:
                    val = atomize(val.value)
                else:
                    print(type(val))
                return val

            first = atomize(first)
            second = atomize(second)

            # Evaluate condition and run it's code
            c = condition(first, second)
            # print(c, self.remove_quotes(first), self.remove_quotes(second), if_condition[0])
        else:
            c = condition(if_condition[1])
            # print(c)
        if c:
            self.compiler_instance.run(if_program)
        else:
            if else_pr is not None:
                self.compiler_instance.run(else_pr[1]['CODE'])

class BoolMod(Module):
    name="BOOLMOD"
    type = Module.MODULE_TYPES.SPECIAL_ACTION

    def __init__(self, compiler_instance):
        super().__init__()

        self.compiler_instance = compiler_instance
    
    def proc_tree(self, tree):
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        conditional_module: Module = self.compiler_instance.get_action('CONDITIONAL')
        empty: Module = self.compiler_instance.get_action('empty') # Actually a function

        pprint(tree)
        op = tree[0]
        first = tree[1]
        second = tree[2]

        if op == 'AND':
            return empty((first,)).value and empty((second,)).value
        elif op == 'OR':
            return empty((first,)).value or empty((second,)).value
        else:
            raise TranspilerExceptions.NotImplemented

        quit()


class WhileMod(Module):
    name="WHILE"
    type = Module.MODULE_TYPES.ACTION

    def __init__(self, compiler_instance):
        super().__init__()

        self.compiler_instance = compiler_instance

    
    def proc_tree(self, tree):
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        conditional_module: Module = self.compiler_instance.get_action('CONDITIONAL')

        if_condition = tree['CONDITION']
        if_program = tree['PROGRAM']


        conditionals = {
            'EQEQ': conditional_module.equal,
            'NOT_EQEQ': conditional_module.nequal,
            'LESS': conditional_module.less,
            'GREATER': conditional_module.greater
        }


        # Resolve condition
        condition = conditionals[if_condition[0]]

        # Process first and second value
        first = resolution_module(if_condition[1])
        second = resolution_module(if_condition[2])
        
        def atomize(val):
            if type(val) == ID:
                val = self.compiler_instance.get_variable(val.value)['object']
            return val
        
        first_val = atomize(first)
        second_val = atomize(second)


        # Evaluate condition and run it's code
        while condition(first_val, second_val):
            self.compiler_instance.run(if_program)

            # Get vars again
            first_val = atomize(first)
            second_val = atomize(second)
    

class ForEachMod(Module):
    name="FOREACH"
    type = Module.MODULE_TYPES.ACTION

    def __init__(self, compiler_instance):
        super().__init__()

        self.compiler_instance = compiler_instance

    
    def proc_tree(self, tree):
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        iterable = resolution_module(tree['ITERABLE'])
        variable = resolution_module(tree['VARIABLE'])

        line = tree['ITERABLE'][-1]

        finished = []

        program = tree['PROGRAM']

        if type(iterable) == ID:
            var = self.compiler_instance.get_variable(iterable.value)

            if var['type'] == DynArray:
                for value in var['object'].value:
                    # Inject value as the variable
                    

                    instance = self.compiler_instance.new_instance(
                        tree=program,
                        sync="advanced"
                    )

                    instance.create_variable(
                        variable.value,
                        type(value),
                        value,
                        force = True
                    )

                    instance.run()

                    if self.no_construct:
                        finished.append(
                            ''.join(instance.finished)
                        )
                    else:
                        self.compiler_instance.write_back(
                            instance
                        )
                    self.compiler_instance.sync(instance)

            else:
                raise TranspilerExceptions.TypeMissmatch(f"Get ID Index Actor {var['object']}", var['type'], [ID, DynArray], line)
        
        elif type(iterable) == DynArray:
            raise TranspilerExceptions.NotImplemented
        
        else:
            raise TranspilerExceptions.TypeMissmatch("Get Index Actor", type(iterable), [ID, DynArray], line)
        
        if self.no_construct:
            return String(''.join(finished))

class InternalMod(Module):
    name="INTERNAL_CALL"
    type = Module.MODULE_TYPES.SPECIAL_ACTION

    def __init__(self, compiler_instance):
        super().__init__()

        self.compiler_instance = compiler_instance

    def panic(
        self,
        line
    ):
        raise RuntimeExceptions.Panic("Runtime panic. This panic was propagated by an explicit call.",
                                      line=line)
    
    def namespace(self, line):
        return print(self.compiler_instance.namespace)
    
    def die(self, line):
        self.compiler_instance.stop = True
    
    def proc_tree(self, tree):
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')

        value = resolution_module(tree['VALUE'])

        calls = {
            "panic": self.panic,
            "nm": self.namespace,
            "die": self.die
        }

        if value.value in calls:
            return calls[value.value](tree['VALUE'][-1])
        else:
            raise TranspilerExceptions.NotImplemented

        # Hardcode some features for now
        