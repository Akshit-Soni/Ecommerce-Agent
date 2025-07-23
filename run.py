"""Entry point for the E-commerce AI Agent.

This script handles application startup, database initialization,
and CSV data loading.
"""

import argparse
import logging
from pathlib import Path

import uvicorn
from config.settings import settings
from db.loader import loader

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

def init_database(csv_paths: list[Path]) -> bool:
    """Initialize database with CSV data.
    
    Args:
        csv_paths: List of paths to CSV files
        
    Returns:
        bool: True if successful
    """
    try:
        for csv_path in csv_paths:
            if not csv_path.exists():
                logger.error(f"CSV file not found: {csv_path}")
                return False
            
            # Generate table name from file name
            table_name = csv_path.stem.lower().replace(' ', '_')
            
            # Load CSV into SQLite
            loader.load_csv(csv_path, table_name)
            logger.info(f"Loaded {csv_path} into table {table_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="E-commerce AI Agent - Natural language interface for data analysis")
    
    parser.add_argument(
        "--csv",
        type=str,
        nargs="+",
        help="Paths to CSV files to load"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default=settings.api_host,
        help="Host address for the API server"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=settings.api_port,
        help="Port number for the API server"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        default=settings.debug_mode,
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Initialize database if it doesn't exist
    db_path = Path(settings.db_path.split("///")[-1])
    if not db_path.exists():
        logger.info("Database not found, initializing...")
        csv_dir = Path("csv")
        if not csv_dir.exists():
            logger.error(f"CSV directory not found at {csv_dir.resolve()}")
            return
        
        csv_files = list(csv_dir.glob("*.csv"))
        if not csv_files:
            logger.warning("No CSV files found in 'csv/' directory. The application will run with an empty database.")
        elif not init_database(csv_files):
            logger.error("Failed to initialize database from CSV files.")
            return

    # Start FastAPI server
    logger.info(f"Starting server on {args.host}:{args.port}")
    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=args.debug
    )

if __name__ == "__main__":
    main()