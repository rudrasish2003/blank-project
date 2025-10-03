import os
import sys
import uvicorn

# Ensure project root is on sys.path regardless of current working directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.main import app  # Import the FastAPI app directly to avoid importer issues

if __name__ == "__main__":
    # Use direct app instance and disable reload to avoid multiprocessing import issues on Windows
    uvicorn.run(app=app, host="0.0.0.0", port=8000, reload=False)