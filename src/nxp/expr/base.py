
import logging
from .match import TMatch, MatchError

# ------------------------------------------------------------------------

class Token:
    """
    A Token is the abstract parent of all expressions (Regex, Set, Seq, etc.).
    They mainly implement the logic of a match with multiplicity.

    Matching is implemented in derived classes and:
    - returns TMatch if there is a match, otherwise throws MatchError;
    - takes a cursor in input, and updates it in case of match.
    """

    def __init__(self):
        self._name = None 

    def __str__(self): # to be overloaded
        raise NotImplementedError()

    # capture match with an explicit name
    @property
    def name(self):
        return self._name 

    def capture(self,name):
        self._name = name

    # matching
    def __call__(self,cur):
        return self.match(cur)
        
    def match(self,cur,cap=None):
        """
        Returns TMatch in case of successful match, 
        throws MatchError otherwise.
        """
        m = self._match(cur,cap)
        if self._name and cap is not None:
            cap[self._name] = m
        return m

    def _match(self,cur,cap):
        raise NotImplementedError()

    # search
    def find(self,cur):
        logging.debug('[Token] Find token at: L=%d, C=%d', *cur.pos)
        while cur.isvalid():
            try:
                return self.match(cur)
            except:
                cur.nextchar()
        return None

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
