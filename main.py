import markov_words 
import l33t 
from stats import stats

def generate(length, number):
    length = int(length)
    length_valid = length >= 3
    number = int(number)
    number_valid = number > 0
    if length_valid and number_valid:
        return markov_words.generate(stats, length, number)
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