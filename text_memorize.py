#!/usr/bin/python
# coding=utf-8

import argparse
import codecs
import random
import sys

parser = argparse.ArgumentParser(description="""A tool to help memorize some text! When provided with a file, this program will remove random words from each line of text and ask you to provide the words that were removed.""")
parser.add_argument('--no-color', action='store_true', help='hide colorful underlining')
parser.add_argument('--a', dest='attempts', default=3, help='number of attempts to allow per word (0 for unlimited attempts, default: 3)')
parser.add_argument('filename', metavar='filename', type=str, help='the text file')

args = parser.parse_args()

try:
    with codecs.open(args.filename, 'r', 'utf-8') as f:
        current_line = ''
        for line in f:
            missing_words = [u'']
            idx = 0
            for word in line.split(' '):
                show_word = True
                if random.randrange(10) < 5:
                    show_word = False
                for char_idx in range(0,len(word)):
                    if (word[char_idx].isalpha() and show_word) or not word[char_idx].isalpha():
                        current_line += word[char_idx]
                    else:
                        missing_words[idx] += word[char_idx]
                        if not args.no_color:
                            current_line += '\033[91m'
                        current_line += '_'
                        if not args.no_color:
                            current_line += '\033[0m'
                if word[-1] != '\n':
                    current_line += ' '
                if len(missing_words[idx]):
                    missing_words.append(u'')
                    idx += 1
            missing_words.pop()
            attempts = 0
            while len(missing_words):
                print(current_line)
                try:
                    attempt = raw_input('Enter the next missing word: ')
                    reveal_next_word = False
                    if unicode(attempt,'utf-8') == missing_words[0]:
                        print("Correct! The word was '" + missing_words[0] + "'.")
                        reveal_next_word = True
                        missing_words.pop(0)
                        attempts = 0
                    elif args.attempts > 0 and attempts == args.attempts:
                        print("Too many attempts. The word was '" + missing_words[0] + "'.")
                        reveal_next_word = True
                        missing_words.pop(0)
                        attempts = 0
                    else:
                        print("Incorrect. Please try again.")
                        attempts += 1
                    if reveal_next_word:
                        if args.no_color:
                            current_line = current_line.replace(''.join('_' for char in missing_words[0]),missing_words[0],1)
                        else:
                            current_line = current_line.replace(''.join('\033[91m_\033[0m' for char in missing_words[0]),missing_words[0],1)
                except:
                    sys.exit(0)
except IOError:
    print("File not found: '" + args.filename + "'")
