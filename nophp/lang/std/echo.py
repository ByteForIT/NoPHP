from ..compiler import Compiler
from ..exceptions import TranspilerExceptions
from ..module import Module
from ..types import *
import json

class EchoMod(Module):
    name="echo"
    type = Module.MODULE_TYPES.SPECIAL_ACTION_FUNC

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree, stubborn=False):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        values = self.base(tree, ref=stubborn)

        if len(values) > 1:
            raise TranspilerExceptions.TooManyValues(values, "echo($msg)")
        
        value = values[0]

        # Patch echo to correctly handle JSON

        if type(value) in (list, dict, tuple):
            value = json.dumps(value)
        
        # print(value)

        return str(value)
