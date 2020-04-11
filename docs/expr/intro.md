
# Expressions

The building blocks of expressions in NXP are `Token` objects. 
As a user, you are unlikely to interact with them directly, but it is useful to understand couple of things about them:

- Each token is either about **contents** (text pattern itself) or **composition** (structure of a given pattern).
- Each token has its own **multiplicity**.

We explain what this means below.

## Contents

Regex (defined [here](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/impl.py)).

Built-in aliases (defined [here](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/alias.py)):
```
```

## Composition

Set and Seq (defined [here](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/impl.py)).

Operators:
```
a | b   Set( [a,b], min=1 )     One required, more allowed
a ^ b   Set( [a,b], max=1 )     One and only one required
a & b   Set( [a,b], min=2 )     All required, in any order
a + b   Seq( [a,b] )            All required, in order
```

Also works nicely with strings (converted to `Regex`).

## Multiplicity

Allow a given token to be matched multiple times (defined [here](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/multiplicity.py)).
```
'1'     =>  [ 1 ]
'2?'    =>  [ 0, 2 ]
'1-3'   =>  [ (1,3) ]
'4+'    =>  [ (4,Inf) ]
'5-'    =>  [ (1,5) ]
'6+?'   =>  [ 0, (6,Inf) ]
```

> Note: multiplicity is not the same as min/max properties.
