def format_number(value, digits, use_letters=False, letters_upper=True):
    """Format an already-computed absolute integer as the shared numbering
    representation: zero-padded digits, or spreadsheet-style letters.
    `digits` is ignored when use_letters=True. No separator is added —
    callers own their own separator placement."""
    if use_letters:
        return int_to_letters(value, upper=letters_upper)
    return '{:0{width}d}'.format(value, width=digits)


def int_to_letters(n, upper=True):
    """1-based spreadsheet-style base-26: 1->A, 26->Z, 27->AA, ... n<=0 -> ''."""
    if n <= 0:
        return ''
    letters = ''
    while n > 0:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters if upper else letters.lower()


def letters_to_int(letters):
    """Reverse of int_to_letters. Case-insensitive. Non-letter input -> 0."""
    n = 0
    for ch in letters.upper():
        if not ('A' <= ch <= 'Z'):
            return 0
        n = n * 26 + (ord(ch) - 64)
    return n
