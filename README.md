text-memorize
-------------
[![asciicast](https://asciinema.org/a/984avh6xfeaqxe8earjpg6xnn.png)](https://asciinema.org/a/984avh6xfeaqxe8earjpg6xnn)

A tool to help memorize some text!

When provided with a file, this program will remove random words from each line of text and ask you to provide the words that were removed.

You can provide lower and upper bounds to the number of words removed per line by using the `--l` and/or `--u` flags, or remove an exact number with `--n`.  You can also specify the number of attempts you want to allow with the `--a` flag. To turn off colors, just send in the `--no-color` flag.

text-memorize uses Python 2.7.

### How to run

`python text_memorize.py filename`

For between *i* and *j* words removed per line:

`python text_memorize.py --l i --u j filename`

For exactly *k* words removed per line:

`python text_memorize.py --n k filename`

For infinite attempts:

`python text_memorize.py --a 0 filename`

Without color:

`python text_memorize.py --no-color filename`


### Contribute

Contributions are welcome! Just open a pull request and I'll attend to it as soon as possible.
