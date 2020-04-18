
# Language

We finally get to the claim that languages can be defined in NXP with a simple Python dictionary. Thank you for reading the documentation up to this point!

## Definition

We [previously showed](parse/rule) how to define individual rules using Python lists, and [mentioned](parse/intro?id=in-practice) that these rules would then be grouped into scopes before being fed to the `Parser` object. 

Note about nested scope and dots in names. Nested scope in definition does not necessarily correspond with nested scopes during parsing!

```py
{
    'lang': ...,
    'strict': [ ... ]
}
```

### Strict vs. non-strict

Strict scopes throw an error if no matching rule is found.
Non-strict scopes simply move the cursor forward.

## Parsing

Call the following:
```
nxp.parse( lang, text )
nxp.parsefile( lang, file )
nxp.parselines( lang, lines )
```

Alternatively, create parser manually with `nxp.make_parser()` (the previous methods take a parser in input instead of the language dictionary).

<a href='hello wordl!'></a>