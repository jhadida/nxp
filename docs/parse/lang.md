
# Language

The previous section described how individual rules are defined using Python lists. Here, we assemble these rules into scopes, and scopes into dictionaries, in order to create languages to be parsed. 

## Definition

### Scopes and languages

As mentioned in the introduction, a scope is simply a list of rules. Once again, **order matters** here; during parsing, the context keeps track of the current scope, and iterates _sequentially_ over the rules within that scope, in order to find a match at the current position. If a match is found, the cursor is updated, the scope may be updated as well, and the same process repeats until the end of the document is reached.

In order to identify each scope, and to easily define transitions between them, they need to be assigned a human-friendly _name_. Hence, the next step is to regroup all scopes within a dictionary, which represents the entire language to be parsed. Note that if your language has many scopes, or if a rule appears multiple times, you may want to assemble them elsewhere and simply store and use them (or load them) as variables instead. 

### Dictionary structure and nested scopes

The structure of the "language" dictionary is as follows:
```py
{
    'main': [           # main scope
        [], # rule1 
        [], # rule2
        # .. 
    ],
    'bar': [],          # scope 'bar'
    'foo': {
        'main': [],     # scope 'foo'
        'bar': []       # scope 'foo.bar'
    }
}
```

Each field in this dictionary can either be a **list**, or a **dictionary** itself:
- a list simply represents a scope, and contains the corresponding rules to be matched;
- a dictionary represents a _nested_ scope, and its fields (or _subscopes_) can in turn either be lists or dictionaries.

> **Important:** every nested scope **MUST** define a `'main'` key, and it **MUST** be a list.

The nesting allowed in language dictionaries is intended to represent logical hierarchies in the underlying language (e.g. a function within a class). However when the dictionary is processed in order to generate a parser, any hierarchy is **flattened** such that each scope-name refers to a list of rules. In order to ensure that the resulting scope-names are _unique_, each key in a nested scope is prefixed with the keys of its parent scopes, as a **dot-separated string**. For example, the language dictionary above will be converted to:
```py
{
    'main': [],
    'bar': [],
    'foo': [],
    'foo.bar': []
}
```

### Language hierarchies and scope stacks

This is a short but important section, make sure you understand this: 

> Nested scopes in language definitions do NOT necessarily correspond to the nesting of scopes in the syntax tree returned by the parser!

In other words, it is not because you have defined your language with a particular hierarchy, that the resulting syntax tree will be subject to the same hierarchy. The former is only abstract and simply serves to organise scopes in relation to each other; whereas the latter relates to the **graph of transitions** which is encoded by the rules themselves.

The two things are different and it might be confusing at first, but make sure you understand this, so that you know what to expect when using the NXP parsing facilities.

### Creating a parser

Once your language is defined, use `nxp.make_parser` in order to create a `Parser` object:
```py
parser = nxp.make_parser({
    'lang': {},
    'strict': [],
    'start': 'main',
    'finish': None
})
```
where:

- `lang` is the language dictionary created previously;
- `strict` can be used to specify scopes within which a rule MUST match during parsing (otherwise, the cursor simply moves along if nothing matches);
- `start` specifies the scope in which the parsing starts;
- `finish` constrains the parser to end in a specific scope (e.g. to ensure the syntax is correct).

Setting `'strict': True` means that _all_ scopes are strict, or alternatively you can use the option `'nonstrict': []` instead, if only a few scopes are not strict (do not use both options). Finally, note also that scopes can be made strict or non-strict dynamically during parsing, using the [actions](parse/rule?id=actions) `strict` and `relax`.

## Parsing

In the previous section, we explained how to define a language using a Python dictionary, and how to generate a parser for that language. 

With this parser, you can process as many documents as needed, using the following methods:
```py
nxp.parsetext( parser, text )   # text is a string
nxp.parsefile( parser, file )   # file is a path
```

NXP is not designed to be blazing fast (yet), but for a single document and a reasonable language with [a few tweaks](parse/adv?id=language-optimization), this should take betwen 10-100 ms. 
The result is a `RNode` object representing the root of the output syntax tree, which we expand on in the sections below.

### Node object

`RNode` objects represent instances of scopes within the document. They have the following properties:
```py
node.name       # name of the scope they are associated with
node.data       # list of rule matches and nested scopes
node.vars       # dictionary of scope variables (cf. actions)

node.parent     # parent scope (None for the root)
node.depth      # depth of the current node within the AST
```

The first thing you might want to do if you develop your own language, is to visualize the output syntax tree. To do so, you can simply use `print(node)`; this should be self-explanatory, and shows both nested scopes and matched rules with all the details needed.

Items in the list `node.data` may either be of type `RMatch` (rules matched within that scope), or of type `RNode` (nested scopes). For convenience, they can be accessed with a list syntax:
```py
len(node) == len(node.data)
node[3] == node.data[3] 
for item in node: # ...
```



### Match object

`RMatch` object, encountered in [callback functions](parse/adv?id=callback-functions).

