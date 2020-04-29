
"""
A buffer is essentially a list of Line objects.
More complicated buffers (e.g. with stream and cache-drop) can be implemented later.
"""

from .line import Line
from .cursor import Cursor
import logging

# ------------------------------------------------------------------------

class _Buffer:
    def __init__(self):
        self._r2l = False
        self._line = []

    def _readlines(self,obj,r2l):
        offset = 0
        for lnum,line in enumerate(obj):
            if r2l:
                self._line.append(Line(line[::-1],lnum,offset))
            else:
                self._line.append(Line(line,lnum,offset))
            offset += len(line)

        self._r2l = r2l

        # notify
        logging.info(f'Buffer initialized ({len(self)} lines).')

    def write(self,filename):
        with open(filename,'w') as fh:
            fh.writelines( L.full for L in self._line )

    def __len__(self): return len(self._line)
    def __iter__(self): return iter(self._line)
    def __getitem__(self,key): return self._line[key]

    def is_first(self,line): 
        return line.lnum == 0
    def is_last(self,line): 
        return line.lnum == len(self)-1

    @property
    def nlines(self): return len(self)

    @property
    def nchars(self): 
        if self._line:
            last = self._line[-1]
            return last.offset + len(last)
        else:
            return 0
    
    # ----------  =====  ----------
    # Position-related

    @property
    def lastpos(self):
        if self._line:
            return len(self._line)-1, len(self._line[-1])
        else:
            return 0,0

    def cursor(self,line=0,char=0):
        return Cursor( self, line, char )

    def until(self,pos):
        return self._line[pos[0]][0:pos[1]]

    def after(self,pos):
        return self._line[pos[0]][pos[1]:]

    def lbetween(self,pos1,pos2):
        L1, C1 = pos1 
        L2, C2 = pos2
        L, C = L1, C1

        out = []
        while L < L2:
            out.append(self._line[L][C:])
            L += 1
            C = 0
        out.append(self._line[L][C:C2])
        return out

    def between(self,pos1,pos2,nl='\n'):
        return nl.join(self.lbetween(pos1,pos2))

    def distance(self,pos1,pos2):
        L1, C1 = pos1
        L2, C2 = pos2
        off1 = self._line[L1].offset
        off2 = self._line[L2].offset
        return (off2+C2) - (off1+C1)

    # ----------  =====  ----------
    # Display

    def _bounds(self,w,c1,c2,L):
        if w == 0:
            return 0,L
        elif w < 0:
            return 0,min(c2-w,L)
        else:
            return max(0,c1-w),min(c2+w,L)

    def show_around(self,pos,w=13):
        lnum,c = pos 
        L = self._line[lnum]
        b,e = self._bounds(w,c,c,len(L))
        
        s = ' ' if b==e else L[b:e]
        x = list(' ' * len(s))
        x[c-b] = '^'
        return s, ''.join(x)

    def show_between(self,pos1,pos2,w=13):
        l1,c1 = pos1 
        l2,c2 = pos2 
        assert l1==l2, NotImplementedError('Multiline version not implemented.')
        L = self._line[l1]
        b,e = self._bounds(w,c1,c2,len(L))

        s = L[b:e]
        x = list(' ' * len(s))
        for k in range(c1,c2): x[k-b] = '-'
        return s, ''.join(x)

# ------------------------------------------------------------------------

class FileBuffer(_Buffer):
    """
    Buffer instance from input file.
    """
    def __init__(self, filename, r2l=False):
        super().__init__()
        logging.info(f'Initializing buffer from file: "{filename}"')
        with open(filename) as fh:
            self._readlines(fh,r2l)

# ------------------------------------------------------------------------

class ListBuffer(_Buffer):
    """
    Buffer instance from list of strings (each corresp to a line).
    """
    def __init__(self, strlist, r2l=False):
        super().__init__()
        logging.info('Initializing buffer from string list.')
        self._readlines(strlist,r2l)
