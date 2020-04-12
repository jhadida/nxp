
# Overview

The two main tasks in NXP are:

- **Matching** text patterns defined using Python objects called _tokens_ (more on this below); the output is one or several match objects with certain properties (e.g. the location of the match).
- **Parsing** a file by attempting to match _rules_ organised into multiple _scopes_; the output is a so-called Abstract Syntax Tree (or AST), which represents not only the different matches found, but also the hierarchy between them (e.g. nested patterns).

These tasks involve many components within NXP, which are described below.

## Components

To give you an idea of the components involved in matching/parsing, and how they are designed to interact with each-other, here is what NXP contains at a glance (more details in the "Reference" section):

- [`nxp.read`](https://github.com/jhadida/nxp/tree/master/src/nxp/read) implements tools to navigate text contents and match regular expressions.
    - `Line`: represents a single line in a text file or string.
    - `Buffer`: a list of `Line` objects, representing a file or multiline string.
    - `Cursor`: a position `(line,char)` and a reference to the corresponding `Buffer`.

- [`nxp.expr`](https://github.com/jhadida/nxp/tree/master/src/nxp/expr) implements tools to define text expressions with Python objects (similar to [pyparsing](https://github.com/pyparsing/pyparsing)).
    - `Token`: an object capable of matching/searching text patterns for a given `Cursor`.
    - `TMatch`: a single token match, with cursor begin/end positions and corresponding raw text.
    - `TElement`: a list of `TMatch` objects for each repetition of a given `Token` (cf. [multiplicity](expr/intro?id=multiplicity)).

- [`nxp.parse`](https://github.com/jhadida/nxp/tree/master/src/nxp/parse) implements tools to define languages with simple dictionaries (similar to [Monarch](https://microsoft.github.io/monaco-editor/monarch.html)).
    - `Rule`: a `Token` to be matched, pre/post-conditions to be verified for a successful match, and post-processing / callback functions.
    - `Scope`: a list of `Rule` objects along with some parsing properties (e.g. strictness).
    - `RMatch`: a single rule-match, containing a `TElement` object, a reference to corresponding `Rule`, and the post-processed text.
    - `RElement`: a node of the output AST, associated with a scope name, and containing a mixed list of `RMatch` and nested `RElement` objects (children nodes).
    - `Context`: a dictionary of named `Scope` objects, and the active node of the AST (an `RElement` object) which represents the _state_ during parsing. This is the only _stateful_ component.
    - `Parser`: an object capable of processing an input `Cursor`. Contains a `Context` object and defines an event loop used to hook callback functions.

## Workflow

The previous section gave an overview of the different components involved in matching/parsing. Here we illustrate the key functions and methods involved in the execution of these tasks.

### Matching

Every `Token` object defines the method `match( Cursor ) -> TElement`, which updates the location of the input cursor in case of successful matching, or raises a `MatchError` exception otherwise.

As covered in more details [here](expr/intro), `Token` objects have a _multiplicity_ which constrains the number of times a given pattern is expected to appear. 
They can also be combined with each other using binary operations:
```
a + b       Tokens expected in this order
a & b       Tokens expected in any order
a ^ b       One or the other, but not both
a | b       One or the other, or both
```

Finally, all `Token` objects define the following methods
```
find( Cursor )        -> TElement       (stop after first match)
findall( Cursor )     -> [ TElement ]   (find all matches)
finditer( Cursor )    -> generator( TElement )
```

### Parsing

Parsing is carried out by the `Parser` class, which defines the method `parse( Cursor ) -> RElement`. Internally, parsing relies heavily on the `Context` class, which effectively maintains the _state_ of the parser while the cursor is read. 

At any given time, the context is within a certain _scope_ (initially the "main" scope), and attempts to match _rules_ sequentially within that scope. 
When a match is found, the successful rule and corresponding match are saved as an `RMatch` object, and the context returns either `True` or `False` to the parser, depending on whether a matching rule was found.

Many other things happen under the hood when a matching rule is found. The `Rule` class defines the method `match( Cursor, Context ) -> RMatch`, which not only attempts to match a certain expression, but can also:
- check pre- and post-conditions, which may invalidate an otherwise successful match of the expression;
- apply some post-processing to the corresponding text;
- and invoke callback functions which may alter the state of the `Context` (e.g. transitioning to a new scope).

Several function are provided for convenience in order to parse files, multline strings, or lists of strings:
```
nxp.parse( parser, text )
nxp.parsefile( parser, filepath )
nxp.parselines( parser, lines )
```
Parsers can be generated for any language defined as a dictionary, by invoking the function `nxp.make_parser()` (more information [here](parse/intro)).
