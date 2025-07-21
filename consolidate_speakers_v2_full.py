#!/usr/bin/env python3
"""
Enhanced Speaker Data Consolidation Script V2
Transforms data from 10 MongoDB databases into a unified structure
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
from src.normalizers.expertise_normalizer import ExpertiseNormalizer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URI = "mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin"
TARGET_DB = "expert_finder_unified_v2"
TARGET_COLLECTION = "speakers"

# Topic normalization mapping
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
    
    def parse_location(self, location_data) -> Dict[str, Any]:
        """Parse location string or dict into components"""
        if not location_data:
            return {}
            
        # Handle dict input
        if isinstance(location_data, dict):
            return {
                'city': location_data.get('city'),
                'state': location_data.get('state') or location_data.get('state_province'),
                'country': self.normalize_country(location_data.get('country', '')),
                'country_code': location_data.get('country_code'),
                'region': location_data.get('region')
            }
            
        # Handle string input
        if not isinstance(location_data, str):
            return {}
            
        location_str = location_data
        location = {
            'city': None,
            'state': None,
            'country': None,
            'country_code': None,
            'region': None
        }
        
        # Clean and split
        parts = [p.strip() for p in location_str.split(',')]
        
        if len(parts) == 1:
            # Assume country
            location['country'] = self.normalize_country(parts[0])
        elif len(parts) == 2:
            # City, Country or City, State (US)
            location['city'] = parts[0]
            if self.is_us_state(parts[1]):
                location['state'] = parts[1]
                location['country'] = 'United States'
            else:
                location['country'] = self.normalize_country(parts[1])
        elif len(parts) >= 3:
            location['city'] = parts[0]
            location['state'] = parts[1]
            location['country'] = self.normalize_country(parts[2])
        
        # Add country code and region
        if location['country']:
            location['country_code'] = self.get_country_code(location['country'])
            location['region'] = self.get_region(location['country'])
            
        return location
    
    def normalize_country(self, country: str) -> str:
        """Normalize country names"""
        country = country.strip()
        
        # Common mappings
        mappings = {
            'usa': 'United States',
            'us': 'United States',
            'united states of america': 'United States',
            'uk': 'United Kingdom',
            'gb': 'United Kingdom',
            'great britain': 'United Kingdom'
        }
        
        return mappings.get(country.lower(), country)
    
    def is_us_state(self, text: str) -> bool:
        """Check if text is a US state"""
        states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        }
        return text.upper() in states
    
    def get_country_code(self, country: str) -> Optional[str]:
        """Get ISO country code"""
        codes = {
            'United States': 'US',
            'United Kingdom': 'UK',
            'Canada': 'CA',
            'Australia': 'AU',
            'Germany': 'DE',
            'France': 'FR',
            'Spain': 'ES',
            'Italy': 'IT',
            'Netherlands': 'NL',
            'Switzerland': 'CH'
        }
        return codes.get(country)
    
    def get_region(self, country: str) -> Optional[str]:
        """Get geographical region"""
        regions = {
            'United States': 'North America',
            'Canada': 'North America',
            'Mexico': 'North America',
            'United Kingdom': 'Europe',
            'Germany': 'Europe',
            'France': 'Europe',
            'Australia': 'Oceania',
            'New Zealand': 'Oceania',
            'Japan': 'Asia',
            'China': 'Asia',
            'India': 'Asia',
            'Brazil': 'South America',
            'Argentina': 'South America'
        }
        return regions.get(country, 'Other')
    
    def parse_fee(self, fee_text: str) -> Dict[str, Any]:
        """Parse fee text into structured format"""
        if not fee_text:
            return None
            
        fee_info = {
            'min': None,
            'max': None,
            'currency': 'USD',
            'display': fee_text,
            'category': None,
            'negotiable': True
        }
        
        # Handle special cases
        if any(word in fee_text.lower() for word in ['inquire', 'contact', 'request', 'call']):
            fee_info['category'] = 'inquire'
            return fee_info
        
        # Extract numbers
        numbers = re.findall(r'\$?([\d,]+)', fee_text)
        if numbers:
            amounts = []
            for n in numbers:
                try:
                    if n.strip():  # Skip empty strings
                        amounts.append(int(n.replace(',', '')))
                except ValueError:
                    continue
            
            if amounts and 'under' in fee_text.lower():
                fee_info['max'] = amounts[0]
                fee_info['category'] = self.categorize_fee(0, amounts[0])
            elif amounts and ('over' in fee_text.lower() or '+' in fee_text):
                fee_info['min'] = amounts[0]
                fee_info['category'] = self.categorize_fee(amounts[0], float('inf'))
            elif amounts and len(amounts) >= 2:
                fee_info['min'] = amounts[0]
                fee_info['max'] = amounts[1]
                fee_info['category'] = self.categorize_fee(amounts[0], amounts[1])
            elif amounts:
                # Single amount
                fee_info['min'] = amounts[0]
                fee_info['max'] = amounts[0]
                fee_info['category'] = self.categorize_fee(amounts[0], amounts[0])
                
        return fee_info
    
    def categorize_fee(self, min_fee: float, max_fee: float) -> str:
        """Categorize fee into brackets"""
        avg = (min_fee + max_fee) / 2 if max_fee != float('inf') else min_fee
        
        if avg < 5000:
            return 'under-5k'
        elif avg < 10000:
            return '5k-10k'
        elif avg < 20000:
            return '10k-20k'
        elif avg < 30000:
            return '20k-30k'
        elif avg < 50000:
            return '30k-50k'
        elif avg < 75000:
            return '50k-75k'
        elif avg < 100000:
            return '75k-100k'
        else:
            return 'over-100k'
    
    def normalize_topics(self, topics: List[str]) -> Tuple[List[str], List[str]]:
        """Normalize topics to primary categories and preserve all"""
        if not topics:
            return [], []
            
        primary_topics = set()
        all_topics = []
        
        for topic in topics:
            if not topic:
                continue
                
            # Clean topic
            clean_topic = topic.strip()
            all_topics.append(clean_topic)
            
            # Check for primary category matches
            topic_lower = clean_topic.lower()
            for primary, keywords in TOPIC_MAPPING.items():
                if any(keyword in topic_lower for keyword in keywords):
                    primary_topics.add(primary)
                    
        return list(primary_topics), all_topics
    
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
    
    def process_a_speakers(self):
        """Process a_speakers database"""
        logger.info("Processing a_speakers...")
        db = self.client['a_speakers']
        collection = db['speakers']
        
        for doc in collection.find():
            try:
                name = doc.get('name', '')
                if not name:
                    continue
                    
                profile = self.create_profile(name, 'a_speakers')
                
                # Update source ID
                profile['source_ids']['a_speakers'] = doc.get('url', str(doc['_id']))
                
                # Professional info
                profile['professional_info']['title'] = doc.get('job_title')
                profile['professional_info']['tagline'] = doc.get('description')
                
                # Location
                if doc.get('location'):
                    profile['location'] = self.parse_location(doc['location'])
                    
                # Biography
                profile['biography']['full'] = doc.get('full_bio')
                profile['biography']['short'] = doc.get('description')
                
                # Topics - Store in legacy format and as original terms for normalization
                topics = doc.get('topics', [])
                primary_topics, all_topics = self.normalize_topics(topics)
                profile['expertise']['legacy_topics'] = primary_topics
                profile['expertise']['original_terms'] = topics
                
                # Use expertise normalizer
                if topics:
                    normalized = self.expertise_normalizer.normalize_expertise(topics)
                    profile['expertise'].update({
                        'primary_categories': normalized['primary_categories'],
                        'secondary_categories': normalized['secondary_categories'],
                        'parent_categories': normalized['parent_categories'],
                        'keywords': normalized['keywords'],
                        'original_terms': normalized['original_terms']
                    })
                
                # Fee
                if doc.get('fee_range'):
                    profile['speaking_info']['fee_range'] = self.parse_fee(doc['fee_range'])
                    
                # Media
                if doc.get('image_url'):
                    profile['media']['primary_image'] = doc['image_url']
                    profile['media']['images'] = [doc['image_url']]
                    
                if doc.get('videos'):
                    videos = []
                    for v in doc['videos']:
                        if isinstance(v, dict):
                            videos.append({
                                'url': v.get('url', ''),
                                'title': v.get('title', ''),
                                'type': 'demo'
                            })
                        elif isinstance(v, str) and v:
                            videos.append({'url': v, 'type': 'demo'})
                    profile['media']['videos'] = videos
                    
                # Ratings
                if doc.get('average_rating'):
                    profile['engagement']['ratings'] = {
                        'average': doc['average_rating'],
                        'count': doc.get('total_reviews', 0),
                        'distribution': {}
                    }
                    
                # Booking site
                profile['online_presence']['booking_sites']['a_speakers'] = doc.get('url')
                
                # Calculate score
                profile['metadata']['profile_score'] = self.calculate_profile_score(profile)
                
                # Add or merge
                unified_id = profile['unified_id']
                if unified_id in self.profiles:
                    self.profiles[unified_id] = self.merge_profiles(self.profiles[unified_id], profile)
                else:
                    self.profiles[unified_id] = profile
                    
                self.stats['a_speakers'] += 1
                
            except Exception as e:
                logger.error(f"Error processing a_speakers record: {e}")
                self.stats['errors'] += 1
    
    def process_allamericanspeakers(self):
        """Process allamericanspeakers database"""
        logger.info("Processing allamericanspeakers...")
        db = self.client['allamericanspeakers']
        collection = db['speakers']
        
        for doc in collection.find():
            try:
                name = doc.get('name', '')
                if not name:
                    continue
                    
                profile = self.create_profile(name, 'allamericanspeakers')
                
                # Source ID
                profile['source_ids']['allamericanspeakers'] = doc.get('speaker_id', str(doc['_id']))
                
                # Professional info
                profile['professional_info']['title'] = doc.get('job_title')
                
                # Location
                if doc.get('location'):
                    profile['location'] = self.parse_location(doc['location'])
                    
                # Biography
                profile['biography']['full'] = doc.get('biography')
                
                # Topics - Store in legacy format and as original terms for normalization
                topics = doc.get('speaking_topics', [])
                primary_topics, all_topics = self.normalize_topics(topics)
                profile['expertise']['legacy_topics'] = primary_topics
                profile['expertise']['original_terms'] = topics
                profile['expertise']['industries'] = doc.get('categories', [])
                
                # Use expertise normalizer
                if topics:
                    normalized = self.expertise_normalizer.normalize_expertise(topics)
                    profile['expertise'].update({
                        'primary_categories': normalized['primary_categories'],
                        'secondary_categories': normalized['secondary_categories'],
                        'parent_categories': normalized['parent_categories'],
                        'keywords': normalized['keywords'],
                        'original_terms': normalized['original_terms']
                    })
                
                # Fee (handle object format)
                if doc.get('fee_range') and isinstance(doc['fee_range'], dict):
                    fee_obj = doc['fee_range']
                    profile['speaking_info']['fee_range'] = {
                        'min': fee_obj.get('min'),
                        'max': fee_obj.get('max'),
                        'display': fee_obj.get('text', str(fee_obj)),
                        'currency': 'USD'
                    }
                    
                # Videos
                if doc.get('videos'):
                    videos = []
                    for v in doc['videos']:
                        if isinstance(v, dict):
                            videos.append({
                                'url': v.get('url', ''),
                                'title': v.get('title', ''),
                                'type': 'demo'
                            })
                        elif isinstance(v, str) and v:
                            videos.append({'url': v, 'type': 'demo'})
                    profile['media']['videos'] = videos
                    
                # Booking site
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
    
    def process_bigspeak(self):
        """Process bigspeak database"""
        logger.info("Processing bigspeak...")
        db = self.client['bigspeak_scraper']
        speakers_col = db['speakers']
        profiles_col = db['speaker_profiles']
        
        # Create speaker_id -> profile mapping
        profile_map = {}
        for p in profiles_col.find():
            profile_map[p.get('speaker_id')] = p
            
        for doc in speakers_col.find():
            try:
                name = doc.get('name', '')
                if not name:
                    continue
                    
                profile = self.create_profile(name, 'bigspeak')
                detailed = profile_map.get(doc.get('speaker_id'))
                
                # Source ID
                profile['source_ids']['bigspeak'] = doc.get('speaker_id', str(doc['_id']))
                
                # Professional info
                profile['professional_info']['tagline'] = doc.get('description')
                
                # Biography
                if detailed and detailed.get('biography'):
                    profile['biography']['full'] = detailed['biography']
                else:
                    profile['biography']['short'] = doc.get('description')
                    
                # Topics - Store in legacy format and as original terms for normalization
                topics = doc.get('topics', [])
                if detailed and detailed.get('keynote_topics'):
                    topics.extend(detailed['keynote_topics'])
                primary_topics, all_topics = self.normalize_topics(topics)
                profile['expertise']['legacy_topics'] = primary_topics
                profile['expertise']['original_terms'] = topics
                
                # Use expertise normalizer
                if topics:
                    normalized = self.expertise_normalizer.normalize_expertise(topics)
                    profile['expertise'].update({
                        'primary_categories': normalized['primary_categories'],
                        'secondary_categories': normalized['secondary_categories'],
                        'parent_categories': normalized['parent_categories'],
                        'keywords': normalized['keywords'],
                        'original_terms': normalized['original_terms']
                    })
                
                # Fee
                if doc.get('fee_range'):
                    profile['speaking_info']['fee_range'] = self.parse_fee(doc['fee_range'])
                    
                # Languages
                if detailed and detailed.get('languages'):
                    profile['speaking_info']['languages'] = detailed['languages']
                    
                # Media
                if doc.get('image_url'):
                    profile['media']['primary_image'] = doc['image_url']
                    profile['media']['images'] = [doc['image_url']]
                    
                if detailed and detailed.get('videos'):
                    videos = []
                    for v in detailed['videos']:
                        if isinstance(v, dict):
                            videos.append({
                                'url': v.get('url', ''),
                                'title': v.get('title', ''),
                                'type': 'demo'
                            })
                        elif isinstance(v, str) and v:
                            videos.append({'url': v, 'type': 'demo'})
                    profile['media']['videos'] = videos
                    
                # Books
                if detailed and detailed.get('books'):
                    profile['achievements']['books'] = [
                        {'title': b} for b in detailed['books'] if b
                    ]
                    
                # Awards
                if detailed and detailed.get('awards'):
                    profile['achievements']['awards'] = detailed['awards']
                    
                # Testimonials
                if detailed and detailed.get('testimonials'):
                    profile['engagement']['testimonials'] = [
                        {'text': t} for t in detailed['testimonials'] if t
                    ]
                    
                # Social media
                if detailed and detailed.get('social_media'):
                    profile['online_presence']['social_media'] = detailed['social_media']
                    
                # Booking site
                profile['online_presence']['booking_sites']['bigspeak'] = doc.get('profile_url')
                
                # Calculate score
                profile['metadata']['profile_score'] = self.calculate_profile_score(profile)
                
                # Add or merge
                unified_id = profile['unified_id']
                if unified_id in self.profiles:
                    self.profiles[unified_id] = self.merge_profiles(self.profiles[unified_id], profile)
                else:
                    self.profiles[unified_id] = profile
                    
                self.stats['bigspeak'] += 1
                
            except Exception as e:
                logger.error(f"Error processing bigspeak record: {e}")
                self.stats['errors'] += 1
    
    def process_eventraptor(self):
        """Process eventraptor database"""
        logger.info("Processing eventraptor...")
        db = self.client['eventraptor']
        collection = db['speakers']
        
        for doc in collection.find():
            try:
                name = doc.get('name', '')
                if not name:
                    continue
                    
                # Clean pronouns from name
                name = re.sub(r'\s*\(?(she/her|he/him|they/them).*?\)?$', '', name, flags=re.I).strip()
                
                profile = self.create_profile(name, 'eventraptor')
                
                # Source ID
                profile['source_ids']['eventraptor'] = doc.get('speaker_id', str(doc['_id']))
                
                # Professional info
                profile['professional_info']['tagline'] = doc.get('tagline')
                if doc.get('credentials'):
                    profile['professional_info']['credentials'] = doc['credentials'].split(',')
                    
                # Biography
                profile['biography']['full'] = doc.get('biography')
                
                # Topics/Business areas - Store in legacy format and as original terms for normalization
                topics = doc.get('business_areas', [])
                primary_topics, all_topics = self.normalize_topics(topics)
                profile['expertise']['legacy_topics'] = primary_topics
                profile['expertise']['original_terms'] = topics
                
                # Use expertise normalizer
                if topics:
                    normalized = self.expertise_normalizer.normalize_expertise(topics)
                    profile['expertise'].update({
                        'primary_categories': normalized['primary_categories'],
                        'secondary_categories': normalized['secondary_categories'],
                        'parent_categories': normalized['parent_categories'],
                        'keywords': normalized['keywords'],
                        'original_terms': normalized['original_terms']
                    })
                
                # Contact
                if doc.get('email'):
                    profile['contact']['email'] = doc['email']
                    
                # Events
                if doc.get('events'):
                    profile['engagement']['total_speeches'] = len(doc['events'])
                    
                # Media
                if doc.get('profile_image'):
                    profile['media']['primary_image'] = doc['profile_image']
                    profile['media']['images'] = [doc['profile_image']]
                    
                # Social media
                if doc.get('social_media'):
                    profile['online_presence']['social_media'] = doc['social_media']
                    
                # Booking site
                profile['online_presence']['booking_sites']['eventraptor'] = doc.get('url')
                
                # Calculate score
                profile['metadata']['profile_score'] = self.calculate_profile_score(profile)
                
                # Add or merge
                unified_id = profile['unified_id']
                if unified_id in self.profiles:
                    self.profiles[unified_id] = self.merge_profiles(self.profiles[unified_id], profile)
                else:
                    self.profiles[unified_id] = profile
                    
                self.stats['eventraptor'] += 1
                
            except Exception as e:
                logger.error(f"Error processing eventraptor record: {e}")
                self.stats['errors'] += 1
    
    def process_freespeakerbureau(self):
        """Process freespeakerbureau database"""
        logger.info("Processing freespeakerbureau...")
        db = self.client['freespeakerbureau_scraper']
        collection = db['speakers_profiles']
        
        for doc in collection.find():
            try:
                name = doc.get('name', '')
                if not name:
                    continue
                    
                profile = self.create_profile(name, 'freespeakerbureau')
                
                # Source ID
                profile['source_ids']['freespeakerbureau'] = str(doc['_id'])
                
                # Professional info
                profile['professional_info']['title'] = doc.get('role')
                profile['professional_info']['company'] = doc.get('company')
                
                # Location
                location_parts = []
                if doc.get('city'):
                    location_parts.append(doc['city'])
                if doc.get('state'):
                    location_parts.append(doc['state'])
                if doc.get('country'):
                    location_parts.append(doc['country'])
                if location_parts:
                    profile['location'] = self.parse_location(', '.join(location_parts))
                    
                # Biography
                profile['biography']['full'] = doc.get('biography')
                
                # Topics - Store in legacy format and as original terms for normalization
                topics = doc.get('speaking_topics', [])
                primary_topics, all_topics = self.normalize_topics(topics)
                profile['expertise']['legacy_topics'] = primary_topics
                profile['expertise']['original_terms'] = topics
                profile['expertise']['industries'] = doc.get('areas_of_expertise', [])
                
                # Use expertise normalizer
                if topics:
                    normalized = self.expertise_normalizer.normalize_expertise(topics)
                    profile['expertise'].update({
                        'primary_categories': normalized['primary_categories'],
                        'secondary_categories': normalized['secondary_categories'],
                        'parent_categories': normalized['parent_categories'],
                        'keywords': normalized['keywords'],
                        'original_terms': normalized['original_terms']
                    })
                
                # Contact
                if doc.get('contact_info'):
                    contact = doc['contact_info']
                    profile['contact']['email'] = contact.get('email')
                    profile['contact']['phone'] = contact.get('phone')
                    
                # Awards
                if doc.get('awards'):
                    profile['achievements']['awards'] = [doc['awards']]
                    
                # Social media
                if doc.get('social_media'):
                    profile['online_presence']['social_media'] = doc['social_media']
                    
                # One sheet
                if doc.get('speaker_onesheet_url'):
                    profile['media']['one_sheet'] = doc['speaker_onesheet_url']
                    
                # Years speaking
                if doc.get('speaker_since'):
                    years = datetime.now(timezone.utc).year - doc['speaker_since']
                    profile['professional_info']['years_speaking'] = years
                    profile['engagement']['years_experience'] = years
                    
                # Booking site
                profile['online_presence']['booking_sites']['freespeakerbureau'] = doc.get('profile_url')
                
                # Calculate score
                profile['metadata']['profile_score'] = self.calculate_profile_score(profile)
                
                # Add or merge
                unified_id = profile['unified_id']
                if unified_id in self.profiles:
                    self.profiles[unified_id] = self.merge_profiles(self.profiles[unified_id], profile)
                else:
                    self.profiles[unified_id] = profile
                    
                self.stats['freespeakerbureau'] += 1
                
            except Exception as e:
                logger.error(f"Error processing freespeakerbureau record: {e}")
                self.stats['errors'] += 1
    
    def process_leading_authorities(self):
        """Process leading_authorities database"""
        logger.info("Processing leading_authorities...")
        db = self.client['leading_authorities']
        collection = db['speakers_final_details']
        
        for doc in collection.find():
            try:
                name = doc.get('name', '')
                if not name or name == 'N/A':
                    continue
                    
                profile = self.create_profile(name, 'leading_authorities')
                
                # Source ID
                profile['source_ids']['leading_authorities'] = str(doc['_id'])
                
                # Professional info
                profile['professional_info']['title'] = doc.get('job_title')
                profile['professional_info']['tagline'] = doc.get('description')
                
                # Biography
                profile['biography']['full'] = doc.get('description')
                
                # Topics - Store in legacy format and as original terms for normalization
                topics = doc.get('topics', [])
                primary_topics, all_topics = self.normalize_topics(topics)
                profile['expertise']['legacy_topics'] = primary_topics
                profile['expertise']['original_terms'] = topics
                
                # Use expertise normalizer
                if topics:
                    normalized = self.expertise_normalizer.normalize_expertise(topics)
                    profile['expertise'].update({
                        'primary_categories': normalized['primary_categories'],
                        'secondary_categories': normalized['secondary_categories'],
                        'parent_categories': normalized['parent_categories'],
                        'keywords': normalized['keywords'],
                        'original_terms': normalized['original_terms']
                    })
                
                # Fee
                if doc.get('speaker_fees'):
                    fees = doc['speaker_fees']
                    if isinstance(fees, dict):
                        profile['speaking_info']['fee_range'] = {
                            'min': fees.get('min'),
                            'max': fees.get('max'),
                            'display': fees.get('display', str(fees)),
                            'currency': 'USD'
                        }
                        
                # Media
                if doc.get('speaker_image_url'):
                    profile['media']['primary_image'] = doc['speaker_image_url']
                    profile['media']['images'] = [doc['speaker_image_url']]
                    
                if doc.get('videos'):
                    videos = []
                    for v in doc['videos']:
                        if isinstance(v, dict):
                            videos.append({
                                'url': v.get('url', ''),
                                'title': v.get('title', ''),
                                'type': 'demo'
                            })
                        elif isinstance(v, str) and v:
                            videos.append({'url': v, 'type': 'demo'})
                    profile['media']['videos'] = videos
                    
                # Books
                if doc.get('books_and_publications'):
                    profile['achievements']['books'] = [
                        {'title': b} for b in doc['books_and_publications'] if b
                    ]
                    
                # Testimonials
                if doc.get('client_testimonials'):
                    profile['engagement']['testimonials'] = [
                        {'text': t} for t in doc['client_testimonials'] if t
                    ]
                    
                # Social media
                if doc.get('social_media'):
                    profile['online_presence']['social_media'] = doc['social_media']
                    
                # Website
                if doc.get('speaker_website'):
                    profile['online_presence']['website'] = doc['speaker_website']
                    
                # Download links
                if doc.get('download_profile_link'):
                    profile['media']['one_sheet'] = doc['download_profile_link']
                    
                # Booking site
                profile['online_presence']['booking_sites']['leading_authorities'] = doc.get('speaker_page_url')
                
                # Calculate score
                profile['metadata']['profile_score'] = self.calculate_profile_score(profile)
                
                # Add or merge
                unified_id = profile['unified_id']
                if unified_id in self.profiles:
                    self.profiles[unified_id] = self.merge_profiles(self.profiles[unified_id], profile)
                else:
                    self.profiles[unified_id] = profile
                    
                self.stats['leading_authorities'] += 1
                
            except Exception as e:
                logger.error(f"Error processing leading_authorities record: {e}")
                self.stats['errors'] += 1
    
    def process_sessionize(self):
        """Process sessionize database"""
        logger.info("Processing sessionize...")
        db = self.client['sessionize_scraper']
        speakers_col = db['speakers']
        profiles_col = db['speaker_profiles']
        
        # Create username -> profile mapping
        profile_map = {}
        for p in profiles_col.find():
            profile_map[p.get('username')] = p
            
        for doc in speakers_col.find():
            try:
                name = doc.get('name', '')
                if not name:
                    continue
                    
                profile = self.create_profile(name, 'sessionize')
                detailed = profile_map.get(doc.get('username'))
                
                # Source ID
                profile['source_ids']['sessionize'] = doc.get('username', str(doc['_id']))
                
                # Professional info
                profile['professional_info']['tagline'] = doc.get('tagline')
                
                # Location
                if doc.get('location'):
                    profile['location'] = self.parse_location(doc['location'])
                    
                # Categories
                profile['expertise']['categories'] = doc.get('categories', [])
                
                # Events count
                if doc.get('events_count') and isinstance(doc['events_count'], str):
                    count_str = doc['events_count'].split()[0]
                    try:
                        profile['engagement']['total_speeches'] = int(count_str)
                    except:
                        pass
                        
                # Detailed profile data
                if detailed:
                    basic = detailed.get('basic_info', {})
                    prof = detailed.get('professional_info', {})
                    
                    # Biography
                    if basic.get('bio'):
                        profile['biography']['full'] = basic['bio']
                        
                    # Professional details
                    if prof.get('job_title'):
                        profile['professional_info']['title'] = prof['job_title']
                    if prof.get('company'):
                        profile['professional_info']['company'] = prof['company']
                        
                    # Speaking history
                    history = detailed.get('speaking_history', {})
                    if history.get('total_sessions'):
                        profile['engagement']['total_speeches'] = history['total_sessions']
                        
                # Booking site
                profile['online_presence']['booking_sites']['sessionize'] = doc.get('url')
                
                # Calculate score
                profile['metadata']['profile_score'] = self.calculate_profile_score(profile)
                
                # Add or merge
                unified_id = profile['unified_id']
                if unified_id in self.profiles:
                    self.profiles[unified_id] = self.merge_profiles(self.profiles[unified_id], profile)
                else:
                    self.profiles[unified_id] = profile
                    
                self.stats['sessionize'] += 1
                
            except Exception as e:
                logger.error(f"Error processing sessionize record: {e}")
                self.stats['errors'] += 1
    
    def process_speakerhub(self):
        """Process speakerhub database"""
        logger.info("Processing speakerhub...")
        db = self.client['speakerhub_scraper']
        speakers_col = db['speakers']
        details_col = db['speaker_details']
        
        # Create uid -> details mapping
        details_map = {}
        for d in details_col.find():
            details_map[d.get('uid')] = d
            
        for doc in speakers_col.find():
            try:
                name = doc.get('name', '')
                if not name:
                    continue
                    
                profile = self.create_profile(name, 'speakerhub')
                detailed = details_map.get(doc.get('uid'))
                
                # Source ID
                profile['source_ids']['speakerhub'] = doc.get('uid', str(doc['_id']))
                
                # Basic info from speaker doc
                if doc.get('first_name'):
                    profile['basic_info']['first_name'] = doc['first_name']
                if doc.get('last_name'):
                    profile['basic_info']['last_name'] = doc['last_name']
                    
                # Professional info
                profile['professional_info']['title'] = doc.get('job_title')
                profile['professional_info']['company'] = doc.get('company')
                profile['professional_info']['tagline'] = doc.get('bio_summary')
                
                # Location
                location_parts = []
                if doc.get('city'):
                    location_parts.append(doc['city'])
                if doc.get('state'):
                    location_parts.append(doc['state'])
                if doc.get('country'):
                    location_parts.append(doc['country'])
                if location_parts:
                    profile['location'] = self.parse_location(', '.join(location_parts))
                    
                # Available regions
                if doc.get('available_regions'):
                    profile['location']['available_regions'] = doc['available_regions']
                    
                # Biography
                if detailed and detailed.get('full_bio'):
                    profile['biography']['full'] = detailed['full_bio']
                else:
                    profile['biography']['short'] = doc.get('bio_summary')
                    
                # Topics - Store in legacy format and as original terms for normalization
                topics = doc.get('topics', [])
                if detailed and detailed.get('topic_categories'):
                    topics.extend(detailed['topic_categories'])
                primary_topics, all_topics = self.normalize_topics(topics)
                profile['expertise']['legacy_topics'] = primary_topics
                profile['expertise']['original_terms'] = topics
                
                # Use expertise normalizer
                if topics:
                    normalized = self.expertise_normalizer.normalize_expertise(topics)
                    profile['expertise'].update({
                        'primary_categories': normalized['primary_categories'],
                        'secondary_categories': normalized['secondary_categories'],
                        'parent_categories': normalized['parent_categories'],
                        'keywords': normalized['keywords'],
                        'original_terms': normalized['original_terms']
                    })
                
                # Languages
                profile['speaking_info']['languages'] = doc.get('languages', [])
                
                # Event types
                profile['speaking_info']['presentation_types'] = doc.get('event_types', [])
                
                # Media
                if doc.get('profile_picture'):
                    profile['media']['primary_image'] = doc['profile_picture']
                    profile['media']['images'] = [doc['profile_picture']]
                    
                # Detailed data
                if detailed:
                    # Pronouns
                    if detailed.get('pronouns'):
                        profile['basic_info']['pronouns'] = detailed['pronouns']
                        
                    # Timezone
                    if detailed.get('timezone'):
                        profile['location']['timezone'] = detailed['timezone']
                        
                    # Videos
                    if detailed.get('videos'):
                        profile['media']['videos'] = [
                            {'url': v, 'type': 'demo'} for v in detailed['videos'] if v
                        ]
                        
                    # Awards
                    if detailed.get('awards'):
                        profile['achievements']['awards'] = detailed['awards']
                        
                    # Publications
                    if detailed.get('publications'):
                        for pub in detailed['publications']:
                            if isinstance(pub, str):
                                profile['achievements']['books'].append({'title': pub})
                                
                    # Testimonials
                    if detailed.get('testimonials'):
                        profile['engagement']['testimonials'] = [
                            {'text': t} for t in detailed['testimonials'] if t
                        ]
                        
                    # Total talks
                    if detailed.get('total_talks'):
                        profile['engagement']['total_speeches'] = detailed['total_talks']
                        
                    # Competencies/certifications
                    if detailed.get('certifications'):
                        profile['achievements']['certifications'] = detailed['certifications']
                        
                # Booking site
                profile['online_presence']['booking_sites']['speakerhub'] = doc.get('profile_url')
                
                # Calculate score
                profile['metadata']['profile_score'] = self.calculate_profile_score(profile)
                
                # Add or merge
                unified_id = profile['unified_id']
                if unified_id in self.profiles:
                    self.profiles[unified_id] = self.merge_profiles(self.profiles[unified_id], profile)
                else:
                    self.profiles[unified_id] = profile
                    
                self.stats['speakerhub'] += 1
                
            except Exception as e:
                logger.error(f"Error processing speakerhub record: {e}")
                self.stats['errors'] += 1
    
    def process_thespeakerhandbook(self):
        """Process thespeakerhandbook database"""
        logger.info("Processing thespeakerhandbook...")
        db = self.client['thespeakerhandbook_scraper']
        speakers_col = db['speakers']
        profiles_col = db['speaker_profiles']
        
        # Create speaker_id -> profile mapping
        profile_map = {}
        for p in profiles_col.find():
            profile_map[p.get('speaker_id')] = p
            
        for doc in speakers_col.find():
            try:
                name = doc.get('display_name', '')
                if not name:
                    continue
                    
                profile = self.create_profile(name, 'thespeakerhandbook')
                detailed = profile_map.get(doc.get('speaker_id'))
                
                # Source ID
                profile['source_ids']['thespeakerhandbook'] = doc.get('speaker_id', str(doc['_id']))
                
                # Basic info
                if doc.get('first_name'):
                    profile['basic_info']['first_name'] = doc['first_name']
                if doc.get('last_name'):
                    profile['basic_info']['last_name'] = doc['last_name']
                if doc.get('gender'):
                    profile['basic_info']['gender'] = doc['gender']
                    
                # Professional info
                profile['professional_info']['tagline'] = doc.get('strapline')
                
                # Location (country code)
                if doc.get('home_country'):
                    # Map country codes
                    country_map = {
                        'gb': 'United Kingdom',
                        'us': 'United States',
                        'ca': 'Canada',
                        'au': 'Australia'
                    }
                    country = country_map.get(doc['home_country'], doc['home_country'])
                    profile['location']['country'] = country
                    profile['location']['country_code'] = doc['home_country'].upper()
                    
                # Topics - Store in legacy format and as original terms for normalization
                topics = doc.get('topics', [])
                primary_topics, all_topics = self.normalize_topics(topics)
                profile['expertise']['legacy_topics'] = primary_topics
                profile['expertise']['original_terms'] = topics
                
                # Use expertise normalizer
                if topics:
                    normalized = self.expertise_normalizer.normalize_expertise(topics)
                    profile['expertise'].update({
                        'primary_categories': normalized['primary_categories'],
                        'secondary_categories': normalized['secondary_categories'],
                        'parent_categories': normalized['parent_categories'],
                        'keywords': normalized['keywords'],
                        'original_terms': normalized['original_terms']
                    })
                
                # Languages
                profile['speaking_info']['languages'] = doc.get('languages', [])
                
                # Event types
                profile['speaking_info']['presentation_types'] = doc.get('event_type', [])
                profile['speaking_info']['audience_types'] = doc.get('engagement_types', [])
                
                # Media
                if doc.get('image_url'):
                    profile['media']['primary_image'] = doc['image_url']
                    profile['media']['images'] = [doc['image_url']]
                    
                # Notability (as awards)
                if doc.get('notability'):
                    profile['achievements']['awards'] = doc['notability']
                    
                # Detailed profile data
                if detailed:
                    # Biography
                    if detailed.get('biography'):
                        profile['biography']['full'] = detailed['biography']
                        
                    # Company
                    if detailed.get('company'):
                        profile['professional_info']['company'] = detailed['company']
                        
                    # Location details
                    if detailed.get('location'):
                        loc = detailed['location']
                        if loc.get('city'):
                            profile['location']['city'] = loc['city']
                        if loc.get('state'):
                            profile['location']['state'] = loc['state']
                            
                    # Videos
                    if detailed.get('videos'):
                        videos = []
                        for v in detailed['videos']:
                            if isinstance(v, dict):
                                videos.append({
                                    'url': v.get('url', ''),
                                    'title': v.get('title', ''),
                                    'type': 'demo'
                                })
                            elif isinstance(v, str):
                                videos.append({'url': v, 'type': 'demo'})
                        profile['media']['videos'] = videos
                        
                    # Awards
                    if detailed.get('awards'):
                        profile['achievements']['awards'].extend(detailed['awards'])
                        
                    # Books
                    if detailed.get('books'):
                        for book in detailed['books']:
                            if isinstance(book, dict):
                                profile['achievements']['books'].append(book)
                            elif isinstance(book, str):
                                profile['achievements']['books'].append({'title': book})
                                
                    # Testimonials
                    if detailed.get('testimonials'):
                        testimonials = []
                        for t in detailed['testimonials']:
                            if isinstance(t, dict):
                                testimonials.append({
                                    'text': t.get('text', ''),
                                    'author_name': t.get('author', ''),
                                    'author_company': t.get('company', '')
                                })
                            elif isinstance(t, str):
                                testimonials.append({'text': t})
                        profile['engagement']['testimonials'] = testimonials
                        
                    # Contact
                    if detailed.get('contact_info'):
                        contact = detailed['contact_info']
                        profile['contact']['email'] = contact.get('email')
                        profile['contact']['phone'] = contact.get('phone')
                        
                    # Social media
                    if detailed.get('social_media'):
                        profile['online_presence']['social_media'] = detailed['social_media']
                        
                    # Website
                    if detailed.get('website'):
                        profile['online_presence']['website'] = detailed['website']
                        
                # Booking site
                profile['online_presence']['booking_sites']['thespeakerhandbook'] = doc.get('profile_url')
                
                # Calculate score
                profile['metadata']['profile_score'] = self.calculate_profile_score(profile)
                
                # Add or merge
                unified_id = profile['unified_id']
                if unified_id in self.profiles:
                    self.profiles[unified_id] = self.merge_profiles(self.profiles[unified_id], profile)
                else:
                    self.profiles[unified_id] = profile
                    
                self.stats['thespeakerhandbook'] += 1
                
            except Exception as e:
                logger.error(f"Error processing thespeakerhandbook record: {e}")
                self.stats['errors'] += 1
    
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
        
        # Quality distribution
        collection = self.target_db[TARGET_COLLECTION]
        quality_ranges = [
            (0, 25, "Low (0-25%)"),
            (25, 50, "Medium (25-50%)"),
            (50, 75, "Good (50-75%)"),
            (75, 100, "Excellent (75-100%)")
        ]
        
        logger.info("\nProfile quality distribution:")
        for min_score, max_score, label in quality_ranges:
            if max_score == 100:
                count = collection.count_documents({
                    "metadata.profile_score": {"$gte": min_score, "$lte": max_score}
                })
            else:
                count = collection.count_documents({
                    "metadata.profile_score": {"$gte": min_score, "$lt": max_score}
                })
            logger.info(f"  {label}: {count:,}")


def main():
    """Run the enhanced consolidation"""
    consolidator = EnhancedSpeakerConsolidator()
    consolidator.run()


if __name__ == "__main__":
    main()