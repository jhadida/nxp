
# Buffer `nxp.parser.buffer`

Buffers are lists of [`Line`](ref/line) objects.

Currently two implementations:
```
nxp.FileBuffer
nxp.ListBuffer
```

## Usage

The input text is read by a `Buffer`, which is essentially a list of lines.
```py
fb = FileBuffer( filename, r2l=False )

len(fb) == fb.nlines     # number of lines
fb[k]                    # line k
fb.nchars                # total number of chars
```
For now, all lines are stored in the buffer after reading. Future implementation of buffers may support "streaming", whereby the list of lines would be a dequeue, gradually appending and popping lines (e.g. according to memory or data-transfer constraints). 

`Cursor` objects define a position within the buffer, they can:
 - indicate beginning / end-of line, 
 - match patterns to substring from current position,
 - advance after matches,
 - provide proxy to `Context` to define variables / trigger events.

## Future

Implementation of stream buffers.
