"""
Simple Naive Bayes Classifier for Rating Prediction

This is a basic implementation that predicts user ratings based on product features.
We'll use simple features extracted from the review text and product information.
"""

# === IMPORTS (Libraries we need) ===
# Think of these as toolboxes we're opening to use different tools

import pandas as pd  # pandas = Excel for Python, helps organize data in tables
import json  # Helps us read JSON files (a common data format)
import gzip  # Helps us open compressed/zipped files
import os  # Helps us find files on the computer
from collections import defaultdict, Counter  # Special dictionaries for counting things
import numpy as np  # Math library for working with numbers

# These are from scikit-learn, a machine learning library:
from sklearn.model_selection import train_test_split  # Splits data into practice and test sets
from sklearn.naive_bayes import MultinomialNB  # The "brain" that learns patterns
from sklearn.feature_extraction.text import CountVectorizer  # Converts words into numbers
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error  # Tools to measure how good our predictions are

def load_data():
    """
    Load the dataset from a compressed file.
    
    ELI5: This is like opening a treasure chest (the .json.gz file) and 
    taking out all the review papers inside, then organizing them in a 
    neat table so we can read them easily.
    """
    # Step 1: Find where the data file lives on the computer
    dataset_dir = os.path.join(os.path.dirname(__file__), 'Dataset')
    json_file = os.path.join(dataset_dir, 'Books_5.json.gz')
    
    # Step 2: Open the compressed file and read each review (one per line)
    data = []  # An empty basket to collect all the reviews
    with gzip.open(json_file, 'rt', encoding='utf-8') as f:
        # Loop through each line in the file
        for line in f:
            if line.strip():  # Only if the line is not empty
                # Convert the text into a Python dictionary and add to our basket
                data.append(json.loads(line))
    
    # Step 3: Convert the list of reviews into a table (DataFrame)
    # Think of this like putting sticky notes into a spreadsheet
    df = pd.DataFrame(data)
    
    # Step 4: Print some info so we know what we got
    print(f"Loaded {len(df)} reviews")  # How many reviews total
    print(f"Columns: {list(df.columns)}")  # What information each review has
    print(f"\nRating distribution:")  # Show how many 1-star, 2-star, etc.
    print(df['overall'].value_counts().sort_index())
    
    return df  # Give back the table of reviews

def prepare_features_simple(df):
    """
    Prepare the data for our machine learning model.
    
    ELI5: We're getting the data ready for the computer to learn from.
    We take the review text (what people wrote) and the rating (how many 
    stars they gave). The computer will learn: "When someone writes THIS, 
    they usually give THAT many stars."
    """
    # Step 1: Remove any reviews that don't have text (can't learn from nothing!)
    df = df.dropna(subset=['reviewText'])
    
    # Step 2: Combine the main review and the title/summary together
    # This gives us MORE words to learn from (more clues!)
    df['combined_text'] = df['reviewText'].fillna('') + ' ' + df['summary'].fillna('')
    
    # Step 3: Separate the INPUT (what we learn from) and OUTPUT (what we predict)
    X = df['combined_text']  # X = The review text (INPUT: the clues)
    y = df['overall']  # y = The rating 1-5 stars (OUTPUT: what we want to predict)
    
    return X, y  # Give back both the clues and the answers

