
import logging
from .match import RElement, RMatch
from .rule import Scope, PreCheckError, PostCheckError
from nxp import MatchError

# ------------------------------------------------------------------------

class ParseError(Exception): pass 

class Context:
    """
    """
    def __init__(self,scope,event):
        assert isinstance(scope,dict) and 'main' in scope, \
            TypeError('Input should be a dictionary with key "main".')
        assert all([ isinstance(s,Scope) for s in scope.values() ]), \
            TypeError('Scope values should be Scope objects')

        self._event = event
        self._scope = scope
        self._reset()

        # create dedicated channels
        event.create('match')
        event.create('save')
        event.create('open')
        event.create('close')
        event.create('swap')

        logging.debug('[Context] Initialized (%d scopes).',len(self._scope))

    def _reset(self):
        self._node = RElement('main')
        self._hist = []
        self._rule = None
        return self

    # properties
    @property 
    def root(self): return self._node.ancestor(-1)
    @property 
    def depth(self): return self._node.depth
    @property
    def scope(self): return self._scope[ self._node.name ]
    @property
    def scopename(self): return self._node.name
    @property
    def history(self): return self._hist
    @property 
    def stacktrace(self): return self._node.stacktrace()

    # proxy to event hub
    def publish( self, name, *args, **kwargs ):
        self._event.publish(name,self,*args,**kwargs)
        return self
    def subscribe( self, name, fun ):
        return self._event.subscribe(name,fun)

    # main functions
    def log( self, msg, level=None ): # TODO: better handling of logging
        print(msg)
        return self

    def match(self,cur):
        scope = self.scope
        node = self._node 
        pos = cur.pos 
        logging.debug('[Context] Matching cursor at position: %s', pos)

        # try to match a rule
        for idx,rule in enumerate(scope):
            try: 
                # attempt to match current rule (throws if error)
                self._rule = rule
                m = rule.match(cur,self)

                # record all matches in history
                self._hist.append(m)

                logging.info('[Context] Match #%d (scope "%s", rule %d, rule ID %d).', len(self._hist), node.name, idx, rule._id)

                self.publish( 'match', match=m, scope=scope, rule=rule, idx=idx )

                return True
            except (PreCheckError,MatchError,PostCheckError):
                cur.pos = pos

        # raise error if no rule was match in strict parsing
        if scope.strict:
            msg = 'No matching rule (strict parsing, scope "%s").' % node.name
            logging.error(msg)
            cur.error(msg, exc=ParseError)
        
        self._rule = None
        return False

    def save(self,match):
        assert self._rule is not None, RuntimeError('Method save() cannot be called outside of match().')
        self.publish( 'save', match=match )
        return self._node.add_match(match)


    # proxy to scope variables
    def _ancestor(self,level):
        return self._node.ancestor(level)

    def get( self, name, level=0 ):
        return self._ancestor(level).get(name)
    def set( self, name, val, level=0 ):
        return self._ancestor(level).set(name,val)
    def apply( self, name, fun, level=0 ):
        return self._ancestor(level).apply(name,fun)
    def setdefault( self, name, val, level=0 ):
        return self._ancestor(level).setdefault(name,val)

    def append( self, name, val, level=0 ):
        self._ancestor(level).append(val)
    def inc( self, name, level=0 ):
        self._ancestor(level).inc(name)
    def dec( self, name, level=0 ):
        self._ancestor(level).dec(name)

    # scope manipulation
    def strict(self,name):
        self._scope[name].strict = True
        return self

    def relax(self,name):
        self._scope[name].strict = False
        return self

    def open( self, name ):
        assert name in self._scope, KeyError('Scope not found: "%s"' % name)
        self._node = self._node.add_child(name)
        self.publish( 'open', scope=self._node )
        return self

    def close( self, n=1 ):
        assert self.depth >= n, RuntimeError('Cannot close main scope.')
        self.publish( 'close', scope=self._node )
        self._node = self._node.ancestor(n)
        return self

    def swap( self, name ):
        assert self.depth >= 1, RuntimeError('Cannot swap main scope.')
        self.publish( 'swap', scope=self._node, target=name )
        self._node.name = name
        return self

    def next( self, name ):
        self.close()
        self.open(name)
        return self
