# solang
SO Lang: compiler where you can only write stackoverflow answers.

## Instructions

1. Grab your tokens from [the OAuth Server I set up](https://so-lang.scoder12.repl.co).
2. Put the "shared API key" into the `SOLANG_TOKEN` environment variable and the "personal access token" into the `SOLANG_KEY` environment variable. 
3. Write some code and run it using `python lang.py file.solang -`. Optionally replace dash with a filename to write output to a file. 

## Syntax

Hello world example: 

```
4743760
/Testing console/Hello World
```

This outputs: `console.log('Hello World');`

First line: An answer id. You can find this by clicking "share" below any stackoverflow answer and copying the first number in the URL. 
You can optionally include a number after the answer ID, which is the 0-based index of the code block you want to use. 
This defaults to 0 if not provided. 

Second line: A regex replacement. It is in the form of `/regex/replacement`
and is passed directly into [re.sub](https://docs.python.org/3/library/re.html#re.sub)
so you can reference groups in the replacement. 

*Yes*, you could technically write all of your code using regex replacements, but thats against the principles of the language and it would be no fun, 
so try to keep the use of the replacements to the absolute minimum and get the bulk of your code from the answers themselves. 

### Happy Coding!