def train_naive_bayes_simple():
    """
    Train a machine learning model to predict ratings from review text.
    
    ELI5: This is like teaching a student (the computer) by showing it 
    many examples. We show it reviews and their ratings, and it learns 
    patterns like: "When I see words like 'amazing' and 'great', 
    people usually give 5 stars. When I see 'terrible' and 'waste', 
    they give 1 star."
    """
    print("="*60)
    print("SIMPLE NAIVE BAYES CLASSIFIER - TEXT FEATURES")
    print("="*60 + "\n")
    
    # === STEP 1: Load the data ===
    # Get all the reviews from the file
    df = load_data()
    
    # === STEP 2: Prepare the data ===
    # Separate the review text (X) from the ratings (y)
    X, y = prepare_features_simple(df)
    
    # === STEP 3: Split into training and testing sets ===
    # ELI5: We use 80% of reviews to TEACH the computer (training set)
    #       and save 20% to TEST if it learned correctly (test set)
    # It's like studying with some flashcards and saving others to quiz yourself later!
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42  # 0.2 = 20% for testing
    )
    
    print(f"\nTraining set size: {len(X_train)}")  # How many reviews to learn from
    print(f"Test set size: {len(X_test)}")  # How many reviews to test on
    
    # === STEP 4: Convert words to numbers ===
    # ELI5: Computers only understand numbers, not words! So we need to 
    # convert "This magazine is great!" into numbers.
    # We do this by counting words: How many times does "great" appear? 
    # How about "terrible"? Each word becomes a number.
    print("\nConverting text to features...")
    vectorizer = CountVectorizer(
        max_features=500,  # Only use the 500 most common words (keeps it simple)
        stop_words='english'  # Ignore boring words like "the", "and", "is"
    )
    
    # Learn which words are important from the training reviews
    X_train_vec = vectorizer.fit_transform(X_train)
    # Apply the same conversion to test reviews
    X_test_vec = vectorizer.transform(X_test)
    
    print(f"Number of features: {X_train_vec.shape[1]}")  # How many different words we're tracking
    
    # === STEP 5: Train the AI "brain" ===
    # ELI5: Create a "brain" (classifier) and teach it by showing all the 
    # training examples. It learns: "These words usually mean 5 stars, 
    # these words usually mean 1 star", etc.
    print("\nTraining Naive Bayes classifier...")
    clf = MultinomialNB()  # Create the brain
    clf.fit(X_train_vec, y_train)  # Teach it using the training data
    
    # === STEP 6: Test how well it learned ===
    # ELI5: Now we quiz the computer with the test set (reviews it's never 
    # seen before) and see if it can guess the correct ratings!
    y_pred = clf.predict(X_test_vec)
    
    # === STEP 7: Check the results ===
    # ELI5: Compare the computer's guesses (y_pred) to the real answers (y_test)
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    # Accuracy = What percentage did it get exactly right?
    accuracy = accuracy_score(y_test, y_pred)
    
    # MAE (Mean Absolute Error) = On average, how far off are the guesses?
    # Example: If real rating is 5 and it guesses 4, that's an error of 1
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"\nAccuracy: {accuracy:.4f}")  # Percentage correct (e.g., 0.5000 = 50%)
    print(f"Mean Absolute Error: {mae:.4f}")  # Average mistake size (e.g., 0.8 = off by 0.8 stars)
    
    # Detailed report showing performance for each rating (1-5 stars)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Give back the trained brain and the word-to-number converter
    # (We'll need these to make predictions on new reviews later!)
    return clf, vectorizer

def predict_rating(clf, vectorizer, review_text):
    """
    Use our trained model to predict the rating for a new review.
    
    ELI5: Now that the computer has learned, we can give it a NEW review 
    (that it's never seen before) and ask: "Based on what you learned, 
    how many stars do you think this person will give?"
    """
    # Step 1: Convert the new review text into numbers (same way we did during training)
    review_vec = vectorizer.transform([review_text])
    
    # Step 2: Ask the trained brain to make a prediction
    predicted_rating = clf.predict(review_vec)[0]
    
    # Step 3: Get the probability for each possible rating
    # ELI5: The computer doesn't just guess - it says "I'm 60% sure it's 5 stars, 
    # 30% sure it's 4 stars, etc." These are called probabilities.
    probabilities = clf.predict_proba(review_vec)[0]
    
    # Step 4: Show the results in a nice format
    print(f"\nReview: {review_text[:100]}...")  # Show first 100 characters
    print(f"Predicted Rating: {predicted_rating}")  # The computer's best guess
    print("\nProbability distribution:")  # Show how confident it is for each rating
    for rating, prob in zip(clf.classes_, probabilities):
        print(f"  Rating {rating}: {prob:.4f}")  # prob is between 0 (0%) and 1 (100%)
    
    return predicted_rating  # Return the predicted rating

# === MAIN PROGRAM STARTS HERE ===
# ELI5: This is where the action happens! When you run this file,
# everything below this line will execute in order.

if __name__ == "__main__":
    # Step 1: Train the model
    # ELI5: Teach the computer by showing it thousands of reviews and their ratings
    print("🎓 Starting training process...\n")
    clf, vectorizer = train_naive_bayes_simple()
    
    # Step 2: Test with example reviews
    # ELI5: Now let's try it out! We'll give the computer some NEW reviews 
    # and see what ratings it predicts
    print("\n" + "="*60)
    print("EXAMPLE PREDICTIONS")
    print("="*60)
    
    # Create 3 test reviews: one positive, one negative, one neutral
    examples = [
        "This magazine is absolutely amazing! Great content and very informative.",  # Should predict high rating
        "Terrible magazine, waste of money. Very disappointed.",  # Should predict low rating
        "It's okay, nothing special but decent content."  # Should predict middle rating
    ]
    
    # Loop through each example and make a prediction
    for example in examples:
        predict_rating(clf, vectorizer, example)
        print()  # Empty line for readability
