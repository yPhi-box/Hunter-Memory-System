"""
SQLite database with vector search using sqlite-vec.
Single file, portable, fast.
"""
import sqlite3
import sqlite_vec
import json
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from datetime import datetime


class MemoryDatabase:
    """SQLite database with vector search capabilities."""
    
    def __init__(self, db_path: Path):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        self._init_schema()
    
    def _init_schema(self):
        """Create tables if they don't exist."""
        self.conn.executescript("""
            -- Main chunks table
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                line_start INTEGER NOT NULL,
                line_end INTEGER NOT NULL,
                text TEXT NOT NULL,
                chars INTEGER NOT NULL,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_modified_at TIMESTAMP,
                metadata TEXT
            );
            
            -- Create index on file_path for fast lookups
            CREATE INDEX IF NOT EXISTS idx_file_path ON chunks(file_path);
            
            -- Create full-text search index for keyword search
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                text,
                content=chunks,
                content_rowid=id
            );
            
            -- Triggers to keep FTS in sync
            CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
                INSERT INTO chunks_fts(rowid, text) VALUES (new.id, new.text);
            END;
            
            CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
                DELETE FROM chunks_fts WHERE rowid = old.id;
            END;
            
            CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
                UPDATE chunks_fts SET text = new.text WHERE rowid = new.id;
            END;
            
            -- Vector table for semantic search
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0(
                chunk_id INTEGER PRIMARY KEY,
                embedding FLOAT[384]
            );
        """)
        self.conn.commit()
    
    def add_chunk(self, chunk: Dict, embedding: List[float]):
        """
        Add a chunk with its embedding.
        
        Args:
            chunk: Chunk dict with text, file_path, line_start, line_end, etc.
            embedding: Embedding vector
        """
        cursor = self.conn.cursor()
        
        # Insert chunk
        cursor.execute("""
            INSERT INTO chunks (file_path, line_start, line_end, text, chars, file_modified_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            chunk['file_path'],
            chunk['line_start'],
            chunk['line_end'],
            chunk['text'],
            chunk['chars'],
            datetime.now().isoformat(),
            json.dumps(chunk.get('metadata', {}))
        ))
        
        chunk_id = cursor.lastrowid
        
        # Insert embedding
        cursor.execute("""
            INSERT INTO vec_chunks (chunk_id, embedding)
            VALUES (?, ?)
        """, (chunk_id, json.dumps(embedding)))
        
        self.conn.commit()
        return chunk_id
    
    def add_chunks_batch(self, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Add multiple chunks efficiently.
        
        Args:
            chunks: List of chunk dicts
            embeddings: List of embedding vectors
        """
        cursor = self.conn.cursor()
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = self.add_chunk(chunk, embedding)
    
    def search_semantic(self, query_embedding: List[float], limit: int = 10) -> List[Dict]:
        """
        Semantic search using vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            limit: Max results
            
        Returns:
            List of matching chunks with scores
        """
        cursor = self.conn.cursor()
        
        # Vector search using sqlite-vec
        results = cursor.execute("""
            SELECT 
                c.id,
                c.file_path,
                c.line_start,
                c.line_end,
                c.text,
                c.indexed_at,
                vec_distance_cosine(v.embedding, ?) as distance
            FROM vec_chunks v
            JOIN chunks c ON v.chunk_id = c.id
            ORDER BY distance ASC
            LIMIT ?
        """, (json.dumps(query_embedding), limit)).fetchall()
        
        chunks = []
        for row in results:
            chunks.append({
                'id': row[0],
                'file_path': row[1],
                'line_start': row[2],
                'line_end': row[3],
                'text': row[4],
                'indexed_at': row[5],
                'score': 1.0 - row[6]  # Convert distance to similarity
            })
        
        return chunks
    
    def search_keyword(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Keyword search using FTS5.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of matching chunks with scores
        """
        cursor = self.conn.cursor()
        
        results = cursor.execute("""
            SELECT 
                c.id,
                c.file_path,
                c.line_start,
                c.line_end,
                c.text,
                c.indexed_at,
                fts.rank
            FROM chunks_fts fts
            JOIN chunks c ON fts.rowid = c.id
            WHERE chunks_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit)).fetchall()
        
        chunks = []
        for row in results:
            chunks.append({
                'id': row[0],
                'file_path': row[1],
                'line_start': row[2],
                'line_end': row[3],
                'text': row[4],
                'indexed_at': row[5],
                'score': -row[6]  # FTS rank is negative, convert to positive
            })
        
        return chunks
    
    def clear_file(self, file_path: str):
        """
        Remove all chunks for a file.
        
        Args:
            file_path: Path to file
        """
        cursor = self.conn.cursor()
        
        # Get chunk IDs
        chunk_ids = cursor.execute(
            "SELECT id FROM chunks WHERE file_path = ?",
            (file_path,)
        ).fetchall()
        
        # Delete vectors
        for (chunk_id,) in chunk_ids:
            cursor.execute("DELETE FROM vec_chunks WHERE chunk_id = ?", (chunk_id,))
        
        # Delete chunks (FTS will auto-update via triggers)
        cursor.execute("DELETE FROM chunks WHERE file_path = ?", (file_path,))
        
        self.conn.commit()
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        total_chunks = cursor.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        total_files = cursor.execute("SELECT COUNT(DISTINCT file_path) FROM chunks").fetchone()[0]
        db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
        
        return {
            'total_chunks': total_chunks,
            'total_files': total_files,
            'db_size_mb': db_size / 1024 / 1024
        }
    
    def close(self):
        """Close database connection."""
        self.conn.close()
