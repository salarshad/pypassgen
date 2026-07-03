"""Tests for markov_words.prosody and the generate_passphrase() entry point."""
import unittest

import main
import markov_words
from markov_words.prosody import (
    syllabify,
    syllable_count,
    leading_consonant_class,
    dominant_vowel_class,
    ends_in_vowel,
    score_combination,
    select_best_combination,
)


class TestSyllabify(unittest.TestCase):
    """Verify syllable counts for the three user example passphrases."""

    def _count(self, word):
        return len(syllabify(word))

    def test_verisica_count(self):
        self.assertEqual(self._count("verisica"), 4)

    def test_bartimo_count(self):
        self.assertEqual(self._count("bartimo"), 3)

    def test_bartifi_count(self):
        self.assertEqual(self._count("bartifi"), 3)

    def test_grasso_count(self):
        self.assertEqual(self._count("grasso"), 2)

    def test_lectori_count(self):
        self.assertEqual(self._count("lectori"), 3)

    def test_tumblom_count(self):
        self.assertEqual(self._count("tumblom"), 2)

    def test_single_vowel_word(self):
        self.assertEqual(self._count("krt"), 1)   # no vowel → 1 unit
        self.assertEqual(self._count("ba"), 1)     # length 2 → 1 syllable
        self.assertEqual(self._count("bra"), 1)

    def test_syllable_count_helper(self):
        self.assertEqual(syllable_count("verisica"), 4)
        self.assertEqual(syllable_count("bartimo"), 3)


class TestLeadingConsonantClass(unittest.TestCase):
    """Verify phonetic class of the initial consonant/vowel."""

    def test_verisica_fricative(self):
        self.assertEqual(leading_consonant_class("verisica"), "fricative")

    def test_bartimo_stop(self):
        self.assertEqual(leading_consonant_class("bartimo"), "stop")

    def test_bartifi_stop(self):
        self.assertEqual(leading_consonant_class("bartifi"), "stop")

    def test_grasso_stop(self):
        self.assertEqual(leading_consonant_class("grasso"), "stop")

    def test_lectori_liquid(self):
        self.assertEqual(leading_consonant_class("lectori"), "liquid")

    def test_tumblom_stop(self):
        self.assertEqual(leading_consonant_class("tumblom"), "stop")

    def test_vowel_initial(self):
        self.assertEqual(leading_consonant_class("arena"), "vowel")

    def test_nasal_initial(self):
        self.assertEqual(leading_consonant_class("marin"), "nasal")


class TestDominantVowelClass(unittest.TestCase):
    def test_front(self):
        self.assertEqual(dominant_vowel_class("verisica"), "front")

    def test_central_or_back_bartimo(self):
        # 'a'(1), 'i'(1), 'o'(1) → tie broken by first-occurrence 'a' → central
        self.assertEqual(dominant_vowel_class("bartimo"), "central")

    def test_back_tumblom(self):
        # u, o → first occurrence 'u' → back
        self.assertEqual(dominant_vowel_class("tumblom"), "back")


class TestEndsInVowel(unittest.TestCase):
    def test_vowel_ending(self):
        self.assertTrue(ends_in_vowel("verisica"))
        self.assertTrue(ends_in_vowel("bartimo"))
        self.assertTrue(ends_in_vowel("bartifi"))
        self.assertTrue(ends_in_vowel("lectori"))

    def test_consonant_ending(self):
        self.assertFalse(ends_in_vowel("tumblom"))
        self.assertFalse(ends_in_vowel("blorpg"))

    def test_vowel_ending_grasso(self):
        self.assertTrue(ends_in_vowel("grasso"))   # ends in 'o'


