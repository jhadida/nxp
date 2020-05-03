
import logging

# ------------------------------------------------------------------------

class RMatch:
    """
    RMatch objects store individual results of rule-matching.
    They contain:
      * the index of the matching rule in the corresponding Scope;
      * the TMatch object (see nxp.expr.match);
      * the corresponding text as a list of strings, each for a
        given repetition of the Token, which may be processed by
        callbacks in the Rule definition.
    """
    __slots__ = ('rule','match','text')
    
    def __init__(self,r,m,t):
        self.rule = r 
        self.text = t
        self.match = m
        logging.debug(f'[RMatch] Initialized (Rule#{r._id}).')

    def clone(self):
        return RMatch( self.rule, self.match, self.text )

    @property
    def tag(self): return self.rule.tag
    @property 
    def tok(self): return self.match.tok
    @property 
    def beg(self): return self.match.beg 
    @property
    def end(self): return self.match.end
    @property 
    def data(self): return self.match.data

    # match data
    def __len__(self):
        return len(self.match)
    def __getitem__(self,k):
        return self.match[k]

    # captures
    def __call__(self,name):
        return self.match[name]
    def captures(self,overwrite=False):
        return self.match.captures(overwrite)

# ------------------------------------------------------------------------

class RNode:
    """
    RNode objects are designed with several aspects of the parsing in mind:
    
    1.  They store the results of successful rule-matchings in a given
        scope during parsing. Each match is stored as a RMatch object
        (see above).

    2.  They store contextual variables defined by rule actions during 
        parsing, and provide several methods to access and modify them.

    3.  They implement a hierarchy that reflects the nesting of scopes
        encountered during parsing. Note that this does not necessarily
        correspond to the nesting of scopes in the language definition 
        (the transitions defined by the rules are not restricted to this
        hierarchy, although they will often follow it closely).
    """
    __slots__ = ('name','data','vars','_parent','_depth')

    def __init__( self, name, parent=None ):
        self.name = name
        self.data = []
        self.vars = dict()

        self._parent = parent 
        try:
            self._depth = parent.depth + 1
        except:
            self._depth = 0

        logging.debug(f'[RNode] Initialized (scope "{name}").')

    @property
    def nchild(self): return sum([ isinstance(x,RNode) for x in self.data ])
    @property 
    def nmatch(self): return sum([ isinstance(x,RMatch) for x in self.data ])
    @property 
    def nvars(self): return len(self.vars)
    @property 
    def depth(self): return self._depth
    @property
    def parent(self): return self._parent

    def is_root(self): return self._parent is None
    def is_leaf(self): return self.nchild == 0

    def has_vars(self): return self.nvars > 0
    def is_empty(self): return len(self.data) == 0

    def children(self): return [x for x in self.data if isinstance(x,RNode)]
    def matches(self): return [x for x in self.data if isinstance(x,RMatch)]

    # magic methods
    def __len__(self): return len(self.data)
    def __iter__(self): return iter(self.data)
    def __getitem__(self,key): return self.data[key]
    def __contains__(self,key): return key in self.vars

    def str(self,num=None,pat=False):
        off = '\t' * self.depth 
        pfx = '' if num is None else f'[{num}] '
        out = [ off + pfx + f'Scope("{self.name}"): {len(self)} element(s)' ]

        if self.has_vars():
            out.append(off + f'\t{self.vars}')
        for k,x in enumerate(self.data):
            if isinstance(x,RMatch):
                if pat:
                    out.append( off + f'\t[{k}] {x.rule}' )
                    out.append( off + f'\t\t{x.match}' )
                else:
                    out.append( off + f'\t[{k}] {x.match}' )
            else:
                out.append(x.str(num=k))
        return '\n'.join(out)

    def show(self,*arg,**kv):
        print(self.str(*arg,**kv))

    def __str__(self):
        return self.str()
        
    # variable definition
    def get(self,name):
        return self.vars[name]
    def set(self,name,val):
        self.vars[name] = val
        return val
    def apply(self,name,fun):
        return self.set( name, fun(self.get(name)) )
    def setdefault(self,name,val):
        return self.vars.setdefault(name,val)
    
    def append(self,name,val):
        self.vars.setdefault(name,[]).append(val)
    def inc(self,name):
        self.vars[name] = self.vars.setdefault(name,0) + 1
    def dec(self,name):
        self.vars[name] = self.vars.setdefault(name,0) - 1

    # mutators
    def add_match(self,match):
        assert isinstance(match,RMatch), TypeError(f'Unexpected type: {type(match)}')
        self.data.append(match)
        logging.info(f'[RNode] Match #{len(self)} (scope "{self.name}", rule ID {match.rule._id}).')
        return match

    def add_child(self,name):
        c = RNode(name,self)
        self.data.append(c)
        return c

    def replicate(self):
        return self._parent.add_child( self.name )

    # access ancestors
    # NOTE: use level=-1 to access root
    def ancestor(self,level):
        p = self 
        L = level % (self._depth + 1)
        while L > 0:
            L -= 1
            p = p._parent 
        return p

    # scope names of every ancestor
    def stacktrace(self):
        d = self._depth
        p = self
        s = [ p.name ] * (d + 1)
        while d > 0:
            d -= 1
            p = p._parent 
            s[d] = p.name
        return s
