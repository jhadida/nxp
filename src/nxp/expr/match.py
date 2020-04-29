
import logging
from collections import defaultdict

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
    def pattern(self): 
        return str(self.tok) if self.tok else None

    @property
    def name(self):
        return self.tok.name

    def isvalid(self):
        return self.end >= self.beg
    def isempty(self):
        return self.beg == self.end

    def __str__(self):
        return f'{self.beg} - {self.end} {self.text}'

    # traversal and named matches
    def __iter__(self):
        yield self 
        if isinstance(self.data,list):
            for m in self.data:
                yield from m
    
    def __getitem__(self,name):
        out = []
        for m in self:
            if m.name == name:
                out.append(m)
        return out

    def captures(self,append=True):
        if append:
            out = defaultdict(list)
            for m in self:
                if m.name is not None:
                    out[m.name].append(m)
        else:
            out = dict()
            for m in self:
                if m.name is not None:
                    out[m.name] = m
        return out
        
    # pretty-print
    def insitu(self,buf,w=13):
        s,x = buf.show_between( self.beg, self.end, w )
        return '\n'.join([s,x])
        