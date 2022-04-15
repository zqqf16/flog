from importlib.resources import contents
import pytest

from flog.rule import *
from flog.engine import *

'''
def test_create_file(tmpdir):
    p = tmpdir.mkdir("sub").join("hello.txt")
    p.write("content")
    assert p.read() == "content"
    assert len(tmpdir.listdir()) == 1
    assert 0
'''

log = '''Python 3.9.1 (default, Feb 20 2021, 11:39:07) 
[Clang 12.0.0 (clang-1200.0.32.29)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> s = []
>>> s.pop()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
IndexError: pop from empty list
>>> s = [(1, 2)]
>>> (a, b) = s.pop()
>>> a
1
>>> b
2
>>> s = [(1, 2)]
>>> a, b = s[0]
>>> a
1
>>> b
2
>>> '''


def test_engine(tmpdir):
    src = tmpdir.join('src.txt')
    src.write(log)
    dest = tmpdir.join('dest.txt')

    configs = [
        {
            'name': 'Python version',
            'match': 'Python (3.\\d+\\.\\d+\\.\\d+)',
            'message': 'Python version: {{0}}',
        },
        {
            'match': '^>>>',
        }
    ]

    rules = [Rule(config) for config in configs]
    engine = Engine(rules)
    engine.run(str(src), str(dest))

    content = dest.read()
    assert '>>>' not in content
    assert 'Python'  in content
