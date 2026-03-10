#!/usr/bin/env python3
"""
Remote test script for Argus to test memory system from his VM.
"""
import requests
import json
import sys

SERVER_URL = "http://192.168.1.52:8765"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{SERVER_URL}/health")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    return response.status_code == 200

def test_stats():
    """Test stats endpoint."""
    print("\nTesting stats endpoint...")
    response = requests.get(f"{SERVER_URL}/stats")
    print(f"  Status: {response.status_code}")
    stats = response.json()
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Total files: {stats['total_files']}")
    print(f"  DB size: {stats['db_size_mb']:.2f} MB")
    return response.status_code == 200

def test_search(query, max_results=3):
    """Test search endpoint."""
    print(f"\nSearching for: '{query}'")
    response = requests.post(
        f"{SERVER_URL}/search",
        json={
            "query": query,
            "max_results": max_results,
            "min_score": 0.0
        }
    )
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"  Found: {results['total']} results")
        
        for i, result in enumerate(results['results'], 1):
            filename = result['file_path'].split('/')[-1]
            print(f"\n  [{i}] {filename}:{result['line_start']}")
            print(f"      Score: {result['score']:.3f} (sem: {result['semantic_score']:.3f}, kw: {result['keyword_score']:.3f})")
            preview = result['text'][:100].replace('\n', ' ')
            print(f"      Preview: {preview}...")
        
        return True
    else:
        print(f"  Error: {response.text}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Hunter Memory System - Remote Test (from Argus)")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test health
    tests_total += 1
    if test_health():
        tests_passed += 1
    
    # Test stats
    tests_total += 1
    if test_stats():
        tests_passed += 1
    
    # Test searches
    test_queries = [
        "Foxx Insurance Florida",
        "Argus monitoring Hunter",
        "WordPress login credentials",
        "SEO backlinks strategy"
    ]
    
    for query in test_queries:
        tests_total += 1
        if test_search(query, max_results=2):
            tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("\nAll tests PASSED! Memory system working from remote VM.")
        return 0
    else:
        print(f"\nSome tests FAILED ({tests_total - tests_passed} failures)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
