
import sys
import os.path as op
sys.path.insert(0,op.realpath('../src'))

import nxp

# ------------------------------------------------------------------------

from nxp import Seq, Rep, Mul, Either, XML, String, Fenced

# rules and expressions
escape = [ r'\\[(){}\[\]*_`#+-.!$]', ('tag','esc'), ('proc',lambda t: t[1:]) ]
empty = [ r'^\s*$', ('tag','empty') ]

list_item = r'^(\s*[-+*]\s*)'
list_digit = r'^(\s*\d\.\s*)'

# emphasis
emph = Either( Fenced('*',empty=False), Fenced('_',empty=False) )
bold = Either( r'\*\*((\\\*)|[^*])+\*\*', r'__((\\_)|[^_])+__' )

# other
code = Fenced('`')
math = Fenced('$')

# links and images
ref_value = Either( String(), r'(\S+)' )
ref_label = Fenced( ('[',']'), esc=False )
tgt_value = Either( String(), r'([^\)\s]+)' )

tgt_link = Seq( [r'\(\s*', tgt_value, Seq([ '\s+', tgt_value ]), r'\s*\)'], skip=[1,2] )
target = Either( tgt_link, ref_label ) 

img = Seq( [Fenced( ('![',']') ), target] )
url = Seq( [r'\[\s*', Either( img, r'((\\\])|[^\]])+' ), r'\s*\]', target] )
ref = Seq( [ ref_label, r':\s*', ref_value, Seq([ '\s+', ref_value ]) ], skip=3 )

# ------------------------------------------------------------------------

def saveIndent(c,x,m): 
    x.set('indent',len(m[0].text))
def validIndent(c,x,m): 
    return len(m[0].text) == x.get('indent')
def checkIndent(c,x): 
    return len(c.line.indent) >= x.get('indent')

lang = {
    'main': [
        empty, # empty line
        [ r'<!--', ('open','comment') ],
        [ XML() ], # html
        escape,
        [ r'^\s*(#+)', ('goto','eol'), ('tag','sec') ], # section
        [ r'^\s*((---+)|(\*\*\*+))\s*$', ('tag','rule') ], # horizontal rule
        [ list_item, ('open','list.item'), ('call',saveIndent), ('goto','eol'), ('tag','item') ],
        [ list_digit, ('open','list.digit'), ('call',saveIndent), ('goto','eol'), ('tag','item') ],
        [ r'^\s*>', ('open','quote'), ('goto','eol'), 'save' ], # blockquote
        [ r'^\s*\|', ('open','table'), ('goto','eol'), 'save' ], # table
        [ img, ('tag','img') ], # image
        [ url, ('tag','url') ], # link
        [ ref, ('pos_before','bot'), ('goto','eol'), ('tag','ref') ], # reference
        [ bold, ('tag','bold') ], # bold
        [ emph, ('tag','emph') ], # emphasis
        [ r'^```(\S*)', ('open','codeblock'), 'save' ], # codeblock
        [ r'^\$\$', ('open','mathblock'), 'save' ], # mathblock
        [ code, ('tag','code') ], # inline code
        [ math, ('tag','code') ] # inline math
    ],
    'comment': [ [ r'-->', 'close' ] ],
    'codeblock': [ [ r'^```', 'save', 'close' ] ],
    'mathblock': [ [ r'^\$\$', 'save', 'close' ] ],
    'quote': [
        [ r'^\s*>', ('goto','eol'), 'save' ],
        [ None, 'close' ]
    ],
    'table': [
        [ r'^\s*\|', ('goto','eol'), 'save' ],
        [ None, 'close' ]
    ],
    'list.item': [
        [ None, ('check',checkIndent), ('goto','eol') ],
        empty,
        [ list_item, ('valid',validIndent), ('goto','eol'), ('tag','item') ],
        [ list_item, ('next','list.item'), ('call',saveIndent), ('goto','eol'), ('tag','item') ],
        [ None, 'close' ]
    ],
    'list.digit': [
        [ None, ('check',checkIndent), ('goto','eol') ],
        empty,
        [ list_digit, ('valid',validIndent), ('goto','eol'), ('tag','item') ],
        [ list_digit, ('next','list.digit'), ('call',saveIndent), ('goto','eol'), ('tag','item') ],
        [ None, 'close' ]
    ]
}

parser = nxp.make_parser({ 'lang': lang })

# ------------------------------------------------------------------------

html5doc = """
<!doctype html>
<html lang=en>
<head>
    <meta charset=utf-8>
    <title>{title}</title>
</head>
<body>
{body}
</body>
</html>
"""

def html_wrapper(body,title):
    return html5doc.format( title=title, body=body )

def attr2str(kv):
    return ''.join([ f' {k}="{v}"' for k,v in kv.items() ])

def btag(name,body,**kv):
    return f"<{name}{attr2str(kv)}>\n{body}\n</{name}>"

def itag(name,body,**kv):
    return f"<{name}{attr2str(kv)}>{body}</{name}>"

def stag(name,**kv):
    return f"<{name}{attr2str(kv)}>"

# ----------  =====  ----------

md_ref = dict()

class md_reflink:
    __slots__ = ('body','key')
    def __init__(self,body,key):
        self.body = body
        self.key = key 
    def __str__(self):
        val = md_ref[self.key]
        if isinstance(val,str):
            return itag('a',self.body,href=val)
        else:
            return itag('a',self.body,href=val[0],title=val[1])

class md_refimg:
    __slots__ = ('alt','key')
    def __init__(self,alt,key):
        self.alt = alt
        self.key = key 
    def __str__(self):
        val = md_ref[self.key]
        if isinstance(val,str):
            return stag('img',alt=self.alt,src=val)
        else:
            return stag('img',alt=self.alt,src=val[0],title=val[1])

class md_list:
    def __init__(self,ord=False):
        self.ord = ord
        self.item = []
    
    def __len__(self): return len(self.item)
    def __getitem__(self,key): return self.item[key]
    
    def __str__(self):
        return btag(
            'ol' if self.ord else 'ul',
            '\n'.join([ itag('li',t) for t in self.item ])
        )
    
    def append(self,body):
        self.item.append(body)

def md_procval(elm):
    pass

def md_procimg(elm):
    pass

def md_procurl(elm):
    pass

def md_callback(tsf,elm):
    if isinstance(elm,nxp.RMatch):
        beg,end = elm.beg, elm.end 
        tag = elm.tag 

        if tag == 'esc':
            tsf.append( beg, end, ''.join(elm.text) )
        elif tag == 'sec':
            dpt = len(elm[0].text)
            txt = tsf.buf.after(end).strip()
            tsf.appendl( beg[0], itag(f'h{dpt}',txt) )
        elif tag == 'img':
            pass
        elif tag == 'url':
            pass
        elif tag == 'bold':
            pass
        elif tag == 'emph':
            pass
        elif tag == 'code':
            pass
        elif tag == 'math':
            pass
        elif tag == 'ref':
            pass # save reference

    else:
        pass

def compile( infile, outfile, wrap=html_wrapper ):
    pass
