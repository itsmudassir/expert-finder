#!/usr/bin/env python3
"""
Extract sample data from each MongoDB database for analysis
"""

import pymongo
from pymongo import MongoClient
import json
from datetime import datetime
import os

# MongoDB connection
MONGO_URI = "mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin"

# List of databases and their main collections
DATABASE_COLLECTIONS = {
    "a_speakers": ["speakers"],
    "allamericanspeakers": ["speakers"],
    "bigspeak_scraper": ["speakers", "speaker_profiles"],
    "eventraptor": ["speakers"],
    "freespeakerbureau_scraper": ["speakers_profiles"],
    "leading_authorities": ["speakers_final_details"],
    "sessionize_scraper": ["speakers", "speaker_profiles"],
    "speakerhub_scraper": ["speakers", "speaker_details"],
    "thespeakerhandbook_scraper": ["speakers", "speaker_profiles"]
}

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__str__'):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def extract_samples():
    """Extract sample documents from each database"""
    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI)
    
    # Create samples directory
    os.makedirs("samples", exist_ok=True)
    
    for db_name, collections in DATABASE_COLLECTIONS.items():
        print(f"\nExtracting samples from {db_name}...")
        db = client[db_name]
        
        for collection_name in collections:
            try:
                collection = db[collection_name]
                
                # Get 5 sample documents
                samples = list(collection.find().limit(5))
                
                if samples:
                    # Save samples to file
                    filename = f"samples/{db_name}_{collection_name}_samples.json"
                    with open(filename, 'w') as f:
                        json.dump(samples, f, indent=2, default=json_serial)
                    print(f"  Saved {len(samples)} samples to {filename}")
                else:
                    print(f"  No documents found in {collection_name}")
                    
            except Exception as e:
                print(f"  Error extracting from {collection_name}: {e}")
    
    client.close()
    print("\nSample extraction complete!")

if __name__ == "__main__":
    extract_samples()