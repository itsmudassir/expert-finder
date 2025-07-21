#!/usr/bin/env python3
"""
Data Transformation Logic for consolidating speaker data from multiple sources
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
from unified_schema import *

class DataTransformer:
    """Transform data from various sources to unified schema"""
    
    def __init__(self):
        self.topic_normalizer = TopicNormalizer()
        self.fee_parser = FeeParser()
        self.name_parser = NameParser()
        self.location_parser = LocationParser()
    
    def transform_a_speakers(self, data: Dict[str, Any]) -> UnifiedSpeakerProfile:
        """Transform a_speakers data to unified schema"""
        # Generate unified ID
        unified_id = self.generate_unified_id(data.get('name', ''), 'a_speakers')
        
        # Parse name
        first_name, last_name = self.name_parser.parse_name(data.get('name', ''))
        
        # Create profile
        profile = UnifiedSpeakerProfile(
            unified_id=unified_id,
            source_ids={'a_speakers': data.get('url', '')},
            basic_info=BasicInfo(
                full_name=data.get('name', ''),
                first_name=first_name,
                last_name=last_name
            ),
            professional_info=ProfessionalInfo(
                job_title=data.get('job_title'),
                tagline=data.get('description')
            ),
            location=self.location_parser.parse_location(data.get('location')),
            biography=Biography(
                short=data.get('description'),
                full=data.get('full_bio')
            ),
            expertise=Expertise(
                topics=self.topic_normalizer.normalize_topics(data.get('topics', [])),
                categories=data.get('topics', [])
            ),
            speaking_info=SpeakingInfo(
                fee_info=self.fee_parser.parse_fee(data.get('fee_range')),
                keynote_topics=[KeynoteTopic(title=k) for k in data.get('keynotes', [])]
            ),
            media=Media(
                profile_images=[data.get('image_url')] if data.get('image_url') else [],
                videos=[Video(url=v) for v in data.get('videos', [])]
            ),
            engagement_history=EngagementHistory(
                ratings=Ratings(
                    average=data.get('average_rating'),
                    count=data.get('total_reviews', 0)
                ) if data.get('average_rating') else None,
                testimonials=[Testimonial(text=r) for r in data.get('reviews', [])]
            ),
            metadata=Metadata(
                sources=['a_speakers'],
                last_updated=data.get('scraped_at', datetime.now())
            )
        )
        
        return profile
    
    def transform_allamericanspeakers(self, data: Dict[str, Any]) -> UnifiedSpeakerProfile:
        """Transform allamericanspeakers data to unified schema"""
        unified_id = self.generate_unified_id(data.get('name', ''), 'allamericanspeakers')
        first_name, last_name = self.name_parser.parse_name(data.get('name', ''))
        
        # Parse location
        location = self.location_parser.parse_location(data.get('location'))
        
        profile = UnifiedSpeakerProfile(
            unified_id=unified_id,
            source_ids={'allamericanspeakers': data.get('speaker_id', '')},
            basic_info=BasicInfo(
                full_name=data.get('name', ''),
                first_name=first_name,
                last_name=last_name
            ),
            professional_info=ProfessionalInfo(
                job_title=data.get('job_title')
            ),
            location=location,
            biography=Biography(
                full=data.get('biography')
            ),
            expertise=Expertise(
                topics=self.topic_normalizer.normalize_topics(data.get('speaking_topics', [])),
                categories=data.get('categories', [])
            ),
            speaking_info=SpeakingInfo(
                fee_info=self.fee_parser.parse_fee_object(data.get('fee_range')) if isinstance(data.get('fee_range'), dict) else None
            ),
            media=Media(
                videos=[Video(url=v) for v in data.get('videos', [])]
            ),
            engagement_history=EngagementHistory(
                ratings=self._parse_rating_object(data.get('rating')) if data.get('rating') else None,
                testimonials=[Testimonial(text=r) for r in data.get('reviews', [])]
            ),
            metadata=Metadata(
                sources=['allamericanspeakers'],
                last_updated=data.get('scraped_at', datetime.now())
            )
        )
        
        return profile
    
    def transform_bigspeak(self, speaker_data: Dict[str, Any], profile_data: Optional[Dict[str, Any]] = None) -> UnifiedSpeakerProfile:
        """Transform bigspeak data to unified schema"""
        unified_id = self.generate_unified_id(speaker_data.get('name', ''), 'bigspeak')
        first_name, last_name = self.name_parser.parse_name(speaker_data.get('name', ''))
        
        profile = UnifiedSpeakerProfile(
            unified_id=unified_id,
            source_ids={'bigspeak': speaker_data.get('speaker_id', '')},
            basic_info=BasicInfo(
                full_name=speaker_data.get('name', ''),
                first_name=first_name,
                last_name=last_name
            ),
            professional_info=ProfessionalInfo(
                tagline=speaker_data.get('description')
            ),
            biography=Biography(
                short=speaker_data.get('description'),
                full=profile_data.get('biography') if profile_data else None
            ),
            expertise=Expertise(
                topics=self.topic_normalizer.normalize_topics(speaker_data.get('topics', [])),
                categories=profile_data.get('keynote_topics', []) if profile_data else []
            ),
            speaking_info=SpeakingInfo(
                fee_info=self.fee_parser.parse_fee(speaker_data.get('fee_range')),
                languages=profile_data.get('languages', []) if profile_data else [],
                keynote_topics=[KeynoteTopic(title=t) for t in profile_data.get('speaking_programs', [])] if profile_data else []
            ),
            media=Media(
                profile_images=[speaker_data.get('image_url')] if speaker_data.get('image_url') else [],
                videos=[Video(url=v) for v in profile_data.get('videos', [])] if profile_data else []
            ),
            publications=Publications(
                books=[Book(title=b) for b in profile_data.get('books', [])] if profile_data else [],
                awards=profile_data.get('awards', []) if profile_data else []
            ),
            engagement_history=EngagementHistory(
                testimonials=[Testimonial(text=t) for t in profile_data.get('testimonials', [])] if profile_data else []
            ),
            social_media=self._parse_social_media(profile_data.get('social_media')) if profile_data else SocialMedia(),
            metadata=Metadata(
                sources=['bigspeak'],
                last_updated=speaker_data.get('scraped_at', datetime.now())
            )
        )
        
        # Parse location from profile data
        if profile_data and profile_data.get('location'):
            profile.location = self.location_parser.parse_location_object(profile_data['location'])
        
        return profile
    
    def transform_eventraptor(self, data: Dict[str, Any]) -> UnifiedSpeakerProfile:
        """Transform eventraptor data to unified schema"""
        # Clean name (remove pronouns)
        name = re.sub(r'(she/her/hers|he/him/his|they/them/theirs)$', '', data.get('name', '')).strip()
        unified_id = self.generate_unified_id(name, 'eventraptor')
        first_name, last_name = self.name_parser.parse_name(name)
        
        profile = UnifiedSpeakerProfile(
            unified_id=unified_id,
            source_ids={'eventraptor': data.get('speaker_id', '')},
            basic_info=BasicInfo(
                full_name=name,
                first_name=first_name,
                last_name=last_name
            ),
            professional_info=ProfessionalInfo(
                tagline=data.get('tagline'),
                credentials=data.get('credentials', '').split(',') if data.get('credentials') else []
            ),
            biography=Biography(
                full=data.get('biography')
            ),
            expertise=Expertise(
                categories=data.get('business_areas', [])
            ),
            engagement_history=EngagementHistory(
                total_events=len(data.get('events', []))
            ),
            contact_info=ContactInfo(
                email=data.get('email')
            ),
            social_media=self._parse_social_media(data.get('social_media')),
            media=Media(
                profile_images=[data.get('profile_image')] if data.get('profile_image') else []
            ),
            metadata=Metadata(
                sources=['eventraptor'],
                last_updated=data.get('scraped_at', datetime.now())
            )
        )
        
        return profile
    
    def transform_speakerhub(self, speaker_data: Dict[str, Any], detail_data: Optional[Dict[str, Any]] = None) -> UnifiedSpeakerProfile:
        """Transform speakerhub data to unified schema"""
        unified_id = self.generate_unified_id(speaker_data.get('name', ''), 'speakerhub')
        
        profile = UnifiedSpeakerProfile(
            unified_id=unified_id,
            source_ids={'speakerhub': speaker_data.get('uid', '')},
            basic_info=BasicInfo(
                full_name=speaker_data.get('name', ''),
                first_name=speaker_data.get('first_name'),
                last_name=speaker_data.get('last_name'),
                pronouns=detail_data.get('pronouns') if detail_data else None
            ),
            professional_info=ProfessionalInfo(
                job_title=speaker_data.get('job_title'),
                company=speaker_data.get('company'),
                tagline=speaker_data.get('bio_summary')
            ),
            location=Location(
                city=speaker_data.get('city'),
                state_province=speaker_data.get('state'),
                country=speaker_data.get('country'),
                timezone=detail_data.get('timezone') if detail_data else None,
                available_regions=speaker_data.get('available_regions', [])
            ),
            biography=Biography(
                short=speaker_data.get('bio_summary'),
                full=detail_data.get('full_bio') if detail_data else None
            ),
            expertise=Expertise(
                topics=self.topic_normalizer.normalize_topics(speaker_data.get('topics', [])),
                categories=detail_data.get('topic_categories', []) if detail_data else []
            ),
            speaking_info=SpeakingInfo(
                languages=speaker_data.get('languages', []),
                event_types=speaker_data.get('event_types', []),
                fee_info=self._parse_speaker_fees(detail_data.get('speaker_fees')) if detail_data else None
            ),
            media=Media(
                profile_images=[speaker_data.get('profile_picture')] if speaker_data.get('profile_picture') else [],
                videos=[Video(url=v) for v in detail_data.get('videos', [])] if detail_data else []
            ),
            publications=Publications(
                awards=detail_data.get('awards', []) if detail_data else []
            ),
            engagement_history=EngagementHistory(
                total_events=detail_data.get('total_talks') if detail_data else None,
                testimonials=[Testimonial(text=t) for t in detail_data.get('testimonials', [])] if detail_data else []
            ),
            metadata=Metadata(
                sources=['speakerhub'],
                last_updated=datetime.fromisoformat(speaker_data.get('scraped_at').replace('Z', '+00:00')) if speaker_data.get('scraped_at') else datetime.now()
            )
        )
        
        return profile
    
    def generate_unified_id(self, name: str, source: str) -> str:
        """Generate a unique ID for a speaker"""
        # Create hash from normalized name
        normalized_name = name.lower().strip()
        hash_input = f"{normalized_name}:{source}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _parse_rating_object(self, rating_obj: Dict[str, Any]) -> Ratings:
        """Parse rating object from various sources"""
        if not rating_obj:
            return None
        
        return Ratings(
            average=rating_obj.get('average') or rating_obj.get('value'),
            count=rating_obj.get('count', 0)
        )
    
    def _parse_social_media(self, social_obj: Optional[Dict[str, Any]]) -> SocialMedia:
        """Parse social media object"""
        if not social_obj:
            return SocialMedia()
        
        return SocialMedia(
            website=social_obj.get('website'),
            linkedin=social_obj.get('linkedin'),
            twitter=social_obj.get('twitter'),
            facebook=social_obj.get('facebook'),
            instagram=social_obj.get('instagram'),
            youtube=social_obj.get('youtube')
        )
    
    def _parse_speaker_fees(self, fees: List[Dict[str, Any]]) -> Optional[FeeInfo]:
        """Parse speaker fees array into FeeInfo"""
        if not fees:
            return None
        
        # For now, just take the first fee entry
        # In production, might want to aggregate or select based on criteria
        if fees and len(fees) > 0:
            fee_text = str(fees[0])
            return self.fee_parser.parse_fee(fee_text)
        
        return None


class TopicNormalizer:
    """Normalize topics to standard categories"""
    
    def normalize_topics(self, topics: List[str]) -> List[str]:
        """Normalize a list of topics"""
        normalized = set()
        
        for topic in topics:
            if not topic:
                continue
            
            topic_lower = topic.lower().strip()
            
            # Check against taxonomy
            for category, keywords in TOPIC_TAXONOMY.items():
                for keyword in keywords:
                    if keyword in topic_lower:
                        normalized.add(category)
                        break
        
        # Also keep original topics that don't match taxonomy
        for topic in topics:
            if topic:
                normalized.add(topic.strip())
        
        return list(normalized)


class FeeParser:
    """Parse fee ranges from various formats"""
    
    def parse_fee(self, fee_text: Optional[str]) -> Optional[FeeInfo]:
        """Parse fee text into structured FeeInfo"""
        if not fee_text:
            return None
        
        fee_text = fee_text.strip()
        
        # Handle "Please Inquire" or similar
        if any(phrase in fee_text.lower() for phrase in ['inquire', 'contact', 'request']):
            return FeeInfo(
                display=fee_text,
                fee_range_enum=FeeRange.PLEASE_INQUIRE
            )
        
        # Try to extract numeric ranges
        # Pattern: $XX,XXX - $XX,XXX
        range_pattern = r'\$?([\d,]+)\s*[-–]\s*\$?([\d,]+)'
        match = re.search(range_pattern, fee_text)
        
        if match:
            try:
                min_amount = float(match.group(1).replace(',', ''))
                max_amount = float(match.group(2).replace(',', ''))
                
                return FeeInfo(
                    min_amount=min_amount,
                    max_amount=max_amount,
                    display=fee_text,
                    fee_range_enum=self._determine_fee_range(min_amount, max_amount)
                )
            except ValueError:
                pass
        
        # Pattern: Under $XX,XXX
        under_pattern = r'[Uu]nder\s*\$?([\d,]+)'
        match = re.search(under_pattern, fee_text)
        if match:
            try:
                max_amount = float(match.group(1).replace(',', ''))
                return FeeInfo(
                    max_amount=max_amount,
                    display=fee_text,
                    fee_range_enum=self._determine_fee_range(0, max_amount)
                )
            except ValueError:
                pass
        
        # Pattern: Over $XX,XXX or $XX,XXX+
        over_pattern = r'([Oo]ver\s*\$?([\d,]+)|\$?([\d,]+)\+)'
        match = re.search(over_pattern, fee_text)
        if match:
            try:
                amount_str = match.group(2) or match.group(3)
                min_amount = float(amount_str.replace(',', ''))
                return FeeInfo(
                    min_amount=min_amount,
                    display=fee_text,
                    fee_range_enum=self._determine_fee_range(min_amount, float('inf'))
                )
            except ValueError:
                pass
        
        # If no pattern matched, just store the display text
        return FeeInfo(display=fee_text)
    
    def parse_fee_object(self, fee_obj: Dict[str, Any]) -> Optional[FeeInfo]:
        """Parse fee object into FeeInfo"""
        if not fee_obj:
            return None
        
        # Extract values based on common keys
        min_val = fee_obj.get('min') or fee_obj.get('minimum')
        max_val = fee_obj.get('max') or fee_obj.get('maximum')
        display = fee_obj.get('display') or fee_obj.get('text') or str(fee_obj)
        
        return FeeInfo(
            min_amount=float(min_val) if min_val else None,
            max_amount=float(max_val) if max_val else None,
            display=display
        )
    
    def _determine_fee_range(self, min_amount: float, max_amount: float) -> FeeRange:
        """Determine fee range enum based on amounts"""
        avg = (min_amount + max_amount) / 2 if max_amount != float('inf') else min_amount
        
        if avg < 5000:
            return FeeRange.UNDER_5K
        elif avg < 10000:
            return FeeRange.RANGE_5K_10K
        elif avg < 20000:
            return FeeRange.RANGE_10K_20K
        elif avg < 30000:
            return FeeRange.RANGE_20K_30K
        elif avg < 50000:
            return FeeRange.RANGE_30K_50K
        elif avg < 75000:
            return FeeRange.RANGE_50K_75K
        elif avg < 100000:
            return FeeRange.RANGE_75K_100K
        else:
            return FeeRange.OVER_100K


class NameParser:
    """Parse names into first and last names"""
    
    def parse_name(self, full_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse full name into first and last names"""
        if not full_name:
            return None, None
        
        # Clean the name
        name = full_name.strip()
        
        # Remove titles
        titles = ['Dr.', 'Dr', 'Mr.', 'Mr', 'Mrs.', 'Mrs', 'Ms.', 'Ms', 'Prof.', 'Prof']
        for title in titles:
            if name.startswith(title + ' '):
                name = name[len(title):].strip()
        
        # Split into parts
        parts = name.split()
        
        if len(parts) == 0:
            return None, None
        elif len(parts) == 1:
            return parts[0], None
        elif len(parts) == 2:
            return parts[0], parts[1]
        else:
            # Handle middle names and suffixes
            # For now, simple approach: first part is first name, rest is last name
            return parts[0], ' '.join(parts[1:])


