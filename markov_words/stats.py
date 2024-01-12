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
    for j in range(2, len(word)):
        l3 = word[j]
        if j < len(word) - 2:
            totals = stats['letters'].setdefault(di, {'total': 0})
        elif j < len(word) - 1:
            totals = stats['penultimateLetters'].setdefault(di, {'total': 0})
        else:
            totals = stats['lastLetters'].setdefault(di, {'total': 0})
        count_letter(totals, l3)
        di = di[1] + l3

def calculate_stats(word_list):
    stats = {
        'secondLetters': {},
        'letters': {},
        'penultimateLetters': {},
        'lastLetters': {}
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