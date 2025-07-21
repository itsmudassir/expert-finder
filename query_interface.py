#!/usr/bin/env python3
"""
Query Interface for Expert Finder Unified Database
Provides comprehensive search and filtering capabilities
"""

import pymongo
from pymongo import MongoClient
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime
import re

@dataclass
class SearchFilters:
    """Search filters for querying speakers"""
    # Text search
    query: Optional[str] = None
    
    # Location filters
    country: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    
    # Expertise filters
    topics: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    
    # Fee filters
    min_fee: Optional[float] = None
    max_fee: Optional[float] = None
    fee_range: Optional[str] = None  # FeeRange enum value
    
    # Language filters
    languages: Optional[List[str]] = None
    
    # Profile quality filters
    min_completeness: Optional[float] = None
    has_video: Optional[bool] = None
    has_testimonials: Optional[bool] = None
    has_contact: Optional[bool] = None
    
    # Source filters
    sources: Optional[List[str]] = None
    
    # Sorting
    sort_by: str = "relevance"  # relevance, name, completeness, fee
    sort_order: str = "desc"  # asc, desc
    
    # Pagination
    page: int = 1
    page_size: int = 20


class ExpertFinderQuery:
    """Query interface for the unified expert finder database"""
    
    def __init__(self, mongo_uri: str, database: str = "expert_finder_unified"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database]
        self.collection = self.db['speakers']
    
    def search(self, filters: SearchFilters) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search for speakers based on filters
        Returns: (results, total_count)
        """
        # Build query
        query = self._build_query(filters)
        
        # Build sort
        sort_spec = self._build_sort(filters)
        
        # Calculate pagination
        skip = (filters.page - 1) * filters.page_size
        
        # Execute query
        cursor = self.collection.find(query)
        
        # Get total count
        total_count = self.collection.count_documents(query)
        
        # Apply sorting and pagination
        if sort_spec:
            cursor = cursor.sort(sort_spec)
        
        results = list(cursor.skip(skip).limit(filters.page_size))
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            result['_id'] = str(result['_id'])
        
        return results, total_count
    
    def _build_query(self, filters: SearchFilters) -> Dict[str, Any]:
        """Build MongoDB query from filters"""
        query = {}
        
        # Text search
        if filters.query:
            query["$text"] = {"$search": filters.query}
        
        # Location filters
        if filters.country:
            query["location.country"] = {"$regex": filters.country, "$options": "i"}
        if filters.city:
            query["location.city"] = {"$regex": filters.city, "$options": "i"}
        if filters.state:
            query["location.state_province"] = {"$regex": filters.state, "$options": "i"}
        
        # Expertise filters
        if filters.topics:
            query["expertise.topics"] = {"$in": filters.topics}
        if filters.categories:
            query["expertise.categories"] = {"$in": filters.categories}
        if filters.industries:
            query["expertise.industries"] = {"$in": filters.industries}
        
        # Fee filters
        fee_conditions = []
        if filters.min_fee is not None:
            fee_conditions.append({"speaking_info.fee_info.max_amount": {"$gte": filters.min_fee}})
        if filters.max_fee is not None:
            fee_conditions.append({"speaking_info.fee_info.min_amount": {"$lte": filters.max_fee}})
        if filters.fee_range:
            fee_conditions.append({"speaking_info.fee_info.fee_range_enum": filters.fee_range})
        
        if fee_conditions:
            if len(fee_conditions) == 1:
                query.update(fee_conditions[0])
            else:
                query["$and"] = fee_conditions
        
        # Language filters
        if filters.languages:
            query["speaking_info.languages"] = {"$in": filters.languages}
        
        # Profile quality filters
        if filters.min_completeness is not None:
            query["metadata.profile_completeness"] = {"$gte": filters.min_completeness}
        if filters.has_video is not None:
            if filters.has_video:
                query["media.videos"] = {"$exists": True, "$ne": []}
            else:
                query["$or"] = [
                    {"media.videos": {"$exists": False}},
                    {"media.videos": []}
                ]
        if filters.has_testimonials is not None:
            if filters.has_testimonials:
                query["engagement_history.testimonials"] = {"$exists": True, "$ne": []}
            else:
                query["$or"] = [
                    {"engagement_history.testimonials": {"$exists": False}},
                    {"engagement_history.testimonials": []}
                ]
        if filters.has_contact is not None:
            if filters.has_contact:
                query["$or"] = [
                    {"contact_info.email": {"$exists": True, "$ne": None}},
                    {"contact_info.booking_url": {"$exists": True, "$ne": None}}
                ]
        
        # Source filters
        if filters.sources:
            query["metadata.sources"] = {"$in": filters.sources}
        
        return query
    
    def _build_sort(self, filters: SearchFilters) -> List[Tuple[str, int]]:
        """Build sort specification"""
        direction = pymongo.DESCENDING if filters.sort_order == "desc" else pymongo.ASCENDING
        
        if filters.sort_by == "relevance" and filters.query:
            # Text search score
            return [("score", {"$meta": "textScore"})]
        elif filters.sort_by == "name":
            return [("basic_info.full_name", direction)]
        elif filters.sort_by == "completeness":
            return [("metadata.profile_completeness", direction)]
        elif filters.sort_by == "fee":
            return [("speaking_info.fee_info.min_amount", direction)]
        else:
            return []
    
    def get_by_id(self, speaker_id: str) -> Optional[Dict[str, Any]]:
        """Get a single speaker by ID"""
        from bson import ObjectId
        try:
            result = self.collection.find_one({"_id": ObjectId(speaker_id)})
            if result:
                result['_id'] = str(result['_id'])
            return result
        except:
            return None
    
    def get_facets(self) -> Dict[str, List[Dict[str, int]]]:
        """Get faceted counts for filtering options"""
        pipeline = [
            {
                "$facet": {
                    "countries": [
                        {"$group": {"_id": "$location.country", "count": {"$sum": 1}}},
                        {"$match": {"_id": {"$ne": None}}},
                        {"$sort": {"count": -1}},
                        {"$limit": 20}
                    ],
                    "topics": [
                        {"$unwind": "$expertise.topics"},
                        {"$group": {"_id": "$expertise.topics", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}},
                        {"$limit": 30}
                    ],
                    "languages": [
                        {"$unwind": "$speaking_info.languages"},
                        {"$group": {"_id": "$speaking_info.languages", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}},
                        {"$limit": 20}
                    ],
                    "sources": [
                        {"$unwind": "$metadata.sources"},
                        {"$group": {"_id": "$metadata.sources", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}}
                    ],
                    "fee_ranges": [
                        {"$match": {"speaking_info.fee_info.fee_range_enum": {"$exists": True}}},
                        {"$group": {"_id": "$speaking_info.fee_info.fee_range_enum", "count": {"$sum": 1}}},
                        {"$sort": {"_id": 1}}
                    ]
                }
            }
        ]
        
        result = list(self.collection.aggregate(pipeline))[0]
        
        # Format results
        facets = {}
        for facet_name, facet_data in result.items():
            facets[facet_name] = [
                {"value": item["_id"], "count": item["count"]}
                for item in facet_data
            ]
        
        return facets
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            "total_speakers": self.collection.count_documents({}),
            "speakers_by_source": {},
            "completeness_distribution": {},
            "speakers_with_contact": 0,
            "speakers_with_video": 0,
            "speakers_with_testimonials": 0,
            "top_topics": [],
            "top_locations": []
        }
        
        # Speakers by source
        pipeline = [
            {"$unwind": "$metadata.sources"},
            {"$group": {"_id": "$metadata.sources", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        for item in self.collection.aggregate(pipeline):
            stats["speakers_by_source"][item["_id"]] = item["count"]
        
        # Completeness distribution
        ranges = [(0, 25), (25, 50), (50, 75), (75, 100)]
        for min_val, max_val in ranges:
            count = self.collection.count_documents({
                "metadata.profile_completeness": {
                    "$gte": min_val,
                    "$lt": max_val if max_val < 100 else "$lte": max_val
                }
            })
            stats["completeness_distribution"][f"{min_val}-{max_val}%"] = count
        
        # Speakers with various features
        stats["speakers_with_contact"] = self.collection.count_documents({
            "$or": [
                {"contact_info.email": {"$exists": True, "$ne": None}},
                {"contact_info.booking_url": {"$exists": True, "$ne": None}}
            ]
        })
        
        stats["speakers_with_video"] = self.collection.count_documents({
            "media.videos": {"$exists": True, "$ne": []}
        })
        
        stats["speakers_with_testimonials"] = self.collection.count_documents({
            "engagement_history.testimonials": {"$exists": True, "$ne": []}
        })
        
        # Top topics
        pipeline = [
            {"$unwind": "$expertise.topics"},
            {"$group": {"_id": "$expertise.topics", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        stats["top_topics"] = [
            {"topic": item["_id"], "count": item["count"]}
            for item in self.collection.aggregate(pipeline)
        ]
        
        # Top locations
        pipeline = [
            {"$match": {"location.country": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$location.country", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        stats["top_locations"] = [
            {"country": item["_id"], "count": item["count"]}
            for item in self.collection.aggregate(pipeline)
        ]
        
        return stats
    
    def export_results(self, filters: SearchFilters, format: str = "json", 
                      output_file: Optional[str] = None) -> str:
        """Export search results to file"""
        # Get all results (no pagination)
        query = self._build_query(filters)
        results = list(self.collection.find(query))
        
        # Convert ObjectId to string
        for result in results:
            result['_id'] = str(result['_id'])
        
        if format == "json":
            content = json.dumps(results, indent=2, default=str)
        elif format == "csv":
            content = self._to_csv(results)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(content)
            return f"Exported {len(results)} results to {output_file}"
        else:
            return content
    
    def _to_csv(self, results: List[Dict[str, Any]]) -> str:
        """Convert results to CSV format"""
        import csv
        import io
        
        if not results:
            return ""
        
        # Define CSV columns
        fieldnames = [
            "name", "job_title", "company", "location", "email", 
            "website", "topics", "fee_range", "languages", 
            "profile_completeness", "sources"
        ]
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            row = {
                "name": result.get("basic_info", {}).get("full_name", ""),
                "job_title": result.get("professional_info", {}).get("job_title", ""),
                "company": result.get("professional_info", {}).get("company", ""),
                "location": self._format_location(result.get("location", {})),
                "email": result.get("contact_info", {}).get("email", ""),
                "website": result.get("social_media", {}).get("website", ""),
                "topics": ", ".join(result.get("expertise", {}).get("topics", [])),
                "fee_range": result.get("speaking_info", {}).get("fee_info", {}).get("display", "") if result.get("speaking_info", {}).get("fee_info") else "",
                "languages": ", ".join(result.get("speaking_info", {}).get("languages", [])),
                "profile_completeness": result.get("metadata", {}).get("profile_completeness", 0),
                "sources": ", ".join(result.get("metadata", {}).get("sources", []))
            }
            writer.writerow(row)
        
        return output.getvalue()
    
    def _format_location(self, location: Dict[str, Any]) -> str:
        """Format location dict as string"""
        parts = []
        if location.get("city"):
            parts.append(location["city"])
        if location.get("state_province"):
            parts.append(location["state_province"])
        if location.get("country"):
            parts.append(location["country"])
        return ", ".join(parts)


# Example usage and testing
def main():
    """Example usage of the query interface"""
    mongo_uri = "mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin"
    query_interface = ExpertFinderQuery(mongo_uri)
    
    # Example 1: Search for leadership speakers
    print("Example 1: Leadership speakers")
    filters = SearchFilters(
        query="leadership transformation",
        topics=["leadership"],
        min_completeness=50,
        has_video=True,
        page_size=5
    )
    results, total = query_interface.search(filters)
    print(f"Found {total} results")
    for speaker in results:
        print(f"- {speaker['basic_info']['full_name']} ({speaker['metadata']['profile_completeness']}% complete)")
    
    # Example 2: Get facets for filtering
    print("\nExample 2: Available facets")
    facets = query_interface.get_facets()
    print(f"Top countries: {[f['value'] for f in facets['countries'][:5]]}")
    print(f"Top topics: {[f['value'] for f in facets['topics'][:5]]}")
    
    # Example 3: Get statistics
    print("\nExample 3: Database statistics")
    stats = query_interface.get_statistics()
    print(f"Total speakers: {stats['total_speakers']}")
    print(f"Speakers with video: {stats['speakers_with_video']}")
    print(f"Top source: {list(stats['speakers_by_source'].items())[0]}")


if __name__ == "__main__":
    main()