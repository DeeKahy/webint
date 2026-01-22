"""
Investigate why the model predicts 5 stars for a negative review.
Let's look at the actual dataset and word patterns.
"""

import pandas as pd
import json
import gzip
import os
from collections import Counter
import re

def load_data():
    """Load the dataset."""
    dataset_dir = os.path.join(os.path.dirname(__file__), 'Dataset')
    json_file = os.path.join(dataset_dir, 'Books_5.json.gz')
    
    data = []
    with gzip.open(json_file, 'rt', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    
    return pd.DataFrame(data)

def get_words(text):
    """Extract words from text (simple tokenization)."""
    # Convert to lowercase and split by whitespace
    text = str(text).lower()
    # Remove punctuation
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.split()

def main():
    print("="*70)
    print("INVESTIGATING THE DATASET")
    print("="*70)
    
    df = load_data()
    
    # === 1. Class Distribution ===
    print("\n1️⃣  RATING DISTRIBUTION (How many of each rating?)")
    print("-" * 70)
    rating_counts = df['overall'].value_counts().sort_index()
    print(rating_counts)
    print(f"\nTotal reviews: {len(df)}")
    
    # Calculate percentages
    print("\nPercentages:")
    for rating in sorted(df['overall'].unique()):
        count = (df['overall'] == rating).sum()
        pct = (count / len(df)) * 100
        print(f"  {rating} stars: {count:5d} reviews ({pct:5.1f}%)")
    
    # === 2. Look at specific problematic words ===
    print("\n\n2️⃣  HOW OFTEN DO NEGATIVE WORDS APPEAR IN EACH RATING?")
    print("-" * 70)
    
    # Filter data - only reviews with text
    df = df.dropna(subset=['reviewText'])
    
    # Check for negative words
    negative_words = ['terrible', 'waste', 'disappointed', 'bad', 'poor', 'worst']
    
    for word in negative_words:
        print(f"\n'{word.upper()}' appears in:")
        for rating in sorted(df['overall'].unique()):
            rating_reviews = df[df['overall'] == rating]['reviewText'].str.lower()
            count = rating_reviews.str.contains(word, na=False).sum()
            pct = (count / len(rating_reviews)) * 100 if len(rating_reviews) > 0 else 0
            print(f"  {rating} stars: {count:4d} reviews ({pct:5.1f}%)")
    
    # === 3. Look at actual 5-star reviews with the word "terrible" ===
    print("\n\n3️⃣  ACTUAL 5-STAR REVIEWS CONTAINING 'TERRIBLE'")
    print("-" * 70)
    
    five_star_terrible = df[(df['overall'] == 5.0) & 
                             (df['reviewText'].str.lower().str.contains('terrible', na=False))]
    
    print(f"\nFound {len(five_star_terrible)} 5-star reviews with the word 'terrible'\n")
    
    if len(five_star_terrible) > 0:
        for idx, (i, row) in enumerate(five_star_terrible.head(5).iterrows()):
            print(f"Review {idx+1}:")
            print(f"  Rating: {row['overall']} stars")
            print(f"  Summary: {row.get('summary', 'N/A')}")
            print(f"  Text: {row['reviewText'][:200]}...")
            print()
    
    # === 4. Compare top words in 1-star vs 5-star reviews ===
    print("\n4️⃣  TOP 20 WORDS IN 1-STAR REVIEWS")
    print("-" * 70)
    
    one_star_reviews = df[df['overall'] == 1.0]['reviewText'].fillna('')
    one_star_words = []
    for review in one_star_reviews:
        one_star_words.extend(get_words(review))
    
    # Filter out very short words
    one_star_words = [w for w in one_star_words if len(w) > 3]
    counter_1 = Counter(one_star_words)
    
    print("\n1-star reviews - Top 20 words:")
    for word, count in counter_1.most_common(20):
        print(f"  {word:20s}: {count:5d}")
    
    # === 5. Compare top words in 5-star vs 1-star reviews ===
    print("\n\n5️⃣  TOP 20 WORDS IN 5-STAR REVIEWS")
    print("-" * 70)
    
    five_star_reviews = df[df['overall'] == 5.0]['reviewText'].fillna('')
    five_star_words = []
    for review in five_star_reviews:
        five_star_words.extend(get_words(review))
    
    # Filter out very short words
    five_star_words = [w for w in five_star_words if len(w) > 3]
    counter_5 = Counter(five_star_words)
    
    print("\n5-star reviews - Top 20 words:")
    for word, count in counter_5.most_common(20):
        print(f"  {word:20s}: {count:5d}")
    
    # === 6. Check overlap ===
    print("\n\n6️⃣  WORDS THAT APPEAR IN BOTH 1-STAR AND 5-STAR REVIEWS")
    print("-" * 70)
    
    one_star_set = set(counter_1.keys())
    five_star_set = set(counter_5.keys())
    overlap = one_star_set & five_star_set
    
    print(f"\nTotal unique words in 1-star: {len(one_star_set)}")
    print(f"Total unique words in 5-star: {len(five_star_set)}")
    print(f"Words appearing in BOTH: {len(overlap)}")
    print(f"Overlap percentage: {(len(overlap) / min(len(one_star_set), len(five_star_set)) * 100):.1f}%")
    
    print("\nTop overlapping words (by frequency in 1-star):")
    overlap_list = [(w, counter_1[w], counter_5[w]) for w in list(overlap)[:50]]
    overlap_list.sort(key=lambda x: x[1], reverse=True)
    for word, count_1, count_5 in overlap_list[:15]:
        print(f"  {word:15s}: {count_1:5d} in 1-star, {count_5:5d} in 5-star")
    
    # === 7. Check text length ===
    print("\n\n7️⃣  REVIEW TEXT LENGTH BY RATING")
    print("-" * 70)
    
    df['text_length'] = df['reviewText'].fillna('').str.len()
    
    print("\nAverage review length (characters):")
    for rating in sorted(df['overall'].unique()):
        avg_len = df[df['overall'] == rating]['text_length'].mean()
        print(f"  {rating} stars: {avg_len:.0f} characters")

if __name__ == "__main__":
    main()
