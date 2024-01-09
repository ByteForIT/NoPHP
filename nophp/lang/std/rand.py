import random
from ..exceptions import TranspilerExceptions, Warn
from ..module import Module
from ..types import *


class RandMod(Module):
    name="rand"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        values = []

        # Support weird ass calls
        if tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS'][0][0] == "ARRAY_FILLED":
            tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS'] = tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS'][0][1]['ITEMS']

        for var in tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS']:
            resolved = resolution_module(var)
            value: BasicType = None
            
            if type(resolved) == ID:
                value = resolved.value
                v = self.compiler_instance.get_variable(value)
                if v["type"] == Int32:
                    value = v['object'].value
                else:
                    raise TranspilerExceptions.TypeMissmatch(value, type(value), Int32, var[-1])
            elif type(resolved) == Int32:
                    value = resolved.value
            else:
                raise TranspilerExceptions.TypeMissmatch(resolved, type(resolved), Int32, var[-1])
            

            values.append(value) 

        if len(values) > 2:
            raise TranspilerExceptions.TooManyValues(values, "rand($min, $mix)")
        elif len(values) < 2:
            Warn("Too few values to satisfy 'rand'. Max will default to 2147483647")

        
        return Int32(random.randint(int(values[0]), int(values[1]) if len(values)>1 else 2147483647))
