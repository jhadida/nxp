
import re 
import string 

# ------------------------------------------------------------------------

def unirange(ur):
    """
    Transform list of character range 
    """ 
    assert isinstance(ur,list), TypeError('Expected a list in input')
    h2a = lambda x: int(x,16)
    out = []
    for x in ur:
        if isinstance(x,tuple):
            out.extend([ chr(c) for c in range(h2a(x[0]), h2a(x[1])) ])
        else:
            out.append(chr(h2a(x)))
    return ''.join(out)

# ------------------------------------------------------------------------

# various types of characters
white = re.sub('[\r\n]', '', string.whitespace)
digit = string.digits
punct = string.punctuation

alpha_lo = string.ascii_lowercase
alpha_up = string.ascii_uppercase
alpha = alpha_lo + alpha_up
alpha8 = alpha + unirange([ ('c0','d6'), ('d8','f6'), ('f8','ff') ])

hexanum = string.hexdigits
alphanum = alpha_lo + alpha_up + digit 
printable = ''.join(c for c in string.printable if c not in white)

# quotes and delimiters
quote_open = unirange([ 'ab', '2018', '201c', '2039' ])
quote_close = unirange([ 'bb', '2019', '201a', '201d', '201e', '203a' ])
quote = unirange([ '22', '27', 'ff22', 'ff27' ]) + quote_open + quote_close

delim_open = '({['
delim_close = ']})'
delim = delim_open + delim_close

# backspace, carriage return, line feed
bs = chr(92)
cr = '\r'
lf = '\n'
crlf = cr + lf 
