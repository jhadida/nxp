
import logging
from copy import copy, deepcopy
from .match import TElement, MatchError
from .multiplicity import mulparse

# ------------------------------------------------------------------------

class Token:
    """
    A Token is the abstract parent of all expressions (Regex, Set, Seq, etc.).
    They mainly implement the logic of a match with multiplicity.

    The multiplicity defines the allowed numbers of repetitions for a given
    token (sequentially). The code to match a single instance of a token is 
    implemented in derived classes with the method _match_once(), which:
    - returns True if there is a match, False otherwise;
    - takes a cursor in input, and updates it in case of match;
    - takes a TElement object in input, and appends to it in case of match.

    The overall match() method takes a cursor in input, and returns a TElement
    object if the multiplicity constraints are satisfied, otherwise None.
    """

    def __init__(self): # multiplicity defaults to 1
        self._mul = mulparse(1) 

    # to be overloaded
    def __str__(self): 
        raise NotImplementedError()

    def _match_once(self,cur,out):
        raise NotImplementedError()

    # multiplicity
    def mul(self,m):
        self._mul = mulparse(m)
        return self
    def __imul__(self,m):
        return self.mul(m)
    def __mul__(self,m):
        out = deepcopy(self)
        return out.mul(m)

    # matching
    def __call__(self,cur):
        return self.match(cur)
        
    def match(self,cur):
        """
        Matching with multiplicity iterates over allowed ranges of 
        repetitions, and attempts to match single instances of the 
        token by calling _match_once().

        The match terminates when one of the following happens:
        - The attempt to satisfy the current range succeeds, and there 
        are no more ranges.
        - The attempt to satisfy the current range fails, in which case 
        the match object is reverted to its last commited state, and the 
        cursor is restored to the corresponding position.
        """
        logging.debug('[Token] Match token at: L=%d, C=%d', *cur.pos)

        out = TElement(self)
        pos = cur.pos
        for rmin, rmax in self._mul:

            while len(out) < rmax:
                if not self._match_once(cur,out):
                    break
            
            if len(out) >= rmin:
                logging.debug('[Token] Match success (m=%d).',len(out))
                pos = cur.pos
                out.commit()
            else:
                logging.debug('[Token] Match fail.')
                out.revert()
                break
        
        cur.pos = pos
        if out.isempty(): raise MatchError()
        assert out.isvalid(), RuntimeError('[bug] Invalid TElement object.')
        return out

    # search
    def find(self,cur):
        logging.debug('[Token] Find token at: L=%d, C=%d', *cur.pos)
        while cur.isvalid():
            try:
                return self.match(cur)
            except:
                cur.nextchar()

    def findall(self,cur):
        logging.debug('[Token] Find all tokens at: L=%d, C=%d', *cur.pos)
        out = []
        while cur.isvalid():
            try:
                out.append(self.match(cur))
            except:
                cur.nextchar()

        return out

    def finditer(self,cur):
        logging.debug('[Token] Iterate find token at: L=%d, C=%d', *cur.pos)
        while cur.isvalid():
            try:
                yield self.match(cur)
            except:
                cur.nextchar()
