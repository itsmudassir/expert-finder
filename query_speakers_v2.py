#!/usr/bin/env python3
"""
Enhanced Query Interface for Expert Finder V2
With expertise taxonomy support
"""

import pymongo
from pymongo import MongoClient
import json
from typing import Dict, List, Any, Optional
import argparse
from src.normalizers.expertise_normalizer import ExpertiseNormalizer

MONGO_URI = "mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin"
DB_NAME = "expert_finder_unified_v2"
COLLECTION_NAME = "speakers"

class EnhancedSpeakerQuery:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]
        self.expertise_normalizer = ExpertiseNormalizer()
        
    def search(self, 
               query: str = None,
               expertise_category: str = None,
               parent_category: str = None,
               research_area: str = None,
               country: str = None,
               quality_tier: str = None,
               min_score: int = None,
               has_video: bool = None,
               has_email: bool = None,
               has_education: bool = None,
               limit: int = 10) -> List[Dict[str, Any]]:
        """Enhanced search with expertise categories"""
        
        # Build MongoDB query
        mongo_query = {}
        
        # Text search
        if query:
            mongo_query["$text"] = {"$search": query}
            
        # Expertise category filter
        if expertise_category:
            mongo_query["expertise.primary_categories"] = expertise_category
            
        # Parent category filter
        if parent_category:
            mongo_query["expertise.parent_categories"] = parent_category
            
        # Research area filter
        if research_area:
            mongo_query["expertise.research_areas"] = {"$regex": research_area, "$options": "i"}
            
        # Country filter
        if country:
            mongo_query["location.country"] = {"$regex": country, "$options": "i"}
            
        # Quality tier filter
        if quality_tier:
            mongo_query["metadata.data_quality_tier"] = quality_tier
            
        # Quality score filter
        if min_score:
            mongo_query["metadata.profile_score"] = {"$gte": min_score}
            
        # Has video filter
        if has_video is not None:
            if has_video:
                mongo_query["media.videos"] = {"$exists": True, "$ne": []}
                
        # Has email filter
        if has_email is not None:
            if has_email:
                mongo_query["contact.email"] = {"$exists": True, "$ne": None}
                
        # Has education filter
        if has_education is not None:
            if has_education:
                mongo_query["education.degrees"] = {"$exists": True, "$ne": []}
                
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
        # Get category display names
        categories = []
        for cat_id in doc.get('expertise', {}).get('primary_categories', []):
            cat_info = self.expertise_normalizer.get_category_info(cat_id)
            if cat_info:
                categories.append(cat_info['display_name'])
                
        return {
            'name': doc['basic_info']['full_name'],
            'title': doc['professional_info'].get('title', 'N/A'),
            'company': doc['professional_info'].get('company', 'N/A'),
            'location': self._format_location(doc['location']),
            'expertise_categories': categories,
            'research_areas': doc['expertise'].get('research_areas', [])[:3],  # Top 3
            'education': doc.get('education', {}).get('degrees', [])[:2],  # Top 2
            'quality_tier': doc['metadata'].get('data_quality_tier', 'N/A'),
            'has_video': len(doc['media'].get('videos', [])) > 0,
            'has_email': bool(doc['contact'].get('email')),
            'profile_score': doc['metadata']['profile_score'],
            'sources': doc['metadata']['sources'],
            'booking_sites': list(doc['online_presence'].get('booking_sites', {}).values())[:1]
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
    
    def get_expertise_stats(self) -> Dict[str, Any]:
        """Get statistics about expertise categories"""
        pipeline = [
            {
                "$facet": {
                    "by_parent_category": [
                        {"$unwind": "$expertise.parent_categories"},
                        {"$group": {"_id": "$expertise.parent_categories", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}}
                    ],
                    "by_primary_category": [
                        {"$unwind": "$expertise.primary_categories"},
                        {"$group": {"_id": "$expertise.primary_categories", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}},
                        {"$limit": 20}
                    ],
                    "by_quality_tier": [
                        {"$match": {"metadata.data_quality_tier": {"$exists": True}}},
                        {"$group": {"_id": "$metadata.data_quality_tier", "count": {"$sum": 1}}},
                        {"$sort": {"_id": 1}}
                    ]
                }
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))[0]
        
        # Convert category IDs to display names
        stats = {
            'parent_categories': [],
            'primary_categories': [],
            'quality_tiers': result['by_quality_tier']
        }
        
        # Parent categories
        parent_map = self.expertise_normalizer.parent_categories
        for item in result['by_parent_category']:
            stats['parent_categories'].append({
                'category': parent_map.get(item['_id'], item['_id']),
                'count': item['count']
            })
            
        # Primary categories
        for item in result['by_primary_category']:
            cat_info = self.expertise_normalizer.get_category_info(item['_id'])
            if cat_info:
                stats['primary_categories'].append({
                    'category': cat_info['display_name'],
                    'parent': cat_info['parent_display_name'],
                    'count': item['count']
                })
                
        return stats
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Get enhanced database statistics"""
        total = self.collection.count_documents({})
        
        stats = {
            'total_speakers': total,
            'speakers_with_email': self.collection.count_documents({"contact.email": {"$exists": True, "$ne": None}}),
            'speakers_with_video': self.collection.count_documents({"media.videos": {"$exists": True, "$ne": []}}),
            'speakers_with_education': self.collection.count_documents({"education.degrees": {"$exists": True, "$ne": []}}),
            'speakers_with_research': self.collection.count_documents({"expertise.research_areas": {"$exists": True, "$ne": []}}),
            'speakers_with_expertise': self.collection.count_documents({"expertise.primary_categories": {"$exists": True, "$ne": []}}),
            'average_profile_score': 0,
            'expertise_breakdown': self.get_expertise_stats()
        }
        
        # Average profile score
        pipeline = [
            {"$group": {"_id": None, "avg_score": {"$avg": "$metadata.profile_score"}}}
        ]
        result = list(self.collection.aggregate(pipeline))
        if result:
            stats['average_profile_score'] = round(result[0]['avg_score'], 1)
            
        return stats
    
    def browse_categories(self) -> Dict[str, List[Dict]]:
        """Browse all expertise categories"""
        return self.expertise_normalizer.get_all_categories_hierarchy()


def main():
    parser = argparse.ArgumentParser(description='Query enhanced unified speaker database')
    parser.add_argument('--search', help='Text search query')
    parser.add_argument('--expertise', help='Filter by expertise category ID')
    parser.add_argument('--parent-category', help='Filter by parent category')
    parser.add_argument('--research', help='Filter by research area')
    parser.add_argument('--country', help='Filter by country')
    parser.add_argument('--quality', choices=['cat_1', 'cat_2', 'cat_3', 'cat_4'], 
                       help='Filter by quality tier')
    parser.add_argument('--min-score', type=int, help='Minimum profile score')
    parser.add_argument('--has-video', action='store_true', help='Only speakers with video')
    parser.add_argument('--has-email', action='store_true', help='Only speakers with email')
    parser.add_argument('--has-education', action='store_true', help='Only speakers with education')
    parser.add_argument('--limit', type=int, default=10, help='Number of results')
    parser.add_argument('--stats', action='store_true', help='Show enhanced statistics')
    parser.add_argument('--browse', action='store_true', help='Browse expertise categories')
    
    args = parser.parse_args()
    
    query = EnhancedSpeakerQuery()
    
    if args.stats:
        # Show enhanced statistics
        stats = query.get_enhanced_stats()
        print("\nENHANCED DATABASE STATISTICS")
        print("="*50)
        print(f"Total speakers: {stats['total_speakers']:,}")
        print(f"With email: {stats['speakers_with_email']:,} ({stats['speakers_with_email']/stats['total_speakers']*100:.1f}%)")
        print(f"With video: {stats['speakers_with_video']:,} ({stats['speakers_with_video']/stats['total_speakers']*100:.1f}%)")
        print(f"With education: {stats['speakers_with_education']:,} ({stats['speakers_with_education']/stats['total_speakers']*100:.1f}%)")
        print(f"With research areas: {stats['speakers_with_research']:,} ({stats['speakers_with_research']/stats['total_speakers']*100:.1f}%)")
        print(f"With categorized expertise: {stats['speakers_with_expertise']:,} ({stats['speakers_with_expertise']/stats['total_speakers']*100:.1f}%)")
        print(f"Average profile score: {stats['average_profile_score']}/100")
        
        print("\nExpertise Distribution by Parent Category:")
        for item in stats['expertise_breakdown']['parent_categories']:
            print(f"  {item['category']}: {item['count']:,}")
            
        print("\nTop Expertise Categories:")
        for item in stats['expertise_breakdown']['primary_categories'][:10]:
            print(f"  {item['category']} ({item['parent']}): {item['count']:,}")
            
        print("\nQuality Tier Distribution:")
        for item in stats['expertise_breakdown']['quality_tiers']:
            print(f"  {item['_id']}: {item['count']:,}")
            
    elif args.browse:
        # Browse categories
        hierarchy = query.browse_categories()
        print("\nEXPERTISE CATEGORY HIERARCHY")
        print("="*50)
        
        for parent, categories in hierarchy.items():
            parent_name = query.expertise_normalizer.parent_categories.get(parent, parent)
            print(f"\n{parent_name}:")
            for cat in categories:
                print(f"  - {cat['display_name']} ({cat['keyword_count']} keywords)")
                
    else:
        # Perform search
        search_params = {
            'query': args.search,
            'expertise_category': args.expertise,
            'parent_category': args.parent_category,
            'research_area': args.research,
            'country': args.country,
            'quality_tier': args.quality,
            'min_score': args.min_score,
            'has_video': args.has_video,
            'has_email': args.has_email,
            'has_education': args.has_education,
            'limit': args.limit
        }
        
        # Remove None values
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        results = query.search(**search_params)
        
        # Display results
        print(f"\nFound {len(results)} speakers:")
        print("="*100)
        
        for i, speaker in enumerate(results, 1):
            print(f"\n{i}. {speaker['name']} (Score: {speaker['profile_score']}%, Tier: {speaker['quality_tier']})")
            print(f"   Title: {speaker['title']}")
            print(f"   Company: {speaker['company']}")
            print(f"   Location: {speaker['location']}")
            if speaker['expertise_categories']:
                print(f"   Expertise: {', '.join(speaker['expertise_categories'])}")
            if speaker['research_areas']:
                print(f"   Research: {', '.join(speaker['research_areas'])}")
            if speaker['education']:
                print(f"   Education: {', '.join(speaker['education'])}")
            print(f"   Has Video: {'Yes' if speaker['has_video'] else 'No'}")
            print(f"   Has Email: {'Yes' if speaker['has_email'] else 'No'}")
            print(f"   Sources: {', '.join(speaker['sources'])}")
            if speaker['booking_sites']:
                print(f"   Booking: {speaker['booking_sites'][0]}")


if __name__ == "__main__":
    main()