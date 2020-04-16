
# Advanced usage

## Events

Multiple channels used during parsing:
```
match   fun(match,scope,rule,idx)   after success + history
save    fun(match)                  before adding
open    fun(node)                   after transition
close   fun(node)                   before transition
swap    fun(node,target)            before reassign
bol     fun()                       -
eol     fun()                       before nextline
```

## Nodes

Objects of type `RNode`. List interface. Pretty-printing.
