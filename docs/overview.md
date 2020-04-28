
# Overview

The two main tasks you can perform with NXP are:

- **Matching** text patterns defined using Python objects called _tokens_ (more on this below); the output is one or several match objects with certain properties (e.g. the location of the match).
- **Parsing** a file by attempting to match _rules_ organised into multiple _scopes_; the output is a so-called Abstract Syntax Tree (or AST), which represents not only the different matches found, but also the hierarchy between them (e.g. nested patterns).

These tasks involve many components within NXP, which are briefly described below.

## Components

To give you an idea of the components involved in matching/parsing, and how they interact with each-other, here is what NXP contains at a glance (more details in the "Reference" section of this doc):

- [`nxp.io`](https://github.com/jhadida/nxp/tree/master/src/nxp/io) implements tools to navigate text contents and match regular expressions.
    - `Line`: represents a single line of text in a file or string.
    - `Buffer`: a list of `Line` objects, representing a file or multiline string.
    - `Cursor`: a position `(line,char)` and a reference to the corresponding `Buffer`.
    - `Transform`: a list of substitutions in a `Buffer`, used for post-processing.

- [`nxp.expr`](https://github.com/jhadida/nxp/tree/master/src/nxp/expr) implements tools to define text expressions with Python objects (similar to [pyparsing](https://github.com/pyparsing/pyparsing)).
    - `Token`: an object capable of matching/searching text patterns for a given `Cursor`.
    - `Regex, Set, Seq, Rep`: the building blocks of expressions, derived from `Token`.
    - `TMatch`: a token match, with begin/end positions, corresponding raw text, and a reference to the corresponding `Token`.

- [`nxp.parse`](https://github.com/jhadida/nxp/tree/master/src/nxp/parse) implements tools to define languages with simple dictionaries (similar to [Monarch](https://microsoft.github.io/monaco-editor/monarch.html)).
    - `Rule`: a `Token` to be matched, and callback functions for pre/post-conditions + post-processing.
    - `Scope`: a list of `Rule` objects, with additional parsing properties (e.g. strictness).
    - `RMatch`: a rule match, with the corresponding `TMatch` object, post-processed text, and a reference to the corresponding `Rule`.
    - `RNode`: a node of the output syntax tree, corresponding to one of the scopes defined in the language that was parsed, and containing a mixed list of `RMatch` (matching rules within that scope) and nested `RNode` objects (nested scopes).
    - `Context`: a dictionary of named `Scope` objects, responsible for building the output syntax tree (with one active `RNode` at all times), and effectively representing the _state_ of the parser. This is the only _stateful_ component.
    - `Parser`: an object capable of processing an input `Cursor`, with a `Context` object representing its state, and an event loop allowing callback functions to be hooked at various stages of parsing.

## Workflow

The previous section gave an overview of the different components involved in **matching / parsing**. Here we illustrate the key functions and methods involved in the execution of these tasks.

### Matching

Every `Token` object defines the method `match( Cursor ) -> TMatch`, which updates the location of the input cursor in case of a successful match, or raises a `MatchError` exception otherwise.

Several functions are provided for convenience in order to match strings (and not cursors):
```
nxp.match( token, text )     -> TMatch/MatchError   (beginning of text)
nxp.find( token, text )      -> TMatch/None         (stop after first match)
nxp.findall( token, text )   -> [ TMatch ]          (find all matches)
nxp.finditer( token, text )  -> generator( TMatch )
```

The `Token` class serves as an abstract base class for several concrete implementations, which are the building blocks of expressions in NXP:
- `Regex` simply stores and matches a compiled regular expression. It is intended to be combined with other tokens (using the following classes) in order to form complex expressions to be matched.
- `Seq` allows to combine tokens as a chain, to be matched one after the other in the order specified, with optional skips allowed.
- `Set` allows to group tokens together, and match any number of them without order or distinction (analogous to a scenario such as "pick between 2 and 5 objects amongst 13 without replacement").
- `Rep` allows to match repeated occurrences of a token.

> More information about matching in the [Expression section](expr/intro).

### Parsing

Parsing is carried out by the `Parser` class, which defines the method `parse( Cursor ) -> RNode` (returning the root of the syntax tree). Internally, parsing relies heavily on the `Context` class, which effectively maintains the _state_ of the parser while traversing the text. 

At any given time, the context is within a certain **scope** (initially the "main" scope), and attempts to match **rules** sequentially within that scope. 
When a match is found, the successful rule and corresponding `TMatch` object are stored as an `RMatch` object, along with post-processed text. This match may or may not be added to the output syntax tree, depending on options provided by the user when defining rules.

Many things happen under the hood when a matching rule is found. `Rule` objects define the method `match( Cursor, Context ) -> RMatch`
which not only attempts to match the underlying expression, but may also:

- check pre- and post-conditions, which can invalidate an otherwise successful match;
- apply some post-processing to the corresponding text;
- and invoke callback functions, which can alter the state of the `Context` (e.g. adding a rule-match to the output syntax tree, or transitioning to a new scope).

Several functions are provided for convenience in order to parse files, multline strings, or lists of strings:
```
nxp.parse( parser, text )           -> RNode (root)
nxp.parsefile( parser, filepath )   ->      "
nxp.parselines( parser, lines )     ->      "
```

> More information about parsing in the [Parsing section](parse/intro).
