
# import NXP from current repo
import sys
import os.path as op
sys.path.insert(0,op.realpath('../src'))

import nxp

# ------------------------------------------------------------------------
# 1.    LANGUAGE DEFINITION
# ------------------------------------------------------------------------
# 1.1.  Pattern definitions
# 
#       The following patterns capture common Markdown elements, 
#       and are used below with parsing rules.
# ------------------------------------------------------------------------

from nxp import Seq, Rep, Either, String, Fenced

# list items
list_item = r'^(\s*[-+*]\s*)'
list_digit = r'^(\s*\d\.\s*)'

# emphasis
bold = Fenced('*',empty=False)
emph = Fenced('_',empty=False)
boldit = r'_\*(((\\\*)|(\\_)|[^*_])+)\*_'

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
# 1.2.  Parser definition
#
#       The language is defined around two main scopes: main and text.
#       The text scope should correspond to a block of text, which may
#       contain links, images, inline code/math, and markup. 
#       Other block contents like item lists, blockquotes, and display 
#       code/math, are in separate scopes.
#       Definition of a "ghost" scope for HTML is needed to allow parsing
#       of the fenced contents. 
#
#       Limitations:
#       - italic / bold works slightly differently
#       - indented codeblocks are not supported (by choice)
#       - blockquotes can have arbitrary indentation at the start
#       - multiline list items are not lazy (need to be indented)
#       - quotes and subquotes must be separated from text by a newline
#       - quotes separated by a newline are not merged
#       - table markup is not supported (use HTML)
# ------------------------------------------------------------------------

from nxp import XML_self, XML_open, XML_close

def saveIndent(c,x,m): 
    x.set('indent',len(m.text))
def validIndent(c,x,m): 
    return len(m.text) == x.get('indent')
def checkIndent(c,x): 
    return len(c.line.indent) >= x.get('indent')
def saveTag(c,x,m):
    x.set('tag',m[0][1])
def validTag(c,x,m):
    return m[1] == x.get('tag')
def textEOF(c,x,m):
    if c.eof: x.save(m)

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
        [ r'[^\[_*`$\\<!]+', ('call',textEOF) ], # optimization
        [ boldit, ('tag','boldit') ], # bold
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
        [ XML_open(), ('open','htmlblock'), ('call',saveTag), 'save' ], # html
        [ r'.*', ('pos_after','eof'), ('call',textEOF) ]
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
# 2.    COMPILER DEFINITION
# ------------------------------------------------------------------------
# 2.1.  HTML utilities
#
#       The following functions generate HTML tags with attributes
#       and contents. MathJax is included in the HTML template to
#       support maths rendering.
# ------------------------------------------------------------------------

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

# ------------------------------------------------------------------------
# 2.2.  Utilities for delayed rendering
#
#       The following classes delay the text-rendering of various 
#       components (HTML tag, Markdown URL, image, or list), which
#       is useful e.g. for images and links that depend on a reference
#       defined later in the text.
# ------------------------------------------------------------------------

class md_tag:
    __slots__ = ('name','body','attr','sep')
    def __init__(self,name,body,sep='',**kv):
        self.name = name 
        self.body = body 
        self.attr = dict(kv)
        self.sep = sep
    def __str__(self):
        return itag( self.name, self.body, self.sep, **self.attr )

class md_refurl:
    """
    Postpone the processing of links defined with a reference label.
    """
    __slots__ = ('cpl','body','key')
    def __init__(self,cpl,body,key):
        self.cpl = cpl
        self.body = body
        self.key = key 
    def __str__(self):
        val = self.cpl.getref(self.key)
        if isinstance(val,str):
            return itag('a',self.body,href=val)
        else:
            return itag('a',self.body,href=val[0],title=val[1])

class md_refimg:
    """
    Postpone the processing of images defined with a reference label.
    """
    __slots__ = ('cpl','alt','key')
    def __init__(self,cpl,alt,key):
        self.cpl = cpl
        self.alt = alt
        self.key = key 
    def __str__(self):
        val = self.cpl.getref(self.key)
        if isinstance(val,str):
            return stag('img',alt=self.alt,src=val)
        else:
            return stag('img',alt=self.alt,src=val[0],title=val[1])

class md_item:
    __slots__ = ('cpl','body','par')
    def __init__(self,cpl,line):
        self.cpl = cpl
        self.body = [line] 
        self.par = False
    def append(self,line):
        self.body.append(line)
    def __str__(self): 
        body = self.cpl.process( nxp.ListBuffer(self.body), self.par )
        return str(body)

class md_list:
    """
    Centralise the construction of lists.
    """
    __slots__ = ('cpl','ord','item')
    def __init__(self,cpl,ord=False):
        self.cpl = cpl
        self.ord = ord
        self.item = []
    
    def __len__(self): return len(self.item)
    def __getitem__(self,key): return self.item[key]
    
    def __str__(self):
        name = 'ol' if self.ord else 'ul'
        body = '\n'.join([ itag('li',str(t)) for t in self.item ])
        return itag( name, body, sep='\n' )
    
    def new(self,line):
        it = md_item(self.cpl,line)
        self.item.append(it)
        return it

# ------------------------------------------------------------------------
# 2.3.  Compiler implementation
#
#       Parsing and compilation rely on nxp.procbuf, which requires 
#       a callback function to process each node / rule-match returned 
#       by the parser.
# ------------------------------------------------------------------------

from nxp.error import ScopeError, LengthError, TagError

