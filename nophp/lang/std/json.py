import base64
from ..exceptions import TranspilerExceptions, Warn
from ..module import Module
from ..types import *
from ..compiler import Compiler
from json import dumps
from flask import jsonify

class CommonJSONMod(Module):
    name="COMMONJSON"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def base(self, tree, ref=False):
        values = []

        if 'FUNCTION_ARGUMENTS' not in tree:
            # Advanced handling
            for var in tree:
                value = self.ref_resolve(var) if ref else self.safely_resolve(var)
                values.append(value)
        else:
            if 'POSITIONAL_ARGS' in tree['FUNCTION_ARGUMENTS']:
                for var in tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS']:

                    value = self.ref_resolve(var) if ref else self.safely_resolve(var)

                    values.append(value)

        return values


# json_encode($value) -> Map($value.__attrs)
class JSONEncodeMod(CommonJSONMod):
    name="json_encode"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values = self.base(tree)
        # We optimally want to extract the attributes of the 
        # object which will be value[0].
        # An object (Compiler obj) has the local variables
        # stored in self.variables, which makes it less than
        # optimal to get the attributes. Due to this, we will
        # grab all it's functions that are in the form of "get<N?>"
        # i.e. getters.
        attrs = {}
        obj = values[0] 
        if type(obj) == Compiler:
            for func in obj.functions:
                if func[:3].lower() == 'get':
                    # add their return values to our tracker
                    obj.functions[func]["run_func"]() 
                    attrs[func[3:].lower()] = obj.functions[func]["object"].returns
            return Map(attrs)
        elif type(obj) == list:
            return dumps(obj)
        elif type(obj) == dict:
            return dumps(obj)
        else:
            raise TranspilerExceptions.Generic(f"Couldn't convert {obj} to JSON")

    
_MODS = {
    "json_encode": JSONEncodeMod,
}

def build_funcs(c):
    functions = {}
    for f in _MODS:
        functions[f] = {
                "run_func": _MODS[f](c)
            }
    return functions