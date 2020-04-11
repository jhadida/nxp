
from nxp import FileBuffer, ListBuffer, make_parser

# ------------------------------------------------------------------------

class Substitute:
    __slots__ = ('beg','end','txt')
    def __init__(self,beg,end,txt):
        self.beg = beg 
        self.end = end 
        self.txt = txt

    def __str__(self):
        return str(self.txt)

    def __lt__(self,other): return self.end <= other.beg
    def __gt__(self,other): return other < self

    def overlaps(self,other):
        return not (self < other or self > other)

# ------------------------------------------------------------------------

class Transform:
    def __init__(self,buf,beg=(0,0),end=None):
        if end is None: end = buf.lastpos
        self.buf = buf 
        self.beg = beg 
        self.end = end
        self.sub = []

    def __len__(self): return len(self.sub)
    def __iter__(self): return iter(self.sub)
    def __getitem__(self,key): return self.sub[key]

    def check(self):
        for a,b in zip(self.sub,self.sub[1:]):
            assert a < b, RuntimeError('Bad substitution order.')

    def __str__(self,ind=''):
        self.check()

        out = []
        pos = self.beg 
        for s in self.sub:
            if s.beg < pos: continue 
            if s.beg > self.end: break
            out.append( self.buf.between(pos,s.beg) + str(s) )
            pos = s.end 

        out.append(self.buf.between(pos,self.end))
        return ''.join(out)

    def append(self,beg,end,txt):
        assert self.beg <= beg and end <= self.end, ValueError('Bad bounds.')
        s = Substitute(beg,end,txt)
        self.sub.append(s)
        return s 

    def include(self,beg,end,fpath,r2l=False):
        assert self.beg <= beg and end <= self.end, ValueError('Bad bounds.')
        t = Transform(FileBuffer(fpath,r2l))
        self.append(beg,end,t)
        return t

    def fenced(self,beg,end,w=1):
        assert self.beg <= beg and end <= self.end, ValueError('Bad bounds.')
        bl,bc = beg 
        el,ec = end 
        t = Transform( self.buf, (bl,bc+w), (el,ec-w) )
        self.append(beg,end,t)
        return t

# ------------------------------------------------------------------------

def process( parser, callback, buffer, first=(0,0), last=None ):
    """
    Parse input buffer, and invoke callback for each matched element.

    Callback function should match the following prototype:
        callback( transform, element )
    where 
        'transform' is a Transform object, and 
        'element' is a RElement object.
    """
    if last is None: last = buffer.lastpos 
    tsf = Transform( buffer, first, last )
    res = make_parser(parser).parse( buffer.cursor(*first) )
    for elm in res: callback(tsf,elm)
    assert len(tsf) == 0 or tsf[-1].end <= last, RuntimeError('Last position exceeded.')
    return tsf

def procfile( parser, callback, infile, r2l=False ):
    """
    Process input file using callback function to transform every match 
    in the "main" scope found during parsing. 
    
    The callback function should be:
        callback( transform, element )
    """
    buf = FileBuffer(infile,r2l)
    return process( parser, callback, buf )

def proctxt( parser, callback, text, r2l=False ):
    """
    Same as above, but process input text.
    """
    buf = ListBuffer(text.splitlines(True),r2l)
    return process( parser, callback, buf )
