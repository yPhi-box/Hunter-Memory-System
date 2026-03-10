"""
FastAPI server for OpenClaw integration.
Provides HTTP endpoint for memory search.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
from database import MemoryDatabase
from embedder import Embedder
from search import HybridSearch
from indexer import MemoryIndexer
import uvicorn


app = FastAPI(title="Hunter Memory System")

# Global instances
db_path = Path(__file__).parent / "memory.db"
db = None
embedder = None
search_engine = None
indexer = None


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    global db, embedder, search_engine, indexer
    
    print("Starting Memory System...")
    db = MemoryDatabase(db_path)
    embedder = Embedder()
    search_engine = HybridSearch(db, embedder)
    indexer = MemoryIndexer(db_path)
    print("Memory System ready")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    global db
    if db:
        db.close()
    print("Memory System stopped")


class SearchRequest(BaseModel):
    """Search request."""
    query: str
    max_results: Optional[int] = 10
    min_score: Optional[float] = 0.0
    semantic_weight: Optional[float] = 0.6
    keyword_weight: Optional[float] = 0.4


class SearchResult(BaseModel):
    """Search result."""
    file_path: str
    line_start: int
    line_end: int
    text: str
    score: float
    semantic_score: float
    keyword_score: float


class SearchResponse(BaseModel):
    """Search response."""
    query: str
    results: list[SearchResult]
    total: int


class IndexRequest(BaseModel):
    """Index request."""
    directory: str
    pattern: Optional[str] = "**/*.md"
    force: Optional[bool] = False


class StatsResponse(BaseModel):
    """Stats response."""
    total_chunks: int
    total_files: int
    db_size_mb: float


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search memory.
    
    Args:
        request: Search request
        
    Returns:
        Search results
    """
    try:
        results = search_engine.search(
            query=request.query,
            max_results=request.max_results,
            semantic_weight=request.semantic_weight,
            keyword_weight=request.keyword_weight,
            min_score=request.min_score
        )
        
        # Convert to response format
        search_results = [
            SearchResult(
                file_path=r['file_path'],
                line_start=r['line_start'],
                line_end=r['line_end'],
                text=r['text'],
                score=r['combined_score'],
                semantic_score=r['semantic_score'],
                keyword_score=r['keyword_score']
            )
            for r in results
        ]
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total=len(search_results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
async def index(request: IndexRequest):
    """
    Index a directory.
    
    Args:
        request: Index request
        
    Returns:
        Success message with stats
    """
    try:
        dir_path = Path(request.directory)
        
        if not dir_path.exists():
            raise HTTPException(status_code=404, detail=f"Directory not found: {dir_path}")
        
        indexer.index_directory(dir_path, request.pattern, request.force)
        stats = indexer.get_stats()
        
        return {
            "message": "Indexing complete",
            "stats": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get database statistics.
    
    Returns:
        Database stats
    """
    try:
        stats = db.get_stats()
        return StatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


def run_server(host: str = "0.0.0.0", port: int = 8765):
    """
    Run the server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
