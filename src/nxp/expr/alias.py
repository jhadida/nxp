
"""
Define aliases for expressions with specific content or options.
"""

import re
from .content import Regex
from .compose import Set, Seq
from .repeat import Rep, mulseq

# ------------------------------------------------------------------------

def Opt(tok):
    return Rep(tok,'1-')

def Any(tok,sep=None):
    return Rep(tok,'0+',sep)

def Few(tok,sep=None):
    return Rep(tok,'1+',sep)

def Many(tok,sep=None):
    return Rep(tok,'2+',sep)

def Odd(tok,sep=None,start=1):
    return Rep(tok,mulseq(start,2),sep)

def Even(tok,sep=None,start=2):
    return Rep(tok,mulseq(start,2),sep)

# ------------------------------------------------------------------------

def Xor(*args):
    return Set( args, max=1 )

def All(*args):
    return Set( args, min=len(args) )

def TwoOf(*args):
    return Set( args, min=2, max=2 )

OneOf = Xor 
Either = Xor

# ------------------------------------------------------------------------

def Lit(val, **kwargs):
    return Regex( val, **kwargs )

def Chars(val, **kwargs):
    return Regex( '[' + val + ']+', **kwargs )

def Word():
    return Regex( r'\w+' )

def NumInt():
    return Regex( r'-?\d+' )

def NumFloat():
    return Regex( r'-?\d*\.\d+([eE][-+]?\d+)?' )

def NumHex():
    return Regex( r'0[xX][0-9a-fA-F]+' )

def Num():
    return OneOf( NumHex(), NumFloat(), NumInt() )

def Bool():
    return Either( Lit('True'), Lit('False') )

def Link():
    return Regex( r"(http|ftp)s?://([a-z0-9-.]+\.)+[a-z]{2,}(/\S*)?" )

# see: https://www.regular-expressions.info/email.html
def Email():
    return Regex( r"[a-z0-9][a-z0-9._%+-]*@([a-z0-9-]+\.)+[a-z]{2,}", case=False )
    
def Fenced( boundary, esc=True, empty=True ):
    if isinstance(boundary,str):
        L,R = boundary, boundary
    else:
        L,R = boundary 

    # can only escape single chars
    assert len(R)==1 or not esc, ValueError('Right boundary should be a single char.')

    L = re.escape(L)
    R = re.escape(R)
    mul = '*' if empty else '+'

    if esc: 
        r = f'{L}(((\\\\{R})|[^{R}]){mul}){R}' 
    elif len(R)==1: 
        r = f'{L}([^{R}]{mul}){R}' 
    else: # less efficient
        r = f'{L}(((?!{R}).){mul}){R}' 

    return Regex(r)

def SqString( empty=True ):
    return Fenced( "'", empty=empty )

def DqString( empty=True ):
    return Fenced( '"', empty=empty )

def String( empty=True ):
    return Either( SqString(empty), DqString(empty) )

# ------------------------------------------------------------------------

def XML_attr():
    value = String().append( r'(\w+)' )
    return Seq( [r'\s+(\w+)', Seq([ r'\s*=\s*', value ])], skip=1 )

def XML_open( self=False ):
    end = r'\s*/>' if self else r'\s*>'
    return Seq( [r'<(\w+)', Any(XML_attr()), end], skip=1 )

def XML_self():
    return XML_open(True)

def XML_close():
    return Regex( r'</(\w+)\s*>' )

def XML_any():
    end = r'\s*/?>'
    tag = Seq( [r'<(\w+)', Any(XML_attr()), end], skip=1 )
    return Either( tag, XML_close() )
