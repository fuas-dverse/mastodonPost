import re
from better_profanity import profanity


def load_profanity_filter():
    # Load a custom list of profane words (optionally)
    profanity.load_censor_words()


def is_content_appropriate(content):
    """
    Check if the content is appropriate using various filters.

    Args:
        content (str): The content to check.

    Returns:
        bool: True if content is appropriate, False otherwise.
    """
    # Check for profanity
    if profanity.contains_profanity(content):
        return False

    # We can add more checks as needed, e.g., regex for specific patterns
    inappropriate_patterns = [r'\b(?:inappropriate|offensive)\b']
    for pattern in inappropriate_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False

    return True
