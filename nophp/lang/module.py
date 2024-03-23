import markupsafe
from .types import *
from .exceptions import ModuleExceptions


class Module:
    BUILT_TYPE = str
    class MODULE_TYPES:
        '''
        FUNCTION -> Function module type
        ACTION   -> Internal action used in processing
        '''
        FUNCTION = "Function" 
        ACTION   = "Action"
        SPECIAL_ACTION = "Special Action"
        SPECIAL_ACTION_FUNC = "Special Action Function"
        NON_WRITEABLE = "Something that shouldnt need to be written to the output"

    def __init__(
        self,
        #type: MODULE_TYPES
    ):
        self.type = "Unknown"
        self.built = ""
        self.template = ""
        self.o1 = False
        self.o2 = False
        self.o3 = False
        self.no_construct = False        

    def __call__(
        self,
        tree,
        no_construct = False
    ):

        self.no_construct = no_construct
        _values = self.proc_tree(tree)
        self.override()
        return _values
    
    # Future
    #def optimise(self): pass
    optimise = None

    def remove_quotes(_,s):
        if type(s) != str: return str(s)
        if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
            return s.strip('"')
    
        return s

    # Future: Return true for now
    def verify(self): return True

    def override(self):
        """
        Warning: this should be used with caution since it bypasses the default build structure
        """
        pass

    # Implemented in module child
    def proc_tree(self, tree) -> dict: "Return a dict containing values processed from the tree"

    # Format
    # TODO: Remove this as it's not used
    def _constructor(
        self,
        arguments: dict
    ) -> BUILT_TYPE:
        if arguments == None:
            raise ModuleExceptions.InvalidModuleConstruction(self)
        try:
            return self.template.format(
                    **arguments
                )
        except Exception:
            raise Exception(f"In '{self.name}' - Failed to unpack elements. Perhaps you need to set `no_construct` to True to avoid this module's construction?")

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

        # print(resolved)

        if type(resolved) == Auto:
            resolved = resolved.match()

        if type(resolved) == ID:
            value = resolved.value
            v = self.compiler_instance.get_variable(value)
            # print(v)
            value = self.safely_resolve(v['object'])
        elif type(resolved) == String:
            value = self.remove_quotes(resolved.value)
        elif type(resolved) == Int32:
            value = resolved.value
        elif type(resolved) == Bool:
            value = resolved.value
        elif type(resolved) == sInnerMut:
            value = func_module.run_sInnerMut(resolved).value
        elif type(resolved) == type(self.compiler_instance):
            value = resolved
        elif type(resolved) == SqlConnector:
            value = resolved.value
        elif type(resolved) == Salt:
            value = resolved.value
        elif type(resolved) == DynArray:
            _value = resolved.value
            value = []
            for i in _value:
                value.append(self.safely_resolve(i)) 
        elif type(resolved) == Map:
            _value = resolved.value
            value = {}
            for key in _value:
                value[
                    self.safely_resolve(key)
                ] = self.safely_resolve(_value[key])
                
        # Legacy
        # Markup safe breaks this a bit...
        elif type(resolved) in [int, str, list, tuple, float, markupsafe.Markup]:
            value = resolved
        elif type(resolved) == Auto:
            value = resolved.value
        else:
            print(f"Couldnt resolve {resolved} of {type(resolved)} in Module, returning None")

        print(value)

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