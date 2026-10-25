#!/usr/bin/env python3

import argparse
import os
import random
import sys

parser = argparse.ArgumentParser(description="""A tool to help memorize some
text! When provided with a file, this program will remove random words from
each line of text and ask you to provide the words that were removed.""")

parser.add_argument('--no-color', action='store_true',
                    help='hide colorful underlining')

parser.add_argument('--a', dest='tries', type=int, default=3,
                    help=('number of tries to allow per word '
                         '(0 for unlimited tries, default: 3)'))

parser.add_argument('--n', dest='num', type=int, default=0,
                    help=('number of words to remove from each line '
                         '(0 for random number of removals, default: 0)'))

parser.add_argument('--l', dest='lower', type=int, default=1,
                    help=('lower bound on number of words to remove '
                         '(inclusive, default: 1)'))

parser.add_argument('--u', dest='upper', type=int, default=0,
                    help=('upper bound on number of words to remove '
                         '(inclusive, 0 for no upper bound, default: 0)'))

parser.add_argument('filename', metavar='filename', type=str,
                    help='the text file')

args = parser.parse_args()


def enable_windows_ansi():
    """Turn on ANSI escape handling in the Windows console.

    Windows 10 and later understand the color codes, but only once the
    program asks for it. Returns False when stdout is not a console or the
    console is too old.
    """
    import ctypes
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    mode = ctypes.c_uint32()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return False
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    return bool(kernel32.SetConsoleMode(
        handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING))


if os.name == 'nt' and not args.no_color and not enable_windows_ansi():
    args.no_color = True

try:
    with open(args.filename, encoding='utf-8') as f:
        current_line = ''

        for line in f:
            missing_words = []
            new_word = ''
            split_line = line.split(' ')

            if args.num:
                num = args.num
            else:
                if args.upper:
                    upper = args.upper + 1
                else:
                    upper = len(split_line) + 1

                num = random.randrange(start=args.lower, stop=upper)

            words = [False] * num
            diff = len(split_line) - num
            if diff > 0:
                words.extend([True] * diff)
                random.shuffle(words)

            for i, word in enumerate(split_line):
                show_word = words[i]

                color_started = False

                for char in word:
                    if (char.isalpha() and show_word) or not char.isalpha():
                        if color_started:
                            current_line += '\033[0m'
                            color_started = False

                        current_line += char
                    else:
                        new_word += char

                        if not color_started and not args.no_color:
                            current_line += '\033[91m'
                            color_started = True

                        current_line += '_'
                if word[-1] != '\n':
                    if color_started:
                        current_line += '\033[0m'
                        color_started = False
                    current_line += ' '

                if len(new_word):
                    missing_words.append(new_word)
                    new_word = ''
            tries = 1

            while len(missing_words):
                
                next_word = missing_words[0]
                print(current_line)

                try:
                    guess = input('Enter the next missing word: ')
                except KeyboardInterrupt:
                    sys.exit(0)
                except EOFError:
                    sys.exit(0)

                if guess == next_word:
                    print("Correct! The word was '" + next_word + "'.")
                elif args.tries and tries == args.tries:
                    print("Too many tries. The word was '" + next_word + "'.")
                else:
                    print("Incorrect. Please try again.")
                    tries += 1
                    continue

                if args.no_color:
                    current_line = current_line.replace('_' * len(next_word),next_word,1)
                else:
                    current_line = current_line.replace('\033[91m' + '_' * len(next_word) + '\033[0m',next_word,1)

                missing_words.pop(0)
                tries = 1
except FileNotFoundError:
    print("File not found: '{}'".format(args.filename))
