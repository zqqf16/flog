from typing import Tuple, Optional
from .rule import *

class Engine:
    def __init__(self, rules):
        self.rules = rules
        self.stack = []
        self.dest_fp = None

    def find_rule(self, line: str) -> Tuple[Rule, MatchingResult]:
        for rule in self.rules:
            if result := rule.match(line):
                return (rule, result)
        return None, None
    
    def run(self, src: str, dest: str, append=False):
        self.stack = []
        if dest:
            self.dest_fp = open(dest, 'a' if append else 'w')

        with open(src) as f:
            for line in f:
                self.process(line)

        if self.dest_fp:
            self.dest_fp.close()

    def process(self, line: str):
        rule = None
        context = None
        result = None
    
        if len(self.stack) > 0:
            rule, context = self.stack[-1]
            result = rule.match(line, started=True)
            if not result:
                context.update(None, line)
                output = rule.filter(line)
                self.write(output)
                return
        else:
            rule, result = self.find_rule(line)
            if not rule:
                self.write(line)
                return

        if not rule or not result:
            self.write(line)
            return

        if result.state == MatchingResult.State.Start:
            if result.child: # start a new scope
                context.update(None, line)
                rule = result.child
            context = MatchingContext(result, line)
            self.stack.append((rule, context))

        elif result.state == MatchingResult.State.Match:
            if result.child:  # child match
                context.update(result, line)
                rule = result.child
            context = MatchingContext(result, line)

        elif result.state == MatchingResult.State.End:
            context.update(result, line)
            self.stack.pop()

        if message := rule.message(context, result):
            self.show(message)

        if output := rule.filter(line):
            self.write(output)

    def show(self, message: str):
        print(message)
        pass

    def write(self, content: str):
        if self.dest_fp and content != None:
            self.dest_fp.write(content)
