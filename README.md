# pypassgen
The excellent Memorable (Pronounceable) Password Generator using markov chains by [David Minor](https://github.com/davidminor) ported to Python

The original javascript code is at https://github.com/davidminor/password-supply

## Security hardening notes

- Generation now samples the full transition distribution using secure randomness.
- Lengths of 3 and 4 characters are handled safely.
- You can require minimum estimated entropy during generation:
  - `main.generate(length, number, min_entropy_bits=40)`
- You can estimate entropy of a generated word:
  - `markov_words.estimate_entropy_bits(stats, word)`
