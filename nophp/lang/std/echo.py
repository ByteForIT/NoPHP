from ..compiler import Compiler
from ..exceptions import TranspilerExceptions
from ..module import Module
from ..types import *

class EchoMod(Module):
    name="echo"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        values = []

        # print(tree)

        for var in tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS']:
            v = resolution_module(var)
            value: BasicType = None
            
            if type(v) == ID:
                value = v.value
                v = self.compiler_instance.get_variable(value)
            else:
                v = {
                    "object": v,
                    "type": type(v)
                    }
                
            if v["type"] == String:
                value = self.remove_quotes(v['object'].value)
            elif v["type"] == type(None):
                value = ""
            elif v['type'] == Session:
                value = str(dict(v["object"].value))
            elif v['type'] == Auto:
                value = str(v['object'].value)
            elif type(v) == String:
                value = self.remove_quotes(v.value) # TODO: ADD class instance type
            elif isinstance(v['object'],Compiler):
                value = f"{v['object'].namespace}()"
            else:
                print(f"No known type {v['type']}")
                value = v['object']

            

            values.append(value) 

        if len(values) > 1:
            raise TranspilerExceptions.TooManyValues(values, "echo($msg)")

        return str(value)
