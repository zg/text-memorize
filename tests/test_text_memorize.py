import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'text_memorize.py')
TEXTS = os.path.join(ROOT, 'texts')


def words_of(path):
    """The words text_memorize asks for, in order, when every word is removed."""
    with open(path, encoding='utf-8') as f:
        for line in f:
            for word in line.split(' '):
                letters = ''.join(c for c in word if c.isalpha())
                if letters:
                    yield letters


def run(args, stdin=''):
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    return subprocess.run([sys.executable, SCRIPT] + args, input=stdin,
                          capture_output=True, text=True, encoding='utf-8',
                          env=env, timeout=30)


class TextMemorizeTest(unittest.TestCase):
    def check_all_correct(self, name):
        path = os.path.join(TEXTS, name)
        words = list(words_of(path))
        # --n larger than any line removes every word, so the order is known.
        result = run(['--no-color', '--n', '1000', path],
                     stdin='\n'.join(words) + '\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count('Correct!'), len(words))
        self.assertNotIn('Incorrect', result.stdout)

    def test_english(self):
        self.check_all_correct('english.txt')

    def test_russian(self):
        self.check_all_correct('ch1_1.txt')

    def test_tries_exhausted(self):
        path = os.path.join(TEXTS, 'english.txt')
        result = run(['--no-color', '--n', '1000', '--a', '2', path],
                     stdin='wrong\n' * 18)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count('Too many tries'), 9)

    def test_eof_exits_cleanly(self):
        result = run([os.path.join(TEXTS, 'english.txt')])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            missing = os.path.join(d, 'missing.txt')
            result = run([missing])
        self.assertIn('File not found', result.stdout)


if __name__ == '__main__':
    unittest.main()
