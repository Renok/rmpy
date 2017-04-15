import os
import sys

from enum import Enum


class Codes(Enum):
    GOOD = 0
    CONFLICT = 1
    BAD = 2
    NO_FILE = 3


def ask_confirmation():
    answer = input("Are you sure? [y/n]\n")
    if answer == "n":
        print("Operation canceled")
        sys.exit(Codes.GOOD.value)
    elif answer != "y" and answer != "n":
        ask_confirmation()


def get_size(path):
    total_size = 0
    for dir_path, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(dir_path, f)
            total_size += os.path.getsize(fp)
    return total_size


def output(silent, code, *args):
    phrases = {
        1: "Directory already exists, but conflict were solved",
        2: "Unknown Error",
        3: "No such file",
    }
    if not silent:
        if code == Codes.GOOD.value:
            print(''.join([str(x) for x in args]))
        else:
            print(phrases[code])
    sys.exit(code)


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()
