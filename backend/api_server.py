from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
from flask_cors import CORS

# --- CONFIGURATION (Must match your setup) ---
ES_HOST = "http://localhost:9200" 
INDEX_NAME = "poems"

# --- FLASK SETUP ---
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- ELASTICSEARCH CONNECTION ---
try:
    es = Elasticsearch(ES_HOST)
    if not es.ping():
         raise ConnectionError(f"Could not connect to Elasticsearch at {ES_HOST}")
    print("API connected successfully to Elasticsearch.")
except Exception as e:
    print(f"Failed to connect to Elasticsearch: {e}")
    es = None # Set to None if connection fails

# --- API ROUTE: /search ---
@app.route('/api/search', methods=['GET'])
def search_poems_api():
    if not es:
        return jsonify({"error": "Backend database connection failed."}), 500

    # 1. Get parameters from the frontend URL
    query_text = request.args.get('q', default='')
    genre_filter = request.args.get('genre', default='')
    
    if not query_text:
        return jsonify({"results": []}) # Return empty if no query

    # 2. Build the Elasticsearch Query Body (Query DSL)
    bool_clauses = {
        "must": [
            {"multi_match": {
                "query": query_text,
                "fields": ["text", "title^2", "author"],
                "fuzziness": "AUTO"
            }}
        ],
        "filter": []
    }
    
    # Add genre filter if provided
    if genre_filter:
        bool_clauses["filter"].append({"term": {"genre": genre_filter}})

    search_body = {
        "query": {"bool": bool_clauses},
        "size": 50
    }

    # 3. Execute Search
    try:
        results = es.search(index=INDEX_NAME, body=search_body)
    except Exception as e:
        return jsonify({"error": f"Search failed: {e}"}), 500

    # 4. Format results for the frontend
    formatted_results = []
    for hit in results['hits']['hits']:
        source = hit['_source']
        formatted_results.append({
            "id": hit['_id'],
            "score": hit['_score'],
            "title": source.get('title'),
            "author": source.get('author'),
            "genre": source.get('genre'),
            "snippet": source.get('text', '')[:300] + '...' # First 300 chars
        })

    # 5. Return JSON response
    return jsonify({
        "total_hits": results['hits']['total']['value'],
        "results": formatted_results
    })

# --- API ROUTE: /poem/<id> ---
@app.route('/api/poem/<poem_id>', methods=['GET'])
def get_single_poem(poem_id):
    """Retrieves a single poem document using its Elasticsearch ID."""
    if not es:
        return jsonify({"error": "Backend database connection failed."}), 500

    try:
        # Use the GET API to fetch a document by its ID
        document = es.get(index=INDEX_NAME, id=poem_id)
        
        # Extract the source data and add the ID to the response
        poem_data = document['_source']
        poem_data['id'] = document['_id']
        
        return jsonify(poem_data)
        
    except Exception as e:
        # 404 error if the ID is not found
        return jsonify({"error": f"Poem not found for ID: {poem_id}"}), 404

if __name__ == '__main__':
    # Flask runs on port 5000 by default.
    # The frontend will call http://localhost:5000/api/search
    app.run(debug=True)