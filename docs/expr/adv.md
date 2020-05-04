
# Advanced usage

## Gotchas

In a sequence `Seq`, marking a token as optional is equivalent to using the `skip` option. However, using `skip` is more efficient.
```py
Seq( [tok1, Opt(tok2), tok3] )
Seq( [tok1, tok2, tok3], skip=1 )   # equivalent, but more efficient
```

In a token set `Set`, although marking a token as optional is possible, it should not be done. This is because failure to match an optional token would still constribute to the cardinality constraints specified with `min/max`, and would therefore render such constraints meaningless.

## Token search

The methods:
```py
tok.find( cursor, multi=False )
nxp.find( tok, text, multi=False )
```
are `TMatch` generators, which will look for all matches within a line (if `multi=False`), or across lines (if `multi=True`). They are both inteneded to be used within a for-loop, e.g.:
```py
for match in tok.find(cursor): # do something
```

If you only want to search for a single match, or would prefer a list of all matches, use the following instead:
```py
matches = list(tok.find( cursor ))
match = next(tok.find( cursor ))
```

## Match data

The property `match.data` of `TMatch` object will often contain a list of `TMatch` objects, corresponding to nested matches. The only exception is with `Regex` tokens, in which case `match.data` is a [regex match object](https://docs.python.org/3/library/re.html#match-objects), from the Python reference library.

Match data access:

- if the underlying token is a `Regex` object (use `match.isregex()` to check), then they return captured groups, and the number of groups, respectively;
- otherwise for all other types of tokens, they return `match.data[k]` (which is a `TMatch` object), and `len(match.data)`.

To-do: mphasize difference between match data access, and named captures.

Both [capture-related](expr/match?id=captures) methods use depth-first traversal across nested match objects, so they have the same complexity. Hence, if you need to access several named captures, use `match.captures()` once instead of repeatedly calling `match[name]`.

## Token arithmetic

> **Note:** this is an **experimental** feature, which may be removed in future versions. Please use with care.

Let's be honnest, arithmetic operations on `Token` objects just look cool, don't they? However, beware that the following are experimental at the moment, and may not always behave as expected:

```
a + b + c = Seq( [a,b,c] )      All required, in order
a | b | c = Set( [a,b,c] )      One required, more allowed
a ^ b ^ c = Xor( [a,b,c] )      One and only one required
a & b & c = All( [a,b,c] )      All required, in any order
```

Regex strings (e.g. `r'\w+'`) are supported in these operations, but only when it makes sense. Just make sure that you are not combining strings together:
```py
# this is fine if 'attr' is a token
tag = r'<\w+' + attr + r'\s*/?>'    # matches XML tags

# this is NOT a token, we're are just combining strings here
boo = r'\w+' + r'\s*=\s*' + r'-\d+'
```

## Right-to-left 

> **Note:** this feature **needs testing** and user feedback. It should be considered experimental for now.

Support for right-to-left text was considered very early on in the design of this library, and is currently implemented as a [low-level option](ref/io?id=right-to-left-text) in `Buffer` objects. However, it has **NOT** been tested yet, and requires user feedback (e.g. with documents in arabic or hebrew).

The following top-level functions accept a keyword option `r2l=True`:
```py
nxp.make_cursor(x)
nxp.match(tok,text)
nxp.find(tok,text,multi=False)
nxp.parsefile(parser,fpath)
nxp.parsetext(parser,text)
nxp.procfile(parser,callback,fpath)
nxp.proctext(parser,callback,text)
```
