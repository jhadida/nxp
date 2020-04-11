
# Line `nxp.parser.line`

Line objects segment each line of text into:

- Indent
- Text
- Post
- EOL


## Old description

`Line` objects segment each line of text in **four parts**:
```py
L = Line( '  example \n', lineno, offset )

    # '  example \n'
    #    1      23
    #
    # 1: pre
    # 2: txt
    # 3: eol
```

The properties of a `Line` are:

| Property | Description |
|---|---|
| `lineno` | line index in buffer |
| `offset` | offset of first character from start of buffer |
| `indent` | substring until position 1 |
| `text` | substring between positions 1 and 2 |
| `post` | substring between positions 2 and 3 |
| `eol` | substring after position 3 |

If `eol` is empty, then this is the last line of the buffer.

 - Position object has a line and char number, and methods to increment either. They can be compared to compute the distance.
 - Buffer object contains all lines (may be more complicated in the future to implement streams).
 - Cursor object has reference to Parser, a Position, and the current Line is cached. It also contains flags: `bof/eof` (file), `bol/eol` (line), `boi/eoi` (indent), `bot/eot` (text), `bop/eop` (post), `bow/eow` (word). These are set by comparing current char position to Line segments. It implements methods such as: `is_indent`, `is_text`, `is_post`.

Not sure yet:
 - Namespace object is basically a dictionary.
 - Context object is a list of namespaces. Three namespaces IDs are reserved: global, stack and local. Global and local are scalar Namespace, inherited is a stack of Namespace.

