
import logging
from .match import TMatch

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

    def save(self,name):
        self._name = name
        return self

    # matching
    def __call__(self,cur):
        return self.match(cur)
        
    def match(self,cur):
        """
        Returns TMatch in case of successful match, 
        throws MatchError otherwise.
        """
        raise NotImplementedError()

    # search
    def find(self,cur,multi=False):
        logging.debug('[Token] Find token at: L=%d, C=%d', *cur.pos)
        end = 'eof' if multi else 'eol'
        while not getattr(cur,end):
            try:
                yield self.match(cur)
            except:
                cur.nextchar()

            if multi and cur.eol:
                cur.nextline()
