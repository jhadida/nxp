
import math
import logging
from .match import TMatch
from .base import Token
from .content import conv
from .util import TokenSet
from nxp.error import MatchError

# ------------------------------------------------------------------------

class _TokenList(Token):
    """
    Used as a base-class for Set and Seq below.
    """
    def __init__(self):
        super().__init__()
        self._tok = []
    
    @property
    def tokens(self): return self._tok 

    def __len__(self): return len(self._tok)
    def __iter__(self): return iter(self._tok)
    def __getitem__(self,key): return self._tok[key]

    def _assign(self,tok):
        assert len(tok) > 0, ValueError('List should contain at least one token.')
        self._tok = [ conv(t) for t in tok ]

    def prepend(self,tok):
        self._tok.insert(0,conv(tok))
        return self 

    def append(self,tok): 
        self._tok.append(conv(tok))
        return self 

    def extend(self,tok):
        self._tok.extend([ conv(t) for t in tok ])
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

    def match(self,cur):

        # use token set for fast removal and iteration
        tok = TokenSet(self._tok)
        pos = cur.pos # remember initial position 
        out = []
        nm = -1

        # match tokens until max is reached
        while nm < len(out) < self._max:

            # save current number of matches
            nm = len(out)

            # attempt to match a token
            for it in tok:
                try:
                    out.append(it.tok.match(cur))
                    tok.remove(it) # remove token to match others
                    break
                except MatchError:
                    pass

        # check that sufficiently many tokens were matched
        if len(out) >= self._min:
            txt = cur.buffer.between( pos, cur.pos )
            return TMatch( self, pos, cur.pos, out, txt )
        else:
            cur.pos = pos # reset cursor to input position
            raise MatchError()

# ------------------------------------------------------------------------

class Seq(_TokenList):
    def __init__(self, tok=[], skip=None, maxskip=None):
        super().__init__()
        self._assign(tok)

        # list of token indices to skip
        if skip is True or (maxskip and skip is None):
            skip = range(len(tok))
        if skip is None or skip is False:
            skip = []
        if isinstance(skip,int):
            skip = [skip]

        assert isinstance(skip,list), TypeError(f'Unexpected type: {type(skip)}')
        assert all([ 0 <= s < len(tok) for s in skip ]), IndexError('Skip indices out of range.')

        # maximum number of tokens to skip
        if maxskip is None:
            maxskip = min( len(tok)-1, len(skip) )

        assert 0 <= maxskip <= len(skip), ValueError('Bad maxskip value.')
        
        # assign members
        self._skp = frozenset(skip)
        self._msk = maxskip
        logging.debug(f'[Seq] Initialize with {len(tok)} token(s).')

    def __str__(self):
        return '[' + ', '.join([ str(t) for t in self._tok ]) + ']'

    @property
    def skip(self): return self._skp 
    @property 
    def maxskip(self): return self._msk

    def match(self,cur):
        out = []
        pos = cur.pos # save initial position for reset
        skp = 0

        # iterate over tokens to be matched
        for k,tok in enumerate(self._tok):
            try: # match tokens in sequence
                out.append(tok.match(cur))
            except MatchError:
                skp += 1 # check number of skips and skip index
                if skp > self._msk or k not in self._skp:
                    cur.pos = pos # reset cursor and abort
                    raise MatchError()
        
        # success: save match
        txt = cur.buffer.between( pos, cur.pos )
        return TMatch( self, pos, cur.pos, out, txt )
