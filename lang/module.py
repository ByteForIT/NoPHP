
from lang.exceptions import ModuleExceptions


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
