
# Expression

## Contents

```
Empty()
```

Empty contents are used mainly internally as intermediary expressions, which are removed before parsing.

```
Chars(..., case='fixed')
```

A character set matches any combination of listed characters.
Case can be either:

 - fixed (default)
 - lower
 - upper
 - any

```
Lit(..., case='fixed')
```

A literal matches a specific sequence of characters (order matters).

These character sets are provided for convenience:
```
    - alpha
    - alpha8: alpha utf-8
    - white
    - digit
    - punct: punctuation
    - punct8
    - hexanum
    - delim: delimiter (eg parenthesis, brackets)
    - printable: all printable chars
    ...
```

## Composition

```
Not( Token )
```

Negates the presence of a token:

 - Using `~` is equivalent to `Not(...)`

```
Set( [TokenList], min=0, max=None, chk=None )
```

One or more tokens within the list is present:

- Using `|` creates a set with `min=1` and `max=NTokens`
- Using `^` creates a set with `max=1` (`Xor`)
- Using `&` creates a set with `max=NTokens` (`All`)
- `chk` is a function to validate matched subset

```
Seq( [TokenList], skip=False, chk=None )
```

Tokens in sequence (order matters!).

 - Using `+` on tokens builds a sequence
 - Method is provided to reorder
 - Optionally skip:
    - Boolean: any
    - List of indices
 - `chk` is a function to validate matched sequence (as list of indices)


```
Rep( Token, mul='1+', chk=None )
```

Multiplicity can be:

 - Scalar: exact number of times
 - String: `7?` (7 times, or not), `3+` (3 times, or more), `4-` (4 times, or less), `2-9` (between 2 and 9 times)
 - Array (list thereof)

Notes:

 - Using `*` is equivalent to `Rep( Tok, ... )`
 - `chk` is a function to validate matched multiplicity (e.g. even/odd)

## Condition

Positional elements act as conditions; they do not match text, but can invalidate a match. The only two conditions are: `LineStart` and `LineEnd`.

## Aliases

```
White = Chars(white)
Word = Chars(print)

Any = Set( ..., min=1 )
All = Set( ..., min=NTokens )
Xor = Set( ..., min=1, max=1 )

OneOf = Xor
TwoOf = Set( ..., min=2, max=2 )

Either = Xor
Neither = Not(Any( ... ))

Opt = Rep( ..., mul='1?' )
Many = Rep( ..., mul='1+' ) 
```

Note: 

 - A word is a sequence of non-{space,newline,indent,punctuation}, and can be numeric. Should it be printable only? Maybe make it a pattern?


# Pattern

Patterns are expressions commonly encountered in natural or computer languages.

```
Integer = Either(+ -) Chars(num)
Decimal = Either(+ -) Chars(num) Opt('.' Chars(num))
Float = complicated expression
Expnum = complicated expression
Scinum = complicated expression
Hexa = Either(0x #) Chars(hex)
Octal ...

Base64 ...
Email ...
Line = anything ending with a newline
Paragraph = anything separated by empty lines before and after
```