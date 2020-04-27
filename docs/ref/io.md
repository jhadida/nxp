
# Input/Output module

The submodule [`nxp.io`](https://github.com/jhadida/nxp/tree/master/src/nxp/io) implements tools to navigate text contents, match regular expressions, and perform substitutions within a text.

> Detailed information about the components here:
> [Line](ref/line), [Buffer](ref/buffer), [Cursor](ref/cursor), [Transform](ref/transform)

## Buffers and lines

Within NXP, text contents is considered as a list of lines. Accordingly, the various `Buffer` objects ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/io/buffer.py)) all contain a list of `Line` objects, and implement a list interface for that member (length, iteration, random-access); so `buf[23]` returns the 24th line.

`Line` objects represent a single line of text **without newline** ([source](ttps://github.com/jhadida/nxp/blob/master/src/nxp/io/line.py)); in particular, newline characters do not count towards the length of a `Line` object. Upon initialization, the input text is split into 4 segments:

- newline characters (`line.nl`);
- leading whitespace (`line.indent`);
- trailing whitespace (`line.post`);
- remaining text (`line.text`).

### Right-to-left text

> Experimental, needs user feedback for improvement.


## Cursor and position

`Cursor` objects are essentially pointers to a particular position within the `Buffer`. Positions are formatted as `(line,col)` with indices starting at 0.

Cursors can be moved within a line using `cur.nextchar()`, and across lines using `cur.nextline()`. These methods are constrained by the length of the current line / number of lines to avoid overflows / underflows.

There are also numerous helper functions:
```
cur.goto_bot()  # beginning / end of text on current line
cur.goto_eot()

cur.goto_bol()  # beginning / enf of current line
cur.goto_eol()

cur.goto_bof()  # beginning / end of file
cur.goto_eof()
```

Cursors cannot be deep-copied. The underlying buffer (which contains the entire text) can be accessed via the property `cur.buffer`.

Finally, and most importantly, cursors implement methods to match and search regular expressions:
```
cur.match(r)        match regex from current position
cur.search(r)       search rest of line from current position
```
Note that these methods do NOT update the cursor's location.

## Transform and substitutions

To-do.
