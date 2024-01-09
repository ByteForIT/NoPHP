from ..exceptions import TranspilerExceptions, Warn
from ..module import Module
from ..types import *

class RedirectMod(Module):
    name="redirect"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        values = []

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
                value = self.remove_quotes(String(v['object'].value).value)
            elif type(v) == String:
                value = self.remove_quotes(v.value)
            else:
                print(f"No known type {v['type']}")
                value = v['object'].value

            

            values.append(value) 

        if len(values) > 1:
            raise TranspilerExceptions.TooManyValues(values, "redirect($msg)")
        


        return String(f'<meta http-equiv="refresh" content="0;url={values[0]}">')
