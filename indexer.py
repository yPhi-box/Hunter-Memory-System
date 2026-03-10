"""
Main indexer that coordinates chunking, embedding, and database operations.
"""
from pathlib import Path
from typing import List
from chunker import Chunker
from embedder import Embedder
from database import MemoryDatabase
from tqdm import tqdm


class MemoryIndexer:
    """Coordinate indexing operations."""
    
    def __init__(self, db_path: Path, model_name: str = None):
        """
        Initialize indexer.
        
        Args:
            db_path: Path to database
            model_name: Embedding model name (optional)
        """
        self.db = MemoryDatabase(db_path)
        self.embedder = Embedder(model_name)
        self.chunker = Chunker(chunk_size=500, overlap=50)
    
    def index_file(self, file_path: Path, force: bool = False):
        """
        Index a single file.
        
        Args:
            file_path: Path to file
            force: Force reindex even if already indexed
        """
        print(f"Indexing: {file_path}")
        
        # Clear existing chunks if force
        if force:
            self.db.clear_file(str(file_path))
        
        # Chunk file
        chunks = self.chunker.chunk_file(file_path)
        
        if not chunks:
            print(f"  No chunks generated")
            return
        
        # Generate embeddings
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedder.embed_batch(texts)
        
        # Store in database
        self.db.add_chunks_batch(chunks, embeddings)
        
        print(f"  Indexed {len(chunks)} chunks")
    
    def index_directory(self, dir_path: Path, pattern: str = "**/*.md", force: bool = False):
        """
        Index all files in a directory.
        
        Args:
            dir_path: Directory to scan
            pattern: Glob pattern for files
            force: Force reindex all files
        """
        files = list(dir_path.glob(pattern))
        print(f"Found {len(files)} files to index")
        
        for file_path in tqdm(files, desc="Indexing"):
            try:
                self.index_file(file_path, force=force)
            except Exception as e:
                print(f"Error indexing {file_path}: {e}")
    
    def reindex_file(self, file_path: Path):
        """
        Reindex a file (clear + index).
        
        Args:
            file_path: Path to file
        """
        print(f"Reindexing: {file_path}")
        self.db.clear_file(str(file_path))
        self.index_file(file_path, force=False)
    
    def remove_file(self, file_path: Path):
        """
        Remove a file from the index.
        
        Args:
            file_path: Path to file
        """
        print(f"Removing: {file_path}")
        self.db.clear_file(str(file_path))
    
    def get_stats(self):
        """Get indexing statistics."""
        return self.db.get_stats()
    
    def close(self):
        """Close database connection."""
        self.db.close()
