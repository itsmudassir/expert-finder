#!/usr/bin/env python3
"""
MongoDB Database Explorer for Expert Speaker Profiles
Analyzes schema structure across multiple speaker databases
"""

import pymongo
from pymongo import MongoClient
import json
from datetime import datetime
from collections import defaultdict
import pprint

# MongoDB connection
MONGO_URI = "mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin"

# List of databases to explore
DATABASES = [
    "a_speakers",
    "allamericanspeakers",
    "bigspeak_scraper",
    "eventraptor",
    "freespeakerbureau_scraper",
    "leading_authorities",
    "sessionize_scraper",
    "speakerhub_scraper",
    "thespeakerhandbook_scraper"
]

def get_field_type(value):
    """Determine the type of a field value"""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, list):
        return f"array[{len(value)}]"
    elif isinstance(value, dict):
        return "object"
    elif isinstance(value, datetime):
        return "datetime"
    else:
        return str(type(value).__name__)

def analyze_collection_schema(collection, sample_size=100):
    """Analyze the schema of a collection by sampling documents"""
    schema_info = {
        "total_documents": collection.count_documents({}),
        "fields": defaultdict(lambda: {"types": defaultdict(int), "count": 0, "examples": []})
    }
    
    # Sample documents
    documents = list(collection.find().limit(sample_size))
    
    for doc in documents:
        for field, value in doc.items():
            field_info = schema_info["fields"][field]
            field_info["count"] += 1
            field_type = get_field_type(value)
            field_info["types"][field_type] += 1
            
            # Store examples (limit to 3)
            if len(field_info["examples"]) < 3 and value is not None and value != "":
                if isinstance(value, (str, int, float, bool)):
                    field_info["examples"].append(value)
                elif isinstance(value, list) and len(value) > 0:
                    field_info["examples"].append(f"[{len(value)} items]")
                elif isinstance(value, dict):
                    field_info["examples"].append("{...}")
    
    return schema_info

def explore_databases():
    """Main function to explore all databases"""
    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI)
    
    exploration_results = {}
    
    for db_name in DATABASES:
        print(f"\n{'='*60}")
        print(f"Exploring database: {db_name}")
        print(f"{'='*60}")
        
        db = client[db_name]
        collections = db.list_collection_names()
        
        if not collections:
            print(f"No collections found in {db_name}")
            continue
            
        db_info = {
            "collections": {}
        }
        
        for collection_name in collections:
            print(f"\n  Collection: {collection_name}")
            collection = db[collection_name]
            
            schema_info = analyze_collection_schema(collection)
            db_info["collections"][collection_name] = schema_info
            
            print(f"    Total documents: {schema_info['total_documents']}")
            print(f"    Number of fields: {len(schema_info['fields'])}")
            
            # Print field summary
            print("\n    Fields:")
            for field_name, field_info in sorted(schema_info['fields'].items()):
                types_str = ", ".join([f"{t}({c})" for t, c in field_info['types'].items()])
                print(f"      - {field_name}: {types_str}")
                if field_info['examples']:
                    examples_str = str(field_info['examples'][:2])[:100]
                    print(f"        Examples: {examples_str}")
        
        exploration_results[db_name] = db_info
    
    # Save results to JSON
    with open('database_exploration_results.json', 'w') as f:
        json.dump(exploration_results, f, indent=2, default=str)
    
    print("\n\nExploration complete! Results saved to database_exploration_results.json")
    
    client.close()
    return exploration_results

if __name__ == "__main__":
    results = explore_databases()