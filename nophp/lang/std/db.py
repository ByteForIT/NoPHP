from ..exceptions import TranspilerExceptions, Warn
from ..module import Module
from ..types import *

import sqlite3
sqlite3.enable_callback_tracebacks(True)

class DbCommonMod(Module):
    name="DBCOMMON"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def base(self, tree):
        values = []

        if 'POSITIONAL_ARGS' in tree['FUNCTION_ARGUMENTS']:
            for var in tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS']:

                value = self.safely_resolve(var)

                values.append(value)

        return values
    
    def safely_resolve(self, var, instance=None):
        if instance is None:
            instance = self.compiler_instance
        # Dependencies
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        func_module: Module = self.compiler_instance.get_action('FUNCTION_CALL')
        if type(var) == tuple:
            resolved = resolution_module(var)
        else: resolved = var
        value: BasicType = resolved

        if type(resolved) == Auto:
            value = self.safely_resolve(resolved.value)

        # print("\t\t", value)

        if type(value) == ID:
            value = value.value
            v = instance.get_variable(value)
            # print("var:",v)
            if v["type"] == String:
                value = self.remove_quotes(v['object'].value)
            elif v["type"] is None:
                value = ""
            elif v["type"] == Auto:
                value = self.safely_resolve(v["object"].value)
            elif v["type"] == ID:
                value = self.safely_resolve(v["object"], instance=instance.parent)
            elif type(v['object']) in BASE_TYPES:
                value = v['object']
            else:
                value = v['object'].value
        elif type(value) == String:
            value = self.remove_quotes(value.value)
            # print("\t", value)
        elif type(value) == Int32:
            value = value.value
        elif type(value) == sInnerMut:
            value = func_module.run_sInnerMut(value).value
        elif type(value) == SqlConnector:
            value = value.value
        elif type(value) == DynArray:
            _value = value.value
            value = []
            for i in _value:
                value.append(self.safely_resolve(i)) 
        return value
    

# sql_connect("db.sql")
class DbConnect(DbCommonMod):
    name="DBCONN"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values = self.base(tree)

        connection = sqlite3.connect(values[0])

        return SqlConnector(connection)
    
# sql_query($conn, $sql)
class DbQuery(DbCommonMod):
    name="DBQ"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values = self.base(tree)


        if len(values) < 2:
            raise TranspilerExceptions.IncorrectNumberOfValues(values, "sql_query($conn, $sql)")
        
        conn, sql = values[:2]

        # print(values)

        returns = sql.split(' ')[0] == "SELECT"
            
        cursor: sqlite3.Cursor = conn.cursor()
        out = cursor.execute(sql)

        if returns:
            arr = DynArray([], type='auto')
            for val in out.fetchall():
                arr.value.append(
                    DynArray(list(val), type='auto')
                )
            return arr
        cursor.close()
        return Auto(out, type='basic')

# sql_query_one($conn, $sql)
class DbQueryOne(DbCommonMod):
    name="DBQ1"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values = self.base(tree)


        if len(values) < 2:
            raise TranspilerExceptions.IncorrectNumberOfValues(values, "sql_query_one($conn, $sql)")
        
        conn, sql = values[:2]

        # print(values)

        returns = sql.split(' ')[0] == "SELECT"
            
        cursor: sqlite3.Cursor = conn.cursor()
        out = cursor.execute(sql)

        if returns:
            return Auto(out.fetchone(), type='basic')
        cursor.close()
        return Auto(out)

# sql_close($conn)
class DbCloseConn(DbCommonMod):
    name="DBCLOSECONN"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values = self.base(tree)

        if len(values) < 1:
            raise TranspilerExceptions.IncorrectNumberOfValues(values, "sql_close($conn)")

        conn: sqlite3.Connection = values[0]
        conn.close()

# sql_query_sane($sql, $args[...])
class DbSane(DbCommonMod):
    name="DBSANE"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values =  self.base(tree)
        
        if len(values) < 3:
            raise TranspilerExceptions.IncorrectNumberOfValues(values, "sql_sane($conn, $sql, $args[...])")
        
        conn, sql, args = values[:3]

        returns = sql.split(' ')[0] == "SELECT"
            
        cursor: sqlite3.Cursor = conn.cursor()
        # print("Args:",args)
        out = cursor.execute(sql, args)


        # if returns:
        #     return Auto(out.fetchone(), type='basic')
        # cursor.close()
        # return Auto(out, type='basic')

        # print(out.fetchall())
    
        if returns:
            arr = DynArray([], type='auto')
            for val in out.fetchall():
                arr.value.append(
                    DynArray(list(val), type='basic')
                )
            # print(arr)
            return arr
        cursor.close()
        return Auto(out, type='basic')

#sql_commit_sane($conn, $sql, $args[...])
class DbSaneCommit(DbCommonMod):
    name="DBSANECOMMIT"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)
        self.compiler_instance = compiler_instance

    def proc_tree(self, tree):
        values =  self.base(tree)
        
        if len(values) < 3:
            raise TranspilerExceptions.IncorrectNumberOfValues(values, "sql_commit_sane($conn, $sql, $args[...])")
        
        conn, sql, args = values[:3]


        returns = sql.split(' ')[0] == "SELECT"
        if returns:
            raise TranspilerExceptions.Generic("sql_commit_sane only handles writes and updates, not select")
        
        try:
            cursor: sqlite3.Cursor = conn.cursor()
            cursor.execute(sql, args)
            out = cursor.lastrowid

            conn.commit()

            cursor.close()
            return Int32(out)
        except sqlite3.Error as e:
            print("DB Error:", e)
            return Nil(0)


_MODS = {
    "sql_connect": DbConnect,
    "sql_query": DbQuery,
    "sql_query_one": DbQueryOne,
    "sql_query_sane": DbSane,
    "sql_commit_sane": DbSaneCommit,
    "sql_close": DbCloseConn,

}

def build_funcs(c):
    functions = {}
    for f in _MODS:
        functions[f] = {
                "run_func": _MODS[f](c)
            }
    return functions