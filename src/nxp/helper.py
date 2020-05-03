
import re 
from .ruledef import make_rule
from nxp import Cursor, ListBuffer, FileBuffer, Transform, Scope, Parser

# ------------------------------------------------------------------------
# EXPRESSION
# ------------------------------------------------------------------------

def make_cursor( c, r2l=False ):
    if isinstance(c,Cursor):
        return c 
    elif isinstance(c,str):
        assert len(c) > 0, ValueError('Cannot create a cursor from empty string.')
        return ListBuffer( c.splitlines(True), r2l ).cursor()
    else:
        raise TypeError(f'Unexpected type: {type(c)}')

def match( tok, text, r2l=False ):
    return tok.match(make_cursor(text,r2l))

def find( tok, text, r2l=False, multi=False ):
    yield from tok.find(make_cursor(text,r2l),multi)

# ------------------------------------------------------------------------
# PARSER
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
        assert isinstance(sub['main'],list), TypeError(f'main (sub)scope should be a list (prefix: {pfx}).')
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
    already a Parser, it is reset before being returned.

    Language definition should be a dictionary with field "main", and 
    may contain additional fields. See make_scope above for more details
    about the requirements for field names and values, and _mkrule for 
    details about rule definitions.
    """
    if isinstance(p,Parser):
        return p.reset()
    elif isinstance(p,dict):
        # create scope dictionary
        scope = make_scope( 'main', p['lang'] )

        # strict scope processing
        strict = p.setdefault('strict',[])
        if 'nonstrict' in p:
            strict = [ name for name in scope.keys() if name not in p['nonstrict'] ]
        if isinstance(strict,bool):
            strict = scope.keys() if strict else []
        for name in strict: 
            scope[name].strict = True

        # start/end scopes
        start = p.setdefault('start','main')
        finish = p.setdefault('finish',None)

        return Parser(scope,start,finish)
    else:
        raise TypeError(f'Unexpected type: {type(p)}')

def parsebuf( parser, buffer ):
    return make_parser(parser).parse(buffer.cursor())

def parsefile( parser, fpath, r2l=False ):
    return parsebuf( parser, FileBuffer(fpath,r2l) )

def parsetext( parser, text, r2l=False ):
    return parsebuf( parser, ListBuffer(text.splitlines(True),r2l) )

# ------------------------------------------------------------------------
# PROCESSING
# ------------------------------------------------------------------------

def procbuf( parser, callback, buffer, first=(0,0), last=None, **kv ):
    """
    Parse input buffer, and invoke callback for each matched element.

    Callback function should match the following prototype:
        callback( transform, element )
    where 
        'transform' is a Transform object, and 
        'element' is a RNode object.
    """
    if last is None: last = buffer.lastpos 
    tsf = Transform( buffer, first, last )
    res = make_parser(parser).parse( buffer.cursor(*first) )
    for elm in res: callback(tsf,elm,**kv)
    assert len(tsf) == 0 or tsf[-1].end <= last, RuntimeError('Last position exceeded.')
    return tsf

def procfile( parser, callback, infile, r2l=False, **kv ):
    """
    Process input file using callback function to transform every match 
    in the "main" scope found during parsing. 
    
    The callback function should be:
        callback( transform, element )
    """
    buf = FileBuffer(infile,r2l)
    return procbuf( parser, callback, buf, **kv )

def proctext( parser, callback, text, r2l=False, **kv ):
    """
    Same as above, but process input text.
    """
    buf = ListBuffer(text.splitlines(True),r2l)
    return procbuf( parser, callback, buf, **kv )
