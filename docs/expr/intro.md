
# Expressions

The building blocks of expressions in NXP are `Token` objects ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/base.py)), and although you may only interact with derived classes in practice (each with their own specific properties), it is useful to understand that there are two kinds of tokens: either about **contents** (the text pattern itself) or **composition** (the structure of the pattern).

For practical use, you can find a notebook with commented examples in [`examples/expressions.ipynb`](https://github.com/jhadida/nxp/blob/master/examples/expressions.ipynb).

## Contents

The main contents token is the `Regex` class, which stores a regular expression pattern. 

_Wait, didn't you say we were avoiding complicated regex?_

Yes, but regex are still very useful to describe simple patterns, and they are also computationally efficient. 
They _can_ be used to define more complicated patterns (with captures, self-references, etc.), but this is where it usually starts to hurt; and this is where NXP enters the picture. 
The next sections show how to assemble contents tokens into sequences; sets with optional members; and how to deal with repetitions. 

For now, let's talk about contents. 
The base class is called `Regex` ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/content.py)), and is used like this:
```py
from nxp import Regex
r = Regex( r'-?\d+' )  # match (signed) integer numbers
```

NXP also defines many useful aliases ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/alias.py)), which you might want to use in your code for improved clarity:
```
Lit('Foo')      string literal (case sensitive)
Chars('a-z')    characters in any order
Word()          letters, digits and underscore
Bool()          True or False
NumInt()        integer number
NumFloat()      floating-point number
NumHex()        hexadecimal number
Num()           any of the above types of number
SqString()      single-quoted string
DqString()      double-quoted string
String()        either type of string
Link()          hyperlink (protocol required)
Email()         e-mail addresses
Fenced(...)     delimited contents (bracket/quote/etc.)
XML_open()      opening XML tag
XML_close()     closing XML tag
XML_self()      self-closing XML tag
XML_any()       any of the above
```

> **Note:** these aliases are **NOT** intended for validation purposes.
> It is likely that patterns like `XML_any()` or `Link()` will capture invalid contents, or occasionally fail to capture valid ones. They are intended to be **simple** patterns that capture _most_ encountered cases, with a bias towards false positives.

If you would like to add more aliases (bear in mind these need to be really generic), check the [contribution guidelines](dev/contrib).

## Composition

<!-- If you don't like it, just know that you can keep using regular expressions for parsing. -->

This is where expressions in NXP become interesting. Token composition relies on two base classes ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/compose.py)): 

```
Set( [TokenList], min=1, max=math.inf )

# derived aliases
OneOf   = Set( ..., max=1 )
TwoOf   = Set( ..., min=2, max=2 )
All     = Set( ..., min=NToken )
```

`Set` objects match one or more tokens from the input list, **in any order**. 
However, note that the arguments `min` and `max` refer to _unique_ matches within the list: so if `min == 2`, then two _distinct_ items have to match the cursor sequentially. This is analogous to a scenario such as "pick between 2 and 5 objects amongst 13 without replacement".
We will see how to match one token several times in the next section.

```
Seq( [TokenList], skip=None, maxskip=None )
```

`Seq` objects match a list of tokens **in a specific order**.
The `skip` argument can be used to allow items to be skipped, and `maxskip` limits the overall number of skips. These options can be combined to produce quite funky behaviors (use with care):

- Setting `skip` as a list of indices and `maxskip` to a positive value, means that only the specified items can be skipped, up until `maxskip` is exceeded;
- Setting `skip=True`, or setting `maxskip` only, means that any item can be skipped;
- If `maxskip` is unset, it defaults to the length of `skip`, or `NToken-1`, whichever is smallest.

> **Notes:**
> - Regex strings (i.e. `r'\w+'`) in token lists are automatically converted to `Regex` objects. 
> - If you don't like this object-oriented frenzy (aka <i>the oof</i> :smile:), please know that you can still use the [parsing module](parse/intro) with plain old regular expressions all the way.

## Repetition

The previous sections showed how to define contents tokens, and how to combine them together in order to create complex patterns to be matched. 
One special kind of composition is *self-*composition — or the repetition of a given token. The key concept here is that of _multiplicity_, which refers to the number repetitions allowed or expected to be found.

Multiplicities in NXP are represented by lists of tuples, or tuple-generating functions ([source](https://github.com/jhadida/nxp/blob/master/src/nxp/expr/repeat.py)):
```
[ (L1,U1), (L2,U2), ... ]
```
Each tuple corresponds to an **interval of validity** (bounds are _inclusive_) for the number of repetitions, with the constraint `U[i] < L[i+1]`, such that no two intervals overlap.

In practice, use the command `Rep( token, mul )` to repeat a token, where `mul` is a formatted string:
```
'1'     =>  [ (1,1) ]           exactly once
'1-3'   =>  [ (1,3) ]           between 1 and 3
'4+'    =>  [ (4,Inf) ]         4 or more
'5-'    =>  [ (0,5) ]           between 0 and 5
```

There are also a few aliases defined for convenience:
```
Opt(tok)    = Rep( tok, '1-' )
Any(tok)    = Rep( tok, '0+' )
Few(tok)    = Rep( tok, '1+' )
Many(tok)   = Rep( tok, '2+' )
Even(tok)   => [ (2,2), (4,4), (6,6), ... ]
Odd(tok)    => [ (1,1), (3,3), (5,5), ... ]
```

Last but not least, `Rep` tokens have an optional property `sep` which can be used to specify a pattern that should be found between matches of the specified token.
