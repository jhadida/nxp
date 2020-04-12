
# Expressions

The building blocks of expressions in NXP are `Token` objects (defined [here](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/base.py)). 
As a user, you are unlikely to interact with them directly, but it is useful to understand couple of things about them:

- Each token is either about **contents** (text pattern itself) or **composition** (structure of a given pattern).
- Each token has its own **multiplicity**.

Detailed explanations below.

## Contents

The main contents token is the `Regex` class, which stores a regular expression pattern. 

_Wait, didn't you say we were avoiding complicated regex?_

I did, but regex are very good to describe small, simple patterns. They _can_ also be used to define more complicated ones, but this is where it usually starts to hurt; and this is where NXP enters the picture.

Built-in aliases (defined [here](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/alias.py)):
```
Lit
Chars
White
Word
NumInt
NumFloat
NumHex
Num
Bool
Link
Email
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
