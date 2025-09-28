#!/usr/bin/env python3

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add the current directory to Python path to handle imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        "GEMINI_API_KEY"
    ]
    
    optional_vars = {
        "CHROMA_HOST": "localhost",
        "CHROMA_PORT": "8000", 
        "MOCK_USER_ID": "test_user"
    }
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file.")
        return False
    
    # Set defaults for optional vars
    for var, default in optional_vars.items():
        if not os.getenv(var):
            os.environ[var] = default
            print(f"Using default value for {var}: {default}")
    
    return True

def load_datasets():
    """Load external datasets on startup."""
    try:
        print("Loading external datasets...")
        
        # Import here to ensure proper initialization order
        from app.data_loader import load_external_datasets
        from app.database import CHROMA_CLIENT, CHROMA_COLLECTIONS
        
        if not CHROMA_CLIENT:
            print("Error: Cannot connect to ChromaDB. Please ensure ChromaDB server is running.")
            print("Start ChromaDB with: chroma run --host localhost --port 8000")
            print("Or install and run: pip install chromadb && chroma run")
            return False
            
        if not CHROMA_COLLECTIONS:
            print("Error: ChromaDB collections not initialized.")
            return False
        
        # Load the datasets
        load_external_datasets()
        print("Data loading completed successfully.")
        return True
        
    except Exception as e:
        print(f"Warning: Data loading failed: {e}")
        print("API will still start but may have limited functionality.")
        print("Make sure ChromaDB is running and files exist in the data directory.")
        return False

def main():
    """Main entry point with proper startup sequence."""
    print("=" * 60)
    print("StyleSense AI Backend - Starting Up")
    print("=" * 60)
    
    # Check environment variables
    if not check_environment():
        print("Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Load datasets (non-blocking)
    load_datasets()
    
    # Import and start the API server
    print("\n" + "=" * 60)
    print("Starting API Server on http://0.0.0.0:8080")
    print("=" * 60)
    
    try:
        from app.api import app
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8080, 
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\nShutdown requested by user. Stopping server...")
    except Exception as e:
        print(f"Unexpected error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()