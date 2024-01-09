from sly import Lexer

class PyettyLexer(Lexer):
    tokens = {
        ID,
        FLOAT,
        INT,
        CHAR,
        FUNC,
        CLASS,
        NAMESPACE,
        STRING,
        MULTILINE_STRING,
        FORMATTED_STRING,
        EQ_GREATER,
        EQ_LESS,
        EQEQ,
        PYTHON_CODE,
        COLON_COLON,
        IF,
        ELSE,
        TRUE,
        FALSE,
        NOT_EQEQ,
        WHILE,
        BREAK,
        SKIP,
        FOR,
        FOREACH,
        AS,
        IN,
        DEL,
        RETURN,
        NULL,
        EQ_ADD,
        EQ_SUB,
        EQ_MUL,
        EQ_DIV,
        EQ_MOD,
        IMPORT,
        LIMPORT,
        SANDBOX,
        FARROW,
        TARROW,
        LET,
        TELSE,
        PYTHON_CODE_EXEC,
        OF,
        GLOBAL,
        DEFINE,
        DEBUG,
        DEPENDS,
        SELFISH,
        ENV,
        FROM,
        INIT,
        NEW,
        PHPSTART,
        PHPEND,
        HTMLSTART,
        # HTMLSTRING,
        HTMLEND,
        SARROW,
        # TEXT
        EXTENDS,
        ATTR_LEVEL,
    }
    literals = {
        "+",
        "-",
        "*",
        "/",
        "%",
        "|",
        "&",
        "!",
        ">",
        "<",
        "=",
        "(",
        ")",
        "{",
        "}",
        ";",
        ",",
        ":",
        "[",
        "]",
        "\\",
        "/",
        ".",
        "?",
        "^",
        "#",
        "_",
        "$"
    }

    ignore = " \t"
    ignore_comment_slash = r"//.*"

    FLOAT = r"\d*\.\d+"
    INT = r"\d+"

    PYTHON_CODE = r"\$`[.\W\w]*?`"
    PYTHON_CODE_EXEC = r"\$e`[.\W\w]*?`"
    STRING = r"(\".*?(?<!\\)(\\\\)*\"|'.*?(?<!\\)(\\\\)*')" #r'"[\s\S]*?"' 
    MULTILINE_STRING = r"(`(?:[^`\\]|\\.)*`)"
    FORMATTED_STRING = r"f(`(?:[^`\\]|\\.)*`)"
    CHAR = r"'[\s\S]*?'"
    ID = r"(--[a-zA-Z_]([a-zA-Z0-9_]|!)*--|[a-zA-Z_]([a-zA-Z0-9_]|!)*)"
    PHPSTART = r"<\?php"
    PHPEND = r"\?>"
    HTMLEND = r'</([^<>]+)>'
    HTMLSTART = r'<([^<>]+)>' #r"(\".*?(?<!\\)(\\\\)*\"|'.*?(?<!\\)(\\\\)*')"
    ID["function"] = FUNC
    ID["class"] = CLASS
    ID["extends"] = EXTENDS
    ID["namespace"] = NAMESPACE
    ID["break"] = BREAK
    ID["skip"] = SKIP
    ID["true"] = TRUE
    ID["false"] = FALSE
    ID["while"] = WHILE
    ID["for"] = FOR
    ID["foreach"] = FOREACH
    ID["in"] = IN
    ID["as"] = AS
    ID["if"] = IF
    ID["else"] = ELSE
    ID["del"] = DEL
    ID["null"] = NULL
    ID["return"] = RETURN
    ID["import"] = IMPORT
    ID["limport"] = LIMPORT
    ID["sandbox"] = SANDBOX
    ID["let"] = LET
    ID["of"] = OF
    ID["globals"] = GLOBAL
    ID["define"] = DEFINE
    ID["depends"] = DEPENDS
    ID["debugThis"] = DEBUG
    ID["selfish"] = SELFISH
    ID["env"] = ENV
    ID["from"] = FROM
    ID["_init"] = INIT
    ID["new"] = NEW
    ATTR_LEVEL = r'(public|private|protected)'
    # TEXT = r'>\s*([^<>\s]+)\s*'
    # HTMLSTRING = r'[\s\S]+?'

    TARROW = r'->' # Tiny arrow
    FARROW = r'\=\=>' # Fat arrow
    SARROW = r'\=\>' # Skinny arrow
    TELSE = r'\|\|'
    COLON_COLON = r"::"
    EQEQ = "=="
    NOT_EQEQ = r"!="
    EQ_GREATER = r"=>"
    EQ_LESS = r"=<"
    EQ_ADD = r"\+="
    EQ_SUB = r"-="
    EQ_MUL = r"\*="
    EQ_DIV = r"/="
    EQ_MOD = r"%="

    

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += len(t.value)
