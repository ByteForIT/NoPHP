from ..exceptions import TranspilerExceptions, Warn
from ..module import Module
from ..std.db import SqlConnector
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
    
    def safely_resolve(self, var):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        func_module: Module = self.compiler_instance.get_action('FUNCTION_CALL')
        if type(var) == tuple:
            resolved = resolution_module(var)
        else: resolved = var
        value: BasicType = None

        if type(resolved) == Auto:
            resolved = resolved.match()

        if type(resolved) == ID:
            value = resolved.value
            v = self.compiler_instance.get_variable(value)
            # print(v)
            if v["type"] == String:
                value = self.remove_quotes(v['object'].value)
            elif v["type"] is None:
                value = ""
            else:
                value = v['object'].value
        elif type(resolved) == String:
            value = self.remove_quotes(resolved.value)
        elif type(resolved) == Int32:
            value = resolved.value
        elif type(resolved) == sInnerMut:
            value = func_module.run_sInnerMut(resolved).value
        elif type(resolved) == SqlConnector:
            value = resolved.value
        elif type(resolved) == DynArray:
            _value = resolved.value
            value = []
            for i in _value:
                value.append(self.safely_resolve(i)) 
        else:
            print(f"Couldnt resolve {resolved} in primites, returning None")

        return value
    
    def ref_resolve(self, var):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        func_module: Module = self.compiler_instance.get_action('FUNCTION_CALL')
        if type(var) == tuple:
            resolved = resolution_module(var)
        else: resolved = var
        value: BasicType = None


        if type(resolved) == ID:
            value = resolved.value
            v = self.compiler_instance.get_variable(value)
            # print(v)
            if v["type"] == String:
                value = v['object']
            elif v["type"] is None:
                value = String("")
            else:
                value = v['object']
        elif type(resolved) == String:
            value = resolved
        elif type(resolved) == Int32:
            value = resolved
        elif type(resolved) == sInnerMut:
            value = func_module.run_sInnerMut(resolved)
        elif type(resolved) == SqlConnector:
            value = resolved
        elif type(resolved) == DynArray:
            value = resolved
        else:
            value = resolved
        return value


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