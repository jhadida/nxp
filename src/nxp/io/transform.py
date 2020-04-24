
from .buffer import FileBuffer, ListBuffer

# ------------------------------------------------------------------------

class Substitute:
    __slots__ = ('beg','end','sub')
    def __init__(self,beg,end,sub):
        self.beg = beg 
        self.end = end 
        self.sub = sub

    def __str__(self): return str(self.sub)
    def __lt__(self,other): return self.end <= other.beg
    def __gt__(self,other): return other < self

    def overlaps(self,other):
        return not (self < other or self > other)

# ------------------------------------------------------------------------

class Transform:
    __slots__ = ('_buf','_beg','_end','_sub')
    def __init__(self,buf,beg=(0,0),end=None):
        if end is None: end = buf.lastpos
        self._buf = buf 
        self._beg = beg 
        self._end = end
        self._sub = []

    @property
    def buffer(self): return self._buf

    def __str__(self): return self.str()
    def __len__(self): return len(self._sub)
    def __iter__(self): return iter(self._sub)
    def __getitem__(self,key): return self._sub[key]

    def check(self):
        for a,b in zip(self._sub,self._sub[1:]):
            assert a < b, RuntimeError('Bad substitution order.')

    def restrict(self,beg,end,w=0):
        self._check_range(beg,end)
        if isinstance(w,int): w = (w,w)
        bl,bc = beg 
        el,ec = end 
        self._beg = (bl,bc+w[0])
        self._end = (el,ec-w[1])
        return self

    def clone(self):
        return Transform( self._buf, self._beg, self._end )

    def str(self,proc=None):
        self.check()

        # processing of non-substituted text
        if proc is None: proc = lambda t: t

        # build output as an array
        out = []
        pos = self._beg 
        for s in self._sub:

            # check that extents are compatible
            if s.beg < pos: continue 
            if s.beg >= self._end: break

            # process text and substitution
            txt = proc(self._buf.between(pos,s.beg))
            if isinstance(s,Transform):
                out.append( txt + s.str(proc) )
            else:
                out.append( txt + str(s) )

            # update position
            pos = s.end 

        # last bit of text
        out.append(proc(self._buf.between(pos,self._end)))

        # concatenate all segments
        return ''.join(out)

    def _check_range(self,beg,end):
        assert self._beg <= beg <= end <= self._end, ValueError(f'Bad positions: {self._beg} <= {beg} <= {end} <= {self._end}')
    def _check_lines(self,lbeg,lend):
        assert self._beg[0] <= lbeg <= lend <= self._end[0], ValueError(f'Bad lines: {self._beg[0]} <= {lbeg} <= {lend} <= {self._end[0]}')

    def restricted(self,beg,end,w=0):
        return self.clone().restrict(beg,end,w)

    def include(self,beg,end,fpath,r2l=False):
        self._check_range(beg,end)
        tsf = Transform(FileBuffer( fpath, r2l ))
        self.sub(beg,end,tsf)
        return tsf

    def protect(self,beg,end):
        return self.sub( beg, end, self._buf.between(beg,end) )

    def sub(self,beg,end,sub):
        self._check_range(beg,end)
        s = Substitute(beg,end,sub)
        self._sub.append(s)
        return s 

    def sub_line(self,lnum,sub):
        return self.sub_lines(lnum,lnum,sub)

    def sub_lines(self,lbeg,lend,sub):
        self._check_lines(lbeg,lend)
        line = self._buf[lend]
        beg = (lbeg,0)
        end = (lend,len(line))
        return self.sub(beg,end,sub)
