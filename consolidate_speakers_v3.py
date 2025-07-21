#!/usr/bin/env python3
"""
Enhanced Speaker Data Consolidation Script V3
Includes Industry Normalization along with Expertise Normalization
Transforms data from 10 MongoDB databases into a unified structure
"""

import pymongo
from pymongo import MongoClient
import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Set
import logging
from collections import defaultdict
from src.normalizers.expertise_normalizer import ExpertiseNormalizer
from src.normalizers.industry_normalizer import IndustryNormalizer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URI = "mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin"
TARGET_DB = "expert_finder_unified_v3"  # New version with industry normalization
TARGET_COLLECTION = "speakers"

# Topic normalization mapping (legacy)
TOPIC_MAPPING = {
    'leadership': ['leadership', 'leader', 'leading', 'executive', 'management'],
    'innovation': ['innovation', 'innovative', 'creativity', 'creative', 'disruption'],
    'technology': ['technology', 'tech', 'digital', 'ai', 'artificial intelligence'],
    'motivation': ['motivation', 'motivational', 'inspiration', 'inspiring'],
    'business': ['business', 'entrepreneurship', 'strategy', 'corporate'],
    'diversity': ['diversity', 'inclusion', 'dei', 'equity', 'inclusive'],
    'communication': ['communication', 'speaking', 'presentation', 'storytelling'],
    'change': ['change', 'transformation', 'transform', 'transition'],
    'wellness': ['wellness', 'wellbeing', 'health', 'mental health', 'mindfulness'],
    'sales': ['sales', 'selling', 'revenue', 'business development'],
    'marketing': ['marketing', 'branding', 'brand', 'digital marketing'],
    'future': ['future', 'trends', 'futurist', 'emerging', 'tomorrow']
}

