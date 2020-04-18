
# Matching

In the [introduction](expr/intro), we presented two different types of tokens (contents and composition), and talked about how multiplicity is different from multiple distinct matches (tl;dr: contiguous matches are grouped under a single `TMatch` object). Here we expand on practical explanations of matching in NXP, and working with the output.

## Functions

All `Token` objects implement the following methods:
```
tok.match( cursor )         must match from the current position
tok.find( cursor )          advance cursor until a match is found
tok.findall( cursor )       advance cursor until the end of the text
tok.finditer( cursor )      generator implementation of findall
```

Note that these methods expect a `Cursor` object in input (not text), and that they may modify its position. 
Cursors can be created from a string using `nxp.make_cursor(text)`, but to make this even easier, the following top-level functions are provided for convenience ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/helper.py)):
```
nxp.match( token, text )     -> TMatch/MatchError
nxp.find( token, text )      -> TMatch/None
nxp.findall( token, text )   -> [ TMatch ]
nxp.finditer( token, text )  -> generator( TMatch )
```

> More info about the cursor object [here](ref/read?id=cursor-and-position).

## Output

The outputs of the previous methods are (lists of) `TMatch` objects, each of which may contain multiple `TOccur` items (related to the multiplicity of the `Token`). In turn, each `TOccur` object stores information about the location and contents of the occurrence:
```
occur.beg       postition where the occurrence begins
occur.end               "           "          ends
occur.text      the raw text between these positions
occur.data      additional data depending on the Token type
```
The positions saved within each occurrence are relative to the underlying `Buffer` object used by the input cursor. However, in order to remain lightweight, no additional information about the surrounding text is saved. 

In order to access each occurrence of the pattern, `TMatch` objects implement a list interface:
```
len(match)                  number of occurrences
match[k]                    access each occurrence by index
for occur in match: ...     iterate over occurrences (type TOccur)
```

In order to show information about a particular match, you can simply `print` the corresponding object. The string representation of a match is formatted as follows:
```
[0] pos_begin - pos_end text_matched
[1] pos_begin - pos_end text_matched
...
```
where:
- each line corresponds to a different occurence (they should be contiguous);
- the begin/end positions are formatted as `(line,col)` (starting at 0, not 1);
- the text matched corresponds to the raw text between these positions.

Finally, because it is sometimes useful to place each match within the surrounding text, NXP also provides a way of displaying more information with:
```
print( match.insitu(cursor.buffer) )
```
which shows the surrounding text with the match underlined with dashes.
