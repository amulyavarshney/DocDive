import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from app.core.config import settings

# MongoDB connection - Using synchronous PyMongo client
client = MongoClient(settings.MONGODB_URI, server_api=ServerApi('1'))
db = client[settings.DB_NAME]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
except Exception as e:
    print(e)

# Collections
documents_collection = db["documents"]
queries_collection = db["queries"]
metrics_collection = db["metrics"]

# Create indices
documents_collection.create_index("document_id", unique=True)
documents_collection.create_index("file_name")
documents_collection.create_index("upload_date")

queries_collection.create_index("query_id", unique=True)
queries_collection.create_index("timestamp")
queries_collection.create_index("document_ids")

metrics_collection.create_index("timestamp")
metrics_collection.create_index("metric_type")

# Document operations
# Note: These functions are marked as async for compatibility with the rest of the app,
# but the actual PyMongo operations are synchronous
async def insert_document(document_data: Dict[str, Any]) -> str:
    """Insert document metadata into the database"""
    result = documents_collection.insert_one(document_data)
    return str(result.inserted_id)

async def get_document(document_id: str) -> Optional[Dict[str, Any]]:
    """Get document by ID"""
    return documents_collection.find_one({"document_id": document_id})

async def get_documents_by_ids(document_ids: List[str]) -> List[Dict[str, Any]]:
    """Get multiple documents by their IDs"""
    return list(documents_collection.find(
        {"document_id": {"$in": document_ids}},
        {"_id": 0}  # Exclude MongoDB's _id field
    ))

async def get_all_documents(limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
    """Get all documents with pagination"""
    return list(documents_collection.find({}, {"_id": 0}).skip(skip).limit(limit))

async def delete_document(document_id: str) -> bool:
    """Delete document by ID"""
    result = documents_collection.delete_one({"document_id": document_id})
    return result.deleted_count > 0

# Query operations
async def log_query(query_data: Dict[str, Any]) -> str:
    """Log a query to the database"""
    result = queries_collection.insert_one(query_data)
    return str(result.inserted_id)

async def get_query(query_id: str) -> Optional[Dict[str, Any]]:
    """Get query by ID"""
    return queries_collection.find_one({"query_id": query_id})

async def get_queries(limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
    """Get all queries with pagination"""
    return list(queries_collection.find({}, {"_id": 0}).skip(skip).limit(limit))

# Metrics operations
async def log_metric(metric_data: Dict[str, Any]) -> str:
    """Log a metric to the database"""
    result = metrics_collection.insert_one(metric_data)
    return str(result.inserted_id)

async def get_daily_query_volume(days: int = 7) -> List[Dict[str, Any]]:
    """Get query volume per day for the last N days"""
    start_date = datetime.utcnow() - timedelta(days=days)
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    return list(queries_collection.aggregate(pipeline))

async def get_average_latency(days: int = 7) -> List[Dict[str, Any]]:
    """Get average latency per day for the last N days"""
    start_date = datetime.utcnow() - timedelta(days=days)
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date}, "latency": {"$exists": True}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "avg_latency": {"$avg": "$latency"}
        }},
        {"$sort": {"_id": 1}}
    ]
    return list(queries_collection.aggregate(pipeline))

async def get_success_rate(days: int = 7) -> List[Dict[str, Any]]:
    """Get success rate per day for the last N days"""
    start_date = datetime.utcnow() - timedelta(days=days)
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "total": {"$sum": 1},
            "success": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}}
        }},
        {"$project": {
            "_id": 1,
            "success_rate": {"$divide": ["$success", "$total"]}
        }},
        {"$sort": {"_id": 1}}
    ]
    return list(queries_collection.aggregate(pipeline))

async def get_top_queries(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top queried questions"""
    pipeline = [
        {"$group": {
            "_id": "$query_text",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit}
    ]
    return list(queries_collection.aggregate(pipeline))

async def get_top_documents(limit: int = 10) -> List[Dict[str, Any]]:
    """Get top queried documents"""
    pipeline = [
        {"$unwind": "$document_ids"},
        {"$group": {
            "_id": "$document_ids",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {"$lookup": {
            "from": "documents",
            "localField": "_id",
            "foreignField": "document_id",
            "as": "document_info"
        }},
        {"$project": {
            "document_id": "$_id",
            "count": 1,
            "file_name": {"$arrayElemAt": ["$document_info.file_name", 0]}
        }}
    ]
    return list(queries_collection.aggregate(pipeline)) 