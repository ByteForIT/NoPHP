from ..exceptions import TranspilerExceptions, Warn
from ..module import Module
from ..types import *
from flask import session

class RedirectMod(Module):
    name="redirect"
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

    def proc_tree(self, tree):
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        values = self.base(tree)


        if len(values) > 2:
            raise TranspilerExceptions.TooManyValues(values, "redirect($msg) or redirect($msg, $events[str])")
        

        if len(values) == 1:
            return String(f'<meta http-equiv="refresh" content="0;url={values[0]}">')
        elif len(values) == 2:
            # print(values[1])
            session['events'] = values[1]
            return String(f'<meta http-equiv="refresh" content="0;url={values[0]}">')
        else:
            raise TranspilerExceptions.Generic("Not enough values supplied to redirect")
