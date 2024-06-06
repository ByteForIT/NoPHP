from copy import deepcopy
from ..exceptions import TranspilerExceptions, Warn
from ..module import Module
from ..types import *


class CommonMod(Module):
    name="COMMON"
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
    

# TODO: What is this for??? it's been a month since I wrote this??
# set_session($key, $value) -> <remembers value for the session>
class SetSessionMod(CommonMod):
    name="set_session"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values = self.base(tree)

        # TODO: Check if enough arguments are passed
        
        key = values[0]
        value = values[1]

        pass
    
    
_MODS = {
    "set_session": SetSessionMod,
}

def build_funcs(c):
    functions = {}
    for f in _MODS:
        functions[f] = {
                "run_func": _MODS[f](c)
            }
    return functions