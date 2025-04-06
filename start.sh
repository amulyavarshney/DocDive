#!/bin/bash

# Create necessary directories
mkdir -p data/uploads data/chroma_db

# Check if MongoDB is running
if ! command -v mongod &> /dev/null
then
    echo "MongoDB is not installed. Please install MongoDB first."
    echo "Visit https://www.mongodb.com/docs/manual/installation/ for installation instructions."
    exit 1
fi

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example"
    cp .env.example .env
    echo "Please edit .env file and add your API keys"
    echo "After editing, run this script again"
    exit 1
fi

# Start the FastAPI application
echo "Starting Document Q&A Platform..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --workers 4 --log-level debug --reload-include "*.py"