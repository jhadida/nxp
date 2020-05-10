
import logging
from .match import RNode, RMatch
from .rule import Scope
from nxp.error import MatchError, PreCheckError, PostCheckError, ParseError

# ------------------------------------------------------------------------

class Context:
    """
    """
    def __init__(self,scope,event,start):
        assert isinstance(scope,dict) and 'main' in scope, \
            TypeError('Input should be a dictionary with key "main".')
        assert all([ isinstance(s,Scope) for s in scope.values() ]), \
            TypeError('Scope values should be Scope objects')

        self._event = event
        self._scope = scope
        self._reset(start)

        # create dedicated channels
        event.create('reset')
        event.create('match')
        event.create('save')
        event.create('open')
        event.create('close')
        event.create('swap')

        logging.debug(f'[Context] Initialized ({len(self._scope)} scopes).')

    def _reset(self,start):
        self._node = RNode('main')
        self._hist = []
        self._last = None
        self.publish('reset')
        self.open(start)
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
    def publish( self, _chan, *args, **kwargs ):
        self._event.publish(_chan,*args,**kwargs)
        return self
    def subscribe( self, chan, fun ):
        return self._event.subscribe(chan,fun)

    # main functions
    def log( self, msg, level=None ): # TODO: better handling of logging
        print(msg)
        return self

    def match(self,cur):
        scope = self.scope
        node = self._node 
        pos = cur.pos 
        logging.debug(f'[Context] Matching cursor at position: {pos}')

        # try to match a rule
        for idx,rule in enumerate(scope):
            try: 
                # attempt to match current rule (throws if error)
                m = rule.match(cur,self)
                self._hist.append(m)

                logging.info(f'[Context] Match #{len(self._hist)} (scope "{node.name}", ruleNum {idx}, ruleID {rule.id}).')

                self.publish( 'match', match=m, scope=scope, rule=rule, rnum=idx )

                return True
            except (PreCheckError,MatchError,PostCheckError):
                cur.pos = pos

        # raise error if no rule was match in strict parsing
        if scope.strict:
            msg = f'No matching rule (strict parsing, scope "{node.name}").'
            logging.error(msg)
            cur.error(msg, exc=ParseError)
        
        return False

    def save(self,match):
        # safeguard against duplicate save
        if match != self._last:
            self.publish( 'save', match=match )
            self._node.add_match(match)
            self._last = match
        return match

    # proxy to scope variables
    def _an(self,level):
        return self._node.ancestor(level)

    def get( self, name, level=0 ):
        return self._an(level).get(name)
    def set( self, name, val, level=0 ):
        return self._an(level).set(name,val)
    def apply( self, name, fun, level=0 ):
        return self._an(level).apply(name,fun)
    def setdefault( self, name, val, level=0 ):
        return self._an(level).setdefault(name,val)

    def append( self, name, val, level=0 ):
        self._an(level).append(val)
    def inc( self, name, level=0 ):
        self._an(level).inc(name)
    def dec( self, name, level=0 ):
        self._an(level).dec(name)

    # scope manipulation
    def strict(self,name):
        self._scope[name].strict = True
        return self

    def relax(self,name):
        self._scope[name].strict = False
        return self

    def open( self, name ):
        assert name in self._scope, KeyError(f'Scope not found: "{name}"')
        if name != self.scopename:
            self._node = self._node.add_child(name)
            self.publish( 'open', node=self._node )
        return self

    def close( self, n=1 ):
        assert self.depth >= n, RuntimeError(f'Cannot close main scope (in scope: {self.scopename}).')
        self.publish( 'close', node=self._node )
        self._node = self._node.ancestor(n)
        return self

    def swap( self, name ):
        assert self.depth >= 1, RuntimeError(f'Cannot swap main scope to {name}.')
        self.publish( 'swap', node=self._node, target=name )
        self._node.name = name
        return self

    def next( self, name, n=1 ):
        self.close(n)
        self.open(name)
        return self
