
# Components

## Rules

`Rule` objects associate a `Token` to be matched, with different actions that are triggered in case of match:
```
pre     pre-condition
        function (cursor,context) -> bool
post    post-condition
        function (cursor,context,token) -> bool
proc    post-processing
        function (text) -> text
call    callback
        function (cursor,context,match) -> void
```

Rules can also be assigned a "tag", which can be useful to label nodes in the output AST.

Most importantly, Rule object implement a method to match a cursor within a given context:
```
rule.match(cur,ctx)

    check pre-conditions
    match expression
    check post-conditions
    post-process text
    callback functions
```

Output is an `RMatch` object which contains reference to rule, `TMatch` match and post-processed text.

More about rule definition on the next page.

## Context

Context objects are where all the magic happens:

- They contain a dictionary of named scopes (groups of rules), and build the output AST as a tree of `RNode` objects.
- They implement matching of a cursor, which iterates over the rules of the current scope sequentially in order to find a match.
- They provide methods to update the AST:
```
open    create a new RNode nested within current one
close   select parent of current RNode as active
swap    reassign scope of current RNode 
next    equivalent to open + close
```
- They act as a facade for the definition of variables in the current scope (store in the active `RNode` object).
- They provide relay methods to publish / subscribe to events.

## Output

AST nodes are `RNode` objects. They contain a list of `RMatch` or `RNode` objects. The latter correspond to children nodes (or nested scopes).

They implement list interface with regards to contained items.

Ancestors can be selected with `node.ancestor(level)`. Stacktrace (list of scope names) can be obtained with `node.stacktrace()`.

They also store variables and provide methods:
```
get(name)
set(name,value)
setdefault(name,value)
apply(name,fun)
append(name,value)
inc(name)
dec(name
```
