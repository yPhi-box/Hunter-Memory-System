"""
Local embedding generation using sentence-transformers.
Zero API costs, runs entirely on the VM.
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from pathlib import Path


class EmbeddingGenerator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', cache_dir: str = None):
        """
        Initialize embedding model.
        
        Args:
            model_name: HuggingFace model name (default: all-MiniLM-L6-v2, 384 dims, fast)
            cache_dir: Where to cache the model
        """
        if cache_dir is None:
            cache_dir = str(Path(__file__).parent / 'models')
        
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of embeddings
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of embeddings (n_texts, embedding_dim)
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 100
        )
        return embeddings
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1, higher is more similar)
        """
        # Normalize vectors
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)
        
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2)
        return float(similarity)


if __name__ == '__main__':
    # Test
    print("Testing embedding generator...")
    generator = EmbeddingGenerator()
    
    # Test single embedding
    text = "This is a test sentence for embedding generation."
    embedding = generator.embed_text(text)
    print(f"\nSingle embedding shape: {embedding.shape}")
    print(f"First 5 values: {embedding[:5]}")
    
    # Test batch
    texts = [
        "Python is a programming language.",
        "Machine learning uses neural networks.",
        "The weather is nice today."
    ]
    embeddings = generator.embed_batch(texts)
    print(f"\nBatch embeddings shape: {embeddings.shape}")
    
    # Test similarity
    sim_1_2 = generator.similarity(embeddings[0], embeddings[1])
    sim_1_3 = generator.similarity(embeddings[0], embeddings[2])
    print(f"\nSimilarity (programming vs ML): {sim_1_2:.3f}")
    print(f"Similarity (programming vs weather): {sim_1_3:.3f}")
