import uvicorn
from app.api import app
from app.data_loader import load_external_datasets
import os

def startup():
    """Load data on startup"""
    print("Loading external datasets...")
    try:
        load_external_datasets()
        print("Data loading completed successfully.")
    except Exception as e:
        print(f"Warning: Data loading failed: {e}")
        print("API will still start but may have limited functionality.")

if __name__ == "__main__":
    # Load data first
    startup()
    
    # Start the API server
    print("Starting StyleSense AI Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8080)