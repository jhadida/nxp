
def clamp(x,lo,up):
    """
    Ensure x is between lo and up (inclusive).
    """
    assert lo <= up, 'Bad input bounds.'
    return min( max(x,lo), up )

def rstrip(text,chars):
    """
    Right-strip chars from text.
    Return corresponding left and right substrings.
    """
    strip = text.rstrip(chars)
    return strip, text[len(strip):]

def rstripn(text,chars):
    """
    Return char index corresponding to end of text after right-strip.
    """
    strip = text.rstrip(chars)
    return len(strip)

def lstripn(text,chars):
    """
    Return char index corresponding to beginning of text after left-strip.
    """
    strip = text.lstrip(chars)
    return len(text)-len(strip)
