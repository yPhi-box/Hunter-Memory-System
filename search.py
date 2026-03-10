"""
Hybrid search combining semantic and keyword search.
Includes temporal decay for recent content prioritization.
"""
from typing import List, Dict
from datetime import datetime, timedelta
from embedder import Embedder
from database import MemoryDatabase
import math


class HybridSearch:
    """Hybrid search engine combining semantic + keyword + temporal."""
    
    def __init__(self, db: MemoryDatabase, embedder: Embedder):
        """
        Initialize search engine.
        
        Args:
            db: Memory database
            embedder: Embedding generator
        """
        self.db = db
        self.embedder = embedder
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.4,
        temporal_decay_days: int = 30,
        min_score: float = 0.0
    ) -> List[Dict]:
        """
        Hybrid search with semantic + keyword + temporal scoring.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword matching (0-1)
            temporal_decay_days: Days for temporal decay (newer = higher score)
            min_score: Minimum score threshold
            
        Returns:
            List of results sorted by combined score
        """
        # Get semantic results
        query_embedding = self.embedder.embed(query)
        semantic_results = self.db.search_semantic(
            query_embedding.tolist(),
            limit=max_results * 2  # Get more for merging
        )
        
        # Get keyword results
        keyword_results = self.db.search_keyword(
            query,
            limit=max_results * 2
        )
        
        # Merge and score
        merged = self._merge_results(
            semantic_results,
            keyword_results,
            semantic_weight,
            keyword_weight,
            temporal_decay_days
        )
        
        # Filter by min score and limit
        filtered = [r for r in merged if r['combined_score'] >= min_score]
        return filtered[:max_results]
    
    def _merge_results(
        self,
        semantic: List[Dict],
        keyword: List[Dict],
        semantic_weight: float,
        keyword_weight: float,
        temporal_decay_days: int
    ) -> List[Dict]:
        """
        Merge semantic and keyword results with combined scoring.
        
        Args:
            semantic: Semantic search results
            keyword: Keyword search results
            semantic_weight: Weight for semantic score
            keyword_weight: Weight for keyword score
            temporal_decay_days: Days for temporal decay
            
        Returns:
            Merged and scored results
        """
        # Build result map by chunk ID
        result_map = {}
        
        # Add semantic results
        for result in semantic:
            chunk_id = result['id']
            result_map[chunk_id] = {
                **result,
                'semantic_score': result['score'],
                'keyword_score': 0.0
            }
        
        # Add/merge keyword results
        for result in keyword:
            chunk_id = result['id']
            if chunk_id in result_map:
                result_map[chunk_id]['keyword_score'] = result['score']
            else:
                result_map[chunk_id] = {
                    **result,
                    'semantic_score': 0.0,
                    'keyword_score': result['score']
                }
        
        # Calculate combined scores with temporal decay
        results = []
        now = datetime.now()
        
        for chunk_id, result in result_map.items():
            # Normalize scores (0-1)
            semantic_norm = self._normalize_score(result['semantic_score'], 0, 1)
            keyword_norm = self._normalize_score(result['keyword_score'], 0, 10)
            
            # Base score
            base_score = (
                semantic_norm * semantic_weight +
                keyword_norm * keyword_weight
            )
            
            # Temporal decay
            indexed_at = datetime.fromisoformat(result['indexed_at'])
            days_old = (now - indexed_at).days
            temporal_factor = self._temporal_decay(days_old, temporal_decay_days)
            
            # Combined score
            combined_score = base_score * temporal_factor
            
            result['combined_score'] = combined_score
            result['temporal_factor'] = temporal_factor
            results.append(result)
        
        # Sort by combined score
        results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return results
    
    def _normalize_score(self, score: float, min_val: float, max_val: float) -> float:
        """Normalize score to 0-1 range."""
        if max_val == min_val:
            return 0.0
        return max(0.0, min(1.0, (score - min_val) / (max_val - min_val)))
    
    def _temporal_decay(self, days_old: int, decay_days: int) -> float:
        """
        Calculate temporal decay factor.
        
        Args:
            days_old: Age in days
            decay_days: Half-life in days
            
        Returns:
            Decay factor (0-1), where 1 = today, 0.5 = decay_days ago
        """
        if days_old <= 0:
            return 1.0
        
        # Exponential decay: 0.5^(days_old / decay_days)
        return math.pow(0.5, days_old / decay_days)