class LocationParser:
    """Parse location information"""
    
    def parse_location(self, location_str: Optional[str]) -> Location:
        """Parse location string into Location object"""
        if not location_str:
            return Location()
        
        location_str = location_str.strip()
        
        # Common patterns:
        # "City, State, Country"
        # "City, Country"
        # "Country"
        
        parts = [p.strip() for p in location_str.split(',')]
        
        if len(parts) == 1:
            # Assume it's a country
            return Location(country=parts[0])
        elif len(parts) == 2:
            # Could be City, Country or City, State (US)
            if parts[1].upper() in ['USA', 'US', 'UNITED STATES', 'UNITED STATES OF AMERICA']:
                return Location(city=parts[0], country='United States')
            elif len(parts[1]) == 2:  # Likely US state abbreviation
                return Location(city=parts[0], state_province=parts[1], country='United States')
            else:
                return Location(city=parts[0], country=parts[1])
        elif len(parts) >= 3:
            return Location(
                city=parts[0],
                state_province=parts[1],
                country=parts[2]
            )
        
        return Location()
    
    def parse_location_object(self, location_obj: Dict[str, Any]) -> Location:
        """Parse location object into Location"""
        return Location(
            city=location_obj.get('city'),
            state_province=location_obj.get('state') or location_obj.get('state_province'),
            country=location_obj.get('country'),
            country_code=location_obj.get('country_code'),
            timezone=location_obj.get('timezone')
        )