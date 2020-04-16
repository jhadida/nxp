
# Parsing

The difference between parsing a file versus looking for patterns within it usually boils down to **context**. When parsing a computer program for example, it matters to know whether a given function is defined within a class (in which case it is a method) or on its own; or whether a given word is within a string or not.

The NXP library implements parsing as follows:

- The expressions to be matched (`Token` objects) are associated with different **actions** to be triggered in case of match (e.g. pre/post-conditions to be verified), and stored together as `Rule` objects.

- Rules are then grouped into **scopes**, which represent the different contexts encountered during parsing (e.g. a double-quoted string, or a function call), and **transitions** are defined to change scope upon the successful match of certain rules (e.g. closing a quote, or parenthesis).

- These scopes are then given to a `Parser` object, along with a `Cursor` to be parsed. The parser internally maintains a **context** while reading the cursor, to keep track of the active scope at any point, and hence of the set of rules to be matched.

- The result of parsing has a tree-structure (due to the possible nesting of scopes), which is stored as a `RNode` object. Each `RNode` corresponds to a scope, and contains a mixed list of matches (`RMatch` objects) and nested scopes.

For the user, this process is greatly simplified by the introduction of a domain specific language of sorts:

 - Rules are defined with Python lists, which contain the expression to match, and actions defined as tuples.
 - Scopes are defined as lists of rules, which are effectively lists of lists.
 - Finally, the parser is defined with a dictionary, which associates each scope with a name.

These steps are described below.

## Defining rules

Rules are defined with Python lists formatted as follows:
```
rule = [ token, action1, action2, ... ]
```

The token can either be a `Token` object (see [expressions](expr/intro)), or a string representing a regular expression. It is also possible to set the token to `None`, in which case the corresponding rule will match without moving the cursor (this is sometimes useful to close the current scope if no other rule matches).

Actions are tuples formatted as `( name, args... )`, where name is one of the following:
```
error(msg)              interrupt parsing with ParseError exception

  SCOPE

strict(name)            make named scope strict (no match is an error)
relax(name)             relax named scope (cursor advances if no match)
open(name)              create nested scope
close(n=1)              close current scope (and n-1 parent scopes)
swap(name)              rename current scope
next(name,n=1)          close current scope and open nested scope

  VARIABLE

define(name,value)      assign variable to current scope
increment(name)         increment a variable (initialized to 0 if needed)
decrement(name)         decrement       "               " 

  RULE

save()                  append match to current node
label(name)             save match, and assign label to corresp. rule
check(fun,*args)        call: fun(cursor,context,*args) -> bool
validate(fun,*args)     call: fun(cursor,context,text,*args) -> bool
process(fun,*args)      call: fun(text,*args) -> text
replace(string)         replace matched text with string
callback(fun,*args)     call: fun(cursor,context,match)

  CURSOR

advance(n)              move cursor n characters forwards
reverse(n)                      "                backwards
goto(name)              move cursor to: bol/eol, bot/eot, bof/eof
```

> Note: order of actions matters!

### Action aliases

Short names for actions:
```
error           err
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
replace         rep
callback        call,cb
advance         adv
reverse         rev
```

### Details about rule actions

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

## Creating a parser

Note about nested scope and dots in names. Nested scope in definition does not necessarily correspond with nested scopes during parsing!

```
nxp.make_parser({
        'lang': ...,
        'strict': [ ... ]
})
```

## Parsing functions

```
nxp.parse( parser, text )
nxp.parsefile( parser, file )
nxp.parselines( parser, lines )
```

