
from .event import Hub
from .context import Context

# ------------------------------------------------------------------------

class _Fuse:
    # maximum number of attempts for the context to match the 
    # cursor without changing its position
    MAX_ATTEMPTS = 1000

    __slots__ = ('_pos','_num')
    def __init__(self,pos):
        self._pos = pos
        self._num = 0

    def update(self,pos):
        if pos == self._pos:
            self._num += 1
            assert self._num < self.MAX_ATTEMPTS, \
                RuntimeError('Cursor has remained in the same position for too long; parsing aborted.')
        else:
            self._pos = pos 
            self._num = 0

# ------------------------------------------------------------------------

class Parser:
    """
    Implement matching logic between Cursor and Context.
    """
    __slots__ = ('_evt','_ctx','_chk')
    def __init__( self, scope, start='main', end=None ):
        self._evt = Hub()
        self._ctx = Context( scope, self._evt, start )
        self._chk = (start,end)

    @property
    def context(self): return self._ctx
    @property
    def start(self): return self._chk[0]
    @property
    def end(self): return self._chk[1]

    def reset(self):
        self._evt = Hub()
        self._ctx._reset(self.start)
        return self

    def clone(self):
        return Parser( self._ctx._scope, self.start, self.end )

    # modify strictness
    def scope(self,name):
        return self._ctx._scope[name]
    def strict(self,name):
        self.scope(name).strict = True
        return self
    def relax(self,name):
        self.scope(name).strict = False
        return self

    # proxy to event hub
    def publish( self, name, *args, **kwargs ):
        self._evt.publish(name,self,*args,**kwargs)
        return self
    def subscribe( self, name, fun ):
        return self._evt.subscribe(name,fun)

    # parsing
    def parse(self,cur):
        
        # do the parsing
        fuse = _Fuse(cur.pos)
        while not cur.eof:
            
            if cur.bol: 
                self._ctx.publish('bol',pos=cur.pos)
            
            if not self._ctx.match(cur):
                cur.nextchar()

            if cur.eol:
                self._ctx.publish('eol',pos=cur.pos)
                cur.nextline()
            
            fuse.update(cur.pos)

        # check end context
        scope = self._ctx.scopename
        check = self.end
        assert check is None or scope == check, \
            RuntimeError(f'Parsing should end in scope "{check}", but ended in scope "{scope}" instead.')

        
        
        return self._ctx.root
 