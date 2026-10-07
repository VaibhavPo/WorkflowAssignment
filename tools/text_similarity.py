import difflib

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate the similarity between two strings using SequenceMatcher.
    Returns a float between 0.0 and 1.0.
    """
    if text1 is None or text2 is None:
        return 0.0
    text1 = str(text1).lower().strip()
    text2 = str(text2).lower().strip()
    return difflib.SequenceMatcher(None, text1, text2).ratio()
