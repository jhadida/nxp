
import re
from .util import clamp
import logging

# ------------------------------------------------------------------------

class Cursor:
    """
    Cursor objects act as "pointers" to buffer contents.
    Properties:
    - reference to the corresponding buffer, 
    - line/char position.
    """
    __slots__ = ('_buf','_line','_char')

    def __init__(self, buf, line, char=0):
        self._buf = buf
        self.setpos(line,char)

    def reset(self):
        return self.goto_bof()

    def isvalid(self):
        return self._char >= 0 and self._char < len(self._line)

    # "real" positions
    def linepos(self): return self._char
    def filepos(self): return self._char + self._line.offset

    # WARNING!
    # filepos returns a character count which excludes newline characters,
    # this cannot be used with fseek or similar methods!

    # change line or cursor position
    @property 
    def buffer(self): return self._buf
    @property 
    def line(self): return self._line
    @property 
    def lnum(self): return self._line.lnum
    @property 
    def char(self): return self._char

    @property 
    def pos(self): return self.lnum, self._char
    @pos.setter
    def pos(self,p):
        self.setpos(p[0],p[1])

    def setpos(self, line, char=0):
        self._line = self._buf[line]
        self._char = clamp( char, 0, len(self._line) )
        logging.debug(f'[cursor] Set position to: L={self.lnum}, C={self.char}')
        return self

    def nextchar(self, n=1):
        self._char += clamp( n, -self._char, len(self) )
        return self 

    def nextline(self, n=1):
        L = self.lnum
        if L+n < len(self._buf):
            logging.debug(f'[cursor] Skip {n} line(s).')
            return self.setpos(max( L+n, 0 ))
        else:
            logging.debug(f'[cursor] Cannot skip {n} line(s): go to EOF.')
            return self.goto_eof()

    # disallow deep copies of cursors
    def copy(self,other):
        self._buf = other._buf 
        self._line = other._line 
        self._char = other._char 
    def __copy__(self):
        return Cursor( self._buf, self.lnum, self._char )
    def __deepcopy__(self,memo):
        raise NotImplementedError('Cursors cannot be deep-copied.')

    # underlying line / buffer properties
    def __len__(self): return len(self._line) - self._char
    def __getitem__(self,key): return self.line[key]

    # comparison with other cursors
    def __eq__(self,cur):
        return self.pos == cur.pos
    def __lt__(self,cur):
        return self.pos < cur.pos
    def __gt__(self,cur):
        return self.pos > cur.pos
    def __ne__(self,cur):
        return not self.__eq__(cur)
    def __le__(self,cur):
        return not self.__gt__(cur)
    def __ge__(self,cur):
        return not self.__lt__(cur)

    def __sub__(self,cur):
        return self.filepos - cur.filepos
    def __str__(self):
        l,c = self.pos
        return f'({l},{c}) "{self._line[self._char:]}"'

    # beginning/end of line/text
    @property
    def bol(self): return self._char == 0
    @property
    def eol(self): return self._char >= len(self._line)
    @property
    def bot(self): return self._char == self._line.prelen
    @property
    def eot(self): return self._char >= self._line.textlen
    @property 
    def bof(self): return self.bol and self._buf.is_first(self._line)
    @property 
    def eof(self): return self.eol and self._buf.is_last(self._line)

    # move the cursor at key points
    def goto_bol(self): 
        self._char = 0
        return self 
    def goto_eol(self): 
        self._char = len(self._line)
        return self 

    def goto_bot(self):
        self._char = self._line.bot
        return self
    def goto_eot(self):
        self._char = self._line.eot
        return self

    def goto_bof(self):
        self.setpos(0,0)
        return self 
    def goto_eof(self):
        self._line = self._buf[-1]
        self._char = len(self._line)
        return self

    # match text contents (expects compiled regex)
    def match(self,pat):
        if isinstance(pat,str): pat = re.compile(pat)
        logging.debug(f'[cursor] Match pattern: {pat.pattern}')
        return pat.match( self._line.raw, self._char )

    def search(self,pat):
        if isinstance(pat,str): pat = re.compile(pat)
        logging.debug(f'[cursor] Search pattern: {pat.pattern}')
        return pat.search( self._line.raw, self._char )

    # raise exceptions
    def show(self,width=13):
        s,x = self._buf.show_around(self.pos)
        print('\n'.join([s,x]))

    def error(self, msg, width=13, exc=RuntimeError):
        p = self.pos
        s,x = self._buf.show_around(p)
        p = f'line {p[0]+1}, col {p[1]+1}'

        logging.error(f'[cursor] Error at L={self.lnum}, C={self.char}: {msg}')
        raise exc('\n'.join([ p, '\t'+s+'..', '\t'+x, msg ]))
