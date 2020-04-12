
[![License: MPLv2](https://img.shields.io/badge/license-MPLv2-green)](https://choosealicense.com/licenses/mpl-2.0/)
[![Documentation](https://img.shields.io/badge/docs-https%3A%2F%2Fjhadida.github.io%2Fnxp%2F-blue)](https://jhadida.github.io/nxp/)

# NXP: Natural eXpression Parsing

NXP is a parsing library written in Python 3, inspired by [pyparsing](https://github.com/pyparsing/pyparsing) and [Microsoft Monarch](https://microsoft.github.io/monaco-editor/monarch.html). 

It allows users to do two things:

- Define text patterns by combining Python objects, instead of writing complicated regular expressions.
- Define and parse complex languages, with a simple dictionary!

Can it be that simple, you ask? <br/>
Don't take my word for it; check out the example below, and see for yourself. :blush:

## Example: simple LaTeX-like language

We want to parse the following file, say `foo.txt`, which contains LaTeX-like patterns `\command{ body }`:
```txt
Inspirational quote:
\quote{
    Time you enjoy wasting is \it{not} wasted time.
}

Command without a body \command, or with an empty one \command{}.
```

NXP allows you to easily define a language to match such patterns:
```py
import nxp

# define these rules separately so they can be re-used
backslash = [ r'\\\\', ('rep','\\') ] 
command = [ r'\\(\w+)', ('open','command'), ('tag','cmd') ] 

# create a parser
parser = nxp.make_parser({
	'lang': {
		'main': [
			backslash,  # replace escaped backslashes
			command     # open "command" scope if we find something like '\word'
		],
		'command': { # the "command" scope
			'main': [
				[ r'\{', ('open','command.body'), ('tag','body') ],
					# open "body" subscope if command is followed by '{'
				[ None, 'close' ] 
					# otherwise close the scope
			],
			'body': [ # the "command.body" scope
				backslash,
				[ r'\\\{', ('rep','{') ],
				[ r'\\\}', ('rep','}') ],
					# deal with escapes before looking for a nested command
				command, 
					# look for nested commands
				[ r'\}', ('tag','/body'), ('close',2) ]
					# the command ends when the body ends: close both scopes
			]
		}
	}
})

print(nxp.parsefile( parser, 'foo.txt' ))
```

The output is a simple AST:
```
+ Scope("main"): 3 element(s)
	[0] Scope("command"): 2 element(s)
		[0] \\(\w+)
			(0) (1, 0) - (1, 6) \quote
		[1] Scope("command.body"): 3 element(s)
			[0] \{
				(0) (1, 6) - (1, 7) {
			[1] Scope("command"): 2 element(s)
				[0] \\(\w+)
					(0) (2, 30) - (2, 33) \it
				[1] Scope("command.body"): 2 element(s)
					[0] \{
						(0) (2, 33) - (2, 34) {
					[1] \}
						(0) (2, 37) - (2, 38) }
			[2] \}
				(0) (3, 0) - (3, 1) }
	[1] Scope("command"): 1 element(s)
		[0] \\(\w+)
			(0) (5, 23) - (5, 31) \command
	[2] Scope("command"): 2 element(s)
		[0] \\(\w+)
			(0) (5, 54) - (5, 62) \command
		[1] Scope("command.body"): 2 element(s)
			[0] \{
				(0) (5, 62) - (5, 63) {
			[1] \}
				(0) (5, 63) - (5, 64) }
```

> **Note:** begin/end positions are given in the format `(line,col)`, **starting at 0** (not 1).
