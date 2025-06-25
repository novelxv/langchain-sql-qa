import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
import sqlalchemy

load_dotenv()

def create_database_connection():
    """Create database connection with fallback options"""
    base_url = os.getenv("DATABASE_URL", "postgresql://postgres:nooveel@localhost:5432/chinook")
    
    connection_options = [
        f"{base_url}?client_encoding=utf8",
        f"{base_url}?client_encoding=utf8&connect_timeout=10",
        "postgresql://postgres:nooveel@localhost:5432/chinook?client_encoding=utf8&connect_timeout=10"
    ]
    
    for i, url in enumerate(connection_options, 1):
        try:
            engine = sqlalchemy.create_engine(
                url, 
                pool_pre_ping=True,
                connect_args={"client_encoding": "utf8"}
            )
            
            with engine.connect() as conn:
                result = conn.execute(sqlalchemy.text("SELECT 1"))
                result.fetchone()
            
            db = SQLDatabase.from_uri(url)
            return db
            
        except Exception as e:
            if i == len(connection_options):
                raise Exception(f"All database connection attempts failed. Last error: {e}")
            continue
    
    raise Exception("All database connection attempts failed")

try:
    db = create_database_connection()
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    print("Troubleshooting steps:")
    print("1. Check if PostgreSQL service is running")
    print("2. Run: python scripts/clean_database.py")
    exit(1)