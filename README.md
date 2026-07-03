# pypassgen
The excellent Memorable (Pronounceable) Password Generator using markov chains by [David Minor](https://github.com/davidminor) ported to Python

The original javascript code is at https://github.com/davidminor/password-supply

## Security hardening notes

- Generation now samples the full transition distribution using secure randomness.
- Lengths of 3 and 4 characters are handled safely.
- Default generation is now stronger (preset-based, capitalization and l33t enabled).
- You can require minimum estimated entropy during generation:
  - `main.generate(length=12, number=5, min_entropy_bits=40)`
- You can use strength presets:
  - `main.generate(number=5, strength_preset="interactive")`
  - `main.generate(number=5, strength_preset="standard")`
  - `main.generate(number=5, strength_preset="high")`
- Common weak outputs are rejected with built-in blacklist/pattern checks.
- You can estimate entropy of a generated word:
  - `markov_words.estimate_entropy_bits(stats, word)`
- l33t substitution selection is randomized for less predictability.
