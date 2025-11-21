# -*- coding: utf-8 -*-

from py_compile import compile, PyCompileError

def compilation_success(fname: str) -> bool:
    """
    Check whether the given python file compiles using py_compile.compile

    :param fname: File name of the file to be compiled
    :returns: True if file compiles successfully, else False
    """

    try:
        # compile the given file
        compile(fname, doraise=True)
        # successful compilation
        return True
    except PyCompileError:
        # compilation failed
        return False
