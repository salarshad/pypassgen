import markov_words
import l33t
from stats import stats
from markov_words.prosody import score_combination, select_best_combination
from markov_words.markov import estimate_entropy_bits

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


def generate_passphrase(
    num_words=2,
    word_length=7,
    strength_preset="standard",
    capitalize=True,
    separator="",
    substitute=False,
    candidate_pool_size=None,
    blocked_words=None,
    return_details=False,
):
    """Generate a prosody-scored passphrase.

    Builds a candidate pool using the Markov chain, selects the best
    *num_words*-length combination by rhythm/phonetic contrast, and
    verifies that the combined entropy meets the preset threshold.

    Parameters
    ----------
    num_words : int
        Number of words in the passphrase (default 2; supports 3, 4).
    word_length : int
        Per-word character length (default 7).
    strength_preset : str
        One of ``"interactive"``, ``"standard"`` (default), ``"high"``.
    capitalize : bool
        Capitalise the first letter of each word (default True → CamelCase).
    separator : str
        String inserted between words (default ``""`` → no separator).
    substitute : bool
        Apply l33t substitutions (default False for readability).
    candidate_pool_size : int or None
        Size of the generation pool; auto-scaled to ``max(20, num_words*10)``
        when *None*.
    blocked_words : set or None
        Additional words to block (merged with ``COMMON_BLOCKED_WORDS``).
    return_details : bool
        When True, return a dict with keys ``passphrase``, ``words``,
        ``entropy_bits``, and ``rhythm_score`` instead of just the string.

    Returns
    -------
    str or dict
    """
    preset = _resolve_strength(strength_preset)
    min_entropy = preset.get("min_entropy_bits", 0)

    all_blocked = set(COMMON_BLOCKED_WORDS)
    if blocked_words:
        all_blocked.update(w.lower() for w in blocked_words)

    if candidate_pool_size is None:
        candidate_pool_size = max(20, num_words * 10)

    max_rounds = 5
    for attempt in range(max_rounds):
        pool_size = candidate_pool_size * (attempt + 1)
        # Generate candidate pool without a per-word entropy threshold so
        # the prosody selector has enough variety to choose from.
        candidates = markov_words.generate(
            stats,
            word_length,
            pool_size,
            blocked_words=all_blocked,
        )

        chosen = select_best_combination(candidates, num_words)

        # Verify combined entropy
        try:
            total_entropy = sum(estimate_entropy_bits(stats, w) for w in chosen)
        except ValueError:
            total_entropy = 0.0

        if total_entropy >= min_entropy:
            break
    else:
        raise ValueError(
            f"Could not generate a passphrase with ≥ {min_entropy} entropy bits "
            f"using preset '{strength_preset}'. Try a lower strength preset or "
            "shorter word length."
        )

    if substitute:
        chosen = [l33t.substitute(w) for w in chosen]
    if capitalize:
        chosen = [w.capitalize() for w in chosen]

    passphrase = separator.join(chosen)
    rhythm = score_combination([w.lower() for w in chosen])

    if return_details:
        return {
            "passphrase": passphrase,
            "words": chosen,
            "entropy_bits": total_entropy,
            "rhythm_score": rhythm,
        }
    return passphrase

if __name__ == '__main__':
    print("Passwords:")
    print(generate_passwords())
    print()
    print("Passphrase (2 words):")
    print(generate_passphrase())
    print()
    print("Passphrase (3 words, with details):")
    print(generate_passphrase(num_words=3, return_details=True))