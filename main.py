import markov_words 
import l33t 
from stats import stats

COMMON_BLOCKED_WORDS = {
    "password", "passwrd", "letmein", "welcome", "admin",
    "qwerty", "dragon", "monkey", "baseball", "football"
}

STRENGTH_PRESETS = {
    "interactive": {"length": 8, "min_entropy_bits": 22},
    "standard": {"length": 10, "min_entropy_bits": 30},
    "high": {"length": 12, "min_entropy_bits": 40}
}

def _resolve_strength(strength_preset):
    if strength_preset is None:
        return {}
    preset_key = str(strength_preset).lower()
    if preset_key not in STRENGTH_PRESETS:
        raise ValueError("Invalid strength preset")
    return STRENGTH_PRESETS[preset_key]

def generate(length=None, number=1, min_entropy_bits=None, strength_preset=None, blocked_words=None):
    preset = _resolve_strength(strength_preset)
    if length is None:
        length = preset.get("length", 10)
    length = int(length)
    length_valid = length >= 3
    number = int(number)
    number_valid = number > 0

    if min_entropy_bits is None:
        min_entropy_bits = preset.get("min_entropy_bits")
    if min_entropy_bits is not None:
        min_entropy_bits = float(min_entropy_bits)
        min_entropy_valid = min_entropy_bits > 0
    else:
        min_entropy_valid = True

    if blocked_words is None:
        blocked_words = COMMON_BLOCKED_WORDS

    if length_valid and number_valid and min_entropy_valid:
        return markov_words.generate(
            stats,
            length,
            number,
            min_entropy_bits=min_entropy_bits,
            blocked_words=blocked_words
        )
    return []

def generate_passwords():
    strength_preset = "standard"
    number = 12
    substitute = True
    capitalize = True
    
    words = generate(number=number, strength_preset=strength_preset)
    if capitalize:
        words = [word.capitalize() for word in words]
    if substitute:
        words = [l33t.substitute(word) for word in words] 

    return words    

if __name__ == '__main__':
    print(generate_passwords())