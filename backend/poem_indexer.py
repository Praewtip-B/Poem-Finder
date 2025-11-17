import pandas as pd
from elasticsearch import Elasticsearch, helpers
import pandas as pd

from elasticsearch.helpers import BulkIndexError

# --- CONFIGURATION ---
ES_HOST = "http://localhost:9200" # Using HTTP since security is disabled
INDEX_NAME = "poems"
CSV_FILE = "PoemDataset.csv"
CSV_COLUMNS = ['Title', 'Poem', 'Poet', 'Genre'] 

# --- ELASTICSEARCH MAPPING (Schema) ---
# Defines how Elasticsearch should store and search your data
MAPPING = {
    "properties": {
        "title": {
            "type": "text",
            "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
        },
        "author": { # Maps to the 'Poet' column
            "type": "text",
            "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
        },
        "text": { # Maps to the 'Poem' column (for full-text search)
            "type": "text", 
        },
        "genre": { # Uses 'keyword' for exact filtering/faceting
            "type": "keyword", 
        }
    }
}

def create_index(es_client):
    """Deletes old index and creates a new one with the defined mapping."""
    if es_client.indices.exists(index=INDEX_NAME):
        print(f"Deleting existing index: {INDEX_NAME}")
        es_client.indices.delete(index=INDEX_NAME)

    print(f"Creating new index: {INDEX_NAME}")
    es_client.indices.create(index=INDEX_NAME, mappings=MAPPING)
    print("Index created successfully.")

def dataframe_generator(df):
    """
    Generator function to yield document dictionaries for the bulk helper,
    mapping CSV columns to the ES schema fields.
    """
    for _, row in df.iterrows():
        yield {
            "_index": INDEX_NAME,
            "title": row.get('Title'), 
            "author": row.get('Poet'),  # Mapping 'Poet' CSV column to 'author' ES field
            "text": row.get('Poem'),    # Mapping 'Poem' CSV column to 'text' ES field
            "genre": row.get('Genre')
        }

def ingest_data(es_client):
    """Reads CSV, cleans data, and uses the bulk API to ingest efficiently."""
    print(f"Reading data from {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE, usecols=CSV_COLUMNS)
    except FileNotFoundError:
        print(f"Error: {CSV_FILE} not found. Please ensure it's in the same directory.")
        return

    # --- CRITICAL FIX: Replace NaN with empty strings in required fields ---
    # Missing Titles, Poems, Poets, or Genres should be empty strings, not NaN
    TEXT_FIELDS = ['Title', 'Poem', 'Poet', 'Genre']
    df[TEXT_FIELDS] = df[TEXT_FIELDS].fillna('')

    # Drop rows where 'Poem' or 'Poet' might be empty strings (optional, but safer)
    # The previous code only dropped NaNs, now it's better to check after filling
    # df.dropna(subset=['Poem', 'Poet'], inplace=True) # <-- Use this if you want to skip rows with missing poem/poet data
    
    # We will proceed with the assumption that filling NaN with "" is enough,
    # and if the Poem/Poet is "", it will be indexed as an empty field.

    print(f"Indexing {len(df)} documents...")
    success, errors = helpers.bulk(
        es_client, 
        dataframe_generator(df),
        chunk_size=500,
        max_retries=3,
        request_timeout=60
    )

    print(f"\nBulk indexing complete. Successfully indexed {success} documents.")
    if errors:
        print(f"Encountered {len(errors)} errors during indexing.")

if __name__ == "__main__":
    try:
        es = Elasticsearch(ES_HOST)
        
        if not es.ping():
             raise ConnectionError(f"Could not connect to Elasticsearch at {ES_HOST}")

        print("Successfully connected to Elasticsearch.")
        
        create_index(es)
        ingest_data(es)

        print("\nIndexing process finished. You can now run poem_searcher.py.")

    except BulkIndexError as e:
        # This block catches the failure and prints the detailed error list
        print("\n--- DETAILED INDEXING ERROR ---")
        print(f"Bulk indexing failed for {len(e.errors)} document(s).")
        print("First error detail (copy this for diagnosis):")
        print(e.errors[0])
        print("-------------------------------\n")
        
    except Exception as e:
        # This catches any other unexpected errors
        print(f"An unexpected error occurred: {e}")