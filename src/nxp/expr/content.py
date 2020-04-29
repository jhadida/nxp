
import re
import logging
from typing import Pattern
from .match import TMatch
from .base import Token
from nxp.error import MatchError

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

    def match(self,cur):
        
        # attempt to match regex at current position
        p = cur.pos
        m = cur.match(self._pat)

        if m:
            # success: update cursor position
            cur.nextchar(m.end() - m.start())
            return TMatch( self, p, cur.pos, m, m[0] )
        else:
            raise MatchError()

# ------------------------------------------------------------------------

def conv(x): 
    """
    Convert string to regex.
    """
    if isinstance(x,Token):
        return x 
    elif isinstance(x,str):
        return Regex(x)
    else:
        raise TypeError(f'Unexpected type: {type(x)}')
