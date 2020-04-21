
# import NXP from current repo
import sys
import os.path as op
sys.path.insert(0,op.realpath('../src'))

import nxp

# ------------------------------------------------------------------------
# 1. LANGUAGE DEFINITION
# ------------------------------------------------------------------------

from nxp import Seq, Rep, Either, String, Fenced, XML_self, XML_open, XML_close

# list items
list_item = r'^(\s*[-+*]\s*)'
list_digit = r'^(\s*\d\.\s*)'

# emphasis
emph = Either( Fenced('*',empty=False), Fenced('_',empty=False) )
bold = Either( r'\*\*(((\\\*)|[^*])+)\*\*', r'__(((\\_)|[^_])+)__' )

# other
code = Fenced('`')
math = Fenced('$')

# elements
def label(name):
    return Fenced( ('[',']'), esc=False ).save(name)

def target(lname,vname):
    return Either( 
        label(lname), 
        Seq([ 
            r'\(\s*', 
            Rep(
                Either( String(), r'([^\)\s]+)' ),
                '2-', sep='\s+'
            ).save(vname),  
            r'\s*\)' 
        ]) 
    ) 

img = Seq([ 
    Fenced( ('![',']') ).save('alt'), 
    target('imglabel','imgvalue')
])

url = Seq([
    r'\[\s*', 
    Either( img, r'((\\\])|[^\]])+' ).save('body'), 
    r'\s*\]', 
    target('urllabel','urlvalue')
])

ref = Seq([ 
    label('label'), r':\s*', 
    Rep(
        Either( String(), r'(\S+)' ), 
        '1-2', sep='\s+'
    ).save('value') 
])

# ------------------------------------------------------------------------

def saveIndent(c,x,m): 
    x.set('indent',len(m.text))
def validIndent(c,x,m): 
    return len(m.text) == x.get('indent')
def checkIndent(c,x): 
    return len(c.line.indent) >= x.get('indent')
def saveTag(c,x,m):
    x.set('tag',m.data[0].data[1])
def validTag(c,x,m):
    return m.data[1] == x.get('tag')
def checkEOF(c,x,m):
    if c.eof:
        x.save(m)
        x.close()

# limitations:
#   blockquotes can have arbitrary intentation at the start
#   multiline list items are not lazy (need to be indented)
#   quotes and subquotes need to be separated from text by a newline
#   quotes separated by a newline are not merged
#   tables are not supported

lang = {
    'main': [
        [ r'^\s*$' ], 
        [ r'^\s*(#+)', ('goto','eol'), ('tag','sec') ], # section
        [ r'^\s*((---+)|(\*\*\*+))\s*$', ('tag','rule') ], # horizontal rule
        [ r'^\s*> ', ('open','quote'), ('goto','eol'), 'save' ], # blockquote
        [ r'^```(\S*)', ('open','codeblock'), 'save' ], # codeblock
        [ r'^\$\$', ('open','mathblock'), 'save' ], # mathblock
        [ r'\s+' ], # consume spaces
        [ r'<!--', ('open','comment'), 'save' ],
        [ XML_self(), ('tag','html') ], # html
        [ XML_open(), ('open','htmlblock'), 'save', ('open','text'), ('call',saveTag) ], # html
        [ list_item, ('open','list.item'), ('call',saveIndent), ('goto','eol'), ('tag','item') ],
        [ list_digit, ('open','list.digit'), ('call',saveIndent), ('goto','eol'), ('tag','item') ],
        [ ref, ('pos_before','bot'), ('goto','eol'), ('tag','ref') ], # reference
        [ None, ('open','text'), 'save' ]
    ],
    'text': [
        [ r'^\s*$', 'save', 'close' ],
        [ list_item, ('next','list.item'), ('call',saveIndent), ('goto','eol'), ('tag','item') ],
        [ list_digit, ('next','list.digit'), ('call',saveIndent), ('goto','eol'), ('tag','item') ],
        [ r'[^\[_*`$\\<!]+', ('call',checkEOF) ], # optimization
        [ bold, ('tag','bold') ], # bold
        [ emph, ('tag','emph') ], # emphasis
        [ r'\\[(){}\[\]*_`#+-.!$]', ('tag','esc'), ('proc',lambda t: t[1:]) ], # escape
        [ img, ('tag','img') ], # image
        [ url, ('tag','url') ], # link
        [ r'^```(\S*)', ('next','codeblock'), 'save' ], # codeblock
        [ r'^\$\$', ('next','mathblock'), 'save' ], # mathblock
        [ code, ('tag','code') ], # inline code
        [ math, ('tag','math') ], # inline math
        [ r'<!--', ('open','comment'), 'save' ],
        [ XML_close(), ('valid',validTag), 'close', 'save', 'close' ],
        [ XML_self(), ('tag','html') ], # html
        [ XML_open(), ('open','htmlblock'), ('call',saveTag), 'save' ] # html
    ],
    'comment': [ [ r'-->', 'save', 'close' ] ],
    'codeblock': [ [ r'^```', 'save', 'close' ] ],
    'mathblock': [ [ r'^\$\$', 'save', 'close' ] ],
    'htmlblock': [],
    'quote': [
        [ r'^\s*>', ('goto','eol'), 'save' ],
        [ None, 'close' ]
    ],
    'list.item': [
        [ None, ('check',checkIndent), ('goto','eol'), 'save' ],
        [ r'^\s+$', ('check',checkIndent), ('tag','empty') ],
        [ list_item, ('valid',validIndent), ('goto','eol'), ('tag','item') ],
        [ list_item, ('next','list.item'), ('call',saveIndent), ('goto','eol'), ('tag','item') ],
        [ None, 'close' ]
    ],
    'list.digit': [
        [ None, ('check',checkIndent), ('goto','eol'), 'save' ],
        [ r'^\s+$', ('check',checkIndent), ('tag','empty') ],
        [ list_digit, ('valid',validIndent), ('goto','eol'), ('tag','item') ],
        [ list_digit, ('next','list.digit'), ('call',saveIndent), ('goto','eol'), ('tag','item') ],
        [ None, 'close' ]
    ]
}

