
from .event import Hub
from .context import Context

# ------------------------------------------------------------------------

class _Fuse:
    # maximum number of attempts for the context to match the 
    # cursor without changing its position
    MAX_ATTEMPTS = 1000

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
    def __init__( self, scope ):
        self._evt = Hub()
        self._ctx = Context(scope,self._evt)

    @property
    def context(self): return self._ctx

    def reset(self):
        self._evt = Hub()
        self._ctx._reset()
        return self

    def clone(self):
        return Parser( self._ctx._scope )

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
            
            # notify about EOL/BOL
            if cur.eol:
                self._ctx.publish('eol')
                cur.nextline()
                continue 
            elif cur.bol: 
                self._ctx.publish('bol')

            # match rules
            if not self._ctx.match(cur):
                cur.nextchar()

            # update fuse
            fuse.update(cur.pos)

        # check that context is in main state
        scope = self._ctx.scopename
        assert scope == 'main', RuntimeError(f'Parsing should end in main scope, but ended in scope "{scope}" instead.')
        
        return self._ctx.root
 