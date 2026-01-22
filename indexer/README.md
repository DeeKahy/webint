# Search Engine Indexer

A basic boolean search engine with inverted index for the web crawler project.

## Overview

This indexer builds an inverted index from the crawled web pages and provides boolean query capabilities (AND/OR operations).

## Components

### 1. `preprocessing.py`
Text preprocessing and tokenization:
- **Lowercase normalization**: All text converted to lowercase
- **Punctuation removal**: Non-alphanumeric characters removed
- **Stopword filtering**: Common words (a, the, is, etc.) removed
- **Length filtering**: Tokens < 2 characters removed

**Corner cut**: Basic stopword list (24 words). A production system would use a comprehensive list (200+ words).

### 2. `build_index.py`
Inverted index construction:
- **Data structure**: `term -> set(document_ids)`
- **Document store**: Metadata (URL, title, content snippet)
- **Persistence**: Pickle-based serialization for fast load/save

**Corner cut**: 
- No stemming/lemmatization (e.g., "running" and "run" are different terms)
- No term frequency tracking (can't do TF-IDF ranking)
- Stores only first 500 chars of content as snippet

### 3. `search.py`
Interactive CLI search interface:
- **Single term**: Returns all documents containing the term
- **AND query**: "python programming" or "python AND programming"
- **OR query**: "python OR java"

**Corner cut**:
- No phrase queries (can't search "exact phrase")
- No NOT operator
- No wildcards or fuzzy matching
- No ranking (results are unordered)

## Usage

### Build the Index
```bash
cd indexer
python3 build_index.py
```

This reads all JSON files from `data/processed/` and creates `inverted_index.pkl`.

### Search
```bash
python3 search.py
```

Interactive prompt:
```
Search> aalborg university
Query type: AND
Terms: ['aalborg', 'university']

Found 57 documents:
...

Search> python OR java
Query type: OR
Terms: ['python', 'java']

Found 20 documents:
...
```

### Run Tests
```bash
python3 test_search.py
```

## Statistics

- **Documents indexed**: 832 pages
- **Unique terms**: 150,622 terms
- **Index size**: ~15 MB (pickle file)

## Corners Cut & Implications

### What We Did:
✅ Inverted index with term → doc_id mapping  
✅ Basic text normalization (lowercase, punctuation removal)  
✅ Stopword filtering  
✅ Boolean AND/OR queries  
✅ Fast lookups using set operations  

### What We Didn't Do (Corners Cut):

1. **No Stemming/Lemmatization**
   - Implication: "run", "running", "runs" are treated as different words
   - Impact: Reduced recall (miss relevant documents)
   - Why: Time constraint; would need NLTK/spaCy

2. **No Term Frequency (TF-IDF)**
   - Implication: Can't rank results by relevance
   - Impact: Results are unordered; users must scan all results
   - Why: Requires storing term frequencies per document

3. **Basic Stopword List**
   - Implication: Some common words still indexed (e.g., "also", "just")
   - Impact: Slightly larger index, minor noise
   - Why: Kept it simple with 24 core stopwords

4. **No Phrase Queries**
   - Implication: Can't search for exact phrases like "machine learning"
   - Impact: Less precise queries
   - Why: Would need positional index (term → [(doc_id, position), ...])

5. **No Query Operators** (NOT, wildcards, fuzzy)
   - Implication: Limited query expressiveness
   - Impact: Can't exclude terms or handle typos
   - Why: Time constraint

6. **Simple Pickle Persistence**
   - Implication: Index loaded fully into memory
   - Impact: Won't scale to millions of documents
   - Why: Quick and simple; production would use DB (SQLite/Elasticsearch)

## Performance

- **Index build time**: ~5 seconds for 832 documents
- **Query time**: <1ms for most queries (in-memory set operations)
- **Memory usage**: ~20 MB (index + documents in RAM)

## Future Improvements

For production/larger scale:
1. Add stemming (Porter stemmer)
2. Implement TF-IDF ranking
3. Add positional index for phrase queries
4. Use database (SQLite/PostgreSQL) instead of pickle
5. Add caching for frequent queries
6. Implement query expansion (synonyms)
