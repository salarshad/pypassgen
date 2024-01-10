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
    letter_index = word.find(subst[0])
    if letter_index >= 0:
        word = word[:letter_index] + subst[1] + word[letter_index+1:]
    return word

def substitute(word, number_of_substitutions=1):
    if not word:
        raise ValueError("No word given")
    
    number = True
    num_index = 0
    sym_index = 0
    num_length = len(number_subs)
    sym_length = len(symbol_subs)
    orig_word = word
    
    while number_of_substitutions > 0 and (num_index < num_length or sym_index < sym_length):
        if number:
            while num_index < num_length:
                orig_word = word
                word = try_sub(word, number_subs[num_index])
                if word != orig_word:
                    number_of_substitutions -= 1
                    break
                num_index += 1
        else:
            while sym_index < sym_length:
                orig_word = word
                word = try_sub(word, symbol_subs[sym_index])
                if word != orig_word:
                    number_of_substitutions -= 1
                    break
                sym_index += 1
        number = not number
    
    return word

# Example usage:
if __name__ == "__main__":
    word_to_substitute = "substitution"
    number_of_substitutions = 3
    substituted_word = substitute(word_to_substitute, number_of_substitutions)
    print(substituted_word)