"""Basic tests for the E-commerce AI Agent.

This module contains tests for core functionality including:
- API endpoints
- SQL generation
- Data loading
- Visualization
"""

import json
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import pandas as pd
import sqlite3

from api.main import app
from config.settings import settings
from db.loader import loader
from llm.sql_translator import translator

# Initialize test client
client = TestClient(app)

# Sample test data
TEST_DATA = {
    'products': pd.DataFrame({
        'product_id': [1, 2, 3],
        'name': ['Product A', 'Product B', 'Product C'],
        'sales': [1000, 2000, 3000],
        'ad_spend': [100, 200, 300]
    })
}

@pytest.fixture
def test_db():
    """Create temporary test database."""
    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    
    # Load test data
    for table_name, df in TEST_DATA.items():
        df.to_sql(table_name, conn, index=False)
    
    yield conn
    conn.close()

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ask_endpoint():
    """Test question answering endpoint."""
    question = {
        "question": "What is the total sales?",
        "enable_viz": False,
        "stream_response": False
    }
    
    response = client.post("/ask", json=question)
    assert response.status_code == 200
    
    data = response.json()
    assert "sql_query" in data
    assert "result" in data

def test_sql_generation():
    """Test SQL query generation."""
    question = "What is the total sales?"
    sql, metadata = translator.translate_to_sql(question)
    
    assert sql is not None
    assert "SELECT" in sql.upper()
    assert metadata["success"] is True

def test_data_loading(test_db):
    """Test CSV data loading."""
    # Create temporary CSV
    test_csv = Path("test_data.csv")
    TEST_DATA['products'].to_csv(test_csv, index=False)
    
    try:
        # Load CSV into database
        success = loader.load_csv(test_csv, "test_products")
        assert success is True
        
        # Verify data
        with loader.db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM test_products")
            count = cursor.fetchone()[0]
            assert count == len(TEST_DATA['products'])
            
    finally:
        # Cleanup
        test_csv.unlink()

def test_visualization():
    """Test visualization generation."""
    from visualizer.plotter import plotter
    
    # Test data
    data = {
        "x": [1, 2, 3],
        "y": [10, 20, 30]
    }
    
    # Visualization config
    viz_config = {
        "chart_type": "bar",
        "x_axis": "x",
        "y_axis": "y",
        "title": "Test Plot"
    }
    
    # Generate plot
    viz_base64 = plotter.create_plot(data, viz_config)
    assert viz_base64 is not None
    assert len(viz_base64) > 0

def test_rate_limiting():
    """Test API rate limiting."""
    # Make multiple requests quickly
    for _ in range(settings.rate_limit_calls + 1):
        response = client.get("/health")
    
    # Last request should be rate limited
    assert response.status_code == 429