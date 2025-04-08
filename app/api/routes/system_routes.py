from fastapi import APIRouter, HTTPException, Query, Depends, Body
from app.services import system_service
import subprocess
import threading
import os
import shutil
from typing import Optional
from pydantic import BaseModel, HttpUrl

router = APIRouter()

class LocustTestConfig(BaseModel):
    target_url: HttpUrl
    num_users: Optional[int] = 10
    spawn_rate: Optional[int] = 2
    run_time: Optional[str] = "1m"

@router.get("/diagnostics", tags=["system"])
async def run_diagnostics():
    """
    Test all service connections and return diagnostic information.
    
    This endpoint performs connection tests to MongoDB, Azure OpenAI, and ChromaDB
    to help diagnose connection issues.
    """
    try:
        results = await system_service.test_connections()
        return {"status": "success", "diagnostics": results}
    
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "diagnostics": {"error": str(e)}
        }


@router.delete("/reset-chromadb", tags=["system"])
async def reset_chroma_database():
    """
    Reset the ChromaDB storage directory.
    
    This endpoint creates a backup of the existing ChromaDB directory and creates
    a new empty one to fix corruption issues. Note that this will require re-embedding
    all documents.
    """
    try:
        result = await system_service.reset_chroma_db()
        return result
    
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e)
        }


@router.delete("/reset-mongodb", tags=["system"])
async def reset_mongo_database():
    """
    Reset the MongoDB database.
    
    This endpoint drops all collections in the MongoDB database and recreates them
    with proper indexes. Note that this will delete all stored documents and queries.
    """
    try:
        result = await system_service.reset_mongo_db()
        return result
    
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e)
        }


@router.post("/run-locust", tags=["system"])
async def run_locust_test(config: LocustTestConfig = Body(...)):
    """
    Start a Locust load test with web UI.
    
    This endpoint launches a Locust instance with web UI enabled on port 8089.
    Users can then visit the Locust web interface to configure and run tests.
    
    Parameters:
    - target_url: The backend URL to test against (e.g., https://api.example.com)
    - num_users: Number of simulated users (default: 10)
    - spawn_rate: Rate of user spawning per second (default: 2)
    - run_time: Duration of the test (default: "1m")
    """
    try:
        # Define the command to run Locust with web UI
        port = 8089
        cmd = [
            "locust", 
            "-f", "tests/load_tests/locustfile.py", 
            "--web-host", "0.0.0.0", 
            "--web-port", str(port),
            "--host", str(config.target_url),
            "--users", str(config.num_users),
            "--spawn-rate", str(config.spawn_rate),
            "--run-time", config.run_time
        ]
        
        # Start Locust in a separate thread
        def run_locust_in_background():
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            print(f"Locust started with PID: {process.pid}")
            print(f"Access the Locust web UI at: http://localhost:{port}")
            print(f"Testing against: {config.target_url}")
        
        # Start the thread
        thread = threading.Thread(target=run_locust_in_background)
        thread.daemon = True
        thread.start()
        
        # Return the URL for redirection
        return {
            "status": "success",
            "message": "Locust started with web UI",
            "url": f"http://localhost:{port}",
            "command": " ".join(cmd),
            "test_config": {
                "target_url": str(config.target_url),
                "num_users": config.num_users,
                "spawn_rate": config.spawn_rate,
                "run_time": config.run_time
            }
        }
    
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e)
        }


@router.delete("/reset-data-folder", tags=["system"])
async def reset_data_folder():
    """
    Delete and recreate the ./data folder.
    
    This endpoint completely removes the ./data directory and all its contents,
    then creates a new empty ./data folder.
    """
    try:
        data_path = "./data"
        
        # Delete the data directory if it exists
        if os.path.exists(data_path):
            shutil.rmtree(data_path)
        
        # Create a new empty data directory
        os.makedirs(data_path, exist_ok=True)
        
        return {
            "status": "success",
            "message": "Data folder has been reset successfully"
        }
    
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e)
        } 