parser = nxp.make_parser({ 'lang': lang })

# ------------------------------------------------------------------------
# 2. PROCESSING THE RESULTS OF PARSING
# ------------------------------------------------------------------------

from nxp.error import ScopeError, LengthError, TagError

html5doc = """
<!doctype html>
<html lang=en>
<head>
    <meta charset=utf-8>
    <title>{title}</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script>
    MathJax = {{ tex: {{ inlineMath: [['$', '$']] }} }};
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
{body}
</body>
</html>
"""

# HTML-related functions
def html_wrapper(body,title=''):
    return html5doc.format( title=title, body=body )

def attr2str(kv): 
    return ''.join([ f' {k}="{v}"' for k,v in kv.items() ])

def itag(name,body,sep='',**kv): # inline
    return f"<{name}{attr2str(kv)}>{sep}{body}{sep}</{name}>"

def stag(name,**kv): # self-closing
    return f"<{name}{attr2str(kv)} />"

class rtag:
    __slots__ = ('name','body','attr','sep')
    def __init__(self,name,body,sep='',**kv):
        self.name = name 
        self.body = body 
        self.attr = dict(kv)
        self.sep = sep
    def __str__(self):
        return f"<{self.name}{attr2str(self.attr)}>{self.sep}{self.body}{self.sep}</{self.name}>"

# ------------------------------------------------------------------------

md_ref = dict() # used to store references
md_par = True   # used to wrap text in paragraph

def md_getref(name):
    # empty keys are valid (but invalid keys are not)
    if name:
        return md_ref[name]
    else:
        return name

class md_refurl:
    """
    Postpone the processing of links defined with a reference label.
    """
    __slots__ = ('body','key')
    def __init__(self,body,key):
        self.body = body
        self.key = key 
    def __str__(self):
        val = md_getref(self.key)
        if isinstance(val,str):
            return itag('a',self.body,href=val)
        else:
            return itag('a',self.body,href=val[0],title=val[1])

class md_refimg:
    """
    Postpone the processing of images defined with a reference label.
    """
    __slots__ = ('alt','key')
    def __init__(self,alt,key):
        self.alt = alt
        self.key = key 
    def __str__(self):
        val = md_getref(self.key)
        if isinstance(val,str):
            return stag('img',alt=self.alt,src=val)
        else:
            return stag('img',alt=self.alt,src=val[0],title=val[1])

class md_item:
    __slots__ = ('body','par')
    def __init__(self,line):
        self.body = [line] 
        self.par = False
    def append(self,line):
        self.body.append(line)
    def __str__(self):
        global md_par
        md_par = self.par 
        body = nxp.process( 
            parser, md_callback, 
            nxp.ListBuffer(self.body) 
        )
        md_par = True
        return str(body)

class md_list:
    """
    Centralise the construction of lists.
    """
    __slots__ = ('ord','item')
    def __init__(self,ord=False):
        self.ord = ord
        self.item = []
    
    def __len__(self): return len(self.item)
    def __getitem__(self,key): return self.item[key]
    
    def __str__(self):
        return itag( 'ol' if self.ord else 'ul',
            '\n'.join([ itag('li',str(t)) for t in self.item ]),
            sep='\n' )
    
    def new(self,line):
        it = md_item(line)
        self.item.append(it)
        return it

# ------------------------------------------------------------------------

def md_procval(m):
    m = m.data[0] # switch string/regex
    if isinstance(m.data,list): 
        # dq/sq string > group between quotes
        return m.data[0].data[1]
    else: # raw text
        return m.data[0]

def md_procimg(elm):
    alt = elm['alt'].data[1]
    if 'imgvalue' in elm:
        val = elm['imgvalue'].data
        att = { 'alt': alt, 'src': md_procval(val[0]) }
        if len(val) > 1: att['title'] = md_procval(val[1])
        return stag('img',**att)
    else:
        lab = elm['imglabel'].data[1]
        return md_refimg( alt, lab )

