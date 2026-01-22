"""
Text preprocessing and tokenization for the search engine.
"""
import re
import string


# Common English stopwords (words that don't add much meaning)
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with'
}


def tokenize(text):
    """
    Tokenize and normalize text.
    
    Steps:
    1. Convert to lowercase
    2. Remove punctuation
    3. Split into words
    4. Remove stopwords
    5. Filter out very short tokens (< 2 chars)
    
    Args:
        text: Input text string
        
    Returns:
        List of normalized tokens
    """
    if not text:
        return []
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and split into words
    # Keep only alphanumeric characters and spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Split into tokens
    tokens = text.split()
    
    # Filter: remove stopwords and very short tokens
    tokens = [
        token for token in tokens 
        if token not in STOPWORDS and len(token) >= 2
    ]
    
    return tokens


def tokenize_with_positions(text):
    """
    Tokenize text and keep track of positions for potential phrase queries.
    
    Args:
        text: Input text string
        
    Returns:
        List of (token, position) tuples
    """
    if not text:
        return []
    
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    tokens = text.split()
    
    # Return tokens with their positions, filtering stopwords
    result = []
    for position, token in enumerate(tokens):
        if token not in STOPWORDS and len(token) >= 2:
            result.append((token, position))
    
    return result
