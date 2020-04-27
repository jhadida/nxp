
# Line

Line objects represent a single line of text in a [`Buffer`](ref/buffer). 
They are initialised with a string, and with the corresponding line number and character offset (provided by the buffer).

## Segmentation

At initialization, the newline characters are stripped from the input string.
The remaining string is stored as property `line.raw`, and the striped newline characters are stored separately as `line.nl`.
Then, the raw string is segmented by locating two "special" positions:

1. the index of the first non-whitespace character, accessed via `line.bot` (beginning-of-text);
2. the index of the last non-whitespace character, accessed via `line.eot` (end-of-text).

These two positions delineate three segments of the `raw` string (each of which may be empty):

1. segment `line.indent`, between positions `0` and `line.bot`;
2. segment `line.text`, between positions `line.bot` and `line.eot`;
3. segment `line.post`, between positions `line.eot` and the end of `line.raw`. 

## Contents and indexing

As mentioned in the previous section, the newline characters are stripped from the input string upon initialization, which has the following consequences:

- the "raw" contents of a line, accessed via `line.raw`, exclude newline characters;
- square-bracket indexing is implemented, such that `line[k]` returns character at index `k` **in the raw string** (i.e. excluding newline characters);
- the length of a line, obtained with `len(line)`, therefore corresponds to the length of the raw string;
- the entire string including newline characters can be obtained via property `line.full`.

The rationale behind this design choice is that newline characters are (unfortunately) platform-specific, and do not actually contribute to the text contents. 
This is a purely logical stance, and has no practical consequence for the user. In particular the representation of positions within the buffer as `(line,col)` tuples is unaffected by this choice.

For the developper however, this has two main consequences:

- the `offset` property, calculated in a rolling manner by the buffer, **cannot** be used for low-level file operations like `fseek`;
- the distance between positions, obtained with `buffer.distance(pos1,pos2)`, excludes all newline characters from the character count.

Although this can be seen as an annoyance, the benefit is that distances and offsets within the parser logic are actually comparable across platforms.

