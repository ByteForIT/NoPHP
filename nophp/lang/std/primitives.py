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
    


# count($value) -> len($value)
class CountMod(CommonMod):
    name="count"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values = self.base(tree)

        return Int32(len(values[0]))
    
# empty($value)
class EmptyMod(CommonMod):
    name="empty"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        value = self.base(tree)[0]

        emptiness = value is None or value == "" or value == [] or value == {} or value == set()

        return Bool(emptiness)

# For arrays
# array()
class ArrayMod(CommonMod):
    name="array"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        Warn("It is discouraged to use array(), instead construct an empty array via []")
        return DynArray([])


# array_push($array, $value)
class ArrayPushMod(CommonMod):
    name="array_push"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        array, value = self.base(tree, ref=True)[:2]

        array.value.append(value)

        return Bool(True)
    
_MODS = {
    "count": CountMod,
    "ArrayMod": ArrayMod,
    "array_push": ArrayPushMod,
    "empty": EmptyMod
}

def build_funcs(c):
    functions = {}
    for f in _MODS:
        functions[f] = {
                "run_func": _MODS[f](c)
            }
    return functions