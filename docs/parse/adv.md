
# Advanced usage

## Callback functions

Custom callback functions.
Variables can be saved at different levels.

## Working with events

Multiple channels used during parsing:
```
match   fun(match,scope,rule,idx)   after success + history
save    fun(match)                  before adding
open    fun(node)                   after transition
close   fun(node)                   before transition
swap    fun(node,target)            before reassign
bol     fun(pos)                    -
eol     fun(pos)                    before nextline
```

## Language optimization

In each scope, define a rule early on to consume characters that cannot match any other rule.
