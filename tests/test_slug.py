import unittest
from slug import slugify


class SlugifyTest(unittest.TestCase):
    def test_lowercases_and_joins_words(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_drops_punctuation(self):
        self.assertEqual(slugify("Hello, World!"), "hello-world")

    def test_collapses_separators(self):
        self.assertEqual(slugify("  a -- b __ c  "), "a-b-c")

    def test_keeps_digits(self):
        self.assertEqual(slugify("Release 2.0 notes"), "release-2-0-notes")

    def test_empty_is_empty(self):
        self.assertEqual(slugify("!!!"), "")

    def test_max_length_cuts_at_a_hyphen(self):
        self.assertEqual(slugify("one two three four", max_length=12), "one-two")


if __name__ == "__main__":
    unittest.main()
