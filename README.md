text-memorize
-------------
[![asciicast](https://asciinema.org/a/984avh6xfeaqxe8earjpg6xnn.png)](https://asciinema.org/a/984avh6xfeaqxe8earjpg6xnn)

A tool to help memorize some text!

When provided with a file, this program will remove random words from each line of text and ask you to provide the words that were removed.

You can provide lower and upper bounds to the number of words removed per line by using the `--l` and/or `--u` flags, or remove an exact number with `--n`.  You can also specify the number of attempts you want to allow with the `--a` flag. To turn off colors, just send in the `--no-color` flag.

When you finish (or quit with Ctrl-C/Ctrl-D), text-memorize lists every word you guessed wrong at least once so you know what to practice.

text-memorize requires Python 3.

### Windows

Use Python 3.10 or later. Colors work in Windows Terminal and in the
Windows 10/11 console; on older consoles, or when output is redirected,
text-memorize turns colors off automatically. Russian and other non-ASCII
text works in the console. If you pipe answers in, set
`PYTHONIOENCODING=utf-8` (or run `python -X utf8`) so the piped text is
read as UTF-8.

### How to run

`python3 text_memorize.py filename`

For between *i* and *j* words removed per line:

`python3 text_memorize.py --l i --u j filename`

For exactly *k* words removed per line:

`python3 text_memorize.py --n k filename`

For infinite attempts:

`python3 text_memorize.py --a 0 filename`

Without color:

`python3 text_memorize.py --no-color filename`


### Tests

`python3 -m unittest discover tests`

GitHub Actions runs the tests on Linux, macOS and Windows for every push to `main` and every pull request.

### Contribute

Contributions are welcome! Just open a pull request and I'll attend to it as soon as possible.
