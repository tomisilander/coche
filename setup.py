#!/usr/bin/env python

import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info < (2, 7):
    raise NotImplementedError("You need at least Python 2.7 or Python 3.2+ to use bottle.")

setup(name='coche',
      version='0.8',
      description='A simple command line checker around argparse',
long_description="""
Coche is a simple Python-module that provies simplified interface to python 
argparse package in order to handle command line arguments. 
While it cannot do everything argparse can do, 
it tries to make providing simple command line argument handling support 
so easy that one has no excuse to not provide one.""",
      author='Tomi Silander',
      author_email='tomi.silander@iki.fi',
      url='https://github.com/tomisilander/coche',
      py_modules=['coche'],
      scripts=['coche.py'],
      license='MIT',
      platforms='any',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   ],
      )
