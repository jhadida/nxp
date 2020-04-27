
# Buffer

Buffers are lists of [`Line`](ref/line) objects. They may represent a text file stored on your hard-drive, or a list of strings, or even text being streamed from a server.

## Lines and positions

Buffers implement a list-like interface in order to access the underlying `Line` objects:
```py
buf[k]                    # line k
len(buf) == buf.nlines    # number of lines
for line in buf: ...      # iterate over lines
```

Particular locations within the text are identified by so-called "_positions_" in NXP, which are simple pairs `(line,col)` where `line` indicates the line number, and `col` the index of a character on that line (starting at 0). 

Buffers implements many operations involving positions:
- `buf.cursor(line,col)` creates a [`Cursor`](ref/cursor) object at a given position;
- `buf.after(pos)` returns text from the given position until the next end-of-line (similarly `buf.until(pos)` from the beginning of line);
- `buf.between(pos1,pos2,nl='\n')` returns text between the given positions, with newline characters if the range spans multiple lines (use `buf.lbetween` for a list of lines instead);
- `buf.distance(pos1,pos2)` returns the number of characters between two positions, **excluding newlines**.

## Contents

Text between, until and after position. Show text around and between positions.


## Implementations

There are currently two implementations:
```
nxp.FileBuffer
nxp.ListBuffer
```

> Experimental: `r2l`
> Future implementation of stream buffers.

