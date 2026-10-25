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


def console_font():
    """The classic console window's font as (face name, TrueType?, code page).

    Returns None unless stdout is a visible console window. Windows Terminal,
    VS Code and SSH sessions run behind a hidden console window and draw text
    themselves, falling back to other fonts for missing characters.
    """
    import ctypes
    from ctypes import wintypes

    class CONSOLE_FONT_INFOEX(ctypes.Structure):
        _fields_ = [('cbSize', wintypes.ULONG),
                    ('nFont', wintypes.DWORD),
                    ('dwFontSize', wintypes._COORD),
                    ('FontFamily', wintypes.UINT),
                    ('FontWeight', wintypes.UINT),
                    ('FaceName', wintypes.WCHAR * 32)]

    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    kernel32.GetConsoleWindow.restype = wintypes.HWND
    kernel32.GetStdHandle.restype = wintypes.HANDLE
    kernel32.GetCurrentConsoleFontEx.argtypes = [
        wintypes.HANDLE, wintypes.BOOL, ctypes.POINTER(CONSOLE_FONT_INFOEX)]
    user32.IsWindowVisible.argtypes = [wintypes.HWND]

    window = kernel32.GetConsoleWindow()
    if not window or not user32.IsWindowVisible(window):
        return None
    info = CONSOLE_FONT_INFOEX()
    info.cbSize = ctypes.sizeof(info)
    handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    if not kernel32.GetCurrentConsoleFontEx(handle, False, ctypes.byref(info)):
        return None
    TMPF_TRUETYPE = 0x04
    return (info.FaceName, bool(info.FontFamily & TMPF_TRUETYPE),
            kernel32.GetConsoleOutputCP())


def undisplayable(chars, face, truetype, codepage):
    """The characters in chars that the console font cannot draw."""
    chars = [c for c in chars if 0x7f < ord(c) <= 0xffff and c.isprintable()]
    if not chars:
        return []

    if not truetype:
        # Raster fonts only have glyphs for the console's code page.
        missing = []
        for c in chars:
            try:
                c.encode('cp{}'.format(codepage))
            except UnicodeEncodeError:
                missing.append(c)
        return missing

    import ctypes
    from ctypes import wintypes
    gdi32 = ctypes.windll.gdi32
    user32 = ctypes.windll.user32
    user32.GetDC.restype = wintypes.HDC
    user32.GetDC.argtypes = [wintypes.HWND]
    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    gdi32.CreateFontW.restype = wintypes.HFONT
    gdi32.CreateFontW.argtypes = [ctypes.c_int] * 5 + [wintypes.DWORD] * 8 + [
        wintypes.LPCWSTR]
    gdi32.SelectObject.restype = wintypes.HGDIOBJ
    gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
    gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
    gdi32.GetGlyphIndicesW.restype = wintypes.DWORD
    gdi32.GetGlyphIndicesW.argtypes = [
        wintypes.HDC, wintypes.LPCWSTR, ctypes.c_int,
        ctypes.POINTER(wintypes.WORD), wintypes.DWORD]

    DEFAULT_CHARSET = 1
    GGI_MARK_NONEXISTING_GLYPHS = 1
    text = ''.join(chars)
    glyphs = (wintypes.WORD * len(text))()
    dc = user32.GetDC(None)
    font = gdi32.CreateFontW(0, 0, 0, 0, 0, 0, 0, 0, DEFAULT_CHARSET,
                             0, 0, 0, 0, face)
    previous = gdi32.SelectObject(dc, font)
    result = gdi32.GetGlyphIndicesW(dc, text, len(text), glyphs,
                                    GGI_MARK_NONEXISTING_GLYPHS)
    gdi32.SelectObject(dc, previous)
    gdi32.DeleteObject(font)
    user32.ReleaseDC(None, dc)
    if result == 0xFFFFFFFF:  # GDI_ERROR
        return []
    return [c for c, glyph in zip(text, glyphs) if glyph == 0xFFFF]


def warn_about_console_font(text):
    try:
        font = console_font()
        if not font:
            return
        missing = undisplayable(sorted(set(text)), *font)
    except Exception:
        # Only a hint; never let it stop the program.
        return
    if missing:
        examples = ', '.join('U+{:04X}'.format(ord(c)) for c in missing[:3])
        print('Warning: the console font "{}" cannot display some characters '
              'in {} ({}), so they will show as "?". Choose a font that '
              'supports this language (right-click the title bar, then '
              'Properties > Font), or use Windows Terminal.'.format(
                  font[0], args.filename, examples), file=sys.stderr)


missed_words = []


def print_missed_words():
    if missed_words:
        print()
        print('Words to practice: ' + ', '.join(missed_words))


try:
    with open(args.filename, encoding='utf-8') as f:
        if os.name == 'nt':
            warn_about_console_font(f.read())
            f.seek(0)

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
                except (KeyboardInterrupt, EOFError):
                    print_missed_words()
                    sys.exit(0)

                if guess != next_word and next_word not in missed_words:
                    missed_words.append(next_word)

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

    print_missed_words()
except FileNotFoundError:
    print("File not found: '{}'".format(args.filename))
