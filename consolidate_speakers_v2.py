#!/usr/bin/env python3
"""
Enhanced Speaker Data Consolidation Script V2
Includes llm_parsed_db and advanced expertise normalization
"""

import pymongo
from pymongo import MongoClient
import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Set
import logging
from collections import defaultdict
from expertise_normalizer import ExpertiseNormalizer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URI = "mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin"
TARGET_DB = "expert_finder_unified_v2"
TARGET_COLLECTION = "speakers"

class EnhancedSpeakerConsolidator:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.target_db = self.client[TARGET_DB]
        self.profiles = {}  # unified_id -> profile
        self.stats = defaultdict(int)
        self.expertise_normalizer = ExpertiseNormalizer()
        
    def run(self):
        """Main consolidation process"""
        logger.info("Starting enhanced speaker data consolidation V2...")
        
        # Process original sources
        logger.info("Processing original speaker databases...")
        self.process_a_speakers()
        self.process_allamericanspeakers()
        self.process_bigspeak()
        self.process_eventraptor()
        self.process_freespeakerbureau()
        self.process_leading_authorities()
        self.process_sessionize()
        self.process_speakerhub()
        self.process_thespeakerhandbook()
        
        # Process new llm_parsed_db
        logger.info("Processing llm_parsed_db collections...")
        self.process_llm_parsed_db()
        
        # Save consolidated data
        self.save_to_mongodb()
        
        # Print statistics
        self.print_stats()
        
        logger.info("Enhanced consolidation complete!")
    
    def generate_unified_id(self, name: str, primary_source: str) -> str:
        """Generate unique ID from normalized name"""
        normalized = name.lower().strip()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        return hashlib.md5(f"{normalized}:{primary_source}".encode()).hexdigest()
    
    def parse_name(self, full_name: str) -> Tuple[str, str, str]:
        """Parse name into components"""
        if not full_name or full_name.lower() in ['none', 'n/a', '']:
            return "", "", ""
            
        # Clean name
        display_name = full_name.strip()
        clean_name = full_name
        
        # Remove common titles
        titles = ['Dr.', 'Dr', 'Mr.', 'Mr', 'Mrs.', 'Mrs', 'Ms.', 'Ms', 'Prof.', 'Prof']
        for title in titles:
            clean_name = re.sub(f'^{title}\\s+', '', clean_name, flags=re.I)
        
        # Remove pronouns
        clean_name = re.sub(r'\s*\(?(she/her|he/him|they/them).*?\)?$', '', clean_name, flags=re.I)
        
        parts = clean_name.strip().split()
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        return first_name, last_name, display_name
    
    def create_profile(self, name: str, source: str) -> Dict[str, Any]:
        """Create empty profile structure with enhanced fields"""
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
                'job_description': None  # New field from llm_parsed_db
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
                'research_areas': [],         # Specific research areas (from llm_parsed_db)
                'industries': [],
                'legacy_topics': []           # Old topic system for backward compatibility
            },
            'education': {                   # New section from llm_parsed_db
                'degrees': [],
                'institutions': [],
                'fields_of_study': []
            },
            'speaking_info': {
                'fee_range': None,
                'languages': [],
                'presentation_types': [],
                'audience_types': [],
                'speech_topics': [],
                'event_types': []            # From llm_parsed_db
            },
            'media': {
                'primary_image': None,
                'images': [],
                'videos': [],
                'speaker_reel': None,
                'one_sheet': None
            },
            'online_presence': {
                'website': None,
                'social_media': {},
                'booking_sites': {}
            },
            'achievements': {
                'books': [],
                'awards': [],
                'certifications': [],
                'media_features': [],
                'patents': [],               # New field
                'publications': []           # Academic publications
            },
            'engagement': {
                'years_experience': None,
                'total_speeches': None,
                'notable_clients': [],
                'testimonials': [],
                'ratings': None,
                'case_studies': []           # New field
            },
            'contact': {
                'email': None,
                'phone': None,
                'agent': None,
                'booking_url': None,
                'preferred_contact': None
            },
            'metadata': {
                'sources': [source],
                'primary_source': source,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'last_verified': None,
                'profile_score': 0,
                'data_quality_tier': None,   # cat_1 through cat_4 from llm_parsed_db
                'verification_status': 'unverified',
                'merge_confidence': 1.0,
                'data_quality': {}
            }
        }
    
    def process_llm_parsed_db(self):
        """Process all categories from llm_parsed_db"""
        db = self.client['llm_parsed_db']
        
        # Process each category (cat_1 = highest quality, cat_4 = lowest)
        for cat_num in range(1, 5):
            cat_name = f'cat_{cat_num}'
            logger.info(f"Processing llm_parsed_db.{cat_name}...")
            
            collection = db[cat_name]
            count = 0
            
            for doc in collection.find():
                try:
                    # Skip if no name
                    name = doc.get('speaker_name', '')
                    if not name or name.lower() in ['none', 'n/a', '']:
                        continue
                    
                    profile = self.create_profile(name, 'llm_parsed_db')
                    
                    # Source ID
                    profile['source_ids']['llm_parsed_db'] = str(doc['_id'])
                    
                    # Professional info
                    profile['professional_info']['title'] = doc.get('job_title')
                    
                    # Biography
                    if doc.get('bio'):
                        profile['biography']['full'] = doc['bio']
                    
                    # Expertise - Use advanced normalization
                    expertise_fields = doc.get('field_of_expertise', [])
                    if expertise_fields:
                        normalized = self.expertise_normalizer.normalize_expertise(expertise_fields)
                        profile['expertise'].update({
                            'primary_categories': normalized['primary_categories'],
                            'secondary_categories': normalized['secondary_categories'],
                            'parent_categories': normalized['parent_categories'],
                            'keywords': normalized['keywords'],
                            'original_terms': normalized['original_terms'],
                            'research_areas': expertise_fields  # Keep original for research areas
                        })
                    
                    # Education
                    if doc.get('education'):
                        for edu in doc['education']:
                            if edu and edu != 'None':
                                # Try to parse degree and institution
                                profile['education']['degrees'].append(edu)
                    
                    # Event types
                    if doc.get('event_types'):
                        profile['speaking_info']['event_types'] = [
                            e for e in doc['event_types'] if e and e != 'None'
                        ]
                    
                    # Quality tier
                    profile['metadata']['data_quality_tier'] = cat_name
                    
                    # Calculate score with tier bonus
                    tier_bonus = {
                        'cat_1': 20,  # Highest quality
                        'cat_2': 10,
                        'cat_3': 5,
                        'cat_4': 0    # Lowest quality
                    }
                    profile['metadata']['profile_score'] = self.calculate_profile_score(profile) + tier_bonus.get(cat_name, 0)
                    
                    # Add or merge
                    unified_id = profile['unified_id']
                    if unified_id in self.profiles:
                        self.profiles[unified_id] = self.merge_profiles(self.profiles[unified_id], profile)
                    else:
                        self.profiles[unified_id] = profile
                    
                    count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {cat_name} document {doc.get('_id')}: {e}")
                    self.stats['errors'] += 1
            
            self.stats[f'llm_parsed_{cat_name}'] = count
            logger.info(f"Processed {count} profiles from {cat_name}")
    
    def merge_profiles(self, existing: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced merge with expertise normalization"""
        # Add source
        if new_data['metadata']['primary_source'] not in existing['metadata']['sources']:
            existing['metadata']['sources'].append(new_data['metadata']['primary_source'])
        
        # Merge source IDs
        existing['source_ids'].update(new_data['source_ids'])
        
        # Merge expertise with normalization
        all_original_terms = existing['expertise'].get('original_terms', []) + new_data['expertise'].get('original_terms', [])
        all_research_areas = existing['expertise'].get('research_areas', []) + new_data['expertise'].get('research_areas', [])
        
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
        
        # Standard merging for other fields...
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
    
    def calculate_profile_score(self, profile: Dict[str, Any]) -> int:
        """Enhanced scoring with expertise categories"""
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
        
        # Expertise (20 points) - Enhanced scoring
        expertise = profile['expertise']
        if len(expertise.get('primary_categories', [])) > 0:
            score += 10
        if len(expertise.get('keywords', [])) > 5:
            score += 5
        if len(expertise.get('research_areas', [])) > 0:
            score += 5
        
        # Education (5 points) - New
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
    
    # Include all the original processing methods (process_a_speakers, etc.)
    # from the original consolidate_speakers.py file here...
    # [The methods would be the same as in the original file]
    
    def save_to_mongodb(self):
        """Save consolidated profiles to MongoDB with enhanced indexing"""
        logger.info(f"Saving {len(self.profiles)} profiles to MongoDB...")
        
        # Drop existing collection
        self.target_db[TARGET_COLLECTION].drop()
        
        # Prepare documents
        documents = []
        for profile in self.profiles.values():
            # Update data quality flags
            profile['metadata']['data_quality'] = {
                'has_email': bool(profile.get('contact', {}).get('email')),
                'has_fee': bool(profile.get('speaking_info', {}).get('fee_range')),
                'has_video': len(profile.get('media', {}).get('videos', [])) > 0,
                'has_testimonials': len(profile.get('engagement', {}).get('testimonials', [])) > 0,
                'has_education': len(profile.get('education', {}).get('degrees', [])) > 0,
                'has_research_areas': len(profile.get('expertise', {}).get('research_areas', [])) > 0,
                'biography_length': len(profile.get('biography', {}).get('full', '')) if profile.get('biography', {}).get('full') else 0,
                'expertise_categories': len(profile.get('expertise', {}).get('primary_categories', []))
            }
            
            documents.append(profile)
        
        # Insert in batches
        batch_size = 1000
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            self.target_db[TARGET_COLLECTION].insert_many(batch)
        
        # Create enhanced indexes
        self.create_indexes()
        
        logger.info(f"Successfully saved {len(documents)} profiles")
        self.stats['saved'] = len(documents)
    
    def create_indexes(self):
        """Create indexes for efficient querying with new fields"""
        logger.info("Creating enhanced indexes...")
        collection = self.target_db[TARGET_COLLECTION]
        
        # Text search index - enhanced
        collection.create_index([
            ("basic_info.full_name", "text"),
            ("professional_info.title", "text"),
            ("professional_info.tagline", "text"),
            ("biography.full", "text"),
            ("expertise.keywords", "text"),
            ("expertise.research_areas", "text"),
            ("education.degrees", "text")
        ])
        
        # Other indexes
        collection.create_index("unified_id", unique=True)
        collection.create_index("basic_info.full_name")
        collection.create_index("location.country")
        collection.create_index("location.city")
        collection.create_index("expertise.primary_categories")
        collection.create_index("expertise.parent_categories")
        collection.create_index("expertise.research_areas")
        collection.create_index("speaking_info.fee_range.category")
        collection.create_index("metadata.profile_score")
        collection.create_index("metadata.sources")
        collection.create_index("metadata.data_quality_tier")
        collection.create_index([("metadata.profile_score", -1)])
        
        logger.info("Enhanced indexes created successfully")
    
    def print_stats(self):
        """Print consolidation statistics"""
        logger.info("\n" + "="*50)
        logger.info("ENHANCED CONSOLIDATION STATISTICS")
        logger.info("="*50)
        
        total_source = sum(v for k, v in self.stats.items() 
                          if k not in ['errors', 'saved'])
        
        logger.info(f"\nSource counts:")
        # Original sources
        for source in ['a_speakers', 'allamericanspeakers', 'bigspeak', 
                      'eventraptor', 'freespeakerbureau', 'leading_authorities',
                      'sessionize', 'speakerhub', 'thespeakerhandbook']:
            if source in self.stats:
                logger.info(f"  {source}: {self.stats[source]:,}")
        
        # New sources
        logger.info(f"\nllm_parsed_db counts:")
        for cat in ['llm_parsed_cat_1', 'llm_parsed_cat_2', 'llm_parsed_cat_3', 'llm_parsed_cat_4']:
            if cat in self.stats:
                logger.info(f"  {cat}: {self.stats[cat]:,}")
        
        logger.info(f"\nTotal source records: {total_source:,}")
        logger.info(f"Unique profiles saved: {self.stats['saved']:,}")
        logger.info(f"Duplicates merged: {total_source - self.stats['saved']:,}")
        logger.info(f"Errors encountered: {self.stats['errors']}")
        
        reduction = ((total_source - self.stats['saved']) / total_source * 100) if total_source > 0 else 0
        logger.info(f"\nData reduction: {reduction:.1f}%")


# Copy all the process_* methods from the original consolidate_speakers.py
# Since they're too long to include here, import them or copy them manually

def main():
    """Run the enhanced consolidation"""
    consolidator = EnhancedSpeakerConsolidator()
    
    # Note: You'll need to copy all the process_* methods from the original
    # consolidate_speakers.py file into the EnhancedSpeakerConsolidator class
    
    consolidator.run()


if __name__ == "__main__":
    main()