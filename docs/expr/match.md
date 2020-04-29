
# Matching

In the [introduction](expr/intro), we presented two different types of tokens (contents and composition), and four classes `Regex, Set, Seq, Rep` which are the building blocks of expressions in NXP. Here we expand on practical explanations of matching in NXP, and illustrate how to work with the output.


## Functions

All `Token` objects implement the following methods:
```py
tok.match( cursor )       # must match from the current position
tok.find( cursor )        # advance cursor until EOL and yield matches if any
tok.find( cursor, True )  # advance cursor until EOF and yield matches if any
```

Notice that these methods expect a `Cursor` object in input (not text), and that they may modify its position. 
Cursors can be created from a string using `nxp.make_cursor(text)`, but to make this even easier, the following top-level functions are also provided for convenience ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/helper.py)):
```py
nxp.match( token, text )        # -> TMatch/MatchError
nxp.find( token, text, multi )  # -> generator( TMatch )
```

> If `multi == False` (default), the search is performed within the current 
> line, and the cursor advances until the end-of-line (EOL position). 
> If `multi == True`, the search is performed _across_ lines and the cursor 
> advances until the end-of-file instead (EOF). 
> 
> More info about the cursor object can also be found [here](ref/io?id=cursor-and-position).


## Output

The outputs of the previous methods are (lists of) `TMatch` objects, each corresponding to a single match, and storing the following properties:
```py
match.tok     # reference to the token that was matched
match.beg     # postition where the match begins
match.end     #         "           "     ends
match.text    # the raw text between these positions
match.data    # additional data depending on the Token type
```
The positions saved within each match are relative to the underlying `Buffer` object used by the input cursor. However, in order to remain lightweight, no additional information about the surrounding text is saved. 

Note that if the token matched is a [repetition](expr/intro?id=repetition), then the individual matches are stored in `match.data`, as a list of nested `TMatch` objects. Similarly, composition tokens `Set` and `Seq` also store a list in `match.data`, but `Regex` tokens store a [regex match](https://docs.python.org/3/library/re.html#match-objects) instead, from the Python reference library.

In order to show information about a particular match, you can simply `print` the corresponding object. The string representation of a match is formatted as follows:
```
pos_begin - pos_end text_matched
```
where:
- the begin/end positions are formatted as `(line,col)` (starting at 0, not 1);
- the text matched corresponds to the raw text between these positions.

Finally, because it is sometimes useful to place each match within the surrounding text, NXP also provides a way of displaying more information with:
```py
print( match.insitu(cursor.buffer) )
```
which shows the surrounding text with the match underlined with dashes (see the [examples](https://github.com/jhadida/nxp/blob/master/examples/expressions.ipynb)).


## Captures

Another nifty feature to be mentioned is the ability to _name_ `Token` objects, such that corresponding matches can be retrieved easily within complex expressions. This is called a **capture**.

Every token defines the following:
```py
tok.name            # read-only property
tok.save(name)      # returns self (i.e. can be chained)

# so this is always true: name == tok.save(name).name
```

When matching a complex expression containing the previous token, the output match can retrieve either:

- all instances of a particular named capture, using `match[name]` (returns a list);
- all named captures within the match, using `match.captures()` (returns a dict of lists).
