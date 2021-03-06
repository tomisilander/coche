# Coche

Coche is a simple Python-module that provies simplified interface to
python *argparse* package in order to handle command line arguments.
While it cannot do everything *argparse* can do,
it tries to make providing simple command line argument handling support so
easy that one has no excuse to not provide one.

## Overview

I often find standard argparse too heavy to use.
Coche defines one function, `coche.che`, that 
parses a command line definition (a.k.a usage) string and 
calls the main function with proper parameters.

It is designed to be used to call the main function of the program, say:
```
def main(arg1, arg2, opt1=3, option2=False):
	 print arg1, arg2, opt1, option2
```
by first defining the command line:
```
cldef = """
arg1 : first argument
arg2 : second argument

-o --option1 opt1 (int) : option number one
-p --option2            : option number two
"""
```
and then calling main function (or any provided function) via che:
```
import coche
coche.che(main, cldef)
```

Coche checks that there are correct number of positional arguments
and that the options provided are legal. It also casts the
arguments and builds the usage string.


## Syntax and implementation

Coche works by translating each line into a corresponding *argparse*
*add_argument*-call. There is one definition per line and the empty lines are skipped.
One can also use semicolons as a command separator.
Informally, each line has a structure with seven parts:
```
 -o --long-option dest (type) {choice1, choice2} [default-value] :some help text
```
any of which may be missing. If the first two flags are missing, the *dest* needs
to be present and it is taken to be a positional argument.

Here is an example and the corresponding *argparse*-calls:
```
import coche
argdefs =    """arg1; arg2
                arg3  : the third argument
                -o opt1 (int) [0]         : OPT1 has to be integer, default: 0
                -p --option2 (true)       : a boolean option
                -m --mode mode {Good, Bad, Ugly} [Ugly]
                -v --verbose (true)
                -q --quiet verbose (false)
                --new-pi pi-value (float) : default: 3.14.
                """
cmds = coche.translate(argdefs, description="Here are the add_arg-commands")
print('\n'.join(cmds))
```
that produces output
```
parser = argparse.ArgumentParser(description="Here are the add_arg-commands")
parser.add_argument('arg1')
parser.add_argument('arg2')
parser.add_argument('arg3', help='the third argument')
parser.add_argument('-o', type=int, dest='opt1', default='0', help='OPT1 has to be integer, default: 0')
parser.add_argument('-p', '--option2', action='store_true', help='a boolean option')
parser.add_argument('-m', '--mode', choices=['Good', 'Bad', 'Ugly'], dest='mode', default='Ugly')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-q', '--quiet', action='store_false', dest='verbose')
parser.add_argument('--new-pi', type=float, dest='pi-value', help='default: 3.14.')
args = parser.parse_args()
```

## Usage

The usual usage of coche is to call `coche.che` with a main function and argument definition.
Here an example file *foo.py*:

```
def main(a1, a2, a3, opt1=0, option2=False, mode="", verbose=False, pi_value=3):
	print(a1,a2,a3)
	print(opt1, option2, mode, verbose, pi_value)

import coche
coche.che(main,"""arg1; arg2
                arg3  : the third argument
	        -o opt1 (int) [0]         : OPT1 has to be integer, default: 0
                -p --option2 (true)       : a boolean option
                -m --mode mode {Good, Bad, Ugly} [Ugly]
                -v --verbose (true)
                -q --quiet verbose (false)
                --pi-value (float) [3.14]: default: 3.14.
                """)
```
Running the code above has desired effect:
```
$ python foo.py
usage: foo.py [-h] [-o OPT1] [-p] [-m {Good,Bad,Ugly}] [-v] [-q]
              [--pi-value PI_VALUE]
              arg1 arg2 arg3
foo.py: error: too few arguments

$ python foo.py -h
usage: foo.py [-h] [-o OPT1] [-p] [-m {Good,Bad,Ugly}] [-v] [-q]
              [--pi-value PI_VALUE]
              arg1 arg2 arg3

positional arguments:
  arg1
  arg2
  arg3                  the third argument

optional arguments:
  -h, --help            show this help message and exit
  -o OPT1               OPT1 has to be integer, default: 0
  -p, --option2         a boolean option
  -m {Good,Bad,Ugly}, --mode {Good,Bad,Ugly}
  -v, --verbose
  -q, --quiet
  --pi-value PI_VALUE   default: 3.14.

$ python foo.py a b c -q 
a b c
0 False Ugly False 3.14
```
