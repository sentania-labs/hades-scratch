"""Tests for textstats.count_words."""

import unittest

from textstats import count_words


class TestCountWords(unittest.TestCase):
    """Tests for the count_words function."""

    def test_empty_string(self):
        """Empty string should return 0."""
        self.assertEqual(count_words(""), 0)

    def test_whitespace_only(self):
        """Whitespace-only text should return 0."""
        self.assertEqual(count_words("   \t\n\r  "), 0)

    def test_one_word(self):
        """A single word should return 1."""
        self.assertEqual(count_words("hello"), 1)

    def test_several_words_mixed_separators(self):
        """Several words separated by mixed spaces, tabs, and newlines."""
        self.assertEqual(
            count_words("hello world\nfoo\tbar   baz"),
            5,
        )

    def test_multiple_spaces_between_words(self):
        """Multiple consecutive spaces should not affect count."""
        self.assertEqual(count_words("  hello    world  "), 2)


if __name__ == "__main__":
    unittest.main()
