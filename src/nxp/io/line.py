
import re
from .util import rstrip, rstripn, lstripn
from nxp.charset import white

# regular expressions used to parse lines of text
#_segline = re.compile( r'^(?P<pre>[' + white + r']*)(?P<txt>.*)(?P<pst>[' + white + r']*)$' )
_chkeol = re.compile( r'(\r?\n)?' )

# ------------------------------------------------------------------------

class Line:
    """
    Line objects segment a line of text into:
        indent  leading whitespace
        text    main contents
        post    trailing whitespace
        nl      newline chars
    """
    __slots__ = ('_raw','_num','_off','_bot','_eot','_nl')
    
    def __init__(self, line, lnum=0, offset=0):

        # tokenise input string
        self._raw, self._nl = rstrip(line, '\r\n')
        self._bot = lstripn(self._raw, white)
        self._eot = rstripn(self._raw, white)

        # assign properties
        self._num = lnum
        self._off = offset

        # check invalid EOLs
        if _chkeol.fullmatch(self._nl) is None:
            raise ValueError('Bad end-of-line')

    def __len__(self): return len(self._raw)
    def __str__(self): return self._raw
    def __repr__(self): return str({ 
        'num': self._num, 
        'off': self._off, 
        'raw': self._raw, 
        'nl': self._nl 
    })

    def __getitem__(self,key):
        return self._raw[key]

    # position within file
    @property
    def lnum(self): return self._num
    @property 
    def offset(self): return self._off 

    # begin/end of text
    @property
    def bot(self): return self._bot 
    @property
    def eot(self): return self._eot

    # contents of segments
    @property 
    def indent(self): return self._raw[0:self._bot]
    @property 
    def text(self): return self._raw[self._bot:self._eot]
    @property 
    def post(self): return self._raw[self._eot:]
    @property 
    def nl(self): return self._nl
    @property 
    def raw(self): return self._raw
    @property 
    def full(self): return self._raw + self._nl

    # lengths of segments
    @property 
    def prelen(self): return self._bot 
    @property 
    def textlen(self): return self._eot - self._bot 
    @property 
    def postlen(self): return len(self) - self._eot

    # properties
    def is_empty(self): return len(self) == 0
    def is_white(self): return self._eot == self._bot
    def has_text(self): return self.textlen > 0

    def uses_lf(self): return self._nl == '\n'
    def uses_crlf(self): return self._nl == '\r\n'
    