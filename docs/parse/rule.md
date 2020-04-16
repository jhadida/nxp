
# Rule

Enough chit-chat about class designs and workflows. 
Here we show how to define rules for parsing in practice.

## Definition

Rules are defined with Python lists formatted as follows:
```
rule = [ token, action1, action2, ... ]
```

The token can either be a `Token` object (see [expressions](expr/intro)), or a string representing a regular expression. It is also possible to set the token to `None`, in which case the corresponding rule will match without moving the cursor (this is sometimes useful to close the current scope if no other rule matches).

## Actions

Actions are tuples formatted as `( name, args... )`, where name is one of the following:
```
error(msg)              interrupt parsing with ParseError exception
replace(str)            replace matched text with string

  VARIABLE

define(name,value)      assign variable to current scope
increment(name)         increment a variable (initialized to 0 if needed)
decrement(name)         decrement       "               " 

  CURSOR

advance(n)              move cursor n characters forwards
reverse(n)                      "                backwards
goto(name)              move cursor to: bol/eol, bot/eot, bof/eof

  SCOPE (** details below **)

strict(name)            make named scope strict (no match is an error)
relax(name)             relax named scope (cursor advances if no match)
open(name)              create new nested scope
close(n=1)              close current scope (and n-1 parent scopes)
swap(name)              reinterpret scope without closing
next(name,n=1)          close current scope and open nested scope

  RULE (** details below **)

save()                  append match to current node
label(name)             save match, and assign label to corresp. rule
check(fun,*args)        call: fun(cursor,context,*args) -> bool
validate(fun,*args)     call: fun(cursor,context,text,*args) -> bool
process(fun,*args)      call: fun(text,*args) -> text
callback(fun,*args)     call: fun(cursor,context,match)
```

> **Important:** the order in which actions are specified often **matters**.

## Details

### Action aliases

Several aliases for action names are defined for convenience:
```
error           err
replace         rep
open            push
close           pop
swap            swp
next            nxt
define          def,let
increment       inc
decrement       dec
label           tag
check           chk,pre
validate        valid,post
process         proc,do
callback        call,cb
advance         adv
reverse         rev
```

### Scope transition


### Rule actions

- Pre called before attempting to match
- Post called after successful match
- Proc called after post
- Call called last

Note about capture and tag.

More details about rule [here](parse/comp).

### Built-in validation / post-processing

Validate:
```
range(lo,up,b='()')
gt(val)
lt(val)
geq(val)
leq(val)
path()
file()
dir()
symlink()
```

Process:
```
null()
upper()
lower()
replace(old,new)
lstrip(s=None)
rstrip(s=None)
urlenc()
htmlenc(q=True)
tab2space(n=2)
```