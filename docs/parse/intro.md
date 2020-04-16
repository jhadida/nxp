
# Parsing

The difference between parsing a file versus looking for patterns usually boils down to **context**. When parsing a computer program for example, it matters to know whether a given function is defined within a class (in which case it is a method) or on its own; or whether a given word is within a string or not.

### Internally 

The NXP library implements parsing as follows:

- The expressions to be matched (`Token` objects) are associated with different **actions** to be triggered in case of match (e.g. pre/post-conditions to be verified), and stored together as `Rule` objects.

- Rules are then grouped into **scopes**, which represent the different contexts encountered during parsing (e.g. a double-quoted string, or a function call), and **transitions** are defined to change scope upon the successful match of certain rules (e.g. closing a quote, or parenthesis).

- These scopes are then given to a `Parser` object, along with a `Cursor` to be parsed. The parser internally maintains a **context** while reading the cursor, to keep track of the active scope at any point, and hence of the set of rules to be matched.

- The result of parsing has a tree-structure (due to the possible nesting of scopes), which is stored as a `RNode` object. Each `RNode` corresponds to a scope, and contains a mixed list of matches (`RMatch` objects) and nested scopes.

> Detailed information about the internal components involved [here](ref/parse).

### In practice

For the user, this process is greatly simplified by the introduction of a domain-specific language of sorts:
- Rules are defined with Python lists, which contain the expression to match, and actions defined as tuples.
- Scopes are defined as lists of rules, which are effectively lists of lists.
- Finally, the parser is defined with a dictionary, which mainly associates each scope with a name.

> More information about each of these steps in the upcoming sections:
>
> - [How to define rules?](parse/rule)
> - [How to define a language?](parse/lang)
> - [Advanced usage](parse/adv)