def md_procurl(elm):
    # body can be an image
    body = elm['body'].data[0]
    if isinstance(body.data,list):
        body = md_procimg(elm)
    else:
        body = body.data[0]

    # sort value/ref
    if 'urlvalue' in elm:
        val = elm['urlvalue'].data
        atr = { 'href': md_procval(val[0]) }
        if len(val) > 1: atr['title'] = md_procval(val[1])
        return itag('a',body,**atr)
    else:
        lab = elm['urllabel'].data[1]
        return md_refurl( body, lab )
            
def md_procref(elm):
    lab = elm['label'].data[1]
    val = elm['value'].data
    if len(val) > 1:
        md_ref[lab] = (md_procval(val[0]), md_procval(val[1]))
    else:
        md_ref[lab] = md_procval(val[0])

def md_proclist(buf,elm):
    lst = md_list( elm.name.endswith('digit') )
    ind = elm.get('indent')
    it = None
    for m in elm:
        if m.tag == 'item':
            it = lst.new( buf[m.beg[0]].raw[ind:] )
        elif m.tag == 'empty':
            it.par = True 
        else:
            it.append( buf[m.beg[0]].raw[ind:] )
    return lst

# ------------------------------------------------------------------------

def md_callback( tsf, elm ):
    global md_par
    if isinstance(elm,nxp.RMatch):
        beg,end = elm.beg, elm.end 
        tag = elm.tag 

        if tag == "":
            pass 
        elif tag == 'sec': # section heading
            depth = len(elm.text)
            text = tsf.buffer.after(end).strip()
            tsf.sub_line( beg[0], itag(f'h{depth}',text) )
        elif tag == 'rule': # horizontal rule
            tsf.sub_line( beg[0], '<hr>' )
        elif tag == 'ref': # reference 
            md_procref(elm)
            tsf.sub_line( beg[0], '' )
        elif tag == 'esc': # character escape
            tsf.sub( beg, end, elm.text )
        elif tag == 'img': 
            tsf.sub( beg, end, md_procimg(elm) )
        elif tag == 'url': 
            tsf.sub( beg, end, md_procurl(elm) )
        elif tag == 'bold': 
            tsf.sub( beg, end, itag('strong',elm.data[0].data[1]) )
        elif tag == 'emph':
            tsf.sub( beg, end, itag('emph',elm.data[0].data[1]) )
        elif tag == 'code':
            tsf.sub( beg, end, itag('code',elm.data[1]) )
        elif tag == 'math':
            tsf.protect( beg, end )
        elif tag == 'html':
            tsf.protect(beg,end)
        else:
            raise TagError(tag)

    elif elm.name == 'text':
        if len(elm)==0: return
        beg = elm[0].beg
        end = elm[-1].end
        sub = tsf.restrict(beg,end)
        for m in elm: md_callback(sub,m)
        tsf.sub( beg, end, rtag('p',sub) if md_par else sub )
    elif elm.name.startswith('list'):
        tsf.sub_lines( 
            elm[0].beg[0], elm[-1].end[0], 
            md_proclist(tsf.buffer,elm) 
        )
    elif elm.name == 'quote':
        lines = [ tsf.buffer[m.beg[0]].raw[len(m.text):] for m in elm ]
        md_par = any([ re.match( r'^\s*$', line ) for line in lines ])
        tsf.sub_lines( 
            elm[0].beg[0], elm[-1].end[0], 
            rtag('blockquote',nxp.process( 
                parser, md_callback, 
                nxp.ListBuffer(lines)
            ),sep='\n')
        )
        md_par = True
    elif elm.name == 'htmlblock':
        assert len(elm)==3, LengthError(elm)
        assert elm[1].name == 'text', ScopeError(elm[1].name)
        beg = elm[0].beg 
        end = elm[-1].end
        sub = tsf.restrict(beg,end)
        for m in elm[1]: md_callback(sub,m)
        tsf.sub( beg, end, sub )
    elif elm.name == 'mathblock':
        assert len(elm)==2, LengthError(elm)
        tsf.protect( elm[0].beg, elm[1].end )
    elif elm.name == 'codeblock':
        assert len(elm)==2, LengthError(elm)
        lang = elm[0].data[1]
        attr = {'lang': lang} if lang else {}
        tsf.sub_lines( 
            elm[0].beg[0], elm[1].end[0], 
            itag('pre',itag('code',
                tsf.buffer.between(elm[0].end, elm[1].beg),
                **attr
            )) 
        )
    elif elm.name == 'comment':
        tsf.protect( elm[0].beg, elm[-1].end )
    else:
        raise NameError(f'Unknown element: {elm.name}')

# ------------------------------------------------------------------------
# 3. CREATING A COMPILER
# ------------------------------------------------------------------------

import re

def parse( text ):
    return nxp.parse( parser, text )

def parsefile( infile ):
    return nxp.parsefile( parser, infile )

def compile( infile, outfile=None, wrap=html_wrapper, **kv ):
    proc = lambda t: re.sub( r'\n{2,}', '\n', t )
    tsf = nxp.process( parser, md_callback, nxp.FileBuffer(infile) )
    txt = wrap( tsf.str(proc), **kv )
    if outfile: 
        with open(outfile,'w') as fh:
            fh.write(txt)
    return txt
