import pytest

from flog.loader import *

def str_to_rules(tmpdir, content):
    rule = tmpdir.join('test.yaml')
    rule.write(content)
    loader = Loader(str(rule))
    return loader.load()    

def test_path(tmpdir):
    base = tmpdir.join('base.yaml')
    base.write('''
patterns:
    - name: Python version
      match: Python (3.\\d+\\.\\d+\\.\\d+)
      message: "Python version: {{0}}"''')

    rule = str_to_rules(tmpdir, 'include: base')[0]
    assert rule.name == 'Python version'

    rule = str_to_rules(tmpdir, 'include: base.yaml')[0]
    assert rule.name == 'Python version'

    rule = str_to_rules(tmpdir, 'include: base.yml')[0]
    assert rule.name == 'Python version'

    rule = str_to_rules(tmpdir, 'include: '+str(base))[0]
    assert rule.name == 'Python version'

    with pytest.raises(Exception) as exc_info:   
        str_to_rules(tmpdir, 'include: notfound')
    assert str(exc_info.value) == 'include file not found: notfound'

    sub = tmpdir.mkdir('sub')
    rule = str_to_rules(sub, 'include: ../base')[0]
    assert rule.name == 'Python version'

    with pytest.raises(Exception) as exc_info:   
        str_to_rules(sub, 'include: base')
    assert str(exc_info.value) == 'include file not found: base'

def test_context(tmpdir):
    base = tmpdir.join('base.yaml')
    base.write('''
context:
    name: "version"
patterns:
    - name: Python version
      match: Python (3.\\d+\\.\\d+\\.\\d+)
      message: "Python version: {{0}}"''')
    
    rule = str_to_rules(tmpdir, 'include: base')[0]
    assert rule.global_context['name'].pattern == 'version'

    rule = str_to_rules(tmpdir, '''\
include: base
context:
    name: "new"
''')[0]
    assert rule.global_context['name'].pattern == 'new'

def test_recursive(tmpdir):
    base = tmpdir.join('base.yaml')
    base.write('''
context:
    name: "version"
patterns:
    - name: Python version
      match: Python (3.\\d+\\.\\d+\\.\\d+)
      message: "Python version: {{0}}"''')
    
    base2 = tmpdir.join('base2.yaml')
    base2.write('''
include: base
context:
    name: "version"
patterns:
    - name: Build version
      match: Build (\\d+)
      message: "Buildd version: {{0}}"''')

    rules = str_to_rules(tmpdir, 'include: base2')
    assert rules[0].name == 'Python version'
    assert rules[1].name == 'Build version'

def test_cycle(tmpdir):
    base = tmpdir.join('base.yaml')
    base.write('''
include: base2
context:
    name: "version"
patterns:
    - name: Python version
      match: Python (3.\\d+\\.\\d+\\.\\d+)
      message: "Python version: {{0}}"''')
    
    base2 = tmpdir.join('base2.yaml')
    base2.write('''
include: base
context:
    name: "version"
patterns:
    - name: Build version
      match: Build (\\d+)
      message: "Buildd version: {{0}}"''')

    rules = str_to_rules(tmpdir, 'include: base2')
    assert len(rules) == 2

def test_context(tmpdir):
    base = tmpdir.join('base.yaml')
    base.write('''
context:
    name: "version"
patterns:
    - name: Python version
      match: Python (3.\\d+\\.\\d+\\.\\d+)
      message: "Python version: {{0}}"''')
    
    rule = str_to_rules(tmpdir, 'include: base')[0]
    assert rule.global_context['name'].pattern == 'version'

    rule = str_to_rules(tmpdir, '''\
include: base
context:
    name: "new"
''')[0]
    assert rule.global_context['name'].pattern == 'new'

def test_include_list(tmpdir):
    base = tmpdir.join('base.yaml')
    base.write('''
context:
    name: "version"
patterns:
    - name: Python version
      match: Python (3.\\d+\\.\\d+\\.\\d+)
      message: "Python version: {{0}}"''')
    
    base2 = tmpdir.join('base2.yaml')
    base2.write('''
context:
    name: "version"
patterns:
    - name: Build version
      match: Build (\\d+)
      message: "Buildd version: {{0}}"''')

    rules = str_to_rules(tmpdir, '''
include:
    - base
    - base2
    ''')
    assert rules[0].name == 'Python version'
    assert rules[1].name == 'Build version'