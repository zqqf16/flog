import re
import yaml
import jinja2

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class MatchingResult:
    class State(Enum):
        Match = 0
        Start = 1
        End = 2

    state: State
    captures: List[str]
    child: Optional['MatchingResult']

class MatchingContext: 
    def __init__(self, result: MatchingResult, line: str):
        self.lines = [line]
        self.captureGroups = {result.state: result.captures}

    def update(self, result: Optional[MatchingResult], line: Optional[str]):
        if line != None:
            self.lines.append(line)
        if result != None:
            self.captureGroups[result.state] = result.captures

    @property
    def content(self) -> str:
        return "".join(self.lines).strip('\n')

    def render_context(self, state):
        return {
            'lines': self.lines,
            'content': self.content,
            'captures': self.captureGroups.get(state, [])
        }

class Rule:
    class Action(Enum):
        Drop = 0
        Bypass = 1

    def __init__(self, config):
        self.name = config.get('name', "Anonymous")
        self.re_match = None
        self.re_start = None
        self.re_end = None
        self.children = None

        self.msg_match = None
        self.msg_start = None
        self.msg_end = None

        if msg := config.get('message'):
            self.msg_match = jinja2.Template(msg)
        if msg := config.get('start_message'):
            self.msg_start = jinja2.Template(msg)
        if msg := config.get('end_message'):
            self.msg_end = jinja2.Template(msg)

        if match := config.get('match'):
            self.re_match = re.compile(match)
        elif (start := config.get('start')) and (end := config.get('end')):
            self.re_start = re.compile(start)
            self.re_end = re.compile(end)

        if not self.re_match and not all([self.re_start, self.re_end]):
            raise AttributeError('Invalid rule definition')

        action = config.get('action')
        if action == 'drop':
            self.action = Rule.Action.Drop
        elif action == 'bypass':
            self.action = Rule.Action.Bypass
        elif not self.msg_match and not self.msg_start and not self.msg_end:
            self.action = Rule.Action.Drop
        else:
            self.action = Rule.Action.Bypass

        if children := config.get('patterns'):
            self.children = [Rule(child) for child in children]

    def __str__(self):
        if self.re_match:
            return f'{self.name}: "{self.re_match.pattern}", {self.action.name}'
        else:
            return f'{self.name}: <"{self.re_start.pattern}" - "{self.re_end.pattern}"> {self.action.name}'

    def __repr__(self):
        if self.re_match:
            return f'<Rule name: {self.name} match: {self.re_match.pattern}>'
        else:
            return f'<Rule name: {self.name} start: {self.re_start.pattern} end: {self.re_end.pattern}>'

    def __get_captures(self, regex, line):
        if regex and (match := regex.search(line)):
            return [g for g in match.groups()]

    def match(self, line, started=False) -> Optional[MatchingResult]:
        if started:
            # scope started
            if (captures := self.__get_captures(self.re_end, line)) != None:
                return MatchingResult(MatchingResult.State.End, captures, None)
            if not self.children:
                return None
            for child in self.children:
                if result := child.match(line, started=False):
                    result.child = child
                    return result
            return None

        if (captures := self.__get_captures(self.re_match, line)) != None:
            return MatchingResult(MatchingResult.State.Match, captures, None)
        elif (captures := self.__get_captures(self.re_start, line)) != None:
            return MatchingResult(MatchingResult.State.Start, captures, None)
        
    def filter(self, line) -> Optional[str]:
        if self.action == Rule.Action.Drop:
            return None
        elif self.action == Rule.Action.Bypass:
            return line

    def message(self, context, result) -> Optional[str]:
        state = result.state
        env = context.render_context(state)
        if state == MatchingResult.State.Match:
            if self.msg_match != None:
                return self.msg_match.render(env)
        elif state == MatchingResult.State.Start:
            if temp := self.msg_start or self.msg_match:
                return temp.render(env)
        elif state == MatchingResult.State.End:
            if temp := self.msg_end or self.msg_match:
                return temp.render(env)

    @classmethod
    def load(cls, path):
        rules = []
        with open(path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            for item in data['patterns']:
                rules.append(Rule(item))
        return rules
