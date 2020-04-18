
import re
import math
import logging
from typing import Pattern
from .match import MatchError
from .base import Token
from .util import TokenSet

# ------------------------------------------------------------------------

class Regex(Token):
    def __init__(self, pat, *arg, case=True):
        super().__init__()

        if isinstance(pat,str):
            flag = 0 if case else re.I 
            if arg: flag = arg[0] | flag 
            try:
                self._pat = re.compile( pat, flag )
            except:
                raise RuntimeError(f'Could not compile: {pat}')
        elif isinstance(pat,Pattern): 
            self._pat = pat 
        else:
            raise TypeError(f'Unexpected type: {type(pat)}')

        logging.debug(f'[Regex] Initialize with pattern: {self.pattern}')

    @property
    def pattern(self): return self._pat.pattern
    @property
    def flags(self): return self._pat.flags

    def __str__(self):
        return self.pattern

    # copy of regex is not implemented before Python 3.7
    def __copy__(self):
        return Regex( self._pat )
    def __deepcopy__(self,memo):
        return Regex( self._pat )

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

def _conv(x): 
    if isinstance(x,Token):
        return x 
    elif isinstance(x,str):
        return Regex(x)
    else:
        raise TypeError(f'Unexpected type: {type(x)}')

class _TokenList(Token):
    def __init__(self):
        super().__init__()
        self._tok = []
    
    def __len__(self): return len(self._tok)
    def __iter__(self): return iter(self._tok)
    def __getitem__(self,key): return self._tok[key]

    def _assign(self,tok):
        assert len(tok) > 0, ValueError('List should contain at least one token.')
        self._tok = [ _conv(t) for t in tok ]

    def prepend(self,tok):
        self._tok.insert(0,_conv(tok))
        return self 

    def append(self,tok): 
        self._tok.append(_conv(tok))
        return self 

    def extend(self,tok):
        self._tok.extend([ _conv(t) for t in tok ])
        return self 

# ------------------------------------------------------------------------

class Set(_TokenList):
    def __init__(self, tok=[], min=1, max=math.inf):
        super().__init__()
        self._assign(tok)
        self._min = min
        self._max = max
        logging.debug(f'[Set] Initialize with {len(tok)} token(s).')

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
        tok = TokenSet(self._tok)
        pos = cur.pos
        tmp = []
        nm = -1
        while nm < len(tmp) < self._max:
            nm = len(tmp)
            for it in tok:
                try:
                    tmp.append(it.tok.match(cur))
                    tok.remove(it)
                    break
                except MatchError:
                    pass

        if len(tmp) >= self._min:
            txt = cur.buffer.between( pos, cur.pos )
            out.append( pos, cur.pos, tmp, txt )
            return True 
        else:
            cur.pos = pos
            return False

# ------------------------------------------------------------------------

class Seq(_TokenList):
    def __init__(self, tok=[], skip=None, maxskip=None):
        super().__init__()
        self._assign(tok)

        if skip is True or (maxskip and skip is None):
            skip = range(len(tok))
        if skip is None or skip is False:
            skip = []
        if isinstance(skip,int):
            skip = [skip]

        assert isinstance(skip,list), TypeError(f'Unexpected type: {type(skip)}')
        assert all([ 0 <= s < len(tok) for s in skip ]), IndexError('Skip indices out of range.')

        if maxskip is None:
            maxskip = min( len(tok)-1, len(skip) )

        assert 0 <= maxskip <= len(skip), ValueError('Bad maxskip value.')
        
        self._skp = frozenset(skip)
        self._msk = maxskip
        logging.debug(f'[Seq] Initialize with {len(tok)} token(s).')

    def __str__(self):
        return '[' + ', '.join([ str(t) for t in self._tok ]) + ']'

    @property
    def skip(self): return self._skp 

    def _match_once(self,cur,out):
        tmp = []
        pos = cur.pos
        skp = 0
        for k,tok in enumerate(self._tok):
            try: 
                tmp.append(tok.match(cur))
            except MatchError:
                skp += 1
                if skp > self._msk or k not in self._skp:
                    cur.pos = pos 
                    return False
        
        txt = cur.buffer.between( pos, cur.pos )
        out.append( pos, cur.pos, tmp, txt )
        return True 

# ------------------------------------------------------------------------

"""
a | b   Set( [a,b], min=1 )
a & b   Set( [a,b], min=2 )
a ^ b   Set( [a,b], max=1 )
a + b   Seq( [a,b] )
"""

# composition operations
def _Token_or(self,tok):
    if isinstance(self,Set):
        return self.append(tok)
    else:
        return Set( [self,tok], min=1 )

def _Token_and(self,tok):
    if isinstance(self,Set) and self.min==len(self):
        self.append(tok)
        self._min = len(self)
    else:
        return Set( [self,tok], min=2 )

def _Token_xor(self,tok):
    if isinstance(self,Set) and self.max==1:
        return self.append(tok)
    else:
        return Set( [self,tok], max=1 )

def _Token_add(self,tok):
    if isinstance(self,Seq):
        return self.append(tok)
    else:
        return Seq( [self,tok] )

def _Token_ror(self,oth):
    if isinstance(self,Set):
        return self.prepend(oth)
    else:
        return Set( [oth,self], min=1 )

def _Token_rand(self,oth):
    if isinstance(self,Set) and self.min==len(self):
        self.prepend(oth)
        self._min = len(self)
    else:
        return Set( [oth,self], min=2 )

def _Token_rxor(self,oth):
    if isinstance(self,Set) and self.max==1:
        return self.prepend(oth)
    else:
        return Set( [oth,self], max=1 )

def _Token_radd(self,oth):
    if isinstance(self,Seq):
        return self.prepend(oth)
    else:
        return Seq( [oth,self] )

# extend Token interface
Token.__or__  = _Token_or
Token.__and__ = _Token_and
Token.__xor__ = _Token_xor 
Token.__add__ = _Token_add

Token.__ror__  = _Token_ror
Token.__rand__ = _Token_rand
Token.__rxor__ = _Token_rxor 
Token.__radd__ = _Token_radd
