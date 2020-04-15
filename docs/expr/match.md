
# Matching

## Functions

There are multiple functions implemented in NXP to facilitate matching ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/helper.py)):
```
nxp.match( token, text )     -> TElement/MatchError (beginning of text)
nxp.find( token, text )      -> TElement/None       (stop after first match)
nxp.findall( token, text )   -> [ TElement ]        (find all matches)
nxp.finditer( token, text )  -> generator( TElement )
```

These functions wrap arround a few simple steps which convert the input string into a `Cursor` object, and call `Token` methods:
```
tok.match( cursor )
tok.find( cursor )
tok.findall( cursor )
tok.finditer( cursor )
```

> More info about the cursor object [here](ref/cursor).

## Output

The output of the various methods is a `TElement` object (or an array thereof):

- They may contain multiple `TMatch` items, related to the multiplicity of the `Token`.
- They only contain restricted information in order to remain lightweight. In particular no text surroundings.

`TElement` object implements a list interface with random access `[]`, length, and iteration.

## Pretty-printing

String representation of a `TElement` object is formatted as:
```
[match_index] position_start - position_end text_matched
```
where positions are formatted as `(line,col)` (in reference to the `Buffer` object), and `match_index` refers to the multiplicity of the token.

In order to place the match within the surrounding text, the `Buffer` needs to be supplied to the `TElement` object:
```
print(match.insitu( cursor.buffer ))
```

