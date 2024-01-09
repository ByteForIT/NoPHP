from ..exceptions import TranspilerExceptions, Warn
from ..module import Module
from ..types import *

# Courtesy of AlejandroVD at StackOverflow
def htmlspecialchars(text):
    return (
        text.replace("&", "&amp;").
        replace('"', "&quot;").
        replace("<", "&lt;").
        replace(">", "&gt;")
    )


class HTMLSpecialCharMod(Module):
    name="htmlspecialchars"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        values = []

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

        if len(values) > 1:
            raise TranspilerExceptions.TooManyValues(values, "echo($msg)")
        


        return htmlspecialchars(str(value))
