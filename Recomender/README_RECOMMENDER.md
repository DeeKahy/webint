# Naive Bayes Recommender System - Getting Started Guide

## Overview
This is a simple implementation of a Naive Bayes classifier for predicting user ratings based on product features.

## Quick Start

### 1. Install required packages
```bash
pip install pandas numpy scikit-learn
```

### 2. Run the basic implementation
```bash
python3 naive_bayes_recommender.py
```

## Implementation Approaches

### Simple Version (Current Implementation)
- **Features**: Bag-of-words from review text and summary
- **Target**: Rating (1-5 stars)
- **Algorithm**: Multinomial Naive Bayes
- **Pros**: Very simple, easy to understand, works reasonably well
- **Cons**: Only uses text, ignores other product features

### How It Works

1. **Load Data**: Reads the JSON.gz file containing reviews
2. **Feature Extraction**: Converts review text into numerical features using bag-of-words
3. **Train/Test Split**: 80% training, 20% testing
4. **Train Model**: Fits a Multinomial Naive Bayes classifier
5. **Evaluate**: Shows accuracy and mean absolute error

### Next Steps to Improve

You can enhance the model by:

1. **Add Product Features**:
   - Verified purchase status
   - Review length
   - Time of review
   - Product ID (as categorical feature)

2. **Better Text Features**:
   - TF-IDF instead of simple counts
   - N-grams (bigrams, trigrams)
   - Sentiment scores

3. **Advanced Models**:
   - Try Gaussian Naive Bayes for continuous features
   - Combine multiple feature types
   - Use ensemble methods

## Data Structure

The dataset contains:
- `overall`: Rating (1.0 - 5.0)
- `reviewText`: Full review text
- `summary`: Review summary/title
- `reviewerID`: User ID
- `asin`: Product ID
- `verified`: Whether purchase was verified
- `reviewTime`: Date of review
- `unixReviewTime`: Unix timestamp

## Example Usage

```python
from naive_bayes_recommender import train_naive_bayes_simple, predict_rating

# Train the model
clf, vectorizer = train_naive_bayes_simple()

# Predict a new review
review = "Great magazine with excellent articles!"
predicted_rating = predict_rating(clf, vectorizer, review)
```

## Performance Expectations

For this simple text-based approach:
- **Accuracy**: ~40-60% (exact rating prediction is hard!)
- **MAE**: ~0.5-1.0 (within 1 star on average)

Note: Rating prediction is challenging because ratings are subjective and text alone may not capture all factors.
