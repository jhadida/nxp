
from collections import defaultdict
from nxp.parse import Rule, Validate, Process
from nxp.error import ParseError

# ------------------------------------------------------------------------

def _error(kw,*args):
    kw['call'] = lambda c,x,m: c.error(*args,exc=ParseError)

def _assert(kw,fun,*args):
    def cb(c,x,m):
        if not fun(c,x,m):
            c.error(*args,exc=ParseError)
    kw['call'].append(cb)

def _reject(kw,fun,*args):
    def cb(c,x,m):
        if fun(c,x,m):
            c.error(*args,exc=ParseError)
    kw['call'].append(cb)

def _replace(kw,rep):
    kw['proc'] = [ lambda t: rep ]
    _tag(kw,'rep')

# variable
# ------------------------------

def _let(kw,name,val,level=0):
    kw['call'].append( lambda c,x,m: x.set(name,val,level) )

def _inc(kw,name,level=0):
    kw['call'].append( lambda c,x,m: x.inc(name,level) )

def _dec(kw,name,level=0):
    kw['call'].append( lambda c,x,m: x.dec(name,level) )

# cursor manipulation
# ------------------------------

def _adv(kw,n):
    kw['call'].append( lambda c,x,m: c.nextchar(n) )

def _rev(kw,n):
    kw['call'].append( lambda c,x,m: c.nextchar(-n) )

def _goto(kw,name):
    kw['call'].append( lambda c,x,m: getattr(c,'goto_' + name)() )

def _pos(kw,name):
    kw['pre'].append( lambda c,x: getattr(c,name) )

def _pos_after(kw,name):
    kw['post'].append( lambda c,x,t: getattr(c,name) )

# scope manipulation
# ------------------------------

def _strict(kw,name):
    kw['call'].append( lambda c,x,m: x.strict(name) )

def _relax(kw,name):
    kw['call'].append( lambda c,x,m: x.relax(name) )

def _open(kw,name):
    kw['call'].append( lambda c,x,m: x.open(name) )

def _close(kw,*args):
    kw['call'].append( lambda c,x,m: x.close(*args) )

def _swap(kw,name):
    kw['call'].append( lambda c,x,m: x.swap(name) )

def _next(kw,name,*args):
    kw['call'].append( lambda c,x,m: x.next(name,*args) )

def _save(kw,*args):
    kw['call'].append( lambda c,x,m: x.save(m,*args) )

# rule actions
# ------------------------------

def _tag(kw,tag):
    kw['tag'] = tag
    _save(kw)

def _pre(kw,fun,*args):
    if callable(fun):
        kw['pre'].append( lambda c,x: fun(c,x,*args) )
    else:
        raise TypeError(f'Unexpected type: {type(fun)}')

def _post(kw,fun,*args):
    if callable(fun):
        kw['post'].append( lambda c,x,t: fun(c,x,t,*args) )
    elif isinstance(fun,str):
        kw['post'].append( lambda c,x,t: Validate[fun](t.text,*args) )
    else:
        raise TypeError(f'Unexpected type: {type(fun)}')

def _proc(kw,fun,*args):
    if callable(fun):
        kw['proc'].append( lambda t: fun(t,*args) )
    elif isinstance(fun,str):
        kw['proc'].append( lambda t: Process[fun](t,*args) )
    else:
        raise TypeError(f'Unexpected type: {type(fun)}')

def _call(kw,fun,*args):
    kw['call'].append( lambda c,x,m: fun(c,x,m,*args) )

# ------------------------------------------------------------------------

_argmap = {
    'error': _error, 'raise': _error, 'err': _error,
    'assert': _assert, 'reject': _reject,
    'replace': _replace, 'rep': _replace, 'sub': _replace,
    'define': _let, 'def': _let, 'let': _let,
    'increment': _inc, 'inc': _inc, 
    'decrement': _dec, 'dec': _dec, 
    'advance': _adv, 'adv': _adv,
    'reverse': _rev, 'rev': _rev,
    'goto': _goto,
    'pos_before': _pos, 'pos_after': _pos_after,
    'strict': _strict, 'relax': _relax,
    'open': _open, 'push': _open,
    'close': _close, 'pop': _close,
    'swap': _swap, 'swp': _swap,
    'next': _next, 'nxt': _next,
    'save': _save,
    'tag': _tag, 'label': _tag, 
    'pre': _pre, 'check': _pre, 'chk': _pre, 
    'post': _post, 'validate': _post, 'valid': _post,
    'proc': _proc, 'process': _proc, 'do': _proc,
    'call': _call, 'callback':_call ,'cb': _call
}

def _rule_arg(arg):
    """
    Create a dictionary with fields (defined as needed):
        tag, pre, post, proc, call
    
    from the arguments of rule definition. For example:
        [ r'\\\\', ('rep','\\') ]
    is converted to:
        { 'proc': lambda t: '\\' }

    Input should be a list (asserted in make_rule below), and only those
    items at indices >=1 are processed (the first item is the expression
    to be matched). Rule arguments are optional; rule definitions that 
    only contain the expression to be matched are called _consuming_ 
    rules, because they consume text without affecting the context.

    Items should be tuples of the form:
        ( 'command', args... )
    where 'command' is one of the keys defined in _argmap, each of which
    is associated with a corresponding function defined above. Keyword
    arguments (e.g. foo=5) are NOT supported.

    In some cases, items can simply be a string (e.g. 'close'), in which
    case the corresponding function is called without argument.
    """
    out = defaultdict(list)
    for a in arg[1:]:
        if isinstance(a,str): a=(a,)
        assert isinstance(a,tuple), TypeError(f'Rule arguments should be tuples or strings, but found "{type(a)}" instead.')
        assert isinstance(a[0],str), TypeError(f'Rule argument should begin with a command string, but found "{type(a[0])}" instead.')
        try:
            _argmap[ a[0] ]( out, *a[1:] )
        except KeyError:
            raise KeyError(f'Unknown rule argument: "{a[0]}"')
    return out

def make_rule(r):
    """
    Create a Rule object from a list definition. If input is already a
    Rule object, it is forwarded to output without alteration.

    Rule definitions should be of the form:
        [ expr, args... ]
    where 'expr' is either a regex string, Token to be matched, or None.
    Rule arguments are processed by the function _rule_arg above.
    """
    if isinstance(r,list):
        return Rule( r[0], **_rule_arg(r) )
    elif isinstance(r,Rule):
        return r
    else:
        raise TypeError(f'Unexpected rule type: {type(r)}')