class EnhancedSpeakerConsolidatorV3:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.target_db = self.client[TARGET_DB]
        self.profiles = {}  # unified_id -> profile
        self.stats = defaultdict(int)
        self.expertise_normalizer = ExpertiseNormalizer()
        self.industry_normalizer = IndustryNormalizer()
        
    def generate_unified_id(self, name: str, source: str) -> str:
        """Generate unique ID for a speaker"""
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        unique_str = f"{clean_name}_{source}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def parse_name(self, name: str) -> Tuple[str, str, str]:
        """Parse name into components"""
        if not name:
            return '', '', name
            
        # Clean the name
        name = re.sub(r'\s+', ' ', name.strip())
        name = re.sub(r'["\']', '', name)
        
        # Handle titles
        titles = ['Dr.', 'Dr', 'Prof.', 'Prof', 'Mr.', 'Mr', 'Mrs.', 'Mrs', 'Ms.', 'Ms']
        display_name = name
        for title in titles:
            name = name.replace(title + ' ', '').replace(' ' + title, '')
        
        # Split name
        parts = name.split()
        if len(parts) >= 2:
            first_name = parts[0]
            last_name = ' '.join(parts[1:])
        elif len(parts) == 1:
            first_name = parts[0]
            last_name = ''
        else:
            first_name = ''
            last_name = ''
            
        return first_name, last_name, display_name
    
    def normalize_location(self, location_data: Any) -> Dict[str, str]:
        """Normalize location information"""
        location = {
            'city': None,
            'state': None,
            'country': None,
            'country_code': None,
            'region': None
        }
        
        if not location_data:
            return location
            
        # Handle string location
        if isinstance(location_data, str):
            parts = [p.strip() for p in location_data.split(',')]
            if len(parts) >= 3:
                location['city'] = parts[0]
                location['state'] = parts[1]
                location['country'] = parts[2]
            elif len(parts) == 2:
                location['state'] = parts[0]
                location['country'] = parts[1]
            elif len(parts) == 1:
                location['country'] = parts[0]
                
        # Handle dict location
        elif isinstance(location_data, dict):
            location['city'] = location_data.get('city')
            location['state'] = location_data.get('state', location_data.get('province'))
            location['country'] = location_data.get('country')
            
        # Normalize country names
        country_mapping = {
            'usa': 'United States',
            'us': 'United States',
            'uk': 'United Kingdom',
            'gb': 'United Kingdom',
            'can': 'Canada',
            'ca': 'Canada',
            'aus': 'Australia',
            'au': 'Australia'
        }
        
        if location['country']:
            country_lower = location['country'].lower()
            location['country'] = country_mapping.get(country_lower, location['country'])
            
        return location
    
    def create_profile(self, name: str, source: str) -> Dict[str, Any]:
        """Create empty profile structure with enhanced fields including industry"""
        first_name, last_name, display_name = self.parse_name(name)
        unified_id = self.generate_unified_id(name, source)
        
        return {
            'unified_id': unified_id,
            'source_ids': {},
            'basic_info': {
                'full_name': name,
                'first_name': first_name,
                'last_name': last_name,
                'display_name': display_name,
                'gender': None,
                'pronouns': None
            },
            'professional_info': {
                'title': None,
                'company': None,
                'tagline': None,
                'credentials': [],
                'years_speaking': None,
                'job_description': None
            },
            'location': {
                'city': None,
                'state': None,
                'country': None,
                'country_code': None,
                'region': None,
                'available_for_travel': True,
                'virtual_available': True
            },
            'biography': {
                'brief': None,
                'short': None,
                'full': None
            },
            'expertise': {
                'primary_categories': [],      # From normalized taxonomy
                'secondary_categories': [],    # From normalized taxonomy
                'parent_categories': [],       # High-level categories
                'keywords': [],               # All searchable keywords
                'original_terms': [],         # Original expertise terms
                'research_areas': [],         # Specific research areas
                'industries': [],             # Raw industry data
                'normalized_industries': {     # NEW: Normalized industries
                    'primary': [],
                    'secondary': [],
                    'keywords': []
                },
                'legacy_topics': []           # Old topic system
            },
            'speaking_info': {
                'fee_range': None,
                'fee_details': {},
                'languages': [],
                'presentation_types': [],
                'audience_types': [],
                'event_types': []
            },
            'media': {
                'primary_image': None,
                'images': [],
                'videos': [],
                'audio_clips': [],
                'one_sheets': []
            },
            'achievements': {
                'awards': [],
                'books': [],
                'certifications': [],
                'patents': [],
                'publications': []
            },
            'education': {
                'degrees': [],
                'institutions': [],
                'fields_of_study': []
            },
            'online_presence': {
                'website': None,
                'social_media': {},
                'booking_sites': {}
            },
            'contact': {
                'email': None,
                'phone': None,
                'booking_url': None,
                'agent_info': {}
            },
            'engagement': {
                'testimonials': [],
                'case_studies': [],
                'ratings': {},
                'total_bookings': None
            },
            'metadata': {
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'last_verified': None,
                'profile_score': 0,
                'data_quality_tier': None,
                'primary_source': source,
                'sources': [source],
                'verification_status': 'unverified',
                'profile_active': True
            }
        }
    
    def process_allamericanspeakers(self):
        """Process data from allamericanspeakers with industry normalization"""
        db = self.client['allamericanspeakers']
        collection = db['speakers']
        
        logger.info("Processing allamericanspeakers...")
        
        for doc in collection.find():
            try:
                name = doc.get('name', '')
                if not name or name.lower() in ['none', 'n/a', '']:
                    continue
                
                profile = self.create_profile(name, 'allamericanspeakers')
                
                # Source ID
                profile['source_ids']['allamericanspeakers'] = doc.get('speaker_id', str(doc['_id']))
                
                # Professional info
                profile['professional_info']['title'] = doc.get('job_title')
                
                # Biography
                profile['biography']['full'] = doc.get('biography')
                
                # Location
                if doc.get('location'):
                    profile['location'] = self.normalize_location(doc['location'])
                
                # Topics and expertise normalization
                topics = doc.get('categories', [])
                if topics:
                    # Original expertise normalization
                    normalized = self.expertise_normalizer.normalize_expertise(topics)
                    profile['expertise'].update({
                        'primary_categories': normalized['primary_categories'],
                        'secondary_categories': normalized['secondary_categories'],
                        'parent_categories': normalized['parent_categories'],
                        'keywords': normalized['keywords'],
                        'original_terms': normalized['original_terms']
                    })
                    
                    # NEW: Industry normalization
                    industry_result = self.industry_normalizer.merge_with_categories(topics)
                    profile['expertise']['industries'] = topics  # Keep raw data
                    profile['expertise']['normalized_industries'] = {
                        'primary': industry_result['primary_industries'],
                        'secondary': industry_result['secondary_industries'],
                        'keywords': industry_result['keywords']
                    }
                
                # Media
                if doc.get('image_url'):
                    profile['media']['primary_image'] = doc['image_url']
                    profile['media']['images'] = [doc['image_url']]
                
                # Videos
                if doc.get('videos'):
                    for video in doc['videos']:
                        if isinstance(video, dict):
                            profile['media']['videos'].append({
                                'url': video.get('url', ''),
                                'title': video.get('title', ''),
                                'type': 'demo'
                            })
                
                # Testimonials
                if doc.get('reviews'):
                    for review in doc['reviews']:
                        profile['engagement']['testimonials'].append({
                            'text': review.get('text', ''),
                            'rating': review.get('rating'),
                            'author_name': review.get('author', '')
                        })
                
                # Fee range
                if doc.get('fee_range'):
                    if isinstance(doc['fee_range'], dict):
                        profile['speaking_info']['fee_range'] = doc['fee_range'].get('live_event')
                    else:
                        profile['speaking_info']['fee_range'] = doc['fee_range']
                
                # Online presence
                profile['online_presence']['booking_sites']['allamericanspeakers'] = doc.get('url')
                
                # Calculate score
                profile['metadata']['profile_score'] = self.calculate_profile_score(profile)
                
                # Add or merge
                unified_id = profile['unified_id']
                if unified_id in self.profiles:
                    self.profiles[unified_id] = self.merge_profiles(self.profiles[unified_id], profile)
                else:
                    self.profiles[unified_id] = profile
                
                self.stats['allamericanspeakers'] += 1
                
            except Exception as e:
                logger.error(f"Error processing allamericanspeakers record: {e}")
                self.stats['errors'] += 1
    
    def calculate_profile_score(self, profile: Dict[str, Any]) -> int:
        """Enhanced scoring with industry normalization"""
        score = 0
        
        # Basic info (20 points)
        if profile['basic_info']['full_name']:
            score += 10
        if profile['basic_info']['first_name'] and profile['basic_info']['last_name']:
            score += 5
        if profile['basic_info'].get('display_name'):
            score += 5
        
        # Professional info (10 points)
        if profile['professional_info'].get('title'):
            score += 5
        if profile['professional_info'].get('tagline'):
            score += 5
        
        # Biography (15 points)
        bio = profile['biography']
        if bio.get('full'):
            if len(bio['full']) > 500:
                score += 15
            elif len(bio['full']) > 200:
                score += 10
            else:
                score += 5
        
        # Location (10 points)
        loc = profile['location']
        if loc.get('country'):
            score += 5
        if loc.get('city') or loc.get('state'):
            score += 5
        
        # Expertise (20 points) - Enhanced with industry scoring
        expertise = profile['expertise']
        if len(expertise.get('primary_categories', [])) > 0:
            score += 8
        if len(expertise.get('keywords', [])) > 5:
            score += 4
        if len(expertise.get('research_areas', [])) > 0:
            score += 4
        # NEW: Industry normalization bonus
        if len(expertise.get('normalized_industries', {}).get('primary', [])) > 0:
            score += 4
        
        # Education (5 points)
        if len(profile.get('education', {}).get('degrees', [])) > 0:
            score += 5
        
        # Fee info (5 points)
        if profile['speaking_info'].get('fee_range'):
            score += 5
        
        # Media (10 points)
        if profile['media'].get('images'):
            score += 5
        if profile['media'].get('videos'):
            score += 5
        
        # Contact (5 points)
        if profile['contact'].get('email') or profile['contact'].get('booking_url'):
            score += 5
        
        return min(score, 100)
    
    def merge_profiles(self, existing: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced merge with industry normalization"""
        # Add source
        if new_data['metadata']['primary_source'] not in existing['metadata']['sources']:
            existing['metadata']['sources'].append(new_data['metadata']['primary_source'])
        
        # Merge source IDs
        existing['source_ids'].update(new_data['source_ids'])
        
        # Merge expertise with normalization
        all_original_terms = existing['expertise'].get('original_terms', []) + new_data['expertise'].get('original_terms', [])
        all_research_areas = existing['expertise'].get('research_areas', []) + new_data['expertise'].get('research_areas', [])
        all_industries = existing['expertise'].get('industries', []) + new_data['expertise'].get('industries', [])
        
        # Re-normalize combined expertise
        if all_original_terms:
            normalized = self.expertise_normalizer.normalize_expertise(list(set(all_original_terms)))
            existing['expertise'].update({
                'primary_categories': normalized['primary_categories'],
                'secondary_categories': normalized['secondary_categories'],
                'parent_categories': normalized['parent_categories'],
                'keywords': normalized['keywords'],
                'original_terms': normalized['original_terms']
            })
        
        # Re-normalize combined industries
        if all_industries:
            industry_result = self.industry_normalizer.merge_with_categories(list(set(all_industries)))
            existing['expertise']['industries'] = list(set(all_industries))
            existing['expertise']['normalized_industries'] = {
                'primary': industry_result['primary_industries'],
                'secondary': industry_result['secondary_industries'],
                'keywords': industry_result['keywords']
            }
        
        # Keep unique research areas
        existing['expertise']['research_areas'] = list(set(all_research_areas))
        
        # Merge education
        if new_data.get('education', {}).get('degrees'):
            existing['education']['degrees'].extend(new_data['education']['degrees'])
            existing['education']['degrees'] = list(set(existing['education']['degrees']))
        
        # Take highest quality tier
        if new_data['metadata'].get('data_quality_tier'):
            if not existing['metadata'].get('data_quality_tier') or \
               int(new_data['metadata']['data_quality_tier'].split('_')[1]) < int(existing['metadata']['data_quality_tier'].split('_')[1]):
                existing['metadata']['data_quality_tier'] = new_data['metadata']['data_quality_tier']
        
        # Standard merging for other fields
        self._merge_field(existing['professional_info'], new_data['professional_info'], 'title')
        self._merge_field(existing['professional_info'], new_data['professional_info'], 'company')
        self._merge_field(existing['biography'], new_data['biography'], 'full')
        self._merge_field(existing['contact'], new_data['contact'], 'email')
        
        # Merge arrays
        existing['media']['images'].extend(new_data['media'].get('images', []))
        existing['media']['videos'].extend(new_data['media'].get('videos', []))
        existing['speaking_info']['event_types'].extend(new_data['speaking_info'].get('event_types', []))
        
        # Remove duplicates
        existing['media']['images'] = list(set(existing['media']['images']))
        existing['speaking_info']['event_types'] = list(set(existing['speaking_info']['event_types']))
        
        # Update metadata
        existing['metadata']['updated_at'] = datetime.now(timezone.utc)
        
        # Recalculate score
        existing['metadata']['profile_score'] = self.calculate_profile_score(existing)
        
        return existing
    
    def _merge_field(self, target_obj: Any, source_obj: Any, field_name: str):
        """Merge a single field, preferring non-empty values"""
        target_val = getattr(target_obj, field_name) if hasattr(target_obj, '__getattr__') else target_obj.get(field_name)
        source_val = getattr(source_obj, field_name) if hasattr(source_obj, '__getattr__') else source_obj.get(field_name)
        
        if not target_val and source_val:
            if hasattr(target_obj, '__setattr__'):
                setattr(target_obj, field_name, source_val)
            else:
                target_obj[field_name] = source_val
    
    def save_to_mongodb(self):
        """Save consolidated profiles to MongoDB"""
        collection = self.target_db[TARGET_COLLECTION]
        
        # Clear existing data
        logger.info(f"Clearing existing data in {TARGET_DB}.{TARGET_COLLECTION}")
        collection.drop()
        
        # Insert all profiles
        logger.info(f"Inserting {len(self.profiles)} profiles...")
        if self.profiles:
            documents = list(self.profiles.values())
            collection.insert_many(documents)
        
        # Create indexes
        self.create_indexes(collection)
        
        logger.info("Data saved successfully!")
    
    def create_indexes(self, collection):
        """Create indexes for efficient querying with industry support"""
        logger.info("Creating indexes...")
        
        # Text index for full-text search
        collection.create_index([
            ("basic_info.full_name", "text"),
            ("biography.full", "text"),
            ("professional_info.title", "text"),
            ("expertise.keywords", "text"),
            ("expertise.normalized_industries.keywords", "text")  # NEW
        ])
        
        # Single field indexes
        collection.create_index("unified_id", unique=True)
        collection.create_index("basic_info.last_name")
        collection.create_index("location.country")
        collection.create_index("location.state")
        collection.create_index("expertise.primary_categories")
        collection.create_index("expertise.parent_categories")
        collection.create_index("expertise.normalized_industries.primary")  # NEW
        collection.create_index("metadata.profile_score")
        collection.create_index("metadata.data_quality_tier")
        collection.create_index("metadata.sources")
        
        # Compound indexes
        collection.create_index([
            ("location.country", 1),
            ("expertise.primary_categories", 1)
        ])
        
        collection.create_index([
            ("expertise.normalized_industries.primary", 1),  # NEW
            ("metadata.profile_score", -1)
        ])
        
        logger.info("Indexes created successfully!")
    
    def print_stats(self):
        """Print consolidation statistics"""
        print("\n" + "="*50)
        print("ENHANCED CONSOLIDATION STATISTICS (V3)")
        print("="*50)
        print(f"Total unique profiles: {len(self.profiles)}")
        print("\nProfiles by source:")
        for source, count in sorted(self.stats.items()):
            if source != 'errors':
                print(f"  {source}: {count}")
        print(f"\nErrors encountered: {self.stats['errors']}")
        
        # Industry statistics
        industry_stats = defaultdict(int)
        for profile in self.profiles.values():
            for industry in profile['expertise'].get('normalized_industries', {}).get('primary', []):
                industry_stats[industry] += 1
        
        if industry_stats:
            print("\nTop Industries (Normalized):")
            for industry, count in sorted(industry_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                industry_info = self.industry_normalizer.get_industry_info(industry)
                if industry_info:
                    print(f"  {industry_info['display_name']}: {count}")
    
    def consolidate(self):
        """Main consolidation with simplified single source for testing"""
        logger.info("Starting enhanced speaker data consolidation V3...")
        
        # Process just allamericanspeakers for testing
        self.process_allamericanspeakers()
        
        # Save to MongoDB
        self.save_to_mongodb()
        
        # Print statistics
        self.print_stats()
        
        logger.info("Consolidation complete!")


def main():
    consolidator = EnhancedSpeakerConsolidatorV3()
    consolidator.consolidate()


if __name__ == "__main__":
    main()