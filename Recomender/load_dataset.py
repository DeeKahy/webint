import pandas as pd
import json
import gzip
import os

def load_csv_data(filepath):
    """Load CSV dataset."""
    try:
        df = pd.read_csv(filepath)
        print(f"Loaded CSV: {filepath}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def load_json_gz_data(filepath):
    """Load compressed JSON dataset (JSON Lines format)."""
    try:
        data = []
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    data.append(json.loads(line))
        print(f"Loaded JSON.gz: {filepath}")
        print(f"Number of records: {len(data)}")
        return data
    except Exception as e:
        print(f"Error loading JSON.gz: {e}")
        return None

def main():
    # Get the dataset directory path
    dataset_dir = os.path.join(os.path.dirname(__file__), 'Dataset')
    
    # Load CSV file
    csv_file = os.path.join(dataset_dir, 'Books.csv')
    csv_data = load_csv_data(csv_file)
    
    if csv_data is not None:
        print("\n--- CSV Data Preview ---")
        print(csv_data.head())
    
    print("\n" + "="*50 + "\n")
    
    # Load JSON.gz file
    json_file = os.path.join(dataset_dir, 'Books_5.json.gz')
    json_data = load_json_gz_data(json_file)
    
    if json_data is not None:
        print("\n--- JSON Data Preview ---")
        if isinstance(json_data, list) and len(json_data) > 0:
            print(f"First record: {json_data[0]}")
        elif isinstance(json_data, dict):
            print(f"Keys: {list(json_data.keys())}")
    
    return csv_data, json_data

if __name__ == "__main__":
    csv_data, json_data = main()
