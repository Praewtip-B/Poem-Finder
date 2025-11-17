import pandas as pd
from elasticsearch import Elasticsearch

# --- CONFIGURATION ---
ES_HOST = "http://localhost:9200" # Using HTTP since security is disabled
INDEX_NAME = "poems"

def search_poems(es_client, query_text):
    """Performs a multi-field full-text search."""
    search_body = {
        "query": {
            "multi_match": {
                "query": query_text,
                # Boost title hits for better relevance
                "fields": ["text", "title^2", "author"], 
                "fuzziness": "AUTO" # Helps with minor typos
            }
        },
        "size": 5 
    }

    print(f"\n--- Searching for: '{query_text}' ---")
    results = es_client.search(index=INDEX_NAME, body=search_body)
    
    # Print results
    for hit in results['hits']['hits']:
        source = hit['_source']
        print(f"Score: {hit['_score']:.2f} | Title: **{source['title']}** by {source['author']} (Genre: {source['genre']})")


def search_and_filter_by_genre(es_client, query_text, genre_name):
    """Performs a full-text search filtered by an exact genre."""
    search_body = {
        "query": {
            "bool": {
                "must": [
                    # Full-text match on the query
                    {"multi_match": {
                        "query": query_text,
                        "fields": ["text", "title"]
                    }}
                ],
                "filter": [
                    # Exact match filter on the 'genre' keyword field
                    {"term": {"genre": genre_name}} 
                ]
            }
        },
        "size": 5
    }

    print(f"\n--- Searching for '{query_text}' FILTERED by Genre: '{genre_name}' ---")
    results = es_client.search(index=INDEX_NAME, body=search_body)
    
    print(f"Found {results['hits']['total']['value']} poems matching both criteria.")
    for hit in results['hits']['hits']:
        source = hit['_source']
        print(f"Score: {hit['_score']:.2f} | Title: **{source['title']}** by {source['author']} (Genre: {source['genre']})")



if __name__ == "__main__":
    try:
        # --- SIMPLE INSECURE CONNECTION ---
        es = Elasticsearch(ES_HOST)
        
        if not es.ping():
             raise ConnectionError(f"Could not connect to Elasticsearch at {ES_HOST}")
        
        print("Successfully connected to Elasticsearch. Running search examples...")

        # Example 1: Full-text search
        search_poems(es, "silent night and green moss")

        # Example 2: Search for a phrase, restricted to a specific genre
        
        search_and_filter_by_genre(es, "darkness", "Fear") 

    except Exception as e:
        print(f"An error occurred: {e}")