import secrets

def choose_letter(letter_stats):
    if not letter_stats:
        raise ValueError("NoStats")
    draw = secrets.randbelow(letter_stats['total'] - 1)
    count = 0
    for letter, freq in letter_stats.items():
        if letter == 'total':
            continue
        count += freq
        if count > draw:
            return letter
    raise ValueError("NoStats")  # shouldn't get here with proper stats

def create_word(stats, word_length):
    l1 = choose_letter(stats['firstLetters'])
    l2 = choose_letter(stats['secondLetters'][l1])
    current_word = l1 + l2
    for j in range(2, word_length - 2):
        next_letter = choose_letter(stats['letters'][l1 + l2])
        current_word += next_letter
        l1, l2 = l2, next_letter
    if j < word_length - 1:
        next_letter = choose_letter(stats['penultimateLetters'][l1 + l2])
        current_word += next_letter
        l1, l2 = l2, next_letter
    return current_word + choose_letter(stats['lastLetters'][l1 + l2])

def generate(stats, word_length, number_of_words=1):
    if word_length < 3:
        raise ValueError("Word length must be at least 3 letters")
    if number_of_words < 1:
        raise ValueError("Invalid number of words")
    result = []
    retries = 0
    i = 0
    while i < number_of_words:
        try:
            result.append(create_word(stats, word_length))
            retries = 0
            i += 1
        except ValueError as ex:
            if str(ex) == "NoStats":
                if retries > 5:
                    raise ValueError(
                        "Error generating words - insufficient stats")
                retries += 1
            else:
                raise ex
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