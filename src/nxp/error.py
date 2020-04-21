
class MatchError(Exception): pass

# ----------  =====  ----------

class PreCheckError(Exception): pass
class PostCheckError(Exception): pass

# ----------  =====  ----------

class ParseError(Exception): pass 

class ScopeError(Exception): 
    def __init__(self,name,msg='Bad Scope'):
        self.message = '%s: "%s"' % (msg,name)
    def __str__(self):
        return self.message

class TagError(Exception): 
    def __init__(self,tag,msg='Bad tag'):
        self.message = '%s: "%s"' % (msg,tag)
    def __str__(self):
        return self.message

class LengthError(Exception):
    def __init__(self,obj,msg='Bad length'):
        self.message = '%s: %d' % (msg,len(obj))
    def __str__(self):
        return self.message
    