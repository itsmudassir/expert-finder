#!/usr/bin/env python3
"""
Consolidation Pipeline - Main script to consolidate all speaker data
"""

import pymongo
from pymongo import MongoClient, UpdateOne
from typing import Dict, List, Any, Set, Tuple
import logging
from datetime import datetime
from collections import defaultdict
import json
from data_transformer import DataTransformer
from unified_schema import UnifiedSpeakerProfile
from fuzzywuzzy import fuzz
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsolidationPipeline:
    """Main pipeline for consolidating speaker data"""
    
    def __init__(self, mongo_uri: str, target_db: str = "expert_finder_unified"):
        self.mongo_uri = mongo_uri
        self.client = MongoClient(mongo_uri)
        self.target_db = target_db
        self.transformer = DataTransformer()
        self.duplicate_resolver = DuplicateResolver()
        
        # Statistics
        self.stats = defaultdict(int)
    
    def run(self, batch_size: int = 1000):
        """Run the full consolidation pipeline"""
        logger.info("Starting consolidation pipeline...")
        
        # Step 1: Extract and transform data from all sources
        all_profiles = self.extract_all_profiles()
        
        # Step 2: Resolve duplicates
        merged_profiles = self.duplicate_resolver.resolve_duplicates(all_profiles)
        
        # Step 3: Calculate profile completeness
        for profile in merged_profiles.values():
            profile.metadata.profile_completeness = self.calculate_completeness(profile)
        
        # Step 4: Save to unified database
        self.save_profiles(merged_profiles, batch_size)
        
        # Step 5: Create indexes
        self.create_indexes()
        
        # Print statistics
        self.print_statistics()
        
        logger.info("Consolidation pipeline completed!")
    
    def extract_all_profiles(self) -> List[UnifiedSpeakerProfile]:
        """Extract profiles from all source databases"""
        all_profiles = []
        
        # Process a_speakers
        logger.info("Processing a_speakers...")
        profiles = self.process_a_speakers()
        all_profiles.extend(profiles)
        self.stats['a_speakers'] = len(profiles)
        
        # Process allamericanspeakers
        logger.info("Processing allamericanspeakers...")
        profiles = self.process_allamericanspeakers()
        all_profiles.extend(profiles)
        self.stats['allamericanspeakers'] = len(profiles)
        
        # Process bigspeak
        logger.info("Processing bigspeak...")
        profiles = self.process_bigspeak()
        all_profiles.extend(profiles)
        self.stats['bigspeak'] = len(profiles)
        
        # Process eventraptor
        logger.info("Processing eventraptor...")
        profiles = self.process_eventraptor()
        all_profiles.extend(profiles)
        self.stats['eventraptor'] = len(profiles)
        
        # Process freespeakerbureau
        logger.info("Processing freespeakerbureau...")
        profiles = self.process_freespeakerbureau()
        all_profiles.extend(profiles)
        self.stats['freespeakerbureau'] = len(profiles)
        
        # Process leading_authorities
        logger.info("Processing leading_authorities...")
        profiles = self.process_leading_authorities()
        all_profiles.extend(profiles)
        self.stats['leading_authorities'] = len(profiles)
        
        # Process sessionize
        logger.info("Processing sessionize...")
        profiles = self.process_sessionize()
        all_profiles.extend(profiles)
        self.stats['sessionize'] = len(profiles)
        
        # Process speakerhub
        logger.info("Processing speakerhub...")
        profiles = self.process_speakerhub()
        all_profiles.extend(profiles)
        self.stats['speakerhub'] = len(profiles)
        
        # Process thespeakerhandbook
        logger.info("Processing thespeakerhandbook...")
        profiles = self.process_thespeakerhandbook()
        all_profiles.extend(profiles)
        self.stats['thespeakerhandbook'] = len(profiles)
        
        self.stats['total_extracted'] = len(all_profiles)
        return all_profiles
    
    def process_a_speakers(self) -> List[UnifiedSpeakerProfile]:
        """Process a_speakers database"""
        db = self.client['a_speakers']
        collection = db['speakers']
        profiles = []
        
        for doc in collection.find():
            try:
                profile = self.transformer.transform_a_speakers(doc)
                profiles.append(profile)
            except Exception as e:
                logger.error(f"Error processing a_speakers document {doc.get('_id')}: {e}")
                self.stats['errors'] += 1
        
        return profiles
    
    def process_allamericanspeakers(self) -> List[UnifiedSpeakerProfile]:
        """Process allamericanspeakers database"""
        db = self.client['allamericanspeakers']
        collection = db['speakers']
        profiles = []
        
        for doc in collection.find():
            try:
                profile = self.transformer.transform_allamericanspeakers(doc)
                profiles.append(profile)
            except Exception as e:
                logger.error(f"Error processing allamericanspeakers document {doc.get('_id')}: {e}")
                self.stats['errors'] += 1
        
        return profiles
    
    def process_bigspeak(self) -> List[UnifiedSpeakerProfile]:
        """Process bigspeak database"""
        db = self.client['bigspeak_scraper']
        speakers_col = db['speakers']
        profiles_col = db['speaker_profiles']
        profiles = []
        
        # Create a map of speaker_id to profile data
        profile_map = {}
        for profile in profiles_col.find():
            profile_map[profile.get('speaker_id')] = profile
        
        for speaker in speakers_col.find():
            try:
                speaker_id = speaker.get('speaker_id')
                profile_data = profile_map.get(speaker_id)
                profile = self.transformer.transform_bigspeak(speaker, profile_data)
                profiles.append(profile)
            except Exception as e:
                logger.error(f"Error processing bigspeak document {speaker.get('_id')}: {e}")
                self.stats['errors'] += 1
        
        return profiles
    
    def process_eventraptor(self) -> List[UnifiedSpeakerProfile]:
        """Process eventraptor database"""
        db = self.client['eventraptor']
        collection = db['speakers']
        profiles = []
        
        for doc in collection.find():
            try:
                profile = self.transformer.transform_eventraptor(doc)
                profiles.append(profile)
            except Exception as e:
                logger.error(f"Error processing eventraptor document {doc.get('_id')}: {e}")
                self.stats['errors'] += 1
        
        return profiles
    
    def process_freespeakerbureau(self) -> List[UnifiedSpeakerProfile]:
        """Process freespeakerbureau database"""
        db = self.client['freespeakerbureau_scraper']
        collection = db['speakers_profiles']
        profiles = []
        
        for doc in collection.find():
            try:
                # Transform using generic method for now
                # You would implement a specific transform_freespeakerbureau method
                profile = self._generic_transform(doc, 'freespeakerbureau')
                profiles.append(profile)
            except Exception as e:
                logger.error(f"Error processing freespeakerbureau document {doc.get('_id')}: {e}")
                self.stats['errors'] += 1
        
        return profiles
    
    def process_leading_authorities(self) -> List[UnifiedSpeakerProfile]:
        """Process leading_authorities database"""
        db = self.client['leading_authorities']
        collection = db['speakers_final_details']
        profiles = []
        
        for doc in collection.find():
            try:
                profile = self._generic_transform(doc, 'leading_authorities')
                profiles.append(profile)
            except Exception as e:
                logger.error(f"Error processing leading_authorities document {doc.get('_id')}: {e}")
                self.stats['errors'] += 1
        
        return profiles
    
    def process_sessionize(self) -> List[UnifiedSpeakerProfile]:
        """Process sessionize database"""
        db = self.client['sessionize_scraper']
        speakers_col = db['speakers']
        profiles_col = db['speaker_profiles']
        profiles = []
        
        # Create username to profile map
        profile_map = {}
        for profile in profiles_col.find():
            profile_map[profile.get('username')] = profile
        
        for speaker in speakers_col.find():
            try:
                username = speaker.get('username')
                profile_data = profile_map.get(username)
                profile = self._transform_sessionize(speaker, profile_data)
                profiles.append(profile)
            except Exception as e:
                logger.error(f"Error processing sessionize document {speaker.get('_id')}: {e}")
                self.stats['errors'] += 1
        
        return profiles
    
    def process_speakerhub(self) -> List[UnifiedSpeakerProfile]:
        """Process speakerhub database"""
        db = self.client['speakerhub_scraper']
        speakers_col = db['speakers']
        details_col = db['speaker_details']
        profiles = []
        
        # Create uid to details map
        details_map = {}
        for detail in details_col.find():
            details_map[detail.get('uid')] = detail
        
        for speaker in speakers_col.find():
            try:
                uid = speaker.get('uid')
                detail_data = details_map.get(uid)
                profile = self.transformer.transform_speakerhub(speaker, detail_data)
                profiles.append(profile)
            except Exception as e:
                logger.error(f"Error processing speakerhub document {speaker.get('_id')}: {e}")
                self.stats['errors'] += 1
        
        return profiles
    
    def process_thespeakerhandbook(self) -> List[UnifiedSpeakerProfile]:
        """Process thespeakerhandbook database"""
        db = self.client['thespeakerhandbook_scraper']
        speakers_col = db['speakers']
        profiles_col = db['speaker_profiles']
        profiles = []
        
        # Create speaker_id to profile map
        profile_map = {}
        for profile in profiles_col.find():
            profile_map[profile.get('speaker_id')] = profile
        
        for speaker in speakers_col.find():
            try:
                speaker_id = speaker.get('speaker_id')
                profile_data = profile_map.get(speaker_id)
                profile = self._transform_thespeakerhandbook(speaker, profile_data)
                profiles.append(profile)
            except Exception as e:
                logger.error(f"Error processing thespeakerhandbook document {speaker.get('_id')}: {e}")
                self.stats['errors'] += 1
        
        return profiles
    
    def _generic_transform(self, data: Dict[str, Any], source: str) -> UnifiedSpeakerProfile:
        """Generic transformation for sources without specific transformer"""
        name = data.get('name', '')
        unified_id = self.transformer.generate_unified_id(name, source)
        first_name, last_name = self.transformer.name_parser.parse_name(name)
        
        profile = UnifiedSpeakerProfile(
            unified_id=unified_id,
            source_ids={source: str(data.get('_id', ''))},
            basic_info=BasicInfo(
                full_name=name,
                first_name=first_name,
                last_name=last_name
            ),
            professional_info=ProfessionalInfo(
                job_title=data.get('job_title') or data.get('role'),
                company=data.get('company'),
                tagline=data.get('tagline') or data.get('description')
            ),
            biography=Biography(
                full=data.get('biography') or data.get('bio')
            ),
            expertise=Expertise(
                topics=self.transformer.topic_normalizer.normalize_topics(
                    data.get('topics', []) or data.get('speaking_topics', [])
                )
            ),
            metadata=Metadata(
                sources=[source],
                last_updated=data.get('scraped_at', datetime.now())
            )
        )
        
        return profile
    
    def _transform_sessionize(self, speaker: Dict[str, Any], profile: Optional[Dict[str, Any]]) -> UnifiedSpeakerProfile:
        """Transform sessionize data"""
        name = speaker.get('name', '')
        unified_id = self.transformer.generate_unified_id(name, 'sessionize')
        first_name, last_name = self.transformer.name_parser.parse_name(name)
        
        result = UnifiedSpeakerProfile(
            unified_id=unified_id,
            source_ids={'sessionize': speaker.get('username', '')},
            basic_info=BasicInfo(
                full_name=name,
                first_name=first_name,
                last_name=last_name
            ),
            professional_info=ProfessionalInfo(
                tagline=speaker.get('tagline')
            ),
            location=self.transformer.location_parser.parse_location(speaker.get('location')),
            expertise=Expertise(
                categories=speaker.get('categories', [])
            ),
            engagement_history=EngagementHistory(
                total_events=int(speaker.get('events_count', '0').split()[0]) if speaker.get('events_count') else 0
            ),
            metadata=Metadata(
                sources=['sessionize'],
                last_updated=speaker.get('last_updated', datetime.now())
            )
        )
        
        return result
    
    def _transform_thespeakerhandbook(self, speaker: Dict[str, Any], profile: Optional[Dict[str, Any]]) -> UnifiedSpeakerProfile:
        """Transform thespeakerhandbook data"""
        name = speaker.get('display_name', '')
        unified_id = self.transformer.generate_unified_id(name, 'thespeakerhandbook')
        
        from unified_schema import Gender
        
        result = UnifiedSpeakerProfile(
            unified_id=unified_id,
            source_ids={'thespeakerhandbook': speaker.get('speaker_id', '')},
            basic_info=BasicInfo(
                full_name=name,
                first_name=speaker.get('first_name'),
                last_name=speaker.get('last_name'),
                gender=Gender(speaker.get('gender')) if speaker.get('gender') else None
            ),
            professional_info=ProfessionalInfo(
                tagline=speaker.get('strapline')
            ),
            expertise=Expertise(
                topics=self.transformer.topic_normalizer.normalize_topics(speaker.get('topics', []))
            ),
            speaking_info=SpeakingInfo(
                languages=speaker.get('languages', []),
                event_types=speaker.get('event_type', []),
                engagement_types=speaker.get('engagement_types', [])
            ),
            media=Media(
                profile_images=[speaker.get('image_url')] if speaker.get('image_url') else []
            ),
            metadata=Metadata(
                sources=['thespeakerhandbook'],
                last_updated=speaker.get('scraped_at', datetime.now())
            )
        )
        
        # Add profile data if available
        if profile:
            result.biography.full = profile.get('biography')
            result.publications.awards = profile.get('awards', [])
        
        return result
    
    def calculate_completeness(self, profile: UnifiedSpeakerProfile) -> float:
        """Calculate profile completeness score (0-100)"""
        weights = {
            'name': 10,
            'job_title': 5,
            'biography': 10,
            'location': 5,
            'topics': 10,
            'fee_info': 5,
            'images': 5,
            'videos': 5,
            'contact': 10,
            'social_media': 5,
            'testimonials': 5,
            'languages': 5,
            'books': 5,
            'events': 5,
            'multiple_sources': 10
        }
        
        score = 0
        
        # Basic info
        if profile.basic_info.full_name:
            score += weights['name']
        
        # Professional info
        if profile.professional_info.job_title:
            score += weights['job_title']
        
        # Biography
        if profile.biography.full:
            score += weights['biography']
        
        # Location
        if profile.location.country or profile.location.city:
            score += weights['location']
        
        # Topics
        if len(profile.expertise.topics) > 0:
            score += weights['topics']
        
        # Fee info
        if profile.speaking_info.fee_info:
            score += weights['fee_info']
        
        # Media
        if len(profile.media.profile_images) > 0:
            score += weights['images']
        if len(profile.media.videos) > 0:
            score += weights['videos']
        
        # Contact
        if profile.contact_info.email or profile.contact_info.booking_url:
            score += weights['contact']
        
        # Social media
        if any([profile.social_media.website, profile.social_media.linkedin, 
                profile.social_media.twitter]):
            score += weights['social_media']
        
        # Engagement
        if len(profile.engagement_history.testimonials) > 0:
            score += weights['testimonials']
        if profile.engagement_history.total_events:
            score += weights['events']
        
        # Speaking info
        if len(profile.speaking_info.languages) > 0:
            score += weights['languages']
        
        # Publications
        if len(profile.publications.books) > 0:
            score += weights['books']
        
        # Multiple sources bonus
        if len(profile.metadata.sources) > 1:
            score += weights['multiple_sources']
        
        return min(score, 100)
    
    def save_profiles(self, profiles: Dict[str, UnifiedSpeakerProfile], batch_size: int):
        """Save profiles to MongoDB"""
        logger.info(f"Saving {len(profiles)} profiles to database...")
        
        db = self.client[self.target_db]
        collection = db['speakers']
        
        # Clear existing data
        collection.drop()
        
        # Convert profiles to documents
        documents = []
        for profile in profiles.values():
            documents.append(profile.to_dict())
            
            if len(documents) >= batch_size:
                collection.insert_many(documents)
                documents = []
        
        # Insert remaining documents
        if documents:
            collection.insert_many(documents)
        
        self.stats['saved_profiles'] = len(profiles)
        logger.info(f"Saved {len(profiles)} profiles successfully")
    
    def create_indexes(self):
        """Create indexes for efficient querying"""
        logger.info("Creating indexes...")
        
        db = self.client[self.target_db]
        collection = db['speakers']
        
        # Text search index
        collection.create_index([
            ("basic_info.full_name", "text"),
            ("professional_info.job_title", "text"),
            ("professional_info.tagline", "text"),
            ("biography.full", "text"),
            ("expertise.topics", "text"),
            ("expertise.keywords", "text")
        ])
        
        # Other useful indexes
        collection.create_index("basic_info.full_name")
        collection.create_index("location.country")
        collection.create_index("location.city")
        collection.create_index("expertise.topics")
        collection.create_index("speaking_info.fee_info.fee_range_enum")
        collection.create_index("metadata.profile_completeness")
        collection.create_index("metadata.sources")
        
        logger.info("Indexes created successfully")
    
    def print_statistics(self):
        """Print consolidation statistics"""
        logger.info("\n=== Consolidation Statistics ===")
        for source, count in sorted(self.stats.items()):
            if source not in ['total_extracted', 'saved_profiles', 'duplicates_found', 'errors']:
                logger.info(f"{source}: {count} profiles")
        
        logger.info(f"\nTotal extracted: {self.stats['total_extracted']}")
        logger.info(f"Duplicates found: {self.stats.get('duplicates_found', 0)}")
        logger.info(f"Final profiles saved: {self.stats['saved_profiles']}")
        logger.info(f"Errors encountered: {self.stats.get('errors', 0)}")
        
        reduction_pct = ((self.stats['total_extracted'] - self.stats['saved_profiles']) / 
                        self.stats['total_extracted'] * 100) if self.stats['total_extracted'] > 0 else 0
        logger.info(f"Data reduction: {reduction_pct:.1f}%")


class DuplicateResolver:
    """Resolve duplicate speakers across sources"""
    
    def __init__(self, name_similarity_threshold: int = 85):
        self.name_similarity_threshold = name_similarity_threshold
    
    def resolve_duplicates(self, profiles: List[UnifiedSpeakerProfile]) -> Dict[str, UnifiedSpeakerProfile]:
        """Find and merge duplicate profiles"""
        logger.info(f"Resolving duplicates among {len(profiles)} profiles...")
        
        # Group profiles by potential matches
        groups = self._group_similar_profiles(profiles)
        
        # Merge each group
        merged_profiles = {}
        duplicates_found = 0
        
        for group in groups:
            if len(group) > 1:
                duplicates_found += len(group) - 1
                merged = self._merge_profiles(group)
            else:
                merged = group[0]
            
            merged_profiles[merged.unified_id] = merged
        
        logger.info(f"Found {duplicates_found} duplicates, resulting in {len(merged_profiles)} unique profiles")
        return merged_profiles
    
    def _group_similar_profiles(self, profiles: List[UnifiedSpeakerProfile]) -> List[List[UnifiedSpeakerProfile]]:
        """Group profiles that might be the same person"""
        groups = []
        processed = set()
        
        for i, profile1 in enumerate(profiles):
            if i in processed:
                continue
            
            group = [profile1]
            processed.add(i)
            
            for j, profile2 in enumerate(profiles[i+1:], i+1):
                if j in processed:
                    continue
                
                if self._are_similar(profile1, profile2):
                    group.append(profile2)
                    processed.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_similar(self, profile1: UnifiedSpeakerProfile, profile2: UnifiedSpeakerProfile) -> bool:
        """Check if two profiles are likely the same person"""
        # Name similarity
        name_sim = fuzz.ratio(
            profile1.basic_info.full_name.lower(),
            profile2.basic_info.full_name.lower()
        )
        
        if name_sim >= self.name_similarity_threshold:
            return True
        
        # Check social media overlap
        if self._has_social_media_overlap(profile1, profile2):
            return True
        
        # Check location + similar name
        if name_sim >= 70 and self._has_location_match(profile1, profile2):
            return True
        
        return False
    
    def _has_social_media_overlap(self, profile1: UnifiedSpeakerProfile, profile2: UnifiedSpeakerProfile) -> bool:
        """Check if profiles share social media URLs"""
        urls1 = self._get_social_urls(profile1)
        urls2 = self._get_social_urls(profile2)
        
        return bool(urls1.intersection(urls2))
    
    def _get_social_urls(self, profile: UnifiedSpeakerProfile) -> Set[str]:
        """Get all social media URLs from a profile"""
        urls = set()
        
        for attr in ['website', 'linkedin', 'twitter', 'facebook', 'instagram', 'youtube']:
            url = getattr(profile.social_media, attr)
            if url:
                urls.add(url.lower().strip('/'))
        
        return urls
    
    def _has_location_match(self, profile1: UnifiedSpeakerProfile, profile2: UnifiedSpeakerProfile) -> bool:
        """Check if profiles have matching locations"""
        if not profile1.location.country or not profile2.location.country:
            return False
        
        country_match = profile1.location.country.lower() == profile2.location.country.lower()
        
        if profile1.location.city and profile2.location.city:
            city_match = profile1.location.city.lower() == profile2.location.city.lower()
            return country_match and city_match
        
        return country_match
    
    def _merge_profiles(self, profiles: List[UnifiedSpeakerProfile]) -> UnifiedSpeakerProfile:
        """Merge multiple profiles into one"""
        # Start with the most complete profile
        profiles_sorted = sorted(profiles, key=lambda p: p.metadata.profile_completeness, reverse=True)
        merged = profiles_sorted[0]
        
        # Merge data from other profiles
        for profile in profiles_sorted[1:]:
            # Merge source IDs
            merged.source_ids.update(profile.source_ids)
            
            # Merge sources list
            merged.metadata.sources.extend(profile.metadata.sources)
            merged.metadata.sources = list(set(merged.metadata.sources))
            
            # Merge topics
            merged.expertise.topics.extend(profile.expertise.topics)
            merged.expertise.topics = list(set(merged.expertise.topics))
            
            # Merge other fields (prefer non-empty values)
            self._merge_field(merged.professional_info, profile.professional_info, 'job_title')
            self._merge_field(merged.professional_info, profile.professional_info, 'company')
            self._merge_field(merged.biography, profile.biography, 'full')
            self._merge_field(merged.contact_info, profile.contact_info, 'email')
            
            # Merge arrays
            merged.media.profile_images.extend(profile.media.profile_images)
            merged.media.videos.extend(profile.media.videos)
            merged.publications.books.extend(profile.publications.books)
            merged.engagement_history.testimonials.extend(profile.engagement_history.testimonials)
        
        # Remove duplicates from arrays
        merged.media.profile_images = list(set(merged.media.profile_images))
        merged.expertise.topics = list(set(merged.expertise.topics))
        
        # Update last updated time
        merged.metadata.last_updated = datetime.now()
        
        return merged
    
    def _merge_field(self, target_obj: Any, source_obj: Any, field_name: str):
        """Merge a single field, preferring non-empty values"""
        target_val = getattr(target_obj, field_name)
        source_val = getattr(source_obj, field_name)
        
        if not target_val and source_val:
            setattr(target_obj, field_name, source_val)


def main():
    parser = argparse.ArgumentParser(description='Consolidate speaker data from multiple MongoDB databases')
    parser.add_argument('--mongo-uri', default="mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin",
                       help='MongoDB connection URI')
    parser.add_argument('--target-db', default='expert_finder_unified',
                       help='Target database name for unified data')
    parser.add_argument('--batch-size', type=int, default=1000,
                       help='Batch size for inserting documents')
    
    args = parser.parse_args()
    
    # Install required package if not already installed
    try:
        from fuzzywuzzy import fuzz
    except ImportError:
        import subprocess
        subprocess.check_call(['pip', 'install', 'fuzzywuzzy', 'python-Levenshtein'])
    
    pipeline = ConsolidationPipeline(args.mongo_uri, args.target_db)
    pipeline.run(args.batch_size)


if __name__ == "__main__":
    main()