
import logging

# ------------------------------------------------------------------------

class Channel:
    """
    A channel has a name and keeps a list of subscribers.
    The subscribers are callback functions, identified internally by keys.
    When data is published into the channel, each subscriber is called with it.
    """
    __slots__ = ('_name','_subs','_pubs')
    
    def __init__(self, name):
        self._name = name 
        self._subs = dict()
        self._pubs = 0
        logging.debug(f'[Channel:{name}] Initialized.')

    @property 
    def name(self): return self._name
    @property # number of subscribers
    def nsub(self): return len(self._subs)
    @property # number of published events
    def npub(self): return self._pubs

    def subscribe(self, fun):
        """
        Add subscriber to dictionary, and return the identifier key (for unsubscribe).
        """
        assert callable(fun), 'Subscriber should be callable'
        key = id(fun) # use the ID as key
        self._subs[key] = fun 
        return key

    def unsubscribe(self, key):
        """
        Remove subscriber from the dictionary.
        """
        self._subs.pop(key, None)

    def publish(self, *args, **kwargs):
        """
        Iterate over subscribers, and call them with input args.
        """
        self._pubs += 1
        logging.debug(f'[Channel:{self._name}] Publish (nsub={self.nsub}, npub={self.npub}).')
        for key,fun in self._subs.items():
            fun(*args, **kwargs)

# ------------------------------------------------------------------------

class Hub:
    """
    A hub is an independent collection of named channels, with
    convenient proxy methods to publish/subscribe.

    Hubs define two channels by default:
        '.create': publishes events upon creation of new channels
        '.delete': publishes events upon deletion of existing channels
    """

    def __init__(self):
        self._chan = dict()
        self.create( '.create' )
        self.create( '.delete' )

    def create(self,c):
        if not self.exists(c):
            self._chan[c] = Channel(c)
            self.publish( '.create', c )

    def delete(self,c):
        if self.exists(c):
            self.publish( '.delete', c )
            del self._chan[c]

    def exists(self,c):
        return c in self._chan

    def __getitem__(self, c):
        return self._chan[c]
    
    def subscribe(self,c,fun):
        self.create(c) # create on-the-fly if channel does not exist
        return self._chan[c].subscribe(fun)

    def publish(self, _c, *args, **kwargs):
        self.create(_c)
        self._chan[_c].publish(*args, **kwargs)

# ------------------------------------------------------------------------

"""
This is the main event loop.
It can be used across modules as:
    /fileA.py:
    nxp.event.Loop.subscribe( 'fancy.name', print )

    /fileB.py:
    nxp.event.Loop.publish( 'fancy.name', 'Hello World!' )
"""
Loop = Hub()
