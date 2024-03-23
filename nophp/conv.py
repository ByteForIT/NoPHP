# Well...
# This is used to convert NoPHP -> PHP
# Highly experimental, be careful

from nophp.weaver import compiler

code = compiler.code 

print(code)

# The other way around:
# from phply.phplex import lexer
# from phply.phpparse import make_parser
# from phply import pythonast

# parser = make_parser()
# # body = [pythonast.from_phpast(ast)
# #         for ast in parser.parse(input.read(), lexer=lexer)]

# for ast in parser.parse(input(), lexer=lexer):
#     print(ast)