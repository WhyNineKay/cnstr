def is_number(s: str) -> bool:
    """
    Check if a string represents a valid number.
    """
    if any(c not in "0123456789.-+eE" for c in s):
        return False
    
    try:
        float(s)
    except ValueError:
        return False
    return True

def smart_split(s: str, includeQuotes: bool = False) -> list[str]:
    """
    Split a string by spaces, but keep quoted substrings together.
    Note: doesn't handle escaped quotes.

    :param s: The string to split
    :param includeQuotes: Whether to include the quotes in the output
    :return: A list of strings
    """
    
    inQuotes = ""  # ' " or \w
    words: list[str] = []
    currentWord = ""

    for c in s:
        if c == inQuotes:
            inQuotes = ""
            if includeQuotes:
                currentWord += c
            words.append(currentWord)
            currentWord = ""
        elif inQuotes:
            currentWord += c
        elif c == " ":
            if currentWord:
                words.append(currentWord)
                currentWord = ""
        elif c in ["'", '"']:
            inQuotes = c
            if includeQuotes:
                currentWord += c
        else:
            currentWord += c

    if currentWord:
        words.append(currentWord)
    
    # Remove empty strings
    words = [w for w in words if w]

    return words
