"""
Text chunking logic for memory system.
Handles markdown-aware splitting with overlap.
"""
from pathlib import Path
from typing import List, Dict
import re


class Chunker:
    """Smart text chunker with markdown awareness."""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target characters per chunk
            overlap: Characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_file(self, file_path: Path) -> List[Dict]:
        """
        Chunk a file into overlapping segments.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of dicts with text, line_start, line_end, metadata
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        
        chunks = []
        current_chunk = []
        current_chars = 0
        start_line = 1
        
        for i, line in enumerate(lines, start=1):
            line_len = len(line)
            
            # If adding this line would exceed chunk_size, save current chunk
            if current_chars + line_len > self.chunk_size and current_chunk:
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'line_start': start_line,
                    'line_end': i - 1,
                    'file_path': str(file_path),
                    'chars': current_chars
                })
                
                # Start new chunk with overlap
                overlap_lines = self._get_overlap_lines(current_chunk)
                current_chunk = overlap_lines
                current_chars = sum(len(l) for l in overlap_lines)
                start_line = i - len(overlap_lines)
            
            current_chunk.append(line)
            current_chars += line_len
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'line_start': start_line,
                'line_end': len(lines),
                'file_path': str(file_path),
                'chars': current_chars
            })
        
        return chunks
    
    def _get_overlap_lines(self, lines: List[str]) -> List[str]:
        """Get last N lines for overlap, respecting markdown structure."""
        overlap_chars = 0
        overlap_lines = []
        
        # Work backwards from end
        for line in reversed(lines):
            if overlap_chars + len(line) > self.overlap:
                break
            overlap_lines.insert(0, line)
            overlap_chars += len(line)
        
        return overlap_lines
    
    def chunk_directory(self, dir_path: Path, pattern: str = "**/*.md") -> List[Dict]:
        """
        Chunk all files in a directory matching pattern.
        
        Args:
            dir_path: Directory to scan
            pattern: Glob pattern for files
            
        Returns:
            List of all chunks from all files
        """
        all_chunks = []
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    chunks = self.chunk_file(file_path)
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"Error chunking {file_path}: {e}")
        
        return all_chunks
