#!/usr/bin/env python3
"""
Query the unified speaker database
Simple interface to search and filter speakers
"""

import pymongo
from pymongo import MongoClient
import json
from typing import Dict, List, Any, Optional
import argparse

MONGO_URI = "mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin"
DB_NAME = "expert_finder_unified"
COLLECTION_NAME = "speakers"

class SpeakerQuery:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]
        
    def search(self, 
               query: str = None,
               country: str = None,
               topics: List[str] = None,
               min_score: int = None,
               has_video: bool = None,
               has_email: bool = None,
               limit: int = 10) -> List[Dict[str, Any]]:
        """Search speakers with various filters"""
        
        # Build MongoDB query
        mongo_query = {}
        
        # Text search
        if query:
            mongo_query["$text"] = {"$search": query}
            
        # Country filter
        if country:
            mongo_query["location.country"] = {"$regex": country, "$options": "i"}
            
        # Topics filter
        if topics:
            mongo_query["expertise.primary_topics"] = {"$in": topics}
            
        # Quality score filter
        if min_score:
            mongo_query["metadata.profile_score"] = {"$gte": min_score}
            
        # Has video filter
        if has_video is not None:
            if has_video:
                mongo_query["media.videos"] = {"$exists": True, "$ne": []}
            else:
                mongo_query["$or"] = [
                    {"media.videos": {"$exists": False}},
                    {"media.videos": []}
                ]
                
        # Has email filter
        if has_email is not None:
            if has_email:
                mongo_query["contact.email"] = {"$exists": True, "$ne": None}
            else:
                mongo_query["contact.email"] = {"$in": [None, ""]}
                
        # Execute query
        cursor = self.collection.find(mongo_query)
        
        # Sort by score if text search, otherwise by profile score
        if query:
            cursor = cursor.sort([("score", {"$meta": "textScore"})])
        else:
            cursor = cursor.sort([("metadata.profile_score", -1)])
            
        # Apply limit
        results = list(cursor.limit(limit))
        
        # Format results
        formatted = []
        for doc in results:
            formatted.append(self._format_speaker(doc))
            
        return formatted
    
    def _format_speaker(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Format speaker document for display"""
        return {
            'name': doc['basic_info']['full_name'],
            'title': doc['professional_info'].get('title', 'N/A'),
            'company': doc['professional_info'].get('company', 'N/A'),
            'location': self._format_location(doc['location']),
            'topics': doc['expertise'].get('primary_topics', []),
            'fee_category': doc['speaking_info'].get('fee_range', {}).get('category', 'N/A') if doc['speaking_info'].get('fee_range') else 'N/A',
            'languages': doc['speaking_info'].get('languages', []),
            'has_video': len(doc['media'].get('videos', [])) > 0,
            'has_email': bool(doc['contact'].get('email')),
            'profile_score': doc['metadata']['profile_score'],
            'sources': doc['metadata']['sources'],
            'booking_sites': list(doc['online_presence'].get('booking_sites', {}).values())
        }
    
    def _format_location(self, location: Dict[str, Any]) -> str:
        """Format location for display"""
        parts = []
        if location.get('city'):
            parts.append(location['city'])
        if location.get('state'):
            parts.append(location['state'])
        if location.get('country'):
            parts.append(location['country'])
        return ', '.join(parts) if parts else 'N/A'
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        total = self.collection.count_documents({})
        
        stats = {
            'total_speakers': total,
            'speakers_with_email': self.collection.count_documents({"contact.email": {"$exists": True, "$ne": None}}),
            'speakers_with_video': self.collection.count_documents({"media.videos": {"$exists": True, "$ne": []}}),
            'speakers_with_fee': self.collection.count_documents({"speaking_info.fee_range": {"$exists": True, "$ne": None}}),
            'average_profile_score': 0,
            'top_countries': [],
            'top_topics': []
        }
        
        # Average profile score
        pipeline = [
            {"$group": {"_id": None, "avg_score": {"$avg": "$metadata.profile_score"}}}
        ]
        result = list(self.collection.aggregate(pipeline))
        if result:
            stats['average_profile_score'] = round(result[0]['avg_score'], 1)
            
        # Top countries
        pipeline = [
            {"$match": {"location.country": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$location.country", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        stats['top_countries'] = [
            {'country': item['_id'], 'count': item['count']}
            for item in self.collection.aggregate(pipeline)
        ]
        
        # Top topics
        pipeline = [
            {"$unwind": "$expertise.primary_topics"},
            {"$group": {"_id": "$expertise.primary_topics", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        stats['top_topics'] = [
            {'topic': item['_id'], 'count': item['count']}
            for item in self.collection.aggregate(pipeline)
        ]
        
        return stats
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get speaker by exact name"""
        doc = self.collection.find_one({"basic_info.full_name": {"$regex": f"^{name}$", "$options": "i"}})
        if doc:
            return self._format_speaker(doc)
        return None
    
    def export_search(self, search_params: Dict[str, Any], filename: str):
        """Export search results to JSON file"""
        results = self.search(**search_params, limit=1000)
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
            
        return len(results)


def main():
    parser = argparse.ArgumentParser(description='Query unified speaker database')
    parser.add_argument('--search', help='Text search query')
    parser.add_argument('--country', help='Filter by country')
    parser.add_argument('--topics', nargs='+', help='Filter by topics')
    parser.add_argument('--min-score', type=int, help='Minimum profile score')
    parser.add_argument('--has-video', action='store_true', help='Only speakers with video')
    parser.add_argument('--has-email', action='store_true', help='Only speakers with email')
    parser.add_argument('--limit', type=int, default=10, help='Number of results')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--export', help='Export results to JSON file')
    
    args = parser.parse_args()
    
    query = SpeakerQuery()
    
    if args.stats:
        # Show statistics
        stats = query.get_stats()
        print("\nDATABASE STATISTICS")
        print("="*50)
        print(f"Total speakers: {stats['total_speakers']:,}")
        print(f"Speakers with email: {stats['speakers_with_email']:,} ({stats['speakers_with_email']/stats['total_speakers']*100:.1f}%)")
        print(f"Speakers with video: {stats['speakers_with_video']:,} ({stats['speakers_with_video']/stats['total_speakers']*100:.1f}%)")
        print(f"Speakers with fee info: {stats['speakers_with_fee']:,} ({stats['speakers_with_fee']/stats['total_speakers']*100:.1f}%)")
        print(f"Average profile score: {stats['average_profile_score']}/100")
        
        print("\nTop 10 Countries:")
        for item in stats['top_countries']:
            print(f"  {item['country']}: {item['count']:,}")
            
        print("\nTop 10 Topics:")
        for item in stats['top_topics']:
            print(f"  {item['topic']}: {item['count']:,}")
            
    else:
        # Perform search
        search_params = {
            'query': args.search,
            'country': args.country,
            'topics': args.topics,
            'min_score': args.min_score,
            'has_video': args.has_video,
            'has_email': args.has_email,
            'limit': args.limit
        }
        
        # Remove None values
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        results = query.search(**search_params)
        
        if args.export:
            count = query.export_search(search_params, args.export)
            print(f"Exported {count} results to {args.export}")
        else:
            # Display results
            print(f"\nFound {len(results)} speakers:")
            print("="*100)
            
            for i, speaker in enumerate(results, 1):
                print(f"\n{i}. {speaker['name']} (Score: {speaker['profile_score']}%)")
                print(f"   Title: {speaker['title']}")
                print(f"   Company: {speaker['company']}")
                print(f"   Location: {speaker['location']}")
                print(f"   Topics: {', '.join(speaker['topics'])}")
                print(f"   Fee: {speaker['fee_category']}")
                print(f"   Languages: {', '.join(speaker['languages']) if speaker['languages'] else 'N/A'}")
                print(f"   Has Video: {'Yes' if speaker['has_video'] else 'No'}")
                print(f"   Has Email: {'Yes' if speaker['has_email'] else 'No'}")
                print(f"   Sources: {', '.join(speaker['sources'])}")
                if speaker['booking_sites']:
                    print(f"   Booking: {speaker['booking_sites'][0]}")


if __name__ == "__main__":
    main()