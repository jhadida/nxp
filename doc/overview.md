
# Overview

## Components

Here is what NXP contains at a glance (more details in the "Reference" section).
This is to give you an idea of the components involved in matching/parsing, and how they are designed to interact with each-other.

- [`nxp.read`](link) implements tools to navigate text contents and match regular expressions.
    - `Line`: represents a single line in a text file.
    - `Buffer`: a list of `Line` objects, representing a file or multiline string.
    - `Cursor`: a position `(line,char)` and a reference to the corresponding `Buffer`.

- [`nxp.expr`](link) implements tools to define text expressions with Python objects (similar to [pyparsing](https://github.com/pyparsing/pyparsing)).
    - `Token`: object capable of matching/searching text patterns for a given `Cursor`.
    - `TElement`/`TMatch` = cursor start/end positions with repetitions for a given `Token`

- [`nxp.parse`](link) implements tools to define languages using the previous expressions (similar to [Monarch](https://microsoft.github.io/monaco-editor/monarch.html)).
    - `Rule` = associate `Token` with pre/post-conditions and processing + callback; defines method to match `Cursor` + `Context`
    - `Context` = stateful component; maintains scope stack; registers output (list of `Node`); serves as event-loop; keeps log of parsing
    - `RElement`/`RMatch` = either _matching_ (contains list of `Rule` to be matched), or _parent_ (contains nested `Scope`)
    - `Parser` = maintains `Context`; handles matching of `Cursor`

## Matching

Tokens define a method `match( Cursor )` which returns a `Match` object, or raises `MatchError` exception.

Contexts define a method `match( Cursor )` which returns True or False. This is the _only_ stateful component.

Rules define a method `match( Cursor, Context )` which returns `Match` and processed text.

## Parsing

Todo
