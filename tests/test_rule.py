from contextvars import Context
import pytest

from flog.rule import MatchingContext, MatchingResult, Rule


def test_rule_init():
    config = {
        'name': 'test',
        'match': '^test',
        'message': 'test',
    }
    rule = Rule(config)
    assert rule.name == 'test'
    assert rule.re_match.pattern == '^test'
    assert rule.re_start == None
    assert rule.re_end == None
    assert rule.action == Rule.Action.Bypass

    assert Rule({'match': 'hello'}).action == Rule.Action.Drop
    assert Rule({'match': 'hello', 'action': 'bypass'}).action == Rule.Action.Bypass
    assert Rule({'match': 'hello', 'action': 'other'}).action == Rule.Action.Drop

    with pytest.raises(AttributeError):
        Rule({
            'name': 'test',
            'message': 'test'
        })

    with pytest.raises(AttributeError):
        Rule({
            'name': 'test',
            'start': '^start',
            'message': 'test'
        })
    with pytest.raises(AttributeError):
        Rule({
            'name': 'test',
            'end': '^end',
            'message': 'test'
        })


def test_rule_match():
    config = {
        'name': 'test',
        'match': '^test',
        'message': 'test',
    }
    rule = Rule(config)
    result = rule.match('test the test')
    assert result.captures == []
    assert result.state == MatchingResult.State.Match
    assert rule.match('not match') is None

    config = {
        'name': 'test',
        'start': '^start',
        'end': '^end',
        'message': 'test',
    }
    rule = Rule(config)
    assert rule.match('start the test').state == MatchingResult.State.Start
    assert rule.match('test the test') is None
    assert rule.match(
        'end the test', started=True).state == MatchingResult.State.End
    assert rule.match('end the test', started=False) is None

def test_rule_nested():
    config = {
        'name': 'test',
        'start': '^start',
        'end': '^end',
        'message': 'test',
        'patterns': [
            {
                'name': 'child',
                'start': '^child start',
                'end': '^child end',
            },
            {
                'name': 'match',
                'match': '^match',
            },
        ]
    }
    rule = Rule(config)
    assert rule.match('start the test').state == MatchingResult.State.Start
    nested = rule.match('child start', started=True)
    assert nested.state == MatchingResult.State.Start
    assert nested.child.name == 'child'

    assert rule.match('match balabala', started=True).child.name == 'match'


def test_rule_message():
    rule = Rule({
        'name': 'test',
        'match': '(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}.\\d{3}).*test',
        'message': '{{ content }} {{ lines|length }} {{ captures|length }} {{ captures[0] }}',
    })

    assert rule.msg_match != None

    content = '2022-04-08 16:52:37.152 this is a test message'
    result = rule.match(content)
    ctx = MatchingContext(result, content)

    msg = rule.message(ctx, result)
    assert msg == content+' 1 1'+' 2022-04-08 16:52:37.152'