text-memorize
-------------
A tool to help memorize some text!

When provided with a file, this program will remove random words from each line of text and ask you to provide the words that were removed.

You can specify the number of attempts you want to allow with the `--a` flag. To turn off colors, just send in the `--no-color` flag.

### How to run

`python text_memorize.py filename`

For infinite attempts:

`python text_memorize.py --a 0 filename`

Without color:

`python text_memorize.py --no-color filename`


### Contribute

Contributions are welcome! Just open a pull request and I'll attend to it as soon as possible.
