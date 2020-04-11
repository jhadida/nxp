
import re
from .util import rstrip, rstripn, lstripn
from .charset import white

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
        eol     newline chars
    """
    __slots__ = ('_raw','_num','_off','_pre','_txt','_eol')
    
    def __init__(self, line, lineno=0, offset=0):

        # tokenise input string
        self._raw, self._eol = rstrip(line, '\r\n')
        self._pre = lstripn(self._raw, white)
        self._txt = rstripn(self._raw, white)

        # assign properties
        self._num = lineno
        self._off = offset

        # check invalid EOLs
        if _chkeol.fullmatch(self._eol) is None:
            raise ValueError('Bad end-of-line')

    def __len__(self): return len(self._raw)
    def __str__(self): return self._raw
    def __repr__(self): return str({ 
        'num': self._num, 
        'off': self._off, 
        'raw': self._raw, 
        'eol': self._eol 
    })

    def __getitem__(self,key):
        return self._raw[key]

    def make_last(self): self._eol = ''

    # position within file
    @property
    def lineno(self): return self._num
    @property 
    def offset(self): return self._off 

    # contents of segments
    @property 
    def indent(self): return self._raw[0:self._pre]
    @property 
    def text(self): return self._raw[self._pre:self._txt]
    @property 
    def post(self): return self._raw[self._txt:]
    @property 
    def eol(self): return self._eol
    @property 
    def raw(self): return self._raw
    @property 
    def full(self): return self._raw + self._eol

    # begin/end of text
    def bot(self): return self._pre 
    def eot(self): return self._txt

    # lengths of segments
    @property 
    def prelen(self): return self._pre 
    @property 
    def textlen(self): return self._txt - self._pre 
    @property 
    def postlen(self): return len(self) - self._txt

    # properties
    def is_empty(self): return len(self) == 0
    def is_white(self): return self._txt == self._pre
    def is_first(self): return self._num == 0
    def is_last(self): return not self._eol

    def has_text(self): return self.textlen > 0
    def uses_lf(self): return self._eol == '\n'
    def uses_crlf(self): return self._eol == '\r\n'
    