import secrets

number_subs = [
    ('o', '0'),
    ('i', '1'),
    ('l', '1'),
    ('s', '5'),
    ('g', '9'),
    ('a', '4'),
    ('b', '8'),
    ('t', '7'),
    ('e', '3')
]

symbol_subs = [
    ('a', '@'),
    ('s', '$'),
    ('c', '('),
    ('t', '+'),
    ('i', '!'),
    ('l', '|'),
    ('d', '|)'),
    ('m', '^^'),
    ('k', '|<'),
    ('w', '^/'),
    ('v', '/'),
    ('x', '><'),
    ('n', '/\\'),
    ('o', '()'),
    ('u', '|_|'),
    ('h', '|-|')
]

def try_sub(word, subst):
    source, replacement = subst
    letter_indexes = [index for index, letter in enumerate(word) if letter == source]
    if letter_indexes:
        letter_index = letter_indexes[secrets.randbelow(len(letter_indexes))]
        word = word[:letter_index] + replacement + word[letter_index+1:]
    return word

def _applicable_substitutions(word, substitutions):
    return [subst for subst in substitutions if subst[0] in word]

def substitute(word, number_of_substitutions=1):
    if not word:
        raise ValueError("No word given")

    use_number = bool(secrets.randbelow(2))
    while number_of_substitutions > 0:
        substitutions = number_subs if use_number else symbol_subs
        applicable = _applicable_substitutions(word, substitutions)
        if not applicable:
            fallback = _applicable_substitutions(
                word,
                symbol_subs if use_number else number_subs
            )
            if not fallback:
                break
            substitutions = fallback
        else:
            substitutions = applicable

        selected_sub = substitutions[secrets.randbelow(len(substitutions))]
        new_word = try_sub(word, selected_sub)
        if new_word == word:
            break
        word = new_word
        number_of_substitutions -= 1
        use_number = not use_number
    
    return word

# Example usage:
if __name__ == "__main__":
    word_to_substitute = "substitution"
    number_of_substitutions = 3
    substituted_word = substitute(word_to_substitute, number_of_substitutions)
    print(substituted_word)