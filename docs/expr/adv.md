
# Advanced usage

## Character sets

[source](https://github.com/jhadida/nxp/blob/master/src/nxp/read/charset.py)

Describe `unirange`.

## Right-to-left 

> Experimental, need user feedback for improvement.

Top-level functions for matching have a `r2l` keyword argument (so does `nxp.make_cursor`).

Underlying [buffer option](http://localhost:3000/#/ref/read?id=right-to-left-text).

## Token data

- Regex saves the [match object](https://docs.python.org/3/library/re.html#match-objects) from the Python reference library.
- Sets and sequences save a list of underlying `TMatch` objets.
