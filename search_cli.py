"""
CLI tool for memory search - can be called from OpenClaw via exec.
Returns JSON for easy parsing.
"""

import sys
import json
from pathlib import Path
from indexer import MemoryIndexer


def search(query: str, limit: int = 10):
    """
    Search memory and return results as JSON.
    
    Args:
        query: Search query
        limit: Max results
    """
    # Suppress model loading messages
    import warnings
    warnings.filterwarnings('ignore')
    
    indexer = MemoryIndexer()
    results = indexer.search(query, limit=limit)
    indexer.close()
    
    # Format for JSON output
    output = {
        'query': query,
        'count': len(results),
        'results': []
    }
    
    for result in results:
        output['results'].append({
            'file_path': result['file_path'],
            'file_name': result['file_name'],
            'chunk_index': result['chunk_index'],
            'text': result['text'],
            'similarity': round(result['similarity'], 3),
            'word_count': result['word_count']
        })
    
    return output


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Usage: python search_cli.py "query" [limit]'
        }))
        sys.exit(1)
    
    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    try:
        result = search(query, limit)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            'error': str(e)
        }))
        sys.exit(1)
