
from copy import deepcopy
from itertools import combinations

"""
Multiplicity objects are tuple generators. 
Each tuple must be of the form (min,max).
"""

# ------------------------------------------------------------------------

def _range_overlap(a,b):
    if isinstance(a,int): a = (a,a)
    if isinstance(b,int): b = (b,b)
    return a[0] <= b[1] and b[0] <= a[1]

def _validate_range(r):
    # JH: 0<= changed to 0< to prevent 0 multiplicity
    assert len(r)==2 and 0 < r[0] <= r[1], ValueError('Bad multiplicity range.')

def _to_range(x):
    if isinstance(x,int):
        x = (x,x)
    elif isinstance(x,str):
        """
        Convert strings of the form:
            '1'     =>  (1,1)           exactly once
            '1-3'   =>  (1,3)           between 1 and 3
            '4+'    =>  (4,Inf)         4 or more
            '5-'    =>  (1,5)           between 1 and 5
        """
        if x.endswith('+'):
            x = ( int(x[:-1]), float('Inf') )
        elif x.endswith('-'):
            x = ( 1, int(x[:-1]) )
        elif '-' in x:
            x = tuple( int(x) for x in x.split('-') )
        else:
            x = int(x)
            x = (x,x)

    _validate_range(x)
    return x

# ------------------------------------------------------------------------

class mulrange:
    def __init__(self,*arg):
        self.range = range(*arg) 
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
            yield (m,m)

def mulparse(mul):
    """
    Parse input multiplicity, either:
        string
        integer
        tuple 
        list therof
        iterable object

    Output is either a list of range tuples sorted by lower bound, or a multiplicity object.
    """

    # try to parse input to a list of range tuples
    out = []
    if isinstance(mul,str):
        out.extend(mul.split(','))
    elif isinstance(mul,int):
        out.append(mul)
    elif isinstance(mul,tuple):
        out.append(mul)
    elif isinstance(mul,list):
        out.extend(mul)
    else:
        try:
            # there could be an infinite number of ranges (e.g. odd multiplicities)
            # so just iterate one
            for m in mul:
                _validate_range(m)
                break 
        except:
            raise ValueError('Bad multiplicity object.')
        
        return deepcopy(mul)

    # convert and validate 
    out = [ _to_range(x) for x in out ]

    # sort by lower-bound
    out = sorted( out, key = lambda x: x[0] )

    # check for overlaps
    for a,b in combinations(out,2):
        if _range_overlap(a,b):
            raise ValueError(f'Overlapping multiplicities {a} and {b}')

    return out
