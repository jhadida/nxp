
# Language

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