class TestScoreCombination(unittest.TestCase):
    """Verify that the three user examples score higher than bad alternatives."""

    def test_verisica_bartimo_vs_blornikax_blormix(self):
        good = score_combination(["verisica", "bartimo"])
        bad  = score_combination(["blornikax", "blormix"])
        self.assertGreater(good, bad,
            f"Expected 'verisica bartimo' ({good:.2f}) > "
            f"'blornikax blormix' ({bad:.2f})")

    def test_bartifi_grasso_vs_bringki_blorpg(self):
        good = score_combination(["bartifi", "grasso"])
        bad  = score_combination(["bringki", "blorpg"])
        self.assertGreater(good, bad,
            f"Expected 'bartifi grasso' ({good:.2f}) > "
            f"'bringki blorpg' ({bad:.2f})")

    def test_lectori_tumblom_vs_lectori_lectox(self):
        good = score_combination(["lectori", "tumblom"])
        bad  = score_combination(["lectori", "lectox"])
        self.assertGreater(good, bad,
            f"Expected 'lectori tumblom' ({good:.2f}) > "
            f"'lectori lectox' ({bad:.2f})")

    def test_repeated_word_penalty(self):
        score_no_repeat  = score_combination(["bartifi", "grasso"])
        score_with_repeat = score_combination(["bartifi", "bartifi"])
        self.assertGreater(score_no_repeat, score_with_repeat)

    def test_length_sanity_penalty(self):
        score_normal = score_combination(["bartifi", "grasso"])
        score_short  = score_combination(["ba", "grasso"])   # "ba" is too short
        self.assertGreater(score_normal, score_short)


class TestSelectBestCombination(unittest.TestCase):
    def test_returns_correct_number_of_words(self):
        candidates = ["verisica", "bartimo", "bartifi", "grasso",
                      "lectori", "tumblom", "moriko", "felisan",
                      "torvali", "dunebri"]
        result = select_best_combination(candidates, 2)
        self.assertEqual(len(result), 2)

    def test_words_come_from_candidates(self):
        candidates = ["verisica", "bartimo", "bartifi", "grasso",
                      "lectori", "tumblom"]
        result = select_best_combination(candidates, 2)
        for word in result:
            self.assertIn(word, candidates)

    def test_three_word_selection(self):
        candidates = ["verisica", "bartimo", "bartifi", "grasso",
                      "lectori", "tumblom", "moriko", "felisan",
                      "torvali", "dunebri"]
        result = select_best_combination(candidates, 3)
        self.assertEqual(len(result), 3)


class TestGeneratePassphrase(unittest.TestCase):
    """Integration tests for main.generate_passphrase()."""

    def test_two_words_default(self):
        result = main.generate_passphrase(num_words=2)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # CamelCase: should have at least one uppercase letter
        self.assertTrue(any(c.isupper() for c in result))

    def test_three_words(self):
        result = main.generate_passphrase(num_words=3)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_four_words(self):
        result = main.generate_passphrase(num_words=4)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_return_details_shape(self):
        result = main.generate_passphrase(num_words=2, return_details=True)
        self.assertIsInstance(result, dict)
        self.assertIn("passphrase", result)
        self.assertIn("words", result)
        self.assertIn("entropy_bits", result)
        self.assertIn("rhythm_score", result)
        self.assertIsInstance(result["passphrase"], str)
        self.assertIsInstance(result["words"], list)
        self.assertEqual(len(result["words"]), 2)
        self.assertIsInstance(result["entropy_bits"], float)
        self.assertIsInstance(result["rhythm_score"], float)

    def test_entropy_meets_standard_preset(self):
        result = main.generate_passphrase(
            num_words=2,
            strength_preset="standard",
            return_details=True,
        )
        self.assertGreaterEqual(result["entropy_bits"], 30.0)

    def test_separator_is_applied(self):
        result = main.generate_passphrase(num_words=2, separator="-")
        self.assertIn("-", result)

    def test_no_capitalize_all_lower(self):
        result = main.generate_passphrase(num_words=2, capitalize=False)
        # Without capitalization each word is lower; the joined result should
        # have no uppercase letters (assuming separator="" and no l33t)
        self.assertTrue(result.islower() or result == result.lower())


class TestGeneratePasswordsRegression(unittest.TestCase):
    """Ensure the existing generate_passwords() API is unchanged."""

    def test_returns_list_of_12(self):
        words = main.generate_passwords()
        self.assertEqual(len(words), 12)

    def test_all_strings(self):
        words = main.generate_passwords()
        self.assertTrue(all(isinstance(w, str) for w in words))


if __name__ == "__main__":
    unittest.main()
