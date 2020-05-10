
import logging

# TODO: link to PRL logger

# ------------------------------------------------------------------------

def cfmt( fmt, fg=None, bg=None, style=None ):
    """
    ANSI colour formatting.
    """

    COLCODE = {
        'k': 0, # black
        'r': 1, # red
        'g': 2, # green
        'y': 3, # yellow
        'b': 4, # blue
        'm': 5, # magenta
        'c': 6, # cyan
        'w': 7  # white
    }

    FMTCODE = {
        'b': 1, # bold
        'f': 2, # faint
        'i': 3, # italic
        'u': 4, # underline
        'x': 5, # blinking
        'y': 6, # fast blinking
        'r': 7, # reverse
        'h': 8, # hide
        's': 9, # strikethrough
    }

    # properties
    props = []
    if style:   props.extend([ FMTCODE[s] for s in style ])
    if fg:      props.append( 30 + COLCODE[fg] )
    if bg:      props.append( 40 + COLCODE[bg] )

    # display
    props = ';'.join([ str(x) for x in props ])
    return f'\x1b[{props}m{fmt}\x1b[0m' if props else fmt

def cprint( *args, **kwargs ):
    print(cfmt( *args, **kwargs ))

# ------------------------------------------------------------------------

class Logger:
    def __init__(self,lvl='info'):
        self.verbosity(lvl)

    def verbosity(self,lvl):
        self._verb = self._level(lvl)

    def debug(self,msg):
        if self._verb >= 3:
            cprint( msg, fg='b' )

    def info(self,msg):
        if self._verb >= 2:
            cprint( msg, fg='g' )

    def warn(self,msg):
        if self._verb >= 1:
            cprint( msg, fg='y' )

    def error(self,msg):
        cprint( msg, fg='r' )

    def abort(self,msg):
        cprint( msg, fg='w', gb='r' )
    
    # ----------  =====  ----------
    
    def _level(self,lvl):
        return {
            'd': 3,
            'dbg': 3,
            'debug': 3,
            'i': 2,
            'info': 2,
            'w': 1,
            'warn': 1,
            'warning': 1
        }[lvl]

    def __getitem__(self,chan):
        return {
            'd': self.debug,
            'dbg': self.debug,
            'debug': self.debug,
            'i': self.info,
            'info': self.info,
            'w': self.warn,
            'warn': self.warn,
            'warning': self.warn,
            'e': self.error,
            'err': self.error,
            'error': self.error,
            'x': self.abort,
            'abort': self.abort,
            'critical': self.abort
        }[chan]

    def _assert(self,meth,cond,msg):
        if not cond: meth(msg)
    def _reject(self,meth,cond,msg):
        if cond: meth(msg)
    
    # ----------  =====  ----------
    
    def dassert(self,*args):
        self._assert(self.debug,*args)
    def dreject(self,*args):
        self._reject(self.debug,*args)

    def iassert(self,*args):
        self._assert(self.info,*args)
    def ireject(self,*args):
        self._reject(self.info,*args)

    def wassert(self,*args):
        self._assert(self.warn,*args)
    def wreject(self,*args):
        self._reject(self.warn,*args)

    def eassert(self,*args):
        self._assert(self.error,*args)
    def ereject(self,*args):
        self._reject(self.error,*args)

    def xassert(self,*args):
        self._assert(self.abort,*args)
    def xreject(self,*args):
        self._reject(self.abort,*args)
