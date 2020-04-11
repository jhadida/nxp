
import re
import math
import logging
from copy import copy
from .match import MatchError
from .base import Token

# ------------------------------------------------------------------------

class Regex(Token):
    def __init__(self, pat, case=True):
        super().__init__()
        assert isinstance(pat,str), TypeError('Pattern should be a string.')

        if case:
            self._pat = re.compile( pat )
        else:
            self._pat = re.compile( pat, re.I )

        logging.debug('[Regex] Initialize with pattern: %s',self._pat.pattern)

    def __str__(self):
        return self._pat.pattern

    @property
    def pat(self): return self._pat

    def _match_once(self,cur,out):
        p = cur.pos
        m = cur.match(self._pat)
        if m:
            cur.nextchar(m.end() - m.start())
            out.append( p, cur.pos, m, m[0] )
            return True
        else:
            return False

# ------------------------------------------------------------------------

class _TokenList(Token):
    def __init__(self):
        super().__init__()
        self._tok = []
    
    def __len__(self): return len(self._tok)
    def __iter__(self): return iter(self._tok)
    def __getitem__(self,key): return self._tok[key]

    def prepend(self,tok):
        assert isinstance(tok,Token), TypeError('Expected a Token')
        self._tok.insert(0,tok)
        return self 

    def append(self,tok): 
        assert isinstance(tok,Token), TypeError('Expected a Token')
        self._tok.append(tok)
        return self 

    def extend(self,tok):
        assert all([ isinstance(x,Token) for x in tok ]), TypeError('All elements should be Token')
        self._tok.extend(tok)
        return self 

# ------------------------------------------------------------------------

class Set(_TokenList):
    def __init__(self, tok=[], min=1, max=math.inf):
        super().__init__()
        assert all( isinstance(t,Token) for t in tok ), TypeError('Set items should be Token objects.')

        self._tok = tok
        self._min = min
        self._max = max
        logging.debug('[Set] Initialize with %d token(s).',len(tok))

    def __str__(self):
        return '{' + ', '.join([ str(t) for t in self._tok ]) + '}'

    @property
    def min(self): return self._min
    @property
    def max(self): return self._max
    
    @min.setter
    def min(self,val):
        assert val >= 0, ValueError('min should be >= 0')
        self._min = val
        self._max = max(self._min,self._max)
    @max.setter
    def max(self,val):
        assert val >= self._min, ValueError('max should be >= min')
        self._max = val

    def _match_once(self,cur,out):
        tmp = []
        pos = cur.pos
        nm = -1
        while nm < len(tmp) < self._max:
            nm = len(tmp)
            for tok in self._tok:
                try:
                    tmp.append(tok.match(cur))
                    break
                except MatchError:
                    pass

        if len(tmp) >= self._min:
            txt = cur.text( pos, cur.pos )
            out.append( pos, cur.pos, tmp, txt )
            return True 
        else:
            cur.pos = pos
            return False

# ------------------------------------------------------------------------

class Seq(_TokenList):
    def __init__(self, tok=[], skip=False):
        super().__init__()
        assert all( isinstance(t,Token) for t in tok ), TypeError('Sequence items should be Token objects.')

        self._tok = tok
        self._skp = skip 
        logging.debug('[Seq] Initialize with %d token(s).',len(tok))

    def __str__(self):
        return '[' + ', '.join([ str(t) for t in self._tok ]) + ']'

    @property
    def skip(self): return self._skp 

    @skip.setter
    def skip(self,val):
        if val == True:
            s = range(len(self._tok))
        elif val == False:
            s = []
        elif isinstance(val,list):
            s = val
        else:
            ValueError('Bad skip value.')

        self._skp = set(s)

    def _match_once(self,cur,out):
        tmp = []
        pos = cur.pos
        for num,tok in enumerate(self._tok):
            try: 
                tmp.append(tok.match(cur))
            except MatchError:
                if num not in self._skp:
                    cur.pos = pos 
                    return False
        
        txt = cur.text( pos, cur.pos )
        out.append( pos, cur.pos, tmp, txt )
        return True 

# ------------------------------------------------------------------------

"""
a | b   Set( [a,b], min=1 )
a & b   Set( [a,b], min=2 )
a ^ b   Set( [a,b], max=1 )
a + b   Seq( [a,b] )
"""

def _conv(x): 
    if isinstance(x,Token):
        return x 
    elif isinstance(x,str):
        return Regex(x)
    else:
        raise TypeError('Unexpected type: %s' % type(x))

# composition operations
def _Token_or(self,tok):
    if isinstance(self,Set):
        return self.append(_conv(tok))
    else:
        return Set( [self, _conv(tok)], min=1 )

def _Token_and(self,tok):
    if isinstance(self,Set) and self.min==len(self):
        self.append(_conv(tok))
        self._min = len(self)
    else:
        return Set( [self, _conv(tok)], min=2 )

def _Token_xor(self,tok):
    if isinstance(self,Set) and self.max==1:
        return self.append(_conv(tok))
    else:
        return Set( [self, _conv(tok)], max=1 )

def _Token_add(self,tok):
    if isinstance(self,Seq):
        return self.append(_conv(tok))
    else:
        return Seq( [self, _conv(tok)] )

def _Token_ror(self,oth):
    if isinstance(self,Set):
        return self.prepend(_conv(oth))
    else:
        return Set( [_conv(oth), self], min=1 )

def _Token_rand(self,oth):
    if isinstance(self,Set) and self.min==len(self):
        self.prepend(_conv(oth))
        self._min = len(self)
    else:
        return Set( [_conv(oth),self], min=2 )

def _Token_rxor(self,oth):
    if isinstance(self,Set) and self.max==1:
        return self.prepend(_conv(oth))
    else:
        return Set( [_conv(oth), self], max=1 )

def _Token_radd(self,oth):
    if isinstance(self,Seq):
        return self.prepend(_conv(oth))
    else:
        return Seq( [_conv(oth), self] )

# extend Token interface
Token.__or__  = _Token_or
Token.__and__ = _Token_and
Token.__xor__ = _Token_xor 
Token.__add__ = _Token_add

Token.__ror__  = _Token_ror
Token.__rand__ = _Token_rand
Token.__rxor__ = _Token_rxor 
Token.__radd__ = _Token_radd
