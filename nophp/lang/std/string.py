"""
# This module handles all functions related to Strings
"""
from ..exceptions import TranspilerExceptions
from ..module import Module
from ..std.db import SqlConnector
from ..types import DynArray, String, BasicType, ID, Int32, sInnerMut

class StrMod(Module):
    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def base(self, tree, ref=False):
        values = []

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
        elif type(resolved) == str: # TODO: Fix whatever is causing legacy behavior (Python strings)
            value = resolved
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

class StrLenMod(StrMod):
    name = "strlen"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)

    def proc_tree(self, tree):
        values = self.base(tree)

        if len(values) != 1:
            raise TranspilerExceptions.IncorrectNumberOfValues(values, "strlen()")

        # Extracted the value from the list
        input_string = values[0]

        # Check if it's a string
        if not isinstance(input_string, str):
            raise TranspilerExceptions.TypeMissmatch("strlen()", "string", type(input_string).__name__, 0)

        # Calculate and return the length of the string
        length = len(input_string)
        return Int32(length)
    

class StrReplaceMod(StrMod):
    name = "str_replace"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)

    def proc_tree(self, tree):
        values = self.base(tree)

        if len(values) != 3:
            raise TranspilerExceptions.IncorrectNumberOfValues(values, "str_replace()")

        # Extracted the values from the list
        search_str, replace_str, subject_str = values

        # Check if all arguments are strings

        # Perform the string replacement
        result_str = subject_str.replace(search_str, replace_str)
        return String(result_str)
    
class Nl2BrMod(StrMod):
    name = "nl2br"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)

    def proc_tree(self, tree):
        values = self.base(tree)

        if len(values) != 1:
            raise TranspilerExceptions.IncorrectNumberOfValues(values, "nl2br($str)")

        # Extracted the values from the list
        subject_str = values[0]

        # Check if all arguments are strings

        # Perform the string replacement
        result_str = subject_str.replace('\n', '</br>')
        return String(result_str)

class SubstrMod(StrMod):
    name = "substr"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)

    def proc_tree(self, tree):
        values = self.base(tree)

        if len(values) < 2 or len(values) > 3:
            raise TranspilerExceptions.IncorrectNumberOfValues(values, "substr()")

        # Extract the values from the list
        subject_str, start, length = self.remove_quotes(values[0]), int(values[1]), None

        if len(values) == 3:
            length = int(values[2])

        # Check if all arguments are strings or integers
        if not isinstance(subject_str, str) or not isinstance(start, int) or (length is not None and not isinstance(length, int)):
            raise TranspilerExceptions.TypeMissmatch("substr()", "string, int[, int]", 0)

        # Perform the substring operation
        result_str = subject_str[start:start+length] if length is not None else subject_str[start:]
        # print("res:",result_str, subject_str, start, length)
        return String(result_str)