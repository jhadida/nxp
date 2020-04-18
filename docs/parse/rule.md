
# Rule

Enough chit-chat about class designs and workflows. 
Here we show how to define rules for parsing in practice.

## Definition

Rules are defined with Python lists formatted as follows:
```py
rule = [ token, action1, action2, ... ]
```

The token item can either be a `Token` object (see [expressions](expr/intro)), or a string representing a regular expression. It is also possible to set the token to `None`, in which case the corresponding rule will match without moving the cursor (this is sometimes useful to close the current scope if no other rule matches).

> **Important:** the order in which actions are specified often matters (see details section below)!

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
pos(name)               check cursor is at: bol/eol, bot/eot, bof/eof

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

And here are couple of examples showing how to define rules with actions:
```py
# count and save occurrences of 'foo'
rule = [ r'foo', ('increment','foo'), 'save' ]

# replace patterns "${name}" with data from _some_dict
# and save occurrences with label "var"
def var_replace(text):
    return _some_dict[ text[2:-1] ]

rule = [ r'${\w+}', ('proc',var_replace), ('tag','var') ]
```

## Details

### Order of actions

Changing the order in which actions are specified for a given rule may lead to very different results in output. To make matters worse, the order in which actions are listed is not always the order in which they are executed, which makes this topic a litte bit complicated...

The reason has to do with the implementation of the `Rule` object, which is explained in more details [here](ref/parse). Rules have several properties which store lists of functions to be called at different stages of the matching process. Each action listed above is stored in one of these properties, and is therefore only executed at the corresponding stage, if at all.

Fortunately, _most_ actions are stored in the `call` property, which is the last stage. There are just a few exceptions listed below, which will always be executed before all other actions, if at all:
```
Before the token is matched (property 'pre'):
  check
  pos
  
After the token is matched (property 'post'):
  validate

After post functions (property 'proc'):
  process
  replace
```

That's it. All other actions are executed sequentially in the order specified, but only after these few exceptions.

### Capturing matches

By default, matching rules are **NOT** saved in the output syntax tree. In order to save a match within the `RNode` corresponding to the current scope, the action `'save'` must be listed explicity. 

There are two alternative actions which implicitly save the corresponding match (then `'save'` is not needed):

- `label(name)` assigns a label to the corresponding match before saving it;
- `replace(str)` replaces the text matched, and assigns the label `'rep'` before saving the match.

### Scope transitions

Scope transitions are effected by the following actions:
```
open(name)
close(n=1)
swap(name)
next(name,n=1)
```

To emphasize the importance of ordering actions correctly, beware that the following rule definitions will lead to different outputs:
```py
# save the match in current scope, and then create nested scope
r = [ token, ('label','bar'), ('open','foo') ]

# create nested scope first, then save the match within that new scope
r = [ token, ('open','foo'), ('label','bar') ]
```

### Action aliases

The following aliases are defined for convenience:
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

### Built-in validation / post-processing

For the `validate` action, the input function can be replaced with one of the following names:
```
range(lo,up,b='()')     convert text to float, and check within range
gt(val)                          "            "          greater than >
lt(val)                                                  less than <
geq(val)                                                 greater or equal >=
leq(val)                                                 less or equal <=
path()                  check that matched text is an existing path
file()                          "           "         existing file
dir()                           "           "         existing folder
symlink()                       "           "         valid symlink
```

For the `process` action, the input function can be replaced with one of the following names:
```
null()                replace matched text with empty string ''
upper()               to upper case
lower()               to lower case
replace(old,new)      string substitution
strip(s=None)         strip matched text
lstrip(s=None)        left strip
rstrip(s=None)        right strip
urlenc()              encode special characters for valid URL
htmlenc(q=True)               "               "           HTML
tab2space(n=2)        replace tabs with spaces
```
