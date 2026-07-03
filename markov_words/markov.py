import secrets
import math

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

def _get_transition_stats(stats, key, index, word_length):
    if index < word_length - 2:
        return stats['letters'].get(key)
    if index == word_length - 2:
        return stats['penultimateLetters'].get(key)
    return stats['lastLetters'].get(key)

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

    for index in range(2, word_length):
        transition_stats = _get_transition_stats(stats, l1 + l2, index, word_length)
        next_letter, next_bits = choose_letter_with_entropy(transition_stats)
        letters.append(next_letter)
        entropy_bits += next_bits
        l1, l2 = l2, next_letter

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
        context = word[index - 2:index]
        transition_stats = _get_transition_stats(stats, context, index, len(word))
        entropy_bits += _entropy_for_letter(transition_stats, word[index])
    return entropy_bits

def generate(stats, word_length, number_of_words=1, min_entropy_bits=None, max_attempts_per_word=30):
    if word_length < 3:
        raise ValueError("Word length must be at least 3 letters")
    if number_of_words < 1:
        raise ValueError("Invalid number of words")
    if min_entropy_bits is not None and min_entropy_bits <= 0:
        raise ValueError("Minimum entropy must be greater than 0")

    result = []
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
            if min_entropy_bits is None or entropy_bits >= min_entropy_bits:
                result.append(word)
                i += 1
                break

        if attempts >= max_attempts_per_word:
            raise ValueError("Unable to generate words meeting entropy threshold")
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