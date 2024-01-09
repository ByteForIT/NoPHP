"""
# This module handles all functions related to Sessions.
# This module is based off of Flask sessions used in Spindle.
"""
from ..exceptions import TranspilerExceptions
from ..module import Module
from ..types import *

from flask import session
import random

SESSION_TRACKER = {}

def generate_session():
    global SESSION_TRACKER
    s = random.getrandbits(128)
    if s in SESSION_TRACKER:
        s = random.getrandbits(128)
    
    return "%032x" % s

class _SessionMod(Module):
    def __init__(self, compiler_instance):
        super().__init__()
        self.compiler_instance = compiler_instance

    def base(self, tree):
        resolution_module: Module = self.compiler_instance.get_action('RESOLUT')
        func_module: Module = self.compiler_instance.get_action('FUNCTION_CALL')
        values = []

        if 'POSITIONAL_ARGS' in tree['FUNCTION_ARGUMENTS']:
            for var in tree['FUNCTION_ARGUMENTS']['POSITIONAL_ARGS']:
                resolved = resolution_module(var)
                value: BasicType = None

                if type(resolved) == ID:
                    value = resolved.value
                    v = self.compiler_instance.get_variable(value)
                    if v["type"] is BasicType:
                        if v["type"] == String:
                            value = self.remove_quotes(v['object'].value)
                        else:
                            value = v['object'].value
                    elif v["type"] is None:
                        value = ""
                    else:
                        value = str(v['object'].value)
                elif type(resolved) == String:
                    value = self.remove_quotes(resolved.value)
                elif type(resolved) == Int32:
                    value = resolved.value
                elif type(resolved) == sInnerMut:
                    value = func_module.run_sInnerMut(resolved).value

                values.append(value)
        return values

class SessionStartMod(_SessionMod):
    name = "session_start"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)

    def proc_tree(self, tree):
        # TODO: Change prints to console logs
        values = self.base(tree)

        if len(values) != 0:
            raise TranspilerExceptions.IncorrectNumberOfValues(values, "session_start()")
        
        # session['aa'] = "bb"

        # Session already exists
        if "_noid" in session:
            print("Session exists")
        else:
            global SESSION_TRACKER
            try:
                session['_noid'] = generate_session()
            except RuntimeError as e:
                print("No secret key was set. Unable to securely create a session. Please add a 'secret_key' entry to the wool.yaml config.")
            SESSION_TRACKER[session['_noid']] = {
                "_cin": self.compiler_instance.namespace # Created in
            }
            print(f"Session created for {session['_noid']}")

        # Add new variable 
        self.compiler_instance.create_variable(
            "_SESSION",
            Session,
            Session(), 
            force=True
        )

        return Nil
    

class SessionDestroyMod(_SessionMod):
    name = "session_destroy"
    type = Module.MODULE_TYPES.FUNCTION

    def __init__(self, compiler_instance):
        super().__init__(compiler_instance)

    def proc_tree(self, tree):
        # TODO: Change prints to console logs
        values = self.base(tree)

        if len(values) != 0:
            raise TranspilerExceptions.IncorrectNumberOfValues(values, "session_destroy()")
        
        # session['aa'] = "bb"

        # Session already exists
        if "_noid" in session:
            print("Session exists, destroying")
            global SESSION_TRACKER
            if session['_noid'] in SESSION_TRACKER:
                del SESSION_TRACKER[session['_noid']]
            session.clear()
        return Nil