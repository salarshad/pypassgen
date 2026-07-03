"""
Prosody-based scoring and selection for passphrase generation.

Provides syllabification, phonetic classification, and a multi-factor
scorer that rewards falling cadence, consonant/vowel contrast, and
open word endings — tuned to the user's example passphrases:
  "verisica bartimo", "bartifi grasso", "lectori tumblom"
"""

import itertools

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VOWELS = set('aeiouy')

# Consonant phonetic classes (lower-case keys).  'y' at word-initial position
# is treated as a semivowel; inside a word 'y' is counted as a vowel.
CONSONANT_CLASSES = {
    'p': 'stop',    'b': 'stop',    't': 'stop',    'd': 'stop',
    'k': 'stop',    'g': 'stop',
    'f': 'fricative', 'v': 'fricative', 's': 'fricative', 'z': 'fricative',
    'h': 'fricative', 'x': 'fricative',
    'm': 'nasal',   'n': 'nasal',
    'l': 'liquid',  'r': 'liquid',
    'c': 'affricate', 'j': 'affricate', 'q': 'affricate',
    'w': 'semivowel', 'y': 'semivowel',
}

# Vowel classes for contrast scoring
_FRONT_VOWELS   = set('ie')
_CENTRAL_VOWELS = set('a')
_BACK_VOWELS    = set('ou')


# ---------------------------------------------------------------------------
# Syllabification
# ---------------------------------------------------------------------------

def syllabify(word: str) -> list:
    """Split *word* into pseudo-syllables using a sonority-based rule.

    Algorithm (onset-maximisation heuristic):
    - Each vowel (a/e/i/o/u/y) anchors a syllable.
    - Consonant clusters between two vowels: the *last* consonant in the
      cluster starts the new syllable (goes right); all earlier consonants
      close the previous syllable (go left).
    - All consonants before the first vowel form the onset of the first
      syllable; all consonants after the last vowel are the coda of the
      last syllable.
    """
    word = word.lower()
    if not word:
        return []

    vowel_positions = [i for i, ch in enumerate(word) if ch in VOWELS]

    if not vowel_positions:
        return [word]           # no vowels → one unit

    if len(vowel_positions) == 1:
        return [word]           # single vowel → one syllable

    # Build split points (left boundary of each syllable).
    splits = [0]
    for vi in range(1, len(vowel_positions)):
        prev_v = vowel_positions[vi - 1]
        curr_v = vowel_positions[vi]
        cluster_len = curr_v - (prev_v + 1)   # consonants between the two vowels

        if cluster_len == 0:
            # Adjacent vowels: new syllable starts at current vowel.
            splits.append(curr_v)
        elif cluster_len == 1:
            # Single consonant: goes with the right vowel (onset).
            splits.append(curr_v - 1)
        else:
            # Multiple consonants: keep all but the last in the left syllable;
            # the last consonant opens the right syllable.
            splits.append(curr_v - 1)

    splits.append(len(word))
    return [word[splits[i]:splits[i + 1]] for i in range(len(splits) - 1)]


def syllable_count(word: str) -> int:
    """Return the number of pseudo-syllables in *word*."""
    return len(syllabify(word))


# ---------------------------------------------------------------------------
# Phonetic classifiers
# ---------------------------------------------------------------------------

def leading_consonant_class(word: str) -> str:
    """Return the phonetic class of the first letter of *word*.

    Returns one of: 'stop', 'fricative', 'nasal', 'liquid', 'affricate',
    'semivowel', 'vowel'.  'y' at word-initial position is 'semivowel'.
    """
    if not word:
        return 'vowel'
    first = word[0].lower()
    if first in VOWELS and first != 'y':
        return 'vowel'
    return CONSONANT_CLASSES.get(first, 'vowel')


def dominant_vowel_class(word: str) -> str:
    """Return 'front' (i/e), 'central' (a), or 'back' (o/u).

    Determined by the most frequent vowel; ties broken by first occurrence.
    'y' is treated as a vowel for counting purposes but mapped to 'front'.
    """
    vowel_map = {}
    for ch in word.lower():
        if ch in VOWELS:
            vowel_map[ch] = vowel_map.get(ch, 0) + 1

    if not vowel_map:
        return 'central'        # fallback

    # Sort by (descending frequency, ascending first-occurrence index)
    word_lower = word.lower()
    dominant = max(
        vowel_map.keys(),
        key=lambda v: (vowel_map[v], -word_lower.index(v))
    )
    if dominant in _FRONT_VOWELS or dominant == 'y':
        return 'front'
    if dominant in _CENTRAL_VOWELS:
        return 'central'
    return 'back'


