
<a href="https://choosealicense.com/licenses/mpl-2.0/"><img src="assets/license.svg" alt="License: MPLv2" align="middle" style="margin: 0 20px"></a>
<a href="https://pypi.org/project/nxp/"><img src="assets/pypi.svg" alt="PyPI: nxp" align="middle" style="margin: 0 20px"></a>
<a href="https://jhadida.github.io/nxp/"><img src="assets/docs.svg" alt="Documentation" align="middle" style="margin: 0 20px"></a>

# NXP: Natural eXpression Parsing

NXP is a parsing library written in Python 3, inspired by [pyparsing](https://github.com/pyparsing/pyparsing) and [Microsoft Monarch](https://microsoft.github.io/monaco-editor/monarch.html). 

It allows users to do two things:

- Define text patterns by combining Python objects, instead of writing complicated regular expressions.
- Define and parse complex languages, with a simple dictionary!

Is it really that simple? <br>
Don't take my word for it; see for yourself with the example below, and the notebooks in the `examples/` folder. :blush:

## Example: LaTeX-like commands

This is a quick example to illustrate parsing with NXP. We want to parse (very simplified) LaTeX-like patterns `\command{ body }` in the file `foo.txt`:
```txt
Inspirational quote:
\quote{
    Time you enjoy wasting is \it{not} wasted time.
}

Command without a body \command, or with an empty one \command{}.
```

This is how to define a language to match such patterns in NXP:
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
and the output is a simple AST:
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
