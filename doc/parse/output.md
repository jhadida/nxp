
# Scope

A `Scope` consists of a list of `Rules`, which are capable of matching patterns, and performing `Actions`. Scopes have a name, and contain a `Register` and a `Tokenizer`.

A scope attempts to match rules sequentially from first to last, and fails if it cannot match any rule.

When triggered during parsing, new scopes are instanciated with a clean register.

## Tokenizer

Tokenizer objects take a line in input, and behave as lists. They **must** be able to indicate beginning of line, and end of line.

The most basic tokenizer is of course the string itself, where each character is a token.

A more advanced tokenizer could split a string into whitespace and non-whitespace for example.
