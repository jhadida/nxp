
# Expressions

The building blocks of expressions in NXP are `Token` objects ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/base.py)). 
As a user, you are unlikely to interact with them directly, but it is useful to understand a couple of things about them:

- Each token is either about **contents** (text pattern itself) or **composition** (structure of a given pattern).
- Each token has its own **multiplicity**.

## Contents

The main contents token is the `Regex` class, which stores a regular expression pattern. 

_Wait, didn't you say we were avoiding complicated regex?_

Yes, but regex are still very useful to describe simple patterns, and they are also computationally efficient. 
They _can_ be used to define more complicated patterns (with captures, self-references, etc.), but this is where it usually starts to hurt; and this is where NXP enters the picture. 
The next sections show how to assemble contents tokens into sequences; sets with optional members; and how to deal with repetitions. 

For now, let's talk about contents. 
The base class is called `Regex` ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/impl.py)), and is used like this:
```py
from nxp import Regex
r = Regex( r'-?\d+' )  # match (signed) integer numbers
```

NXP also defines many useful aliases, which you might want to use for improved clarity in your code:
```
Lit('Foo')      string literal (case sensitive)
Chars('a-z')    characters in any order
White()         whitespace characters
Word()          letters, digits and underscore
NumInt()        integer number
NumFloat()      floating-point number
NumHex()        hexadecimal number
Link()          hyperlink
Email()         e-mail addresses
```

If you would like to add more aliases (bear in mind these need to be really generic), the source code is [here](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/alias.py), and you can check the [contribution guidelines](dev/contrib).

## Composition

This is where expressions in NXP become interesting. If you don't like it, just know that you can keep using regular expressions for parsing.

Token composition relies on two base classes ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/impl.py)): 

```
Set( [TokenList], min=1, max=math.inf )

# derived aliases
Any = Set( ..., min=1 )
All = Set( ..., min=NToken )
Xor = Set( ..., max=1 )

# binary operators
a | b | c = Any( [a,b,c] )      One required, more allowed
a ^ b ^ c = Xor( [a,b,c] )      One and only one required
a & b & c = All( [a,b,c] )      All required, in any order
```

`Set` objects match one or more tokens from the input list, in any order. 
Note that the arguments `min` and `max` refer to **unique** matches within the list: if `min == 2` then two **distinct** items have to match the cursor sequentially, which is _different_ from allowing repeated matching via the multiplicity (cf. next section).

```
Seq( [TokenList], skip=None, maxskip=None )

# binary operator
a + b + c = Seq( [a,b,c] )      All required, in order
```

`Seq` objects match a list of tokens in a specific order.
The `skip` argument can be used to allow items to be skipped, and `maxskip` limits the overall number of skips:

- Setting `skip` as a list of indices, and `maxskip` to a positive value, means that the specified items can be skipped up until `maxskip` is exceeded;
- Setting `skip=True`, or setting `maxskip` only, means that any item can be skipped;
- If `maxskip` is unset, it defaults to `NToken-1` (i.e. one matching item required).

> **Note:** strings in binary operations are converted to `Regex`.

## Multiplicity

The previous sections showed how to define contents tokens, and how to combine them together in order to form complex patterns to be matched. The last relevant property of `Token` objects is their _multiplicity_, which refers to the number of occurrences expected to be found (by default 1, of course).

Multiplicities in NXP are represented by lists of tuples ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/multiplicity.py)):
```
[ (L1,U1), (L2,U2), ... ]
```
where each tuple corresponds to an interval of validity for the number of repetitions of a given tokenm, with the constraint `U[i] < L[i+1]` such that no two intervals overlap.

From the user's perspective, all you need to do is call the method `tok.mul(m)` which expects a string formatted as follows:
```
'1'     =>  [ 1 ]               exactly once
'2?'    =>  [ 0, 2 ]            2 or none
'1-3'   =>  [ (1,3) ]           between 1 and 3
'4+'    =>  [ (4,Inf) ]         4 or more
'5-'    =>  [ (1,5) ]           between 1 and 5
'6+?'   =>  [ 0, (6,Inf) ]      6 or more, or none
```

Note that there are also a few aliases defined for convenience, to be used as token modifiers:
```
Rep(tok,m)      =>  tok.mul(m)
Opt(tok)        =>  tok.mul('1?')
Many(tok)       =>  tok.mul('1+')
```

## Examples

Below are a few practical examples of how to define patterns in NXP.

Matching integers or floating point numbers:
```py
from nxp import Regex, Xor

num_integer = Regex( r'-?\d+' )
num_float = Regex( r'-?\d*\.\d+([eE][-+]?\d+)?' )
number = Xor( num_integer, num_float )
```

Find repetitions of "chuck" in a sentence:
```py
from nxp import Regex, Many, make_cursor

s = 'How much wood would a woodchuck chuck if a woodchuck could chuck wood?'
c = make_cursor(s)
p = Regex( r'chuck\s*' )

for m in Many(p).finditer(c):
    print(m.show(c.buffer))
```
output:
```
Pattern: chuck\s*
	[0]  would a woodchuck chuck if a wo
	                 ------             
	[1]  a woodchuck chuck if a woodchuc
	                 ------             
Pattern: chuck\s*
	[0] uck if a woodchuck could chuck w
	                 ------             
Pattern: chuck\s*
	[0] dchuck could chuck wood?
	                 ------ 
```