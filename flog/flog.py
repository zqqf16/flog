#!/usr/bin/env python

import argparse
from ast import arg

from .rule import *
from .engine import *
from .loader import *

def cmd():
    parser = argparse.ArgumentParser(description='Process logs.')
    parser.add_argument('-r', '--rule', help='Rules file', required=True)
    parser.add_argument('src', help='Source file', nargs='+')
    parser.add_argument('-o', '--output', dest='output', help='Output file', nargs='*')
    return parser.parse_args()

def main():
    args = cmd()

    rules = Loader(args.rule).load()
    engine = Engine(rules)

    output = None
    if args.output != None:
        if len(args.output) > 0:
            output = args.output[0]
        else:
            output = args.src[0] + '.out'

    for idx, src in enumerate(args.src):
        engine.run(src, output, idx > 0)
    
    if output:
        print('Output file:', output)