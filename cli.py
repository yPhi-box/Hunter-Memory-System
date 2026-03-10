"""
CLI for memory system operations.
"""
import sys
from pathlib import Path
from indexer import MemoryIndexer
from search import HybridSearch
from embedder import Embedder
from database import MemoryDatabase
import json


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1]
    
    # Default paths
    db_path = Path(__file__).parent / "memory.db"
    
    if command == "index":
        # Index a directory
        if len(sys.argv) < 3:
            print("Usage: cli.py index <directory> [pattern]")
            return
        
        dir_path = Path(sys.argv[2])
        pattern = sys.argv[3] if len(sys.argv) > 3 else "**/*.md"
        
        indexer = MemoryIndexer(db_path)
        indexer.index_directory(dir_path, pattern, force=False)
        
        stats = indexer.get_stats()
        print(f"\nStats: {stats['total_chunks']} chunks, {stats['total_files']} files, {stats['db_size_mb']:.2f} MB")
        
        indexer.close()
    
    elif command == "reindex":
        # Reindex everything
        if len(sys.argv) < 3:
            print("Usage: cli.py reindex <directory> [pattern]")
            return
        
        dir_path = Path(sys.argv[2])
        pattern = sys.argv[3] if len(sys.argv) > 3 else "**/*.md"
        
        indexer = MemoryIndexer(db_path)
        indexer.index_directory(dir_path, pattern, force=True)
        
        stats = indexer.get_stats()
        print(f"\nStats: {stats['total_chunks']} chunks, {stats['total_files']} files, {stats['db_size_mb']:.2f} MB")
        
        indexer.close()
    
    elif command == "search":
        # Search
        if len(sys.argv) < 3:
            print("Usage: cli.py search <query> [max_results]")
            return
        
        query = sys.argv[2]
        max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        
        db = MemoryDatabase(db_path)
        embedder = Embedder()
        search = HybridSearch(db, embedder)
        
        results = search.search(query, max_results=max_results)
        
        print(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['file_path']}:{result['line_start']}-{result['line_end']}")
            print(f"   Score: {result['combined_score']:.3f} (semantic: {result['semantic_score']:.3f}, keyword: {result['keyword_score']:.3f})")
            print(f"   {result['text'][:200]}...")
            print()
        
        db.close()
    
    elif command == "stats":
        # Show stats
        db = MemoryDatabase(db_path)
        stats = db.get_stats()
        print(json.dumps(stats, indent=2))
        db.close()
    
    elif command == "watch":
        # Watch directories for changes
        if len(sys.argv) < 3:
            print("Usage: cli.py watch <directory1> [directory2 ...]")
            return
        
        watch_paths = sys.argv[2:]
        
        from watcher import start_watcher
        
        start_watcher(watch_paths, db_path=str(db_path))
    
    else:
        print(f"Unknown command: {command}")
        print_usage()


def print_usage():
    """Print usage information."""
    print("""
Memory System CLI

Commands:
  index <dir> [pattern]     - Index directory (default pattern: **/*.md)
  reindex <dir> [pattern]   - Reindex directory (clear + index)
  search <query> [max]      - Search memory (default max: 5)
  stats                     - Show database statistics
  watch <dir1> [dir2 ...]   - Watch directories for changes and auto-reindex

Examples:
  python cli.py index C:\\Hunter\\memory
  python cli.py search "foxx insurance"
  python cli.py watch C:\\Hunter\\memory C:\\Users\\Administrator\\.openclaw\\workspace\\memory
""")


if __name__ == "__main__":
    main()
