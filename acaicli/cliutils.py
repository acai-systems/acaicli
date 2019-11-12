import sys


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_info(*msg):
    print(color_msg(*msg, color=Colors.GREEN))


def print_warn(*msg):
    print(color_msg(*msg, color=Colors.YELLOW))


def print_err(*msg):
    print(color_msg(*msg, color=Colors.RED))


def print_err_and_exit(*msg):
    print_err(*msg)
    exit(2)


def color_msg(*msg, color=None):
    if sys.stdout.isatty() and color:
        return color + ' '.join(msg) + Colors.ENDC
    else:
        return ' '.join(msg)
