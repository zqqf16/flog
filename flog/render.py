'''Custom jinja2 filters for flog'''

filters = {
    'black': lambda x: f'\033[30m{x}\033[0m',
    'red': lambda x: f'\033[31m{x}\033[0m',
    'green': lambda x: f'\033[32m{x}\033[0m',
    'yellow': lambda x: f'\033[33m{x}\033[0m',
    'blue': lambda x: f'\033[34m{x}\033[0m',
    'purple': lambda x: f'\033[35m{x}\033[0m',
    'cyan': lambda x: f'\033[36m{x}\033[0m',
    'white': lambda x: f'\033[37m{x}\033[0m',

    'bold': lambda x: f'\033[1m{x}\033[0m',
    'light': lambda x: f'\033[2m{x}\033[0m',
    'italic': lambda x: f'\033[3m{x}\033[0m',
    'underline': lambda x: f'\033[4m{x}\033[0m',
    'blink': lambda x: f'\033[5m{x}\033[0m',
    'reverse': lambda x: f'\033[7m{x}\033[0m',
    'strike': lambda x: f'\033[9m{x}\033[0m',
}