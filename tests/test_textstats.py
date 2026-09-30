"""Tests for textstats.count_words."""

import unittest

from textstats import count_words


class TestCountWords(unittest.TestCase):
    """Run five cases covering the contract of count_words."""

    def test_empty_string(self):
        self.assertEqual(count_words(""), 0)

    def test_whitespace_only(self):
        self.assertEqual(count_words("   \t\n  "), 0)

    def test_one_word(self):
        self.assertEqual(count_words("hello"), 1)

    def test_several_words_mixed_separators(self):
        # spaces, tabs, and newlines between words
        text = "alpha beta\tgamma\ndelta"
        self.assertEqual(count_words(text), 4)

    def test_several_words_mixed_spaces(self):
        text = "one two  three"  # double space between two/three
        self.assertEqual(count_words(text), 3)


if __name__ == "__main__":
    unittest.main()
