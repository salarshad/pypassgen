_VOWELS = set('aeiouy')


def _cv_class(letter):
    """Return 'V' if *letter* is a vowel, 'C' otherwise."""
    return 'V' if letter in _VOWELS else 'C'


def count_letter(totals, letter):
    stat = totals.get(letter, 0)
    totals[letter] = stat + 1
    totals['total'] = totals.get('total', 0) + 1

def incorporate_word(stats, word):
    if len(word) < 3:
        return

    if 'firstLetters' not in stats:
        stats['firstLetters'] = {'total': 0}

    # first letter stats
    l1 = word[0]
    count_letter(stats['firstLetters'], l1)

    # second letter stats, relative to first letter
    l2 = word[1]
    totals = stats['secondLetters'].setdefault(l1, {'total': 0})
    count_letter(totals, l2)

    # remaining letter stats, relative to preceding 2 letters
    di = l1 + l2
    l0 = None   # letter before the current bigram (for trigram key)
    for j in range(2, len(word)):
        l3 = word[j]
        is_middle = j < len(word) - 2
        is_penultimate = j == len(word) - 2

        # Existing 2-letter tables (unchanged)
        if is_middle:
            totals = stats['letters'].setdefault(di, {'total': 0})
        elif is_penultimate:
            totals = stats['penultimateLetters'].setdefault(di, {'total': 0})
        else:
            totals = stats['lastLetters'].setdefault(di, {'total': 0})
        count_letter(totals, l3)

        # New: trigram table for middle positions (requires 3 previous letters)
        if is_middle and l0 is not None:
            tri = l0 + di
            totals3 = stats['letters3'].setdefault(tri, {'total': 0})
            count_letter(totals3, l3)

        # New: CV-pattern table for middle positions
        if is_middle:
            cv_key = _cv_class(di[0]) + _cv_class(di[1])
            totals_cv = stats['cv_letters'].setdefault(cv_key, {'total': 0})
            count_letter(totals_cv, l3)

        l0 = di[0]
        di = di[1] + l3

def calculate_stats(word_list):
    stats = {
        'secondLetters': {},
        'letters': {},
        'penultimateLetters': {},
        'lastLetters': {},
        'letters3': {},
        'cv_letters': {},
    }

    if not word_list:
        return stats

    for word in word_list:
        incorporate_word(stats, word)

    return stats

if __name__ == "__main__":
    # Example usage
    word_list = ["example", "words", "for", "statistics"]
    stats = calculate_stats(word_list)
    print(stats)