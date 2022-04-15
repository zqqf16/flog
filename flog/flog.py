#!/usr/bin/env python

import argparse

from .rule import *
from .engine import *

def cmd():
    parser = argparse.ArgumentParser(description='Process logs.')
    parser.add_argument('-r', '--rule', help='Rules file', required=True)
    parser.add_argument('src', help='Source file', nargs='+')
    parser.add_argument('-o', '--output', help='Output file')
    return parser.parse_args()

def main():
    args = cmd()
    rules = Rule.load(args.rule)
    engine = Engine(rules)

    output = args.output or args.src[0] + '.out'
    for idx, src in enumerate(args.src):
        engine.run(src, output, idx > 0)

    print('Output file:', output)