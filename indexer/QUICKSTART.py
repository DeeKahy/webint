"""
Quick Start Guide for the Search Engine
"""

# ============================================
# QUICK START
# ============================================

# 1. Build the index (one time only, or when data changes)
cd indexer
python3 build_index.py

# 2. Run the search interface
python3 search.py

# 3. Try some queries:
#    - Single word: university
#    - AND query: aalborg university
#    - OR query: python OR java

# 4. Run tests
python3 test_search.py

# ============================================
# WHAT WAS IMPLEMENTED
# ============================================

✓ Inverted index (term -> document IDs)
✓ Text preprocessing:
  - Lowercase normalization
  - Punctuation removal  
  - Stopword filtering (24 common words)
  - Short token filtering (< 2 chars)
✓ Boolean queries:
  - Single term search
  - AND query (all terms must match)
  - OR query (any term can match)
✓ Interactive CLI
✓ Fast in-memory search using set operations

# ============================================
# CORNERS CUT & WHY
# ============================================

❌ No stemming/lemmatization
   → Would need NLTK/spaCy, adds complexity
   → Impact: "run" and "running" treated as different
   
❌ No TF-IDF ranking
   → Would need to store term frequencies
   → Impact: Results are unordered
   
❌ No phrase queries  
   → Would need positional index
   → Impact: Can't search "machine learning" as exact phrase
   
❌ Simple stopword list (24 words)
   → Full list would be 200+ words
   → Impact: Minor - some common words still indexed
   
❌ Pickle persistence (not database)
   → Quick to implement
   → Impact: Doesn't scale to millions of docs

# ============================================
# STATISTICS
# ============================================

Documents indexed: 832
Unique terms: 150,622
Index file size: ~15 MB
Build time: ~5 seconds
Query time: <1ms (in-memory)

# ============================================
# EXAMPLE USAGE
# ============================================

"""
$ python3 search.py

Search> aalborg university
Query type: AND
Terms: ['aalborg', 'university']
Found 57 documents:

1. [Doc 4] Privacy and cookie policy - Aalborg University
   URL: https://www.en.aau.dk/privacy-policy-cookies/
   ...

Search> python OR java  
Query type: OR
Terms: ['python', 'java']
Found 20 documents:
...
"""
