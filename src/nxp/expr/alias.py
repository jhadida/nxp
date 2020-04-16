
"""
Define aliases for expressions with specific content or options.
"""

from nxp.read import charset
from .impl import *

# ------------------------------------------------------------------------

def Mul(tok,*args):
    return tok.__mul__(*args)

def Opt(tok):
    return tok.__mul__('1?')

def Many(tok):
    return tok.__mul__('1+')

Rep = Mul

# ------------------------------------------------------------------------

def Any(*args):
    return Set( args, min=1 )

def All(*args):
    return Set( args, min=len(args) )

def Xor(*args):
    return Set( args, max=1 )

def TwoOf(*args):
    return Set( args, min=2, max=2 )

OneOf = Xor 
Either = Xor

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
    return OneOf( NumFloat(), NumInt(), NumHex() )

def Bool():
    return Either( Lit('True'), Lit('False') )

def Link():
    return Regex( r"(http|ftp)s?://([a-z0-9-.]+\.)+[a-z]{2,}(/\S*)?" )

# see: https://www.regular-expressions.info/email.html
def Email():
    return Regex( r"[a-z0-9][a-z0-9._%+-]*@([a-z0-9-]+\.)+[a-z]{2,}", case=False )
