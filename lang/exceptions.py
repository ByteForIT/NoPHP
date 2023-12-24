class TranspilerExceptions:
    class NamespaceNotFound(Exception):
        def __init__(self, namespace, namespaces):
            Exception.__init__(self, f"No such namespace '{namespace}'. Available namespaces include: {list(namespaces.keys())}")
    class NotImplemented(Exception):
        def __init__(self):
            Exception.__init__(self, "Not implemented")
    class TypeMissmatch(Exception):
        def __init__(self, var, got, expected, line):
            Exception.__init__(self, f"Line {line}: For {var}, got: {got}, expected: {expected}")
    class TypeMissmatchNL(Exception):
        def __init__(self, var, got, expected):
            Exception.__init__(self, f"For {var}, got: {got}, expected: {expected}")
    class Overflow(Exception):
        def __init__(self, var, got, expected):
            Exception.__init__(self, f"For {var}, got: {got}, value overflows the given size of {expected}")
    class UnkownVar(Exception):
        def __init__(self, var, vars, nm="Nil"):
            Exception.__init__(self, f"Got unknown '{var}' (in {nm}). Variables in the current scope only contain: {list(vars.keys())}")
    class VarExists(Exception):
        def __init__(self, var):
            Exception.__init__(self, f"Got '{var}'. This variable already exists in this scope")
    class ClassExists(Exception):
        def __init__(self, cls):
            Exception.__init__(self, f"Got '{cls}'. This class already exists in this scope")
    class ClassNotFound(Exception):
        def __init__(self, cls):
            Exception.__init__(self, f"Got '{cls}'. No such class exists within this scope")
    class InvalidIndexType(Exception):
        def __init__(self, type, types):
            Exception.__init__(self, f"Got type '{type}' for index. Supported types are: {types}")
    class OutOfBounds(Exception):
        def __init__(self, index, length):
            Exception.__init__(self, f"Index {index} is out of bounds. Array length is {length}")
    class UnauthorizedBitSet(Exception):
        def __init__(self):
            Exception.__init__(self, f"This program is not being built in the correct mode for setting the bit configuration.")
    class IncompleteDeclaration(Exception):
        def __init__(self, tree):
            Exception.__init__(self, f"The variable declaration does not contain any matched declaration method. Tree & constructor: {tree}")
    class UnknownActionReference(Exception):
        def __init__(self, act):
            Exception.__init__(self, f"Got unknown action '{act}'")
    class UnknownMode(Exception):
        def __init__(self, mode):
            Exception.__init__(self, f"Got unknown action mode '{mode}'")
    class UnkownMethodReference(Exception):
        def __init__(self, func, funcs):
            Exception.__init__(self, f"Got unknown function '{func}', from '{funcs}'")
    class ActionRequiredButNotFound(Exception):
        def __init__(self, act, acts):
            Exception.__init__(self, f"An action '{act}' is required for this task. But only {list(acts.keys())} are installed")
    class UnkownType(Exception):
        def __init__(self, type):
            Exception.__init__(self, f"Unknown type supplied {type}")
    class TooManyValues(Exception):
        def __init__(self, values, scope):
            Exception.__init__(self, f"Too many values supplied to unpack in current scope. values: {values} scope: {scope}")
    class Generic(Exception):
        def __init__(self, msg):
            Exception.__init__(self, msg)

class RuntimeExceptions:
    class Panic(Exception):
        def __init__(self, msg, line="Unknown"):
            Exception.__init__(self, f"at line {line} | {msg}")

class ModuleExceptions:
    class InvalidModuleConstruction(Exception):
        def __init__(self, module):
            Exception.__init__(self, f"[Module:{module.name}] Invalid arguments supplied to constructor")