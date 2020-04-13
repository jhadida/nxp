
"""
Define aliases for expressions with specific content or options.
"""

from nxp.read import charset
from .impl import *

# ------------------------------------------------------------------------

def Rep(tok,*args):
    return tok.__mul__(*args)

def Opt(tok):
    return tok.__mul__('1?')

def Many(tok):
    return tok.__mul__('1+')

# ------------------------------------------------------------------------

def Any(*args):
    return Set( args, min=1 )

def All(*args):
    return Set( args, min=len(args) )

def Xor(*args):
    return Set( args, max=1 )

def OneOf(*args):
    return Xor(*args)

def TwoOf(*args):
    return Set( args, min=2, max=2 )

def Either(*args):
    return Xor(*args)

# ------------------------------------------------------------------------

def Lit(val, **kwargs):
    return Regex( val, **kwargs )

def Chars(val, **kwargs):
    return Regex( '[' + val + ']+', **kwargs )

def White():
    return Chars( charset.white )

def Word():
    return Regex( r'\w+' )

def NumInt():
    return Regex( r'-?\d+' )

def NumFloat():
    return Regex( r'-?\d*\.\d+([eE][-+]?\d+)?' )

def NumHex():
    return Regex( r'0[xX][0-9a-fA-F]+' )

def Num():
    return OneOf( NumInt(), NumFloat(), NumHex() )

def Bool():
    return Either( Lit('True'), Lit('False') )

def Link():
    return Regex( r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+' )

# see: https://stackoverflow.com/a/201378/472610
def Email():
    fmt = {
        'a': "[a-z0-9!#$%&'*+/=?^_`{|}~-]+",
        'b': "[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
        'c': "(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])",
        'd': "\\[\x01-\x09\x0b\x0c\x0e-\x7f]"
    }
    
    return Regex( "(?:{a}(?:\.{a})*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|{d}*\")@(?:(?:{b}\.)+{b}|\[(?:(?:{c})\.){{3}}(?:{c}|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|{d}+)\])".format_map(fmt) )

