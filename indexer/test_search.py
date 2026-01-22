"""
Test script for the search engine.
"""
from build_index import InvertedIndex
import os


def run_test_queries():
    # Load index
    index_file = os.path.join(os.path.dirname(__file__), 'inverted_index.pkl')
    index = InvertedIndex()
    index.load(index_file)
    
    print("=" * 80)
    print("TEST QUERIES")
    print("=" * 80)
    
    # Test 1: Single word query
    print("\n1. Single word query: 'university'")
    results = index.search('university')
    print(f"   Results: {len(results)} documents")
    if results:
        doc_id = list(results)[0]
        doc = index.get_document(doc_id)
        print(f"   Sample: [{doc_id}] {doc['title'][:60]}...")
    
    # Test 2: AND query
    print("\n2. AND query: 'aalborg' AND 'university'")
    results = index.search_and(['aalborg', 'university'])
    print(f"   Results: {len(results)} documents")
    if results:
        doc_id = list(results)[0]
        doc = index.get_document(doc_id)
        print(f"   Sample: [{doc_id}] {doc['title'][:60]}...")
    
    # Test 3: OR query
    print("\n3. OR query: 'python' OR 'java'")
    results = index.search_or(['python', 'java'])
    print(f"   Results: {len(results)} documents")
    
    # Test 4: Specific topic
    print("\n4. Topic search: 'data' AND 'science'")
    results = index.search_and(['data', 'science'])
    print(f"   Results: {len(results)} documents")
    
    # Test 5: No results
    print("\n5. Query with no results: 'xyzabc123'")
    results = index.search('xyzabc123')
    print(f"   Results: {len(results)} documents")
    
    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)


if __name__ == '__main__':
    run_test_queries()
