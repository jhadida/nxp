
# Processing

Intro to processing and Transform objects. Link to more information.

## Text-processor

Structure of a text-processor using `Transform` and `nxp.procfile`:
```py
from nxp import ScopeError, TagError, procfile, proctext

class Compiler:

    def __init__(self):
        # shared properties

    def procfile(self,fpath):
        return procfile( parser, self._callback, fpath )

    def proctext(self,text):
        return proctext( parser, self._callback, text )

    def _callback(self,elm):
        if isinstance(elm,RMatch):
            beg = elm.beg
            end = elm.end 
            tag = elm.tag

            if tag == 'foo':
                # 'foo' rule was matched
            elif tag == 'bar':
                # 'bar' rule was matched
            else:
                raise TagError(tag)

        elif elm.name == 'foo':
            # matches within scope 'foo'
        elif elm.name == 'bar':
            # matches within scope 'bar'
        else:
            raise ScopeError(elm.name)

    def _proc_foo(self,elm):
        # process matches with scope 'foo'

    def _proc_bar(self,elm):
        # process matches with scope 'bar'
```

See complicated example with [Markdown parser](https://github.com/jhadida/nxp/blob/master/examples/markdown.py).

