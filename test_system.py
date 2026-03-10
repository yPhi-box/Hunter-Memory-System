"""
Test script to verify memory system works correctly.
"""
from pathlib import Path
from chunker import Chunker
from embedder import Embedder
from database import MemoryDatabase
from search import HybridSearch
import tempfile
import shutil


def test_chunker():
    """Test chunking."""
    print("\n=== Testing Chunker ===")
    
    # Create test file
    test_dir = Path(tempfile.mkdtemp())
    test_file = test_dir / "test.md"
    test_file.write_text("# Test\n\n" + "This is a test line.\n" * 100)
    
    chunker = Chunker(chunk_size=200, overlap=20)
    chunks = chunker.chunk_file(test_file)
    
    print(f"âœ“ Created {len(chunks)} chunks")
    print(f"âœ“ First chunk: {len(chunks[0]['text'])} chars")
    print(f"âœ“ Lines: {chunks[0]['line_start']}-{chunks[0]['line_end']}")
    
    # Cleanup
    shutil.rmtree(test_dir)
    
    return True


def test_embedder():
    """Test embedding generation."""
    print("\n=== Testing Embedder ===")
    
    embedder = Embedder()
    
    # Test single embedding
    text = "This is a test"
    embedding = embedder.embed(text)
    
    print(f"âœ“ Model: {embedder.model_name}")
    print(f"âœ“ Dimension: {embedder.dimension}")
    print(f"âœ“ Embedding shape: {embedding.shape}")
    
    # Test batch
    texts = ["Test 1", "Test 2", "Test 3"]
    embeddings = embedder.embed_batch(texts)
    
    print(f"âœ“ Batch embeddings: {len(embeddings)}")
    
    return True


def test_database():
    """Test database operations."""
    print("\n=== Testing Database ===")
    
    # Create test database
    test_db_path = Path(tempfile.mkdtemp()) / "test.db"
    db = MemoryDatabase(test_db_path)
    
    # Add test chunks
    chunk = {
        'file_path': 'test.md',
        'line_start': 1,
        'line_end': 10,
        'text': 'This is a test chunk about Foxx Insurance and FR44.',
        'chars': 50
    }
    
    embedder = Embedder()
    embedding = embedder.embed(chunk['text']).tolist()
    
    chunk_id = db.add_chunk(chunk, embedding)
    print(f"âœ“ Added chunk: {chunk_id}")
    
    # Test semantic search
    query_embedding = embedder.embed("Foxx Insurance").tolist()
    results = db.search_semantic(query_embedding, limit=5)
    
    print(f"âœ“ Semantic search: {len(results)} results")
    if results:
        print(f"  - Score: {results[0]['score']:.3f}")
    
    # Test keyword search
    results = db.search_keyword("Foxx", limit=5)
    
    print(f"âœ“ Keyword search: {len(results)} results")
    
    # Test stats
    stats = db.get_stats()
    print(f"âœ“ Stats: {stats}")
    
    # Cleanup
    db.close()
    shutil.rmtree(test_db_path.parent)
    
    return True


def test_hybrid_search():
    """Test hybrid search."""
    print("\n=== Testing Hybrid Search ===")
    
    # Create test database
    test_db_path = Path(tempfile.mkdtemp()) / "test.db"
    db = MemoryDatabase(test_db_path)
    embedder = Embedder()
    
    # Add test data
    test_chunks = [
        "Foxx Insurance provides FR44 insurance in Florida.",
        "SR22 insurance is required for DUI in some states.",
        "Auto insurance rates vary by state and driving history.",
        "High-risk drivers need specialized insurance coverage.",
        "Naples Florida office serves Southwest Florida region."
    ]
    
    for i, text in enumerate(test_chunks):
        chunk = {
            'file_path': 'test.md',
            'line_start': i * 10 + 1,
            'line_end': i * 10 + 10,
            'text': text,
            'chars': len(text)
        }
        embedding = embedder.embed(text).tolist()
        db.add_chunk(chunk, embedding)
    
    print(f"âœ“ Added {len(test_chunks)} test chunks")
    
    # Test search
    search = HybridSearch(db, embedder)
    results = search.search("Florida insurance", max_results=3)
    
    print(f"âœ“ Search results: {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"  {i}. Score: {result['combined_score']:.3f}")
        print(f"     {result['text'][:60]}...")
    
    # Cleanup
    db.close()
    shutil.rmtree(test_db_path.parent)
    
    return True


def main():
    """Run all tests."""
    print("Testing Hunter Memory System")
    print("=" * 50)
    
    try:
        test_chunker()
        test_embedder()
        test_database()
        test_hybrid_search()
        
        print("\n" + "=" * 50)
        print("âœ“ All tests passed!")
        print("\nMemory system is working correctly.")
        print("\nNext steps:")
        print("1. Index your memory files: python cli.py index C:\\Hunter\\memory")
        print("2. Test search: python cli.py search 'your query'")
        print("3. Start server: python server.py")
        
        return True
    
    except Exception as e:
        print(f"\nâœ— Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

