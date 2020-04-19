
import re 
from .ruledef import make_rule
from nxp import Cursor, Scope, Parser, ListBuffer, FileBuffer

# ------------------------------------------------------------------------

def make_cursor( c, r2l=False ):
    if isinstance(c,Cursor):
        return c 
    elif isinstance(c,str):
        return ListBuffer( c.splitlines(True), r2l ).cursor()
    else:
        raise TypeError(f'Unexpected type: {type(c)}')

def match( tok, text, r2l=False, cap=None ):
    return tok.match(make_cursor(text,r2l),cap)

def find( tok, text, r2l=False ):
    return tok.find(make_cursor(text,r2l))

def findall( tok, text, r2l=False ):
    return tok.findall(make_cursor(text,r2l))

def finditer( tok, text, r2l=False ):
    return tok.finditer(make_cursor(text,r2l))

# ------------------------------------------------------------------------

def make_scope( name, sub, pfx='', out=None ):
    """
    Create a dictionary of Scope objects of the form:
        { ...
            'scopename': Scope(...)
        }

    This function is implemented using tail recursion, in order to
    traverse the input dictionary and create the corresponding scopes.

    Input should be a dictionary with field "main", and may contain
    additional fields. All values should be either:
        * list of lists, each corresponding to a rule definition
        * dictionary with field "main", and possibly other fields

    ALL FIELD NAMES SHOULD ONLY CONTAIN LETTERS AND UNDERSCORES.

    Arbitrary nesting of scopes is possible, but note that the scope
    names defined as a result are composed to reflect this hierarchy.
    For example:
        {
            'main': ...
            'foo': {
                'main': ...
                'bar': ...
            }
        }
    leads to the following output:
        {
            'main'      : Scope(...) 
            'foo'       : Scope(...)
            'foo.bar'   : Scope(...)
        }

    Note in particular how the 'main' scope for the root preserves its 
    name, but 'foo.main' is remapped to 'foo'.
    """
    assert re.fullmatch( r'\w+', name ), ValueError('Scope name should only have letters and underscores.')

    # create / extend output
    if out is None:
        out = dict()
        key = name 
    else:
        key = pfx+name
        assert key not in out, KeyError(f'Duplicate scope name: {key}')
        pfx += name + '.'

    # create sub-scope
    if isinstance(sub,Scope):
        out[key] = sub
        return out
    elif isinstance(sub,dict):
        out[key] = Scope([ make_rule(r) for r in sub['main'] ])
    else:
        raise TypeError(f'Unexpected type: {type(sub)}')

    # sub-scopes
    for key,val in sub.items():
        if key == 'main': continue 
        if isinstance(val,list):
            key = pfx+key
            assert key not in out, KeyError(f'Duplicate scope name: {key}')
            out[key] = Scope([ make_rule(r) for r in val ])
        else:
            make_scope( key, val, pfx, out )

    return out

# ------------------------------------------------------------------------

def make_parser(p):
    """
    Create a Parser object from input language definition. If input is 
    already a Parser, it is forwarded to output without alteration.

    Language definition should be a dictionary with field "main", and 
    may contain additional fields. See make_scope above for more details
    about the requirements for field names and values, and _mkrule for 
    details about rule definitions.
    """
    if isinstance(p,dict):
        # create scope dictionary
        scope = make_scope( 'main', p['lang'] )

        # apply options
        strict = p.setdefault('strict',[])
        if 'nonstrict' in p:
            strict = [ name for name in scope.keys() if name not in p['nonstrict'] ]
        if isinstance(strict,bool):
            strict = scope.keys() if strict else []
        for name in strict: 
            scope[name].strict = True

        # create parser
        return Parser(scope)
    elif isinstance(p,Parser):
        return p 
    else:
        raise TypeError(f'Unexpected type: {type(p)}')

def parsefile( parser, fpath, r2l=False ):
    return make_parser(parser).parse(FileBuffer(fpath,r2l).cursor())

def parselines( parser, lines, r2l=False ):
    return make_parser(parser).parse(ListBuffer(lines,r2l).cursor())

def parse( parser, text, r2l=False ):
    return parselines( parser, text.splitlines(True), r2l )
