import unittest
from textstats import count_words


class TestCountWords(unittest.TestCase):
    """Tests for count_words."""

    def test_empty_string(self):
        self.assertEqual(count_words(""), 0)

    def test_whitespace_only(self):
        self.assertEqual(count_words("   \t\n  "), 0)

    def test_one_word(self):
        self.assertEqual(count_words("hello"), 1)

    def test_several_words_mixed_separators(self):
        text = "hello  world\tfoo\nbar"
        self.assertEqual(count_words(text), 4)

    def test_mixed_spaces_tabs_newlines_only(self):
        self.assertEqual(count_words("  \t\t\n\n  "), 0)


if __name__ == "__main__":
    unittest.main()
