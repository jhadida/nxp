
import logging

class MatchError(Exception): pass

# ------------------------------------------------------------------------

class TMatch:
    """
    Nested match data (e.g. in the context of Seq or Set), is stored in the 
    'data' field of the corresponding match. This allows for arbitrarily deep 
    nesting. The matched text is stored in the field 'text'.
    """
    __slots__ = ('tok','beg','end','data','text')

    def __init__(self,tok,beg,end,data=None,text=''):
        self.tok = tok 
        self.beg = beg
        self.end = end 
        self.data = data 
        self.text = text

    @property 
    def pattern(self): return str(self.tok)

    def isvalid(self):
        return self.end >= self.beg
    def isempty(self):
        return self.beg == self.end

    def __str__(self):
        return f'{self.beg} - {self.end} {self.text}'
        
    # pretty-print
    def insitu(self,buf,w=13):
        s,x = buf.show_between( self.beg, self.end, w )
        return '\n'.join([s,x])
        