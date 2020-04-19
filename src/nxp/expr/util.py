
class TokenSetIterator:
    def __init__(self,item):
        self.item = item 
    
    def __iter__(self):
        return self 

    def __next__(self):
        if self.item:
            it = self.item 
            self.item = it.next 
            return it
        else:
            raise StopIteration()

# ------------------------------------------------------------------------

class TokenSetItem:
    __slots__ = ('tok','prev','next')
    def __init__(self,tok,prev=None,next=None):
        self.tok = tok 
        self.prev = prev 
        self.next = next 

    def remove(self):
        if self.prev: 
            self.prev.next = self.next 
        if self.next:
            self.next.prev = self.prev 

    def append(self,tok):
        it = TokenSetItem(tok,prev=self,next=self.next)
        if self.next:
            self.next.prev = it 
        self.next = it
        return it 

# ------------------------------------------------------------------------

class TokenSet:
    """
    Implementation of Token set as a limited doubly linked-list.
    The aim is to facilitate removal of items during iteration.
    """
    def __init__(self,tlist):
        self.root = TokenSetItem(tlist[0])
        
        cur = self.root 
        for tok in tlist[1:]:
            cur = cur.append(tok)

    def remove(self,it):
        if it.next:
            it.next.prev = it.prev 
        if it.prev:
            it.prev.next = it.next 
        else:
            self.root = it.next 

    def __iter__(self):
        return TokenSetIterator(self.root)

# ------------------------------------------------------------------------

class TokenChain:
    def __init__(self):
        self.tok = []
        self.len = 0

    def isvalid(self): return self.len == len(self.tok)
    def isempty(self): return self.len == 0

    def __len__(self): return len(self.tok)
    def __iter__(self): return iter(self.tok)
    def __getitem__(self,key): return self.tok[key]

    def append(self,tok):
        self.tok.append(tok)

    def commit(self):
        self.len = len(self.tok)
    def revert(self):
        del self.tok[self.len:]
