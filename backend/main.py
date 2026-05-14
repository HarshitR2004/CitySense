"""
Backend Entry Point

Run with: python main.py
Or: uvicorn main:app --reload
"""

from dotenv import load_dotenv
from app.main import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration with sensible defaults
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Use import string for reload mode support
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
    )
