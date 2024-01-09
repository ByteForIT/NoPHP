import json
from werkzeug.datastructures import ImmutableMultiDict

class BasicType:
    def __init__(self):
        self.value: object
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"
    def __repr__(self) -> str:
        return self.__str__()
    
    def __len__(self) -> int:
        return len(self.value)
    
    def __html__(self):
        return str(self.value)

class String(BasicType):
    '''
    Simple String type
    '''
    def __init__(self, value):
        self.value = f'"{value}"'
        self.length = len(value)
        super().__init__()

class ID(BasicType):
    '''
    Simple ID type
    '''
    def __init__(self, value):
        self.value = value
        self.length = len(value)
        super().__init__()

class Char(BasicType):
    '''
    Simple Char type
    '''
    size = 1
    abbr_name = 'char'
    def __init__(self, value):
        self.value = ord(value) if type(value) == str else value
        self.length = value
        self.size = Char.size
        self.hex  = False
        super().__init__()

class Bool(BasicType):
    '''
    Simple Bool type
    '''
    size = 1
    abbr_name = 'bool'
    def __init__(self, value):
        self.value = True if value == 'true' or value == True else False
        self.hex  = False
        super().__init__()

class Int32(BasicType):
    '''
    Simple Int32 type
    '''
    size = 4
    abbr_name = 'int'
    def __init__(self, value):
        self.value = int(value)
        self.length = value
        self.size = Int32.size
        self.hex = False
        super().__init__()

class Float(BasicType):
    '''
    Simple float type
    '''
    size = 4
    abbr_name = 'float'
    def __init__(self, value):
        self.value = float(value)
        self.length = value
        self.size = Int32.size
        self.hex = False
        super().__init__()

class HexInt32(BasicType):
    '''
    Simple Int32 type
    '''
    size = 4
    abbr_name = 'hex'
    def __init__(self, value):
        self.value = value
        self.length = len(value)
        self.size = Int32.size
        self.hex = True
        super().__init__()

class List(BasicType):
    '''
    Simple list type
    '''
    size = 0
    abbr_name = 'list'
    def __init__(self, values, type):
        self.value = values
        self.size = List.size
        self.offset = 0
        self.type = type
        super().__init__()

    @property
    def length(self):
        return len(self.value)

    # Types
    BONE = "Barebone"
    GUESS = "Guess it!"

class Map(BasicType):
    '''
    Simple map type
    '''
    size = 0
    abbr_name = 'Map'
    def __init__(self, values):
        self.value = values
        self.length = len(list(values.keys()))
        self.size = Map.size
        super().__init__()

# TODO: Discourage array() construction in favour of []

class DynArray(List):
    '''
    A dynamic size array
    '''
    size = 0
    abbr_name = 'DynamicArray'
    def __init__(self, values, type=''):
        super().__init__(values, type)
        self.value = list(values)
        # This should adapt to be an ASSOC Array if needed, 
        # or we could have another sub-type?
        # idfk

class Nil(BasicType):
    '''
    A nil or None equivalent 
    '''
    size = 0
    abbr_name = 'Nil'
    value = 'Nil'
    def __init__(self, _=''):
        self.value = ""
        super().__init__()

class Any(BasicType):
    '''
    Any, guess type later
    '''
    size = 0
    abbr_name = 'Any'
    def __init__(self, _):
        self.value = ""
        super().__init__()

class Auto(BasicType):
    '''
    This type will automatically fill 
    in the duties of other types.

    This is used for wrapping Python objects.

    For example: 

        Basic matching.
        We expect a manually defined AutoEncoder and
        AutoDecoder for this object

        Opportunistic matching.
        We expect that the object contains all or most
        of the known types
        ```
        [Request]      -->      [Auto(Request)]
        |- str(method)            |- String(method)
        |- bytes(data)            |- DynArray(data, type=Char)
        |- ...                    |- ...
        ```

    '''
    size = 0
    abbr_name = 'Auto'
    def __init__(self, v, type='none'):
        self.value = self.match_value(v, type) 
        self.match_type = type
        self.length = -1
        super().__init__()

    def match(self):
        "Dangerous, instead expect Auto to resolve automatically"
        return self.match_value(self.value, 'basic')

    def match_value(self, value, _type='none'):
        if type(value) == Auto:
            value = value.value 
        if _type == 'basic':
            _f = {
                None: Nil,
                str: String,
                int: Int32,
                dict: Map,
                list: DynArray,
                tuple: DynArray,
                # bad bad bad
                type(None): Nil,
                ImmutableMultiDict: Map
            }
            if type(value) in _f:
                return _f[type(value)](value)
            return value
        else:
            return value

class sInnerMut(BasicType):
    '''
    System Internal Type
    '''
    size = 0
    abbr_name = 'sINNER'
    def __init__(self, *v):
        self.value = v
        super().__init__()


class Session:
    '''
    Session type.
    This is a special type variant as we need to access Flask's
    internal session object.
    '''
    size = 0
    abbr_name = 'Session'
    def __init__(self):
        pass

    @property
    def value(self):
        from flask import session
        return session
    

class Request:
    '''
    Request type.
    This is a special type variant as we need to access Flask's
    internal request object.
    '''
    size = 0
    abbr_name = 'Request'
    def __init__(self):
        pass

    @property
    def value(self):
        from flask import request
        return request