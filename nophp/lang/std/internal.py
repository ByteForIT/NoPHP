from ..exceptions import TranspilerExceptions, Warn
from ..module import Module
from ..types import *
from importlib.metadata import version

class CommonInternalMod(Module):
    name="COMMONINTERNAL"
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


# nophp_version() -> String($_version)
class VersionInfo(CommonInternalMod):
    name="nophp_version"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        
        v = version("nophp")
        return String(v)
    
# die
class NoPHPDie(CommonInternalMod):
    name="die"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        # Mirror functionality of INTERNAL_CALL(die)
        self.compiler_instance.stop = True
    
_MODS = {
    "nophp_version": VersionInfo,
    "die": NoPHPDie
}

def build_funcs(c):
    functions = {}
    for f in _MODS:
        functions[f] = {
                "run_func": _MODS[f](c)
            }
    return functions