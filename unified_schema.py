#!/usr/bin/env python3
"""
Unified Schema Definition for Expert Speaker Database
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    NOT_SPECIFIED = "not_specified"

class FeeRange(Enum):
    UNDER_5K = "under_5000"
    RANGE_5K_10K = "5000_10000"
    RANGE_10K_20K = "10000_20000"
    RANGE_20K_30K = "20000_30000"
    RANGE_30K_50K = "30000_50000"
    RANGE_50K_75K = "50000_75000"
    RANGE_75K_100K = "75000_100000"
    OVER_100K = "over_100000"
    PLEASE_INQUIRE = "please_inquire"

@dataclass
class BasicInfo:
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[Gender] = None
    pronouns: Optional[str] = None

@dataclass
class ProfessionalInfo:
    job_title: Optional[str] = None
    company: Optional[str] = None
    tagline: Optional[str] = None
    credentials: List[str] = field(default_factory=list)
    years_experience: Optional[int] = None

@dataclass
class Location:
    city: Optional[str] = None
    state_province: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    timezone: Optional[str] = None
    available_regions: List[str] = field(default_factory=list)

@dataclass
class Biography:
    short: Optional[str] = None  # < 200 chars
    medium: Optional[str] = None  # < 500 chars
    full: Optional[str] = None

@dataclass
class Expertise:
    topics: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

@dataclass
class FeeInfo:
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    currency: str = "USD"
    display: Optional[str] = None
    negotiable: bool = True
    fee_range_enum: Optional[FeeRange] = None

@dataclass
class KeynoteTopic:
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None

@dataclass
class SpeakingInfo:
    fee_info: Optional[FeeInfo] = None
    languages: List[str] = field(default_factory=list)
    event_types: List[str] = field(default_factory=list)
    engagement_types: List[str] = field(default_factory=list)
    keynote_topics: List[KeynoteTopic] = field(default_factory=list)

@dataclass
class Video:
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    platform: Optional[str] = None  # youtube, vimeo, etc.
    duration_seconds: Optional[int] = None

@dataclass
class Media:
    profile_images: List[str] = field(default_factory=list)
    videos: List[Video] = field(default_factory=list)
    speaker_reel_url: Optional[str] = None

@dataclass
class SocialMedia:
    website: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None

@dataclass
class Book:
    title: str
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    amazon_url: Optional[str] = None

@dataclass
class Publications:
    books: List[Book] = field(default_factory=list)
    articles: List[str] = field(default_factory=list)
    awards: List[str] = field(default_factory=list)

@dataclass
class Testimonial:
    text: str
    author_name: Optional[str] = None
    author_title: Optional[str] = None
    author_company: Optional[str] = None
    date: Optional[datetime] = None
    rating: Optional[float] = None

@dataclass
class Ratings:
    average: Optional[float] = None
    count: int = 0
    distribution: Dict[int, int] = field(default_factory=dict)  # {5: 10, 4: 5, ...}

@dataclass
class EngagementHistory:
    total_events: Optional[int] = None
    notable_clients: List[str] = field(default_factory=list)
    testimonials: List[Testimonial] = field(default_factory=list)
    ratings: Optional[Ratings] = None

@dataclass
class AgentInfo:
    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

@dataclass
class ContactInfo:
    email: Optional[str] = None
    phone: Optional[str] = None
    booking_url: Optional[str] = None
    agent_info: Optional[AgentInfo] = None

@dataclass
class Metadata:
    sources: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    verification_status: str = "unverified"  # unverified, partial, verified
    profile_completeness: float = 0.0  # 0-100

@dataclass
class UnifiedSpeakerProfile:
    """Unified speaker profile combining data from all sources"""
    
    # Unique identifier
    unified_id: str
    
    # Source identifiers
    source_ids: Dict[str, str] = field(default_factory=dict)
    
    # Profile sections
    basic_info: BasicInfo = field(default_factory=BasicInfo)
    professional_info: ProfessionalInfo = field(default_factory=ProfessionalInfo)
    location: Location = field(default_factory=Location)
    biography: Biography = field(default_factory=Biography)
    expertise: Expertise = field(default_factory=Expertise)
    speaking_info: SpeakingInfo = field(default_factory=SpeakingInfo)
    media: Media = field(default_factory=Media)
    social_media: SocialMedia = field(default_factory=SocialMedia)
    publications: Publications = field(default_factory=Publications)
    engagement_history: EngagementHistory = field(default_factory=EngagementHistory)
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    metadata: Metadata = field(default_factory=Metadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        return {
            "unified_id": self.unified_id,
            "source_ids": self.source_ids,
            "basic_info": {
                "full_name": self.basic_info.full_name,
                "first_name": self.basic_info.first_name,
                "last_name": self.basic_info.last_name,
                "gender": self.basic_info.gender.value if self.basic_info.gender else None,
                "pronouns": self.basic_info.pronouns
            },
            "professional_info": {
                "job_title": self.professional_info.job_title,
                "company": self.professional_info.company,
                "tagline": self.professional_info.tagline,
                "credentials": self.professional_info.credentials,
                "years_experience": self.professional_info.years_experience
            },
            "location": {
                "city": self.location.city,
                "state_province": self.location.state_province,
                "country": self.location.country,
                "country_code": self.location.country_code,
                "timezone": self.location.timezone,
                "available_regions": self.location.available_regions
            },
            "biography": {
                "short": self.biography.short,
                "medium": self.biography.medium,
                "full": self.biography.full
            },
            "expertise": {
                "topics": self.expertise.topics,
                "categories": self.expertise.categories,
                "industries": self.expertise.industries,
                "keywords": self.expertise.keywords
            },
            "speaking_info": {
                "fee_info": {
                    "min_amount": self.speaking_info.fee_info.min_amount if self.speaking_info.fee_info else None,
                    "max_amount": self.speaking_info.fee_info.max_amount if self.speaking_info.fee_info else None,
                    "currency": self.speaking_info.fee_info.currency if self.speaking_info.fee_info else "USD",
                    "display": self.speaking_info.fee_info.display if self.speaking_info.fee_info else None,
                    "negotiable": self.speaking_info.fee_info.negotiable if self.speaking_info.fee_info else True,
                    "fee_range_enum": self.speaking_info.fee_info.fee_range_enum.value if self.speaking_info.fee_info and self.speaking_info.fee_info.fee_range_enum else None
                } if self.speaking_info.fee_info else None,
                "languages": self.speaking_info.languages,
                "event_types": self.speaking_info.event_types,
                "engagement_types": self.speaking_info.engagement_types,
                "keynote_topics": [
                    {
                        "title": kt.title,
                        "description": kt.description,
                        "duration_minutes": kt.duration_minutes
                    } for kt in self.speaking_info.keynote_topics
                ]
            },
            "media": {
                "profile_images": self.media.profile_images,
                "videos": [
                    {
                        "url": v.url,
                        "title": v.title,
                        "description": v.description,
                        "platform": v.platform,
                        "duration_seconds": v.duration_seconds
                    } for v in self.media.videos
                ],
                "speaker_reel_url": self.media.speaker_reel_url
            },
            "social_media": {
                "website": self.social_media.website,
                "linkedin": self.social_media.linkedin,
                "twitter": self.social_media.twitter,
                "facebook": self.social_media.facebook,
                "instagram": self.social_media.instagram,
                "youtube": self.social_media.youtube,
                "tiktok": self.social_media.tiktok
            },
            "publications": {
                "books": [
                    {
                        "title": b.title,
                        "isbn": b.isbn,
                        "publisher": b.publisher,
                        "year": b.year,
                        "amazon_url": b.amazon_url
                    } for b in self.publications.books
                ],
                "articles": self.publications.articles,
                "awards": self.publications.awards
            },
            "engagement_history": {
                "total_events": self.engagement_history.total_events,
                "notable_clients": self.engagement_history.notable_clients,
                "testimonials": [
                    {
                        "text": t.text,
                        "author_name": t.author_name,
                        "author_title": t.author_title,
                        "author_company": t.author_company,
                        "date": t.date.isoformat() if t.date else None,
                        "rating": t.rating
                    } for t in self.engagement_history.testimonials
                ],
                "ratings": {
                    "average": self.engagement_history.ratings.average,
                    "count": self.engagement_history.ratings.count,
                    "distribution": self.engagement_history.ratings.distribution
                } if self.engagement_history.ratings else None
            },
            "contact_info": {
                "email": self.contact_info.email,
                "phone": self.contact_info.phone,
                "booking_url": self.contact_info.booking_url,
                "agent_info": {
                    "name": self.contact_info.agent_info.name,
                    "company": self.contact_info.agent_info.company,
                    "email": self.contact_info.agent_info.email,
                    "phone": self.contact_info.agent_info.phone
                } if self.contact_info.agent_info else None
            },
            "metadata": {
                "sources": self.metadata.sources,
                "last_updated": self.metadata.last_updated.isoformat(),
                "verification_status": self.metadata.verification_status,
                "profile_completeness": self.metadata.profile_completeness
            }
        }

# Topic taxonomy for normalization
TOPIC_TAXONOMY = {
    "leadership": ["leadership", "leading", "management", "executive leadership", "transformational leadership"],
    "innovation": ["innovation", "creativity", "disruption", "innovation strategy", "creative thinking"],
    "technology": ["technology", "tech", "digital transformation", "ai", "artificial intelligence", "machine learning"],
    "diversity": ["diversity", "dei", "inclusion", "equity", "diversity and inclusion"],
    "motivation": ["motivation", "inspiration", "motivational", "inspiring", "empowerment"],
    "business": ["business", "business strategy", "entrepreneurship", "business growth", "strategy"],
    "communication": ["communication", "public speaking", "presentation skills", "storytelling"],
    "sales": ["sales", "selling", "sales strategy", "sales performance", "revenue growth"],
    "marketing": ["marketing", "branding", "digital marketing", "content marketing", "social media"],
    "wellness": ["wellness", "health", "mental health", "wellbeing", "mindfulness", "stress management"],
    "change": ["change management", "transformation", "organizational change", "change leadership"],
    "teamwork": ["teamwork", "team building", "collaboration", "team performance", "team dynamics"],
    "customer": ["customer service", "customer experience", "cx", "customer success", "client relations"],
    "finance": ["finance", "financial", "economics", "investment", "financial planning"],
    "education": ["education", "learning", "training", "development", "teaching"],
    "sports": ["sports", "athletics", "fitness", "peak performance", "sports psychology"],
    "culture": ["culture", "organizational culture", "company culture", "workplace culture"],
    "future": ["future", "trends", "futurism", "future of work", "emerging trends"],
    "sustainability": ["sustainability", "environment", "climate", "esg", "sustainable business"],
    "resilience": ["resilience", "adaptability", "overcoming adversity", "mental toughness", "grit"]
}