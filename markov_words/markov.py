import secrets
import math

VOWELS = set('aeiouy')


def _cv_class(letter):
    """Return 'V' if *letter* is a vowel, 'C' otherwise."""
    return 'V' if letter in VOWELS else 'C'


def choose_letter(letter_stats):
    letter, _ = choose_letter_with_entropy(letter_stats)
    return letter

def choose_letter_with_entropy(letter_stats):
    if not letter_stats:
        raise ValueError("NoStats")
    total = letter_stats.get('total', 0)
    if total < 1:
        raise ValueError("NoStats")
    draw = secrets.randbelow(total)
    count = 0
    for letter, freq in letter_stats.items():
        if letter == 'total':
            continue
        count += freq
        if count > draw:
            probability = freq / total
            return letter, -math.log2(probability)
    raise ValueError("NoStats")  # shouldn't get here with proper stats

def _get_transition_stats(stats, key2, index, word_length, key3=None):
    """Return the letter-frequency distribution for the next letter.

    Lookup order:
    1. ``stats['letters3']`` keyed on the last 3 letters (*key3*), if available.
    2. Position-specific 2-letter table (``letters`` / ``penultimateLetters`` /
       ``lastLetters``) keyed on *key2* — the existing behaviour.
    3. ``stats['cv_letters']`` keyed on the CV pattern of *key2*, as a
       smoothing fallback when both trigram and bigram lookups miss.
    """
    # 1. Trigram lookup
    if key3 is not None and 'letters3' in stats:
        result = stats['letters3'].get(key3)
        if result:
            return result

    # 2. Position-specific bigram lookup (original behaviour)
    if index < word_length - 2:
        result = stats['letters'].get(key2)
    elif index == word_length - 2:
        result = stats['penultimateLetters'].get(key2)
    else:
        result = stats['lastLetters'].get(key2)

    if result:
        return result

    # 3. CV-pattern fallback
    if 'cv_letters' in stats and len(key2) == 2:
        cv_key = _cv_class(key2[0]) + _cv_class(key2[1])
        return stats['cv_letters'].get(cv_key)

    return result  # may be None

def _entropy_for_letter(letter_stats, letter):
    if not letter_stats:
        raise ValueError("NoStats")
    total = letter_stats.get('total', 0)
    freq = letter_stats.get(letter, 0)
    if total < 1 or freq < 1:
        raise ValueError("NoStats")
    return -math.log2(freq / total)

def create_word(stats, word_length, include_entropy=False):
    l1, entropy_bits = choose_letter_with_entropy(stats['firstLetters'])
    second_stats = stats['secondLetters'].get(l1)
    l2, second_bits = choose_letter_with_entropy(second_stats)
    entropy_bits += second_bits
    letters = [l1, l2]

    l0 = None   # letter before the current bigram (enables trigram lookup)
    for index in range(2, word_length):
        key3 = l0 + l1 + l2 if l0 is not None else None
        transition_stats = _get_transition_stats(stats, l1 + l2, index, word_length, key3=key3)
        next_letter, next_bits = choose_letter_with_entropy(transition_stats)
        letters.append(next_letter)
        entropy_bits += next_bits
        l0, l1, l2 = l1, l2, next_letter

    word = ''.join(letters)
    if include_entropy:
        return word, entropy_bits
    return word

def estimate_entropy_bits(stats, word):
    if not word or len(word) < 3:
        raise ValueError("Word length must be at least 3 letters")

    entropy_bits = _entropy_for_letter(stats['firstLetters'], word[0])
    entropy_bits += _entropy_for_letter(
        stats['secondLetters'].get(word[0]),
        word[1]
    )

    for index in range(2, len(word)):
        context2 = word[index - 2:index]
        key3 = word[index - 3:index] if index >= 3 else None
        transition_stats = _get_transition_stats(stats, context2, index, len(word), key3=key3)
        entropy_bits += _entropy_for_letter(transition_stats, word[index])
    return entropy_bits

def _is_weak_word(word, blocked_words=None):
    candidate = word.lower()
    blocked = blocked_words or set()
    if candidate in blocked:
        return True
    if any(candidate[i] == candidate[i + 1] == candidate[i + 2]
           for i in range(0, max(0, len(candidate) - 2))):
        return True
    if candidate.startswith(('pass', 'admin', 'qwer', 'letm')):
        return True
    return False


def _is_unpronounceable(word):
    """Return True if *word* contains patterns that make it hard to say aloud.

    Rejects:
    - Runs of ≥ 3 consecutive consonants (e.g. 'strng', 'bkl').
    - Runs of ≥ 3 consecutive vowels (e.g. 'aei').
    - Any 4-letter window with no vowel.
    """
    candidate = word.lower()
    consonant_run = 0
    vowel_run = 0
    for ch in candidate:
        if ch in VOWELS:
            vowel_run += 1
            consonant_run = 0
        else:
            consonant_run += 1
            vowel_run = 0
        if consonant_run >= 3 or vowel_run >= 3:
            return True
    # No vowel in any 4-letter window
    for i in range(len(candidate) - 3):
        if not any(c in VOWELS for c in candidate[i:i + 4]):
            return True
    return False

def generate(
    stats,
    word_length,
    number_of_words=1,
    min_entropy_bits=None,
    max_attempts_per_word=30,
    blocked_words=None
):
    if word_length < 3:
        raise ValueError("Word length must be at least 3 letters")
    if number_of_words < 1:
        raise ValueError("Invalid number of words")
    if min_entropy_bits is not None and min_entropy_bits <= 0:
        raise ValueError("Minimum entropy must be greater than 0")
    if max_attempts_per_word < 1:
        raise ValueError("Maximum attempts must be at least 1")

    result = []
    blocked_words = {word.lower() for word in blocked_words} if blocked_words else set()
    i = 0
    while i < number_of_words:
        attempts = 0
        retries = 0
        while attempts < max_attempts_per_word:
            try:
                word, entropy_bits = create_word(stats, word_length, include_entropy=True)
            except ValueError as ex:
                if str(ex) != "NoStats":
                    raise ex
                retries += 1
                if retries > 5:
                    raise ValueError("Error generating words - insufficient stats")
                continue

            attempts += 1
            if _is_weak_word(word, blocked_words) or _is_unpronounceable(word):
                continue
            if min_entropy_bits is None or entropy_bits >= min_entropy_bits:
                result.append(word)
                i += 1
                break

        if attempts >= max_attempts_per_word:
            raise ValueError("Unable to generate words meeting security constraints")
    return result

# Example usage:
if __name__ == "__main__":
    # Assuming `stats` is a pre-populated dictionary with the necessary structure
    stats = {
        'firstLetters': {'a': 10, 'b': 5, 'total': 15},
        'secondLetters': {'a': {'a': 5, 'b': 3, 'total': 8}, 'b': {'a': 2, 'b': 1, 'total': 3}},
        'letters': {'aa': {'c': 2, 'd': 1, 'total': 3}, 'ab': {'c': 1, 'd': 1, 'total': 2}},
        'penultimateLetters': {'ac': {'e': 1, 'total': 1}, 'ad': {'e': 1, 'total': 1}},
        'lastLetters': {'ce': {'f': 1, 'total': 1}, 'de': {'f': 1, 'total': 1}}
    }
    words = generate(stats, 5, 10)
    print(words)