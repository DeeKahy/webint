"""
Build inverted index from processed web pages.
"""
import json
import os
import pickle
from collections import defaultdict
from preprocessing import tokenize


class InvertedIndex:
    """
    Inverted index data structure.
    
    Maps: term -> set of document IDs containing that term
    Also stores document metadata (URL, title)
    """
    
    def __init__(self):
        self.index = defaultdict(set)  # term -> set of doc_ids
        self.documents = {}  # doc_id -> {'url': ..., 'title': ..., 'content': ...}
        self.doc_count = 0
        
    def add_document(self, doc_id, url, title, content):
        """Add a document to the index."""
        # Store document metadata
        self.documents[doc_id] = {
            'url': url,
            'title': title,
            'content': content[:500]  # Store first 500 chars as snippet
        }
        
        # Tokenize and index the content
        tokens = tokenize(content)
        
        # Add each unique token to the index
        for token in set(tokens):  # Use set to avoid duplicates
            self.index[token].add(doc_id)
        
        self.doc_count += 1
        
    def search(self, term):
        """Search for a single term."""
        term = term.lower()
        return self.index.get(term, set())
    
    def search_and(self, terms):
        """Boolean AND: Return documents containing ALL terms."""
        if not terms:
            return set()
        
        # Start with documents containing the first term
        result = self.search(terms[0])
        
        # Intersect with documents containing each subsequent term
        for term in terms[1:]:
            result = result & self.search(term)
        
        return result
    
    def search_or(self, terms):
        """Boolean OR: Return documents containing ANY term."""
        result = set()
        for term in terms:
            result = result | self.search(term)
        return result
    
    def get_document(self, doc_id):
        """Retrieve document metadata by ID."""
        return self.documents.get(doc_id)
    
    def save(self, filepath):
        """Save index to disk."""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'index': dict(self.index),  # Convert defaultdict to dict
                'documents': self.documents,
                'doc_count': self.doc_count
            }, f)
        print(f"Index saved to {filepath}")
        
    def load(self, filepath):
        """Load index from disk."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.index = defaultdict(set, data['index'])
            self.documents = data['documents']
            self.doc_count = data['doc_count']
        print(f"Index loaded from {filepath}")
        
    def get_stats(self):
        """Get index statistics."""
        return {
            'num_documents': self.doc_count,
            'num_unique_terms': len(self.index),
            'avg_terms_per_doc': sum(len(docs) for docs in self.index.values()) / self.doc_count if self.doc_count > 0 else 0
        }


def build_index_from_json(data_dir):
    """
    Build inverted index from JSON files in the data directory.
    
    Args:
        data_dir: Path to directory containing page_*.json files
        
    Returns:
        InvertedIndex object
    """
    index = InvertedIndex()
    
    # Get all JSON files
    json_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json')])
    
    print(f"Building index from {len(json_files)} documents...")
    
    for i, filename in enumerate(json_files):
        filepath = os.path.join(data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract document ID from filename (e.g., page_1.json -> 1)
            doc_id = int(filename.replace('page_', '').replace('.json', ''))
            
            # Add to index
            index.add_document(
                doc_id=doc_id,
                url=data.get('url', ''),
                title=data.get('title', ''),
                content=data.get('content', '')
            )
            
            if (i + 1) % 100 == 0:
                print(f"Indexed {i + 1}/{len(json_files)} documents...")
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    print(f"\nIndexing complete!")
    stats = index.get_stats()
    print(f"Documents: {stats['num_documents']}")
    print(f"Unique terms: {stats['num_unique_terms']}")
    
    return index


if __name__ == '__main__':
    # Build index from processed data
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
    index = build_index_from_json(data_dir)
    
    # Save index
    index_dir = os.path.dirname(__file__)
    index_file = os.path.join(index_dir, 'inverted_index.pkl')
    index.save(index_file)
