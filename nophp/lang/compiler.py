


from .exceptions import TranspilerExceptions
from .modules import Module
from .types import Nil
from rich import print as rprint
from copy import deepcopy

from rich.console import Console
from rich.syntax import Syntax
console = Console()

class Compiler:
    def __init__(
            self,
            tree,
            actions = {},
            variables = {},
            functions = {},
            classes = {},
            builtin_functions = {},
            namespace = "main",
            namespaces = {}
    ):
        self.code = tree
        self.actions = actions 
        self._modules = {}
        self.line = 0
        self.variables: dict = variables
        self.builtin_functions = {}
        self.functions = functions
        self.namespace = namespace
        self.namespaces = namespaces
        self.classes = classes
        self.finished = []
        self.finished_funcs = []

        self.parent = None

        self.returns = Nil(None) # No return
        self.stop = False

        # Keep track of current and previous module run
        self.curr = None
        self.prev = None

        self.persistent = False

    def new_instance(
        self,
        tree = None,
        namespace = '_anon',
        namespaces = {},
        variables = {},
        functions = {},
        classes = {},
        sync = ""
    ):
        # Modules and actions need to be recreated with a new scope
        instance = Compiler(
            tree = tree,
            namespace = namespace,
            variables = self.variables if sync in ("object", "advanced") else self.deepcopy_vars(),
            functions = self.functions.copy() if sync == "advanced" else {},
            classes = self.classes if sync in ("class", "object", "advanced") else {},
            namespaces = namespaces,
        )

        Compiler.populate_modules_actions(
            instance,
            self.raw_modules
        )

        # builtins should reflect their new namespace
        for builtin in self.builtin_functions:
            instance.builtin_functions[builtin] = {
                "run_func": type(self.builtin_functions[builtin]['run_func'])(instance)
            }

        instance.parent = self

        return instance
    
    def deepcopy_vars(self):
        v = {}
        for var in self.variables:
            try:
                v[var] = deepcopy(self.variables[var])
            except:
                print(f"Was unable to clone : {var}")
        return v
    
    def __deepcopy__(self, memodict={}):
        copy_object = Compiler(
            tree=[]
        )
        copy_object.functions = self.functions
        return copy_object
    
    def sync_functions(
        self,
        instance
    ):
        for name in instance.functions:
            self.functions[name] = instance.functions[name]
            

    def sync_variables(self, instance):
        for name in instance.variables:
            self.variables[name] = instance.variables[name]
            

    def sync_classes(self, instance: 'Compiler'):
        for name in instance.classes:
            self.classes[name] = instance.classes[name]

    def sync(self, instance: 'Compiler'):
        self.sync_functions(instance)
        self.sync_variables(instance)
        self.sync_classes(instance)

    
    def populate_modules_actions(
        self,
        Modules: list[Module]
    ) -> None:
        # Issue 1: 19-12-23
        #
        # These are fucked...
        # For some reason, they affect the parent compiler instance
        # This should not happen!?
        # I have no idea why this happens!?
        # Hack 1 fixes this... But it's a bad idea
        #   Update: 20-12-23
        # The issue persists with subclass instances
        # This is stupid
        # I have no idea whats causing this
        #   Update: 23-12-23
        # I've been able to track down the id's of these instances
        # They seem to be the same even after 
        # a rebuild of the parent's source
        # Will try to run the rebuild after the sync
        # Turns out this is done by default.
        # I'm still unsure about how to fix the issue
        # Hoping that pycharms debugging features can save my ass
        #   Update: 24-12-23
        # Still no fix
        # Update: 24-12-23
        # Issue has been fixed, the issue was in how the objects were being created.
        # NEVER use deep copy for complex structures.....
        # Update: 25-12-23
        # The issue was not fixed... Scopes are still broken
        # Update 26-12-23
        # The issue has been resolved :pain: hopefully for real this time
        self.raw_modules = Modules
        for module in Modules:
            modobj: Module = module(self)
            modobj.type = module.type
            if modobj.type == Module.MODULE_TYPES.FUNCTION:
                self.functions[module.name] = modobj
            else:
                self.actions[module.name] = modobj

            if module.type == Module.MODULE_TYPES.SPECIAL_ACTION_FUNC:
                self.functions[module.name] = modobj

            self._modules[module.name] = modobj

    def add_builtin_functions(self, funcs):
        self.builtin_functions = funcs

        # Add them as actions too
        for func in funcs:
            self.actions[funcs[func]["run_func"].name] = funcs[func]["run_func"]
    
    def get_action(
        self,
        name
    ) -> Module:
        if name in self.actions:
            return self.actions[name]
        else:
            print(f"At {self.line}")
            raise TranspilerExceptions.ActionRequiredButNotFound(name, self.actions)

    def run(self, code=None):
        # Fixed: Ok so, the issue here was that sometimes the function body wouldnt be ran properly
        # This was due to self.stop persisting. The below disables that 
        self.stop = False
        if code is None:
            code = self.code
        else:
            code = code
        for action in code:
            if self.stop:
                return
            # Hack 1, see issue 1
            self.populate_modules_actions(
                self.raw_modules
            )
            # print(self.namespace, self.variables)
            if action[0] in self.actions:
                # print(self.namespace, "->", action[0])
                self.curr = action[0]
                try:
                    ret = self.actions[action[0]](action[1])
                
                    if self.actions[action[0]].type == Module.MODULE_TYPES.SPECIAL_ACTION:
                        if ret != None:
                            if 'ID' in action[1] and type(action[1]['ID']) == tuple and\
                                self.get_action("RESOLUT")(action[1]['ID']).value == 'echo':
                                self.finished.append(ret)
                    elif self.actions[action[0]].type == Module.MODULE_TYPES.SPECIAL_ACTION_FUNC:
                        if ret != None:
                            self.finished_funcs.append(ret)
                    elif self.actions[action[0]].type == Module.MODULE_TYPES.NON_WRITEABLE:
                        continue
                except Exception as e:
                    console.print_exception(show_locals=False)
                    console.bell()
                    console.print(f"[red]({__file__.split('/')[-1]}:{action[-1]})\n\t({self.namespace})ERROR:[/red]", e)
                    rprint(
                        Syntax(
                            str(action) + '\nPrevious:\t'+ str(self.prev),
                            "lisp",
                            padding=1, 
                            line_numbers=True
                        )
                    )
                    print("Stacktrace:")
                    parent = self.parent
                    while parent is not None:
                        print(parent)
                        parent = parent.parent
                    if self.persistent:
                        raise e
                    else:
                        exit(1)
            else:
                print(code)
                raise TranspilerExceptions.UnknownActionReference(action[0])
            self.line += 1
            self.prev = action[0]

    def pause(self):
        rprint("[yellow bold]Compilation paused. Press enter to continue[/yellow bold]")
        input()

    def get_variable(
        self,
        name: str
    ) -> dict:
        if name in self.variables:
            return self.variables[name]
        else:
            print(f"At {self.line} {self.namespace} during {self.curr}")
            raise TranspilerExceptions.UnkownVar(name, self.variables, nm=self.namespace)

    def create_variable(
        self,
        name: str, 
        type,
        obj,
        level = 'public',
        force = False
    ) -> None:
        # print(f"At {self.line} {self.namespace}")
        if name in self.variables and not force:
            print(f"At {self.line}")
            raise TranspilerExceptions.VarExists(name)
        self.variables[name] = {
                "type": type,
                "object": obj,
                "level": level,
            }
        
    def remove_variable(
        self,
        name: str
    ) -> None:
        if name in self.variables:
            del self.variables[name]
        else:
            raise TranspilerExceptions.UnkownVar(name, self.variables)
        
    def create_function(
        self,
        name: str, 
        obj: object,
        source: str,
        returns,
        arguments=[],
        level = "public",
    ) -> None:
        self.functions[name] = {
                "object": obj,
                "source": source,
                "run_func": obj.run,
                "returns": returns,
                "arguments": arguments,
                "level": level
            }
        
    def write_back(self, origin: 'Compiler'):
        console.log(f"[red]<===>[/red] Writing back from '{origin.namespace}' to '{self.namespace}'")
        self.finished = self.finished + origin.finished
        self.finished_funcs = self.finished_funcs + origin.finished_funcs
        
    def create_class(
        self,
        name: str = '',
        obj = '',
        source = '',
        parent = None,
        force = False
    ) -> None:
        if name in self.classes and not force:
            print(f"At {self.line}")
            raise TranspilerExceptions.ClassExists(name, clss=self.classes)
        
        obj.parent = parent
        
        self.classes[name] = {
                "object": obj,
                "source": source,
                "parent": parent
            }
        
    
    def __str__(self) -> str:
        return f"NS::{self.namespace}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def clean(self):
        self = Compiler([])
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.finished = []
        self.code = []
        self.namespaces = {}
        self.namespace = 'main'
        self.parent = None
        return self
