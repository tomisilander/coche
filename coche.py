#!/usr/bin/env python

from __future__ import print_function
import sys
import re
import argparse
import inspect
import warnings

def called_from_main():
    stack = inspect.stack()
    if len(stack) < 3: return False

    callerframe = stack[2][0]
    callerhash = dict(inspect.getmembers(callerframe))
    caller_globals = callerhash.get('f_globals', False)
    if caller_globals:
        return caller_globals.get('__name__', None) == '__main__'


def gen_lines(s):
    for line in s.splitlines():
        for part in line.split(';'):
            if len(part.strip())>0:
                yield part.strip()

line_rexp = r"""
(?P<short>    -\w)        ?  \s*
(?P<long>     --\w[\w-]*) ?  \s*
(?P<dest>     \w[\w-]*)   ?  \s*
(?P<type>     \([^\)]+\)) ?  \s*
(?P<choices>  \{[^\}]+\}) ?  \s*
(?P<default>  \[[^\]]+\]) ?  \s*
(?P<help>     \:.*$)      ?
"""

lrex = re.compile(line_rexp,re.VERBOSE)
tcrex = re.compile(r"<(type|class) '(\w+)'>")

def kwargstr(kwargs, ks):
    """turn fields in ks into k=v statements"""
    optstr = ''.join(", %s=%s" % (k,repr(kwargs[k]))
                     for k in ks if k in kwargs)
    return tcrex.sub(r"\g<2>",optstr) # get type form its repr

types = {'int':  int,
         'str':  str,
         'None':  str,
         'float': float}

def translate_cmd(m, posargs):
    mgs = dict((k,m.group(k)) for k in m.re.groupindex
               if m.group(k) is not None)
    def peel(k): return mgs[k][1:-1].strip()
        
    kwargs = {}

    if 'type' in mgs:
        type_str = peel('type').lower()
        if type_str in types:
            kwargs['type'] = types[type_str]
        
    if 'choices' in mgs:
        caster = kwargs.get('type',str)
        kwargs['choices'] = [caster(c.strip()) for c in peel('choices').split(',')]

    if 'default' in mgs:
        kwargs['default'] = peel('default')

    if 'help' in mgs:
        kwargs['help'] = mgs['help'][1:].strip()
        
    flags = [mgs[k] for k in ('short','long') if k in mgs]
    
    if len(flags) == 0: # positional argument
        if not 'dest' in mgs:
            raise Exception("No flag or argument found in line: %s\n" %s)
            
        optstr = kwargstr(kwargs, ('type', 'choices', 'default', 'help'))
        cmd = 'parser.add_argument(%s%s)' % (repr(mgs['dest']), optstr) 
        posargs.append(mgs['dest'])
    else: # option
        if 'dest' in mgs:
            kwargs['dest'] = mgs['dest']
        if 'type' in mgs and type_str in ('true', 'false'):
            kwargs['action'] = 'store_'+type_str

        optstr = kwargstr(kwargs, ('action', 'type', 'choices', 'dest', 'default', 'help'))
        flgstr =', '.join(repr(f) for f in flags)
        cmd = 'parser.add_argument(%s%s)' % (flgstr, optstr)

    return cmd


def translate(argdefs, posarglist=[], **arg_parse_kwargs):
    optstr = kwargstr(arg_parse_kwargs, arg_parse_kwargs.keys())[2:]
    yield "parser = argparse.ArgumentParser(%s)" % optstr
    
    for line in gen_lines(argdefs):
        m = lrex.match(line)
        if m is None:
            raise Exception("Coche syntax error: %s\n" % line)

        yield translate_cmd(m, posarglist)

    yield "args = parser.parse_args()"
        

def che(func, argdefs, print_cmds = False, **arg_parse_kwargs):

    if not called_from_main(): return

    posargs = []    
    cmds = '\n'.join(translate(argdefs, posargs, **arg_parse_kwargs))
    ns = {'posargs':posargs, 'argparse':argparse}
    if print_cmds:
        print(cmds)
        
    exec(cmds, ns)
    
    parser= ns['parser']
    if func == None:
        return parser.parse_args()
    else:
        func_kwargs = vars(parser.parse_args())
        pargs = [func_kwargs[posarg] for posarg in posargs]
        for posarg in posargs: del func_kwargs[posarg]
        return func(*pargs, **func_kwargs)
    
if __name__ == '__main__':
    print(che(None, open(sys.argv.pop(1)).read(), print_cmds=True,
              description="Test command line checker by giving a file containing "
                           "the definintion as a first argument."))
