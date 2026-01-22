"""
Command-line search interface for the inverted index.

Usage:
    python search.py <query>
    
Query syntax:
    - Single word: "python"
    - Multiple words (AND): "python programming"
    - OR query: "python OR java"
    - Explicit AND: "python AND programming"
"""
import sys
import os
from build_index import InvertedIndex


def parse_query(query_string):
    """
    Parse query string and determine query type.
    
    Returns:
        (query_type, terms) where query_type is 'AND' or 'OR'
    """
    query_string = query_string.strip()
    
    # Check for explicit OR
    if ' OR ' in query_string.upper():
        terms = [term.strip().lower() for term in query_string.upper().split(' OR ')]
        return 'OR', terms
    
    # Check for explicit AND
    if ' AND ' in query_string.upper():
        terms = [term.strip().lower() for term in query_string.upper().split(' AND ')]
        return 'AND', terms
    
    # Default: multiple words are treated as AND
    terms = query_string.lower().split()
    if len(terms) > 1:
        return 'AND', terms
    else:
        return 'SINGLE', terms


def display_results(index, doc_ids, max_results=10):
    """Display search results."""
    if not doc_ids:
        print("\nNo results found.")
        return
    
    print(f"\nFound {len(doc_ids)} documents:")
    print("=" * 80)
    
    for i, doc_id in enumerate(sorted(doc_ids)[:max_results]):
        doc = index.get_document(doc_id)
        if doc:
            print(f"\n{i+1}. [Doc {doc_id}] {doc['title']}")
            print(f"   URL: {doc['url']}")
            print(f"   Snippet: {doc['content'][:150]}...")
    
    if len(doc_ids) > max_results:
        print(f"\n... and {len(doc_ids) - max_results} more results.")


def main():
    # Check if index exists
    index_file = os.path.join(os.path.dirname(__file__), 'inverted_index.pkl')
    
    if not os.path.exists(index_file):
        print("Error: Index not found!")
        print("Please run 'python build_index.py' first to build the index.")
        sys.exit(1)
    
    # Load index
    print("Loading index...")
    index = InvertedIndex()
    index.load(index_file)
    
    stats = index.get_stats()
    print(f"Loaded index with {stats['num_documents']} documents and {stats['num_unique_terms']} unique terms.")
    print("\nSearch syntax:")
    print("  - Single word: 'python'")
    print("  - AND query (all words): 'python programming'")
    print("  - OR query (any word): 'python OR java'")
    print("  - Type 'quit' or 'exit' to quit\n")
    
    # Interactive search loop
    while True:
        try:
            query = input("Search> ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            # Parse and execute query
            query_type, terms = parse_query(query)
            
            print(f"\nQuery type: {query_type}")
            print(f"Terms: {terms}")
            
            if query_type == 'SINGLE':
                results = index.search(terms[0])
            elif query_type == 'AND':
                results = index.search_and(terms)
            elif query_type == 'OR':
                results = index.search_or(terms)
            else:
                results = set()
            
            display_results(index, results)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    main()
