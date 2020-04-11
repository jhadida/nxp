
# Rule

A rule is contained within a scope, can match a cursor, and perform actions.

## Matching

The most important function of a rule is to match a pattern with the input `Cursor`.


## Action

All rules can be assigned a parsing action, which is executed when matching is successful.

This is instrumental to create contexts; the successful matching of a rule can alter parsing rules dynamically.

Actions can be specified either pre- or post-match (or both).


Can be specified as a dictionary with string or array valued fields:
```
@trigger(name)      trigger event
@log(msg)           log message to console

  SCOPE

@open(scope)        start nested scope
@close              close current scope, and restore parent scope
@next(scope)        equivalent to: @close, @open(scope)

@switch(scope)      reinterpret current scope
                    equivalent to: @goto(scope_start), @close, @open(scope)

  CURSOR

@adv(n)             move n characters forwards
@rev(n)             move n characters backwards
@goto(name)         move to named position (e.g. beginning of scope)


  STORED VALUES

@op(op,args...)     apply operation to variable
                    example operations: { +, -, += }

@let(name,val)      declare inherited variable
@let(name,val,grp)  define variable in named group 
                    special groups: { global, local }

  CONDITIONS

@assert(name)       check named condition
@reject(name)       check named condition
@pos(name)          check that position matches specified
                        bol, eol

  TRANSFORM

@validate(name)     invoke named validator
@sanitize(name)     invoke named sanitizer
@call(name)         invoke registered function
```

Or as a callback:
```
action( actobj ) where

    actobj defines methods for all previous string commands
```

### Capture

A capture is a special kind of action to assign a name to the match, which is used to pull results together after parsing.

Names can either be:
 - global (available at the top level);
 - shared (under namespace);
 - local (current rule only).

<!-- If name is not specified in capture, a per-grammar unique ID is used. -->

### Transform

A transformation is a special kind of action, which is applied to the underlying matched contents.

Provide the following transforms:
```
    same
    null
    upper
    lower
    firstCap (relative to definition of white)
    replace
    stripFence (stripBoth?)
    stripLeft
    stripRight
    strip
    split
```

### Callback

A callback is a special kind of action, which is invoked when a monitored event is triggered.

Callbacks can be added with method `on( evtName, function )`.