def ends_in_vowel(word: str) -> bool:
    """Return True if the last character of *word* is a vowel."""
    return bool(word) and word[-1].lower() in VOWELS


# ---------------------------------------------------------------------------
# Combination scoring
# ---------------------------------------------------------------------------

def score_combination(words: list) -> float:
    """Score a candidate N-word combination.  Higher is better.

    Scoring components (applied pairwise for adjacent words):
    - Rhythm  (+3.0 falling, +1.0 equal, −1.5 rising per pair)
    - Consonant-class contrast  (+2.0 different, 0 same, −1.0 alliteration)
    - Vowel-class contrast  (+1.5 different, 0 same)
    - Open endings  (+0.5 per word ending in a vowel;
                     +1.5 extra if the *final* word ends in a vowel)
    - Length sanity  (−2.0 per word outside [4, 10] letters)
    - No repeated word  (−5.0 if any word appears twice)
    """
    if not words:
        return 0.0

    score = 0.0
    lower_words = [w.lower() for w in words]

    # Repeated-word penalty
    if len(lower_words) != len(set(lower_words)):
        score -= 5.0

    # Per-word components
    for i, w in enumerate(lower_words):
        # Length sanity
        if len(w) < 4 or len(w) > 10:
            score -= 2.0
        # Open ending
        if ends_in_vowel(w):
            score += 0.5
            if i == len(lower_words) - 1:
                score += 1.5

    # Pairwise components
    for i in range(len(lower_words) - 1):
        w1, w2 = lower_words[i], lower_words[i + 1]

        # Rhythm
        sc1, sc2 = syllable_count(w1), syllable_count(w2)
        if sc1 == sc2 + 1:
            score += 3.0          # falling (preferred)
        elif sc1 == sc2:
            score += 1.0          # equal
        else:
            score -= 1.5          # rising

        # Consonant-class contrast
        if w1 and w2:
            cc1 = leading_consonant_class(w1)
            cc2 = leading_consonant_class(w2)
            if w1[0] == w2[0]:    # identical leading letter → alliteration
                score -= 1.0
            elif cc1 != cc2:
                score += 2.0      # different classes

        # Vowel-class contrast
        vc1 = dominant_vowel_class(w1)
        vc2 = dominant_vowel_class(w2)
        if vc1 != vc2:
            score += 1.5

    return score


# ---------------------------------------------------------------------------
# Combination selection
# ---------------------------------------------------------------------------

def select_best_combination(
    candidates: list,
    num_words: int,
    top_k: int = 1,
) -> list:
    """From *candidates*, return the ordered *num_words*-length combination
    with the highest :func:`score_combination`.

    Strategy:
    - Exhaustive search when ``len(candidates) <= 30`` and ``num_words <= 4``.
    - Otherwise greedy: pick the best first word, then repeatedly append the
      candidate that maximises the incremental score.

    Returns a list of ``num_words`` words (from *candidates*).
    """
    if not candidates or num_words < 1:
        return []
    if num_words >= len(candidates):
        # Use all (or as many as available) — avoid crash
        return candidates[:num_words]

    use_exhaustive = len(candidates) <= 30 and num_words <= 4

    if use_exhaustive:
        best_combo = None
        best_score = float('-inf')
        for combo in itertools.permutations(candidates, num_words):
            s = score_combination(list(combo))
            if s > best_score:
                best_score = s
                best_combo = list(combo)
        return best_combo or list(candidates[:num_words])

    # Greedy fill
    remaining = list(candidates)
    chosen = []

    while len(chosen) < num_words and remaining:
        best_word = None
        best_score = float('-inf')
        for candidate in remaining:
            trial = chosen + [candidate]
            s = score_combination(trial)
            if s > best_score:
                best_score = s
                best_word = candidate
        if best_word is None:
            break
        chosen.append(best_word)
        remaining.remove(best_word)

    return chosen
