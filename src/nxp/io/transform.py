
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

    def str(self,proc=None):
        self.check()

        # processing of non-substituted text
        if proc is None: proc = lambda t: t

        # build output as an array
        out = []
        pos = self._beg 
        for s in self._sub:

            # check that extents are compatible
            if s.beg < pos: raise RuntimeError('[bug] Overlapping substitutions.') 
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
    
    # ----------  =====  ----------
    
    def _check_range(self,beg,end):
        assert self._beg <= beg <= end <= self._end, ValueError(f'Bad positions: {self._beg} <= {beg} <= {end} <= {self._end}')
    def _check_lines(self,lbeg,lend):
        assert self._beg[0] <= lbeg <= lend <= self._end[0], ValueError(f'Bad lines: {self._beg[0]} <= {lbeg} <= {lend} <= {self._end[0]}')
    
    # ----------  =====  ----------

    def clone(self):
        """
        Create a new instance of the current Transform (without copying substitutions).
        """
        return Transform( self._buf, self._beg, self._end )

    def restrict(self,beg,end,w=0):
        """
        Restrict current Transform to specified range.
        """
        self._check_range(beg,end)
        if isinstance(w,int): w = (w,w)
        Lb,Cb = beg 
        Le,Ce = end 
        self._beg = (Lb,Cb+w[0])
        self._end = (Le,Ce-w[1])
        return self

    def restricted(self,beg,end,w=0):
        """
        Create new Transform restricted to specified range.
        """
        return self.clone().restrict(beg,end,w)
    
    # ----------  =====  ----------
    
    def include(self,beg,end,fpath,r2l=False):
        """
        Inject file contents within specified range.
        If end is None, beg should be a line number.
        """
        self._check_range(beg,end)
        tsf = Transform(FileBuffer( fpath, r2l ))
        if end is None:
            self.sub_line(beg,tsf,gobble=True)
        else:
            self.sub(beg,end,tsf)
        return tsf

    def protect(self,beg,end):
        """
        Prevent substitutions within specified range.
        """
        self.sub( beg, end, self._buf.between(beg,end) )
        return self

    def sub(self,beg,end,sub):
        """
        Substitute text within sepcified range.
        """
        self._check_range(beg,end)
        self._sub.append(Substitute(beg,end,sub))
        return self

    def sub_line(self,lnum,sub,gobble=False):
        """
        Replace single line with given substitution.
        """
        return self.sub_lines(lnum,lnum,sub,gobble)
    def sub_lines(self,lbeg,lend,sub,gobble=False):
        """
        Replace multiple lines with given substitution.
        """
        self._check_lines(lbeg,lend)
        line = self._buf[lend]
        beg = (lbeg,0)
        if gobble and lend+1 < len(self._buf):
            end = (lend+1,0)
        else:
            end = (lend,len(line))
        return self.sub(beg,end,sub)

    def gobble(self,beg):
        """
        Consume whitespace until the next line.
        """
        L,C = beg 
        line = self._buf[L]

        if L+1 < len(self._buf):
            end = (L+1,0)
        else:
            end = (L,len(line))

        if line.eot <= C: 
            self.sub(beg,end,'')

        return self

    def clear(self,beg,end):
        """
        Delete line if blank outside or specified range, 
        otherwise simply delete range.
        """
        Lb,Cb = beg 
        Le,Ce = end 

        empty_before = self._buf[Lb].bot >= Cb
        empty_after = self._buf[Le].eot <= Ce

        if empty_before and empty_after:
            return self.sub_lines(Lb,Le,'',gobble=True)
        else:
            return self.sub(beg,end,'')
        
    def clear_line(self,lnum):
        """
        Delete line regardless of contents.
        """
        return self.sub_line(lnum,'',gobble=True)
    def clear_lines(self,lbeg,lend):
        """
        Delete lines regardless of contents.
        """
        return self.sub_lines(lbeg,lend,'',gobble=True)