class MarkdownCompiler:
    def __init__(self):
        self._ref = {}
        self._par = True 

    def setref(self,key,val):
        self._ref[key] = val
    def getref(self,key):
        return self._ref[key] if key else ''

    def process( self, buf, par=True ):
        self._par = par 
        return nxp.procbuf( parser, self._callback, buf )

    # main callback function
    def _callback( self, tsf, elm ):
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
                self._proc_ref(elm)
                tsf.clear_line( beg[0] )
            elif tag == 'esc': # character escape
                tsf.sub( beg, end, elm.text )
            elif tag == 'img': 
                tsf.sub( beg, end, self._proc_img(elm) )
            elif tag == 'url': 
                tsf.sub( beg, end, self._proc_url(elm) )
            elif tag == 'boldit': 
                tsf.sub( beg, end, itag('em',itag('strong',elm[1])) )
            elif tag == 'bold': 
                tsf.sub( beg, end, itag('strong',elm[1]) )
            elif tag == 'emph':
                tsf.sub( beg, end, itag('em',elm[1]) )
            elif tag == 'code': # inline code
                tsf.sub( beg, end, itag('code',elm[1]) )
            elif tag == 'math': # inline math
                tsf.protect( beg, end )
            elif tag == 'html': # self-closed HTML tag
                tsf.protect(beg,end)
            else:
                raise TagError(tag)

        elif elm.name == 'text':
            if len(elm)==0: return
            beg = elm[0].beg
            end = elm[-1].end
            sub = tsf.restricted(beg,end)
            for m in elm: self._callback(sub,m)
            tsf.sub( beg, end, md_tag('p',sub) if self._par else sub )

        elif elm.name == 'htmlblock':
            assert len(elm)==3, LengthError(elm)
            assert elm[1].name == 'text', ScopeError(elm[1].name)
            beg = elm[0].beg 
            end = elm[-1].end
            sub = tsf.restricted(beg,end)
            for m in elm[1]: self._callback(sub,m)
            tsf.sub( beg, end, sub )

        elif elm.name == 'quote':
            lines = [ tsf.buffer[m.beg[0]].raw[len(m.text):] for m in elm ]
            self._par = any([ re.match( r'^\s*$', line ) for line in lines ])
            tsf.sub_lines( 
                elm[0].beg[0], elm[-1].end[0], 
                md_tag('blockquote',nxp.procbuf( 
                    parser, self._callback, 
                    nxp.ListBuffer(lines)
                ),sep='\n')
            )
            self._par = True

        elif elm.name == 'codeblock':
            assert len(elm)==2, LengthError(elm)
            lang = elm[0][1]
            attr = {'lang': lang} if lang else {}
            tsf.sub_lines( 
                elm[0].beg[0], elm[1].end[0], 
                itag('pre',itag('code',
                    tsf.buffer.between(elm[0].end, elm[1].beg), 
                    **attr
                )) 
            )

        elif elm.name.startswith('list'):
            tsf.sub_lines( 
                elm[0].beg[0], elm[-1].end[0], 
                self._proc_list(tsf.buffer,elm) 
            )

        elif elm.name == 'mathblock':
            assert len(elm)==2, LengthError(elm)
            tsf.protect( elm[0].beg, elm[1].end )

        elif elm.name == 'comment':
            tsf.protect( elm[0].beg, elm[-1].end )

        else:
            raise NameError(f'Unknown element: {elm.name}')
    
    # ----------  =====  ----------
    
    def _proc_value(self,m):
        m = m[0] # switch string/regex
        if m.isregex(): # raw text
            return m[0]
        else: # dq/sq string > group between quotes
            return m[0][1]

    def _proc_ref(self,elm):
        cap = elm.captures(True)
        lab = cap['label'][1]
        val = cap['value'].data
        if len(val) > 1:
            r = (self._proc_value(val[0]), self._proc_value(val[1]))
        else:
            r = self._proc_value(val[0])
        self.setref(lab,r)

    def _proc_list(self,buf,elm):
        lst = md_list( self, elm.name.endswith('digit') )
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

    def _proc_img(self,elm):
        cap = elm.captures(True)
        alt = cap['alt'][1]
        if 'imgvalue' in cap:
            val = cap['imgvalue'].data
            attr = { 'alt': alt, 'src': self._proc_value(val[0]) }
            if len(val) > 1: attr['title'] = self._proc_value(val[1])
            return stag('img',**attr)
        else:
            lab = cap['imglabel'][1]
            return md_refimg( self, alt, lab )

    def _proc_url(self,elm):
        # body can be an image
        cap = elm.captures(True)
        body = cap['body'][0]
        if body.isregex():
            body = body[0]
        else:
            body = self._proc_img(elm)

        if 'urlvalue' in cap:
            val = cap['urlvalue'].data
            attr = { 'href': self._proc_value(val[0]) }
            if len(val) > 1: attr['title'] = self._proc_value(val[1])
            return itag('a',body,**attr)
        else:
            lab = cap['urllabel'][1]
            return md_refurl( self, body, lab )

# ------------------------------------------------------------------------
# 2.4.  User-level API
#
#       The following functions can be imported and called to parse
#       or compile a Markdown file.
# ------------------------------------------------------------------------

import re

def parse( infile ):
    return nxp.parsefile( parser, infile )

def compile( infile, outfile=None, wrap=html_wrapper, **kv ):
    proc = lambda t: re.sub( r'\n{2,}', '\n', t )
    tsf = MarkdownCompiler().process( nxp.FileBuffer(infile) )
    txt = wrap( tsf.str(proc), **kv )
    if outfile: 
        with open(outfile,'w') as fh:
            fh.write(txt)
    return txt
