
from .base import Token
from .compose import Set, Seq

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
