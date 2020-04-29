
import logging
from itertools import count
from .match import RMatch
from nxp.expr import Token, TMatch, Regex
from nxp.error import PreCheckError, PostCheckError

# ------------------------------------------------------------------------

def _callable_list(L):
    if L is None:
        L = [] 
    elif not isinstance(L,list): 
        L = [L]
        
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
            function (cursor,context,tmatch) -> bool
    proc    post-processing
            function (text) -> text
    call    callback
            function (cursor,context,rmatch) -> void
    """
    __id__ = count(0)
    __slots__ = ('tag','_id','_expr','_pre','_post','_proc','_call')

    def __init__( self, expr, tag='',
        pre=None, post=None, proc=None, call=None ):

        if isinstance(expr,str): expr = Regex(expr)
        assert expr is None or isinstance(expr,Token), \
            TypeError('Expression should be a Token or None.')

        self.tag = tag
        self._id = next(self.__id__)

        self._expr = expr 
        self._pre  = _callable_list(pre)
        self._post = _callable_list(post)
        self._proc = _callable_list(proc)
        self._call = _callable_list(call)
        logging.debug(f'[Rule:{self.id}] Initialized: {expr}')

    @property
    def id(self): return self._id

    def __str__(self):
        return str(self._expr)

    def match(self,cur,ctx):

        # check pre-conditions
        for cond in self._pre:
            if not cond(cur,ctx):
                logging.debug(f'[Rule:{self.id}] Precondition failed.')
                raise PreCheckError()

        # match pattern (raise error on fail)
        if self._expr is None:
            pos = cur.pos 
            match = TMatch(None,pos,pos)
        else:
            match = self._expr.match(cur)

        # check post-conditions
        for cond in self._post:
            if not cond(cur,ctx,match):
                logging.debug(f'[Rule:{self.id}] Postcondition failed.')
                raise PostCheckError()

        # notify
        logging.debug(f'[Rule:{self.id}] Match: {match.beg} - {match.end}')

        # process matched text sequentially
        txt = match.text
        for p in self._proc:
            txt = p(txt)

        # call functions
        out = RMatch(self,match,txt)
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
    