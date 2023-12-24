class BasicType:
    def __init__(self):
        self.value: object
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"
    def __repr__(self) -> str:
        return self.__str__()

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
    Simple static length list type
    '''
    size = 0
    abbr_name = 'list'
    def __init__(self, values, type):
        self.value = values
        self.length = len(values)
        self.size = List.size
        self.offset = 0
        self.type = type
        super().__init__()

    # Types
    BONE = "Barebone"
    GUESS = "Guess it!"

class DynArray(List):
    '''
    A dynamic size array
    '''
    size = 0
    abbr_name = 'DynamicArray'
    def __init__(self, values, type):
        super().__init__(values, type)
        # This should adapt to be an ASSOC Array if needed, 
        # or we could have another sub-type?
        # idfk

class Nil(BasicType):
    '''
    A nil or None equivalent 
    '''
    size = 0
    abbr_name = 'Nil'
    def __init__(self, _):
        self.value = ""
        super().__init__()

class Any(BasicType):
    '''
    Any, guess type later
    '''
    size = 0
    abbr_name = 'Nil'
    def __init__(self, _):
        self.value = ""
        super().__init__()


class sInnerMut(BasicType):
    '''
    System Internal Type
    '''
    size = 0
    abbr_name = 'sINNER'
    def __init__(self, *v):
        self.value = v
        super().__init__()