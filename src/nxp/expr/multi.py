
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
    assert len(r)==2 and 0 <= r[0] <= r[1], ValueError('Bad multiplicity range.')

def _to_range(x):
    if isinstance(x,int):
        x = (x,x)
    _validate_range(x)
    return x

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
        """
        Convert strings of the form:
            '6'     =>  [ 6 ]
            '5?'    =>  [ 0, 5 ]
            '2-7'   =>  [ (2,7) ]
            '7-'    =>  [ (1,7) ]
            '3+?'   =>  [ 0, (3,Inf) ]
        """

        # deal with ?
        if mul.endswith('?'):
            out.append(0)
            mul = mul[:-1]
        
        # parse format
        if mul.endswith('+'):
            out.append(( int(mul[:-1]), float('Inf') ))
        elif mul.endswith('-'):
            out.append(( 1, int(mul[:-1]) ))
        elif '-' in mul:
            out.append(( int(x) for x in mul.split('-') ))
        else:
            out.append(int(mul))

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
            raise ValueError('Overlapping multiplicities %s and %s' % ( str(a), str(b) ))

    return out
