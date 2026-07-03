import unittest

import l33t
import main
import markov_words
from stats import stats


DETERMINISTIC_STATS = {
    "firstLetters": {"a": 1, "total": 1},
    "secondLetters": {"a": {"a": 1, "total": 1}},
    "letters": {"aa": {"a": 1, "total": 1}},
    "penultimateLetters": {"aa": {"a": 1, "total": 1}},
    "lastLetters": {"aa": {"a": 1, "total": 1}},
}


class HardeningTests(unittest.TestCase):
    def test_length_three_and_four_generation(self):
        words3 = markov_words.generate(stats, 3, 5)
        words4 = markov_words.generate(stats, 4, 5)
        self.assertTrue(all(len(word) == 3 for word in words3))
        self.assertTrue(all(len(word) == 4 for word in words4))

    def test_min_entropy_is_enforced(self):
        with self.assertRaises(ValueError):
            markov_words.generate(stats, 6, 1, min_entropy_bits=200, max_attempts_per_word=2)

    def test_blacklist_rejection(self):
        with self.assertRaises(ValueError):
            markov_words.generate(
                DETERMINISTIC_STATS,
                3,
                1,
                blocked_words={"aaa"},
                max_attempts_per_word=2
            )

    def test_strength_preset_generation(self):
        words = main.generate(number=2, strength_preset="interactive")
        self.assertEqual(len(words), 2)
        self.assertTrue(all(len(word) == 8 for word in words))

    def test_substitute_changes_supported_words(self):
        source = "substitution"
        transformed = l33t.substitute(source, number_of_substitutions=3)
        self.assertNotEqual(source, transformed)


if __name__ == "__main__":
    unittest.main()
