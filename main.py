import markov_words 
import l33t 
from stats import stats

def generate(length, number, min_entropy_bits=None):
    length = int(length)
    length_valid = length >= 3
    number = int(number)
    number_valid = number > 0
    if min_entropy_bits is not None:
        min_entropy_bits = float(min_entropy_bits)
        min_entropy_valid = min_entropy_bits > 0
    else:
        min_entropy_valid = True

    if length_valid and number_valid and min_entropy_valid:
        return markov_words.generate(
            stats,
            length,
            number,
            min_entropy_bits=min_entropy_bits
        )
    return []

def generate_passwords():
    length = 6
    number = 12
    substitute = False
    capitalize = False
    
    words = generate(length, number)
    if capitalize:
        words = [word.capitalize() for word in words]
    if substitute:
        words = [l33t.substitute(word) for word in words] 

    return words    

if __name__ == '__main__':
    print(generate_passwords())