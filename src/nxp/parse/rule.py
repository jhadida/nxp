
import logging
from itertools import count
from .match import RMatch
from nxp import Token, TElement, Regex

class PreCheckError(Exception): pass
class PostCheckError(Exception): pass

# ------------------------------------------------------------------------

def _callable_list(L):
    if not isinstance(L,list): L = [L]
    assert all([ callable(f) for f in L ]), ValueError('Items should be callable.')
    return L

# ------------------------------------------------------------------------

class Rule:
    """
    Rule objects associate a Token to be matched, with different actions
    that are triggered in case of match. These actions are:

    pre     pre-condition
            function (cursor,context) -> bool
    post    post-condition
            function (cursor,context,token) -> bool
    proc    post-processing
            function (text) -> text
    call    callback
            function (cursor,context,match) -> void
    """
    _id_ = count(0)
    __slots__ = ('_id','_expr','_tag','_pre','_post','_proc','_call')

    def __init__( self, expr, tag='',
        pre=[], post=[], proc=[], call=[] ):

        if isinstance(expr,str): expr = Regex(expr)
        assert expr is None or isinstance(expr,Token), \
            TypeError('Expression to be matched should be a Token object, or None.')

        self._id = next(self._id_)
        self._expr = expr 
        self._tag  = tag
        self._pre  = _callable_list(pre)
        self._post = _callable_list(post)
        self._proc = _callable_list(proc)
        self._call = _callable_list(call)
        logging.debug('[Rule:%d] Initialized: %s',self._id,str(expr))

    def __str__(self):
        return str(self._expr)

    @property
    def tag(self): return self._tag

    def match(self,cur,ctx):

        # check pre-conditions
        for cond in self._pre:
            if not cond(cur,ctx):
                logging.debug('[Rule:%d] Precondition failed.',self._id)
                raise PreCheckError()

        # match pattern (raise error on fail)
        if self._expr is None:
            pos = cur.pos 
            tok = TElement(None).append(pos,pos)
        else:
            tok = self._expr.match(cur)

        # check post-conditions
        for cond in self._post:
            if not cond(cur,ctx,tok):
                logging.debug('[Rule:%d] Postcondition failed.',self._id)
                raise PostCheckError()

        # notify
        logging.debug('[Rule:%d] Match: %s - %s', self._id, tok.beg, tok.end)

        # process matched text sequentially
        txt = tok.text()
        for p in self._proc:
            txt = list(map(p,txt))


        # call functions
        out = RMatch(self,tok,txt)
        for fun in self._call:
            fun(cur,ctx,out)

        return out

# ------------------------------------------------------------------------

class Scope:
    """
    """
    __slots__ = ('_rule','strict')
    def __init__(self,rule,strict=False):
        assert isinstance(rule,list) and all([ isinstance(r,Rule) for r in rule ]), \
            TypeError('Input should be a list of Rule objects')

        self._rule = rule
        self.strict = strict 

    def __len__(self): return len(self._rule)
    def __getitem__(self,key): return self._rule[key]
    def __iter__(self): return iter(self._rule)
    