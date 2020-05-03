
# Rule

The [introduction](parse/intro) previously described three different levels (rule, scope, language) that are used to define parsers in NXP. Here expand on how rules are defined and used in practice.

## Definition

Rules are defined with Python lists formatted as follows:
```py
rule = [ token, action1, action2, ... ]
```

The token item can either be a `Token` object (see [expressions](expr/intro)), or a string representing a regular expression. It is also possible to set the token to `None`, in which case the corresponding rule will match without moving the cursor (this is sometimes useful to close the current scope if no other rule matches).

> **Important notes:** 
> - the order in which actions are specified often matters;
> - by default, matching rules are **NOT** saved in the output `RNode` (action `'save'` must be listed).
>
> See [details](parse/rule?id=details) section below.

## Actions

Actions are tuples formatted as `( name, args... )`, where the name is one of the following ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/ruledef.py)):
```
error(msg)              interrupt parsing with ParseError exception
assert(fun,*args)       call: fun(cursor,context,match,*args)
                        and raise ParseError if function returns False
reject(fun,*args)       same but if function returns True
replace(str)            replace matched text with string

  VARIABLE

define(name,value)      assign variable to current scope
increment(name)         increment a variable (initialized to 0 if needed)
decrement(name)         decrement       "               " 

  CURSOR

advance(n)              move cursor n characters forwards
reverse(n)                      "                backwards
goto(name)              move cursor to: bol/eol, bot/eot, bof/eof
pos_before(name)        check cursor is at: bol/eol, bot/eot, bof/eof
pos_after(name)         same, but after the match

  SCOPE (** details below **)

strict(name)            make named scope strict (one rule MUST match)
relax(name)             relax named scope (cursor advances if no match)
open(name)              create new nested scope and transition to it
close(n=1)              close current scope (and n-1 parent scopes)
swap(name)              reinterpret current scope without closing
next(name,n=1)          close current scope and open nested scope

  RULE (** details below **)

save()                  append match to current RNode
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

Changing the order in which actions are specified for a given rule may lead to very different results in output. And to make things worse, the order in which actions are listed is not always the order in which they are executed, which makes this topic a litte bit complicated...

The reason has to do with the implementation of the `Rule` object ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/parse/rule.py)). Rules have several properties which store lists of functions to be called at different stages of the matching process. Each action listed above is stored in one of these properties, and is therefore only executed at the corresponding stage, if all previous stages completed successfully.

Fortunately, _most_ actions are stored in the `call` property (the last stage), which means that apart from a few exceptions listed below, the commands will be executed in the order specified (if at all) after those exceptions:
```
Before the token is matched (property 'pre'):
  check
  pos_before
  
After the token is matched (property 'post'):
  validate
  pos_after

After post functions (property 'proc'):
  process
  replace
```

And that's it! All other actions are executed sequentially in the order specified, but only after these exceptions.

### Saving matches

By default, matching rules are **NOT** saved in the output syntax tree. In order to save a match within the `RNode` corresponding to the current scope, the action `'save'` must be listed explicity. 

Alternatively, note that there are twoactions which implicitly save the corresponding match (in which case `'save'` is not needed):

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
where the optional argument `n` can be used to close multiple scopes at once.

To emphasize once more the importance of ordering actions correctly, beware that the following rule definitions will lead to different outputs:
```py
# save the match in current scope, and then transition to a nested scope
r = [ token, ('label','bar'), ('open','foo') ]

# transition to nested scope first, then save the match within that new scope
r = [ token, ('open','foo'), ('label','bar') ]
```

### Shorter aliases

The following aliases are defined as short-name alternatives (action tuple becomes `(alias,*args)`):
```
error           err,raise
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

For the `validate` action, the input function can be replaced with one of the following names (action tuple becomes `('valid',name,*args)`):
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

Similarly for the `process` action (action tuple becomes `('proc',name,*args)`):
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

If you would like to add more functions for validation / processing, the sources are [here](https://github.com/jhadida/nxp/blob/master/src/nxp/parse/util.py), and please refer to the [contribution guidelines](dev/contrib).
