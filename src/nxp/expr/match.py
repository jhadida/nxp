
import logging

class MatchError(Exception): pass

# ------------------------------------------------------------------------

class TMatch:
    __slots__ = ('beg','end','data','text')

    def __init__(self,b,e,d,t):
        self.beg = b
        self.end = e 
        self.data = d
        self.text = t
        logging.debug('[TMatch] New token between %s and %s.',b,e)

    def isvalid(self):
        return self.end >= self.beg
    def isempty(self):
        return self.beg == self.end

    def __str__(self):
        return '%s - %s %s' % (self.beg, self.end, self.text)

# ------------------------------------------------------------------------

class TElement:
    """
    TElement objects contain:
    - the token being matched,
    - and an array of TMatch objects. 
    
    Individual match can be accessed using the [] operator (starting at 
    index 0), and the number of match is obtained by calling len(). Each 
    match corresponds to a single repetition of the token (cf. multiplicity).

    Nested match data (e.g. in the context of Seq or Set), is stored in the 
    'data' field of the corresponding match. This allows for arbitrarily deep 
    nesting. The matched text is stored in the field 'text'.
    """
    __slots__ = ('token','_rep','_len')

    def __init__(self,tok):
        self.token = tok 
        self._rep = []
        self._len = 0

    @property 
    def beg(self): return self._rep[0].beg 
    @property 
    def end(self): return self._rep[-1].end

    def text(self):
        return [ m.text for m in self._rep ]

    def append(self,beg,end,data=None,text=''):
        self._rep.append(TMatch( beg, end, data, text ))
        return self
    def commit(self):
        self._len = len(self._rep)
    def revert(self):
        self._rep = self._rep[0:self._len]

    def isvalid(self):
        return self._len == len(self._rep)
    def isempty(self):
        return len(self._rep) == 0

    def insitu(self,buf,width=13):
        out = [ 'Pattern: %s' % str(self.token) ]
        for k,m in enumerate(self._rep):
            idx = '[%d] ' % k 
            pfx = ' ' * len(idx)
            s,x = buf.show_between( m.beg, m.end, width )
            out.append( '\t' + idx + s )
            out.append( '\t' + pfx + x )
        return '\n'.join(out)

    def __len__(self):
        return len(self._rep)
    def __getitem__(self,key):
        return self._rep[key]
    def __iter__(self):
        return iter(self._rep)
    def __str__(self):
        return '\n'.join([ '[%d] %s' % (k,m) for k,m in enumerate(self._rep) ])
        