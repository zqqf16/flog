import re
import yaml

from typing import List
from pathlib import Path
from .rule import Rule

class Loader:
    suffix = ['.yaml', '.yml']

    def __init__(self, base_path: str):
        self.path = Path(base_path)
        self.included = []
        self.gloabl_context = {}
        self.rules = []

    def __load_yaml(self, path: Path) -> dict:
        with path.open() as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def __load_include(self, name: str) -> dict:
        path = Path(name).expanduser()
        if path.is_absolute():
            # include /User/abc.yaml
            self.__load_file(path)
            return

        path = self.path.parent.joinpath(name)
        if path.is_file():
            # include abc.yaml
            self.__load_file(path)
            return

        # include abc
        for suffix in self.suffix:
            new_path = path.with_suffix(suffix)
            print(new_path)
            if new_path.is_file():
                self.__load_file(new_path)
                return

        raise Exception(f'include file not found: {name}')
    
    def __load_file(self, path: Path):
        if path in self.included:
            return
        self.included.append(path)
        data = self.__load_yaml(path)

        # check include
        if include := data.get('include', None):
            if isinstance(include, str):
                self.__load_include(include)
            if isinstance(include, list):
                for item in include:
                    self.__load_include(item)
        
        # global context
        if context := data.get('context', None):
            for key, value in context.items():
                if key in ["lines", "captures", "content"]:
                    raise AttributeError(f'Invalid context key: {key}')
                self.gloabl_context[key] = re.compile(value)

        if patterns := data.get('patterns', None):
            for item in data['patterns']:
                self.rules.append(Rule(item))

    def load(self) -> List[Rule]:
        self.__load_file(self.path)

        for rule in self.rules:
            rule.global_context = self.gloabl_context
        return self.rules
