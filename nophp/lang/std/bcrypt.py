import base64
from ..exceptions import TranspilerExceptions, Warn
from ..module import Module
from ..types import *


class CommonSaltMod(Module):
    name="COMMONSALT"
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


# gensalt($value) -> Salt
class GenSaltMod(CommonSaltMod):
    name="gensalt"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        from bcrypt import gensalt

        values = self.base(tree)

        slowness = values[0]

        salt = gensalt(slowness)

        return Salt(salt)
    
# hashpw($value) -> String
class HashPWMod(CommonSaltMod):
    name="hashpw"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        from bcrypt import hashpw

        values = self.base(tree)
        text, salt = values[0], values[1]
        enc = hashpw(text.encode('utf-8'), salt)

        # Encode into a string
        string = base64.b64encode(enc).decode('utf-8')

        return String(string)
    
# checkpw($value) -> Bool
class CheckPWMod(CommonSaltMod):
    name="checkpw"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        from bcrypt import checkpw, hashpw, gensalt

        values = self.base(tree)
        text, hashed = values[0], values[1]


        # To bytes
        hashed = base64.b64decode(hashed.encode('utf-8'))
        valid = checkpw(text.encode('utf-8'), hashed)

        return Bool(valid)
    
_MODS = {
    "bcrypt_gensalt": GenSaltMod,
    "bcrypt_hashpw": HashPWMod,
    "bcrypt_checkpw": CheckPWMod
}

def build_funcs(c):
    functions = {}
    for f in _MODS:
        functions[f] = {
                "run_func": _MODS[f](c)
            }
    return functions