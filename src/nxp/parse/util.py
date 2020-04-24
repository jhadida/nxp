
import re 
import html 
from os import path as op
from urllib.parse import quote_plus as urlenc

# ------------------------------------------------------------------------

_cmp = {
    '()': lambda x,l,u: l <  x <  u,
    '(]': lambda x,l,u: l <  x <= u,
    '[)': lambda x,l,u: l <= x <  u,
    '[]': lambda x,l,u: l <= x <= u
}

def _chk_range(x,lo,up,b='()'): return _cmp[b](float(x),lo,up)
def _chk_geq(x,a): return float(x) >= a
def _chk_leq(x,a): return float(x) <= a
def _chk_gt(x,a): return float(x) > a
def _chk_lt(x,a): return float(x) < a

def _chk_dir(x): return op.isdir(x)
def _chk_path(x): return op.exists(x)
def _chk_file(x): return op.isfile(x)
def _chk_symlink(x): return op.islink(x)

Validate = {
    'range': _chk_range,
    'gt': _chk_gt,
    'lt': _chk_lt,
    'geq': _chk_geq,
    'leq': _chk_leq,
    'dir': _chk_dir,
    'path': _chk_path,
    'file': _chk_file,
    'symlink': _chk_symlink
}

# ------------------------------------------------------------------------

# TODO: mirrored strip

def _proc_null(x):
    return ''

def _proc_upper(x):
    return x.upper()

def _proc_lower(x):
    return x.lower()

def _proc_replace(x,y,z=''):
    return x.replace(y,z)

def _proc_lstrip(x,y=None):
    return x.lstrip(y)

def _proc_rstrip(x,y=None):
    return x.rstrip(y)

def _proc_strip(x,y=None):
    return x.strip(y)

def _proc_htmlenc(x,quote=True):
    return html.escape(x,quote)

def _proc_urlenc(x):
    return urlenc(x)

def _proc_tab2space(x,n=2):
    return x.replace('\t',' '*n)

Process = {
    'null': _proc_null,
    'lower': _proc_lower,
    'upper': _proc_upper,
    'replace': _proc_replace,
    'lstrip': _proc_lstrip,
    'rstrip': _proc_rstrip,
    'strip': _proc_strip,
    'htmlenc': _proc_htmlenc,
    'urlenc': _proc_urlenc,
    'tab2space': _proc_tab2space
}
