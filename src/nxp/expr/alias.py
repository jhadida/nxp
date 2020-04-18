
"""
Define aliases for expressions with specific content or options.
"""

from nxp.read import charset
from .impl import *

# ------------------------------------------------------------------------

def Mul(tok,*args):
    return tok.__mul__(*args)

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

def XML():
    value = String().append( r'[\s=\'"<>`]+' )
    attr = Seq( [r'\s+(\w+)', Seq([ r'\s*=\s*', value ])], skip=1 )
    tag = Seq( [r'<(\w+)', attr, r'\s*/?>'], skip=1 )
    return Either( tag, r'</(\w+)\s*>' )
    
def Fenced( boundary, esc=True, empty=True ):
    if isinstance(boundary,str):
        L,R = boundary, boundary
    else:
        L,R = boundary 

    assert len(R)==1, ValueError('Right boundary should be a single char.')

    L = re.escape(L)
    R = re.escape(R)
    mul = '*' if empty else '+'

    if esc:
        r = f'{L}(((\\\\{R})|[^{R}]){mul}){R}' 
    else:
        r = f'{L}([^{R}]{mul}){R}' 

    return Regex(r)

def SqString( empty=True ):
    return Fenced( "'", empty=empty )

def DqString( empty=True ):
    return Fenced( '"', empty=empty )

def String( empty=True ):
    return Either( SqString(empty), DqString(empty) )
