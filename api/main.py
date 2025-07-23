"""FastAPI application for the E-commerce AI Agent.

This module provides the REST API endpoints for natural language querying
of e-commerce data with rate limiting and streaming support.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from db.connection import db
from llm.sql_translator import translator
from visualizer.plotter import plotter

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce AI Agent",
    description="Natural language interface for e-commerce data analysis",
    version="1.0.0"
)
# Configure rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class Question(BaseModel):
    """Request model for questions."""
    question: str
    enable_viz: bool = True
    stream_response: bool = False

class QueryResult(BaseModel):
    """Response model for query results."""
    sql_query: str
    result: list[dict[str, Any]]
    visualization: Optional[str] = None
    error: Optional[str] = None


# API router
api_router = APIRouter(prefix="/api")


@api_router.post("/ask", response_model=QueryResult)
@limiter.limit(f"{settings.rate_limit_calls}/minute")
async def ask_question(request: Request, question: Question):
    """Process natural language questions about e-commerce data.
    
    Args:
        request: FastAPI request object
        question: Question model with query parameters
        
    Returns:
        QueryResult: Query results and optional visualization
    """
    try:
        # Stream response if requested
        if question.stream_response and settings.enable_streaming:
            return StreamingResponse(
                stream_response(question.question),
                media_type="text/event-stream"
            )
        
        # Generate SQL
        sql, metadata = await translator.translate_to_sql(question.question)
        if not sql:
            raise HTTPException(status_code=400, detail="Failed to generate SQL query")
        
        # Execute query
        result = db.execute_query(sql)
        result_dict = [dict(row) for row in result]
        
        # Check if visualization is needed
        viz_base64 = None
        if question.enable_viz and settings.enable_visualization:
            viz_config_str = await translator.analyze_visualization(
                question.question, str(result_dict))
            try:
                viz_config = json.loads(viz_config_str)
                if viz_config.get("needs_visualization"):
                    viz_base64 = plotter.create_plot(result_dict, viz_config)
            except json.JSONDecodeError:
                logger.error("Failed to decode visualization config")
                viz_base64 = None
        
        return QueryResult(
            sql_query=sql,
            result=result_dict,
            visualization=viz_base64
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(api_router)

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/health")
@limiter.limit(f"{settings.rate_limit_calls}/minute")
async def health_check(request: Request):
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

async def stream_response(question: str) -> str:
    """Stream response with simulated typing effect.
    
    Args:
        question: User's question
        
    Yields:
        str: Response chunks
    """
    # Generate SQL
    sql, metadata = await translator.translate_to_sql(question)
    if not sql:
        yield json.dumps({"error": "Failed to generate SQL query"})
        return
    
    yield json.dumps({"sql_query": sql}) + "\n"
    await asyncio.sleep(0.5)
    
    # Execute query
    try:
        result = db.execute_query(sql)
        yield json.dumps({"executing": "Running query..."}) + "\n"
        await asyncio.sleep(0.5)
        
        # Convert result to dict
        result_dict = [dict(row) for row in result]
        yield json.dumps({"result": result_dict}) + "\n"
        
    except Exception as e:
        yield json.dumps({"error": str(e)})



@app.post("/upload")
@limiter.limit(f"{settings.rate_limit_calls}/minute")
async def upload_csv(request: Request):
    """Upload and process CSV files.
    
    This endpoint is a placeholder. In a real implementation, it would:
    1. Accept CSV file uploads
    2. Validate file format
    3. Load data into SQLite
    4. Return table schema
    """
    return {"message": "CSV upload endpoint - To be implemented"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug_mode
    )