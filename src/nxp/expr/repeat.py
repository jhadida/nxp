
import logging
from copy import deepcopy
from .match import TMatch
from .base import Token
from .content import conv
from .util import TokenChain
from nxp.error import MatchError

# ------------------------------------------------------------------------

"""
Multiplicity objects are tuple generators. 
Each tuple must be of the form (min,max).
"""

class mulrange:
    """
    Convert integer range to tuple generator.
    """
    __slots__ = ('range')
    def __init__(self,mul):
        assert isinstance(mul,range), TypeError(f'Unexpected type: {type(mul)}')
        self.range = mul
    def __str__(self):
        return str(self.range)
    def __repr__(self):
        return repr(self.range)
    def __len__(self):
        return len(self.range)
    def __getitem__(self,key):
        return self.range.__getitem__(key)
    def __iter__(self):
        for m in self.range:
            yield m,m

class mulseq:
    """
    Infinite sequence as multiplicity
    """
    __slots__ = ('value','step')
    def __init__(self,start=1,step=1):
        assert isinstance(start,int), TypeError(f'Bad start type: {type(start)}')
        assert isinstance(step,int), TypeError(f'Bad step type: {type(step)}')
        assert start >= 0, ValueError(f'Start should be non-negative: {start}')
        assert step > 0, ValueError(f'Step should be positive: {step}')
        
        self.value = start 
        self.step = step
    def __str__(self):
        return f'V[k] = {self.step}k + {self.value}'
    def __repr__(self):
        return str((self.value,self.step))
    def __getitem__(self,k):
        return self.step*k + self.value 
    def __iter__(self):
        while True:
            yield self.value, self.value
            self.value += self.step

def mulparse(mul):
    """
    Parse input multiplicity, either:
        string
        integer
        tuple 
        list therof
        range object
        iterable object

    Output is either a list of range tuples sorted by lower bound, or a multiplicity object.
    """

    # check utils
    # TODO: could add "and r[0]*r[1] > 0" to forbid (0,0)?
    valid = lambda r: len(r)==2 and 0 <= r[0] <= r[1] 
    overlap = lambda a,b: a[0] <= b[1] and b[0] <= a[1]

    # first, convert input to a list
    out = []
    if isinstance(mul,str):
        out.extend(mul.split(','))
    elif isinstance(mul,int):
        out.append(mul)
    elif isinstance(mul,tuple):
        out.append(mul)
    elif isinstance(mul,list):
        out.extend(mul)
    elif isinstance(mul,range):
        assert mul.start > 0 and mul.step > 0, ValueError(f'Bad range: {mul}')
        return mulrange(mul)
    else:
        # there could be an infinite number of ranges (e.g. odd multiplicities)
        # just iterate a couple
        it = iter(mul)
        m0 = next(it)
        m1 = next(it)
        assert valid(m0) and valid(m1) and not overlap(m0,m1), ValueError(f'Bad iterable: {mul}')
        
        return deepcopy(mul)

    # second, rebuild list by converting each element
    for k,x in enumerate(out):
        if isinstance(x,int):
            x = (x,x)
        elif isinstance(x,str):
            """
            Convert strings of the form:
                '1'     =>  (1,1)     exactly once
                '1-3'   =>  (1,3)     between 1 and 3
                '4+'    =>  (4,Inf)   4 or more
                '5-'    =>  (0,5)     fewer than 5
            """
            if x.endswith('+'):
                x = ( int(x[:-1]), float('Inf') )
            elif x.endswith('-'):
                x = ( 0, int(x[:-1]) )
            elif '-' in x:
                x = tuple( int(x) for x in x.split('-') )
            else:
                x = int(x)
                x = (x,x)

        assert valid(x), ValueError(f'Bad range: {x}')
        out[k] = x

    # sort by lower-bound
    out = sorted( out, key = lambda x: x[0] )

    # check for overlaps
    for a,b in zip(out,out[1:]):
        if overlap(a,b):
            raise ValueError(f'Overlapping multiplicities {a} and {b}.')

    return out

# ------------------------------------------------------------------------

class Rep(Token):
    def __init__(self,tok,mul,sep=None):
        super().__init__()

        self._tok = conv(tok)
        self._mul = mulparse(mul)
        self._sep = conv(sep) if sep else None

        logging.debug(f'[Rep] Initialise with token: {tok}')

    @property
    def token(self): return self._tok

    def __str__(self):
        return f'#({self._tok})'

    def match(self,cur):
        out = TokenChain()
        pos = cur.pos
        chk = None
        
        # iterate over ranges
        for rmin, rmax in self._mul:

            while len(out) < rmax:

                # remember position before separator
                tmp = cur.pos 
                try:
                    # match separator if at least one match exists
                    if self._sep and len(out) > 0:
                        self._sep.match(cur) 

                    # match token
                    out.append(self._tok.match(cur))
                except MatchError:
                    cur.pos = tmp # restore position before separator
                    break

            # Note: we should check that at least one match was successful
            # for the current range. But actually testing against rmin is
            # sufficient, because ranges are not allowed to overlap. This
            # is critical: the upper bound of one range should be STRICTLY
            # less than the lower bound of the next range.
            if len(out) >= rmin:
                chk = cur.pos # update checkpoint
                out.commit()
            else:
                out.revert()
                break
        
        # sanity check
        assert out.isvalid(), RuntimeError('[bug] Invalid TokenChain.')

        # if no checkpoint was created, then no range was satisfied
        if chk is None:
            raise MatchError()
        else:
            cur.pos = chk # restore cursor to last checkpoint
            txt = cur.buffer.between( pos, cur.pos )
            return TMatch( self, pos, cur.pos, out.tok, txt )
