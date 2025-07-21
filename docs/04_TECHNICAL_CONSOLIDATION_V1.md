# 04. Technical Data Consolidation Guide (V1)

[← Previous: Implementation Guide](03_NORMALIZATION_IMPLEMENTATION.md) | [Next: Technical Consolidation V2 →](05_TECHNICAL_CONSOLIDATION_V2.md)

---

## Overview
This guide documents the consolidation of 9 different MongoDB databases containing expert speaker profiles from various speaker bureau websites into a single, unified data structure.

## Source Data Analysis

### 1. Data Sources Summary

| Database | Documents | Key Characteristics |
|----------|-----------|-------------------|
| a_speakers | 3,592 | Structured keynotes, ratings, reviews |
| allamericanspeakers | 11,081 | Largest dataset, fee objects, categories |
| bigspeak_scraper | 2,178 | Two-collection structure (basic + detailed) |
| eventraptor | 2,986 | Direct email contacts, event history |
| freespeakerbureau_scraper | 436 | Most detailed contact info, member levels |
| leading_authorities | 1,230 | Download links, recent news, client testimonials |
| sessionize_scraper | 12,827 | Event/session statistics, username-based |
| speakerhub_scraper | 20,548 | Largest collection, multi-language support |
| thespeakerhandbook_scraper | 3,510 | Gender info, notability rankings |

**Total Raw Documents: ~58,388**

### 2. Common Data Patterns Found

#### Core Information Present in All Sources:
- Speaker name
- Some form of biography/description
- Topics or expertise areas
- Profile images/photos
- Source URLs

#### Frequently Available (50%+ sources):
- Location information (varying formats)
- Professional title/tagline
- Fee information (varying formats)
- Videos
- Social media links
- Contact information (indirect)

#### Sometimes Available (less than 50%):
- Direct email addresses
- Phone numbers
- Languages spoken
- Books/publications
- Awards and recognition
- Client testimonials/reviews
- Event history

### 3. Major Data Quality Issues

1. **Duplicate Speakers**: Same person appears across multiple databases
2. **Inconsistent Formats**:
   - Locations: "USA" vs "United States" vs "New York, NY, USA"
   - Fees: "$10,000-$20,000" vs "10000" vs "Please Inquire"
   - Names: "Bob Smith" vs "Robert Smith" vs "Dr. Bob Smith"
3. **Missing Data**: Many fields are optional and frequently empty
4. **Unstructured Text**: Biographies and descriptions vary wildly in length and format
5. **No Standard Identifiers**: Each source uses different ID systems

## Unified Data Structure Design

### Design Principles
1. **Comprehensive**: Capture all valuable data from all sources
2. **Normalized**: Use consistent formats and controlled vocabularies
3. **Searchable**: Optimize for full-text and faceted search
4. **Extensible**: Allow for future data sources
5. **Quality-Aware**: Track data completeness and verification status

### Final Schema Structure

```javascript
{
  // Unique identifier
  "_id": "MongoDB ObjectId",
  "unified_id": "MD5 hash of normalized name + primary source",
  
  // Source tracking
  "source_ids": {
    "a_speakers": "original_url_or_id",
    "allamericanspeakers": "speaker_id",
    // ... mappings for each source
  },
  
  // Basic Information
  "basic_info": {
    "full_name": "John Smith",
    "first_name": "John",
    "last_name": "Smith",
    "display_name": "Dr. John Smith",
    "gender": "male|female|other|not_specified",
    "pronouns": "he/him"
  },
  
  // Professional Information
  "professional_info": {
    "title": "CEO and Founder",
    "company": "Innovation Corp",
    "tagline": "Transforming Organizations Through Innovation",
    "credentials": ["MBA", "PhD"],
    "years_speaking": 15
  },
  
  // Location
  "location": {
    "city": "New York",
    "state": "NY",
    "country": "United States",
    "country_code": "US",
    "region": "North America",
    "available_for_travel": true,
    "virtual_available": true
  },
  
  // Biography (multiple lengths for different uses)
  "biography": {
    "brief": "50-word elevator pitch...",
    "short": "200-word summary...",
    "full": "Complete biography..."
  },
  
  // Expertise and Topics
  "expertise": {
    "primary_topics": ["leadership", "innovation", "technology"],
    "all_topics": ["leadership", "digital transformation", ...],
    "industries": ["technology", "healthcare", "finance"],
    "keywords": ["AI", "future of work", "disruption"]
  },
  
  // Speaking Information
  "speaking_info": {
    "fee_range": {
      "min": 10000,
      "max": 20000,
      "currency": "USD",
      "display": "$10,000 - $20,000",
      "category": "10k-20k",
      "negotiable": true,
      "travel_additional": true
    },
    "languages": ["English", "Spanish"],
    "presentation_types": ["keynote", "workshop", "panel"],
    "audience_types": ["corporate", "association", "education"],
    "speech_topics": [
      {
        "title": "Leading Through Digital Disruption",
        "description": "How to navigate...",
        "duration_minutes": 60
      }
    ]
  },
  
  // Media Assets
  "media": {
    "primary_image": "https://...",
    "images": ["url1", "url2"],
    "videos": [
      {
        "url": "https://youtube.com/...",
        "title": "TEDx Talk on Innovation",
        "duration": 1080,
        "type": "keynote"
      }
    ],
    "speaker_reel": "https://...",
    "one_sheet": "https://..."
  },
  
  // Social Media & Web Presence
  "online_presence": {
    "website": "https://johnsmith.com",
    "social_media": {
      "linkedin": "https://linkedin.com/in/johnsmith",
      "twitter": "@johnsmith",
      "youtube": "https://youtube.com/c/johnsmith"
    },
    "booking_sites": {
      "a_speakers": "https://a-speakers.com/john-smith",
      "bigspeak": "https://bigspeak.com/speakers/john-smith"
    }
  },
  
  // Publications & Recognition
  "achievements": {
    "books": [
      {
        "title": "The Innovation Mindset",
        "publisher": "Business Press",
        "year": 2023,
        "amazon_url": "https://..."
      }
    ],
    "awards": ["Top 50 Keynote Speakers 2023"],
    "certifications": ["Certified Speaking Professional"],
    "media_features": ["Forbes", "Inc Magazine"]
  },
  
  // Client Engagement History
  "engagement": {
    "years_experience": 15,
    "total_speeches": 500,
    "notable_clients": ["Google", "Microsoft", "IBM"],
    "testimonials": [
      {
        "text": "Outstanding speaker who transformed our event...",
        "author": "Jane Doe",
        "title": "CEO",
        "company": "Tech Corp",
        "date": "2023-10-15",
        "rating": 5
      }
    ],
    "ratings": {
      "average": 4.8,
      "count": 127,
      "distribution": {"5": 100, "4": 20, "3": 7}
    }
  },
  
  // Contact Information
  "contact": {
    "email": "booking@johnsmith.com",
    "phone": "+1-555-123-4567",
    "agent": {
      "name": "Speaker Agency Inc",
      "email": "agent@agency.com",
      "phone": "+1-555-987-6543"
    },
    "booking_url": "https://johnsmith.com/booking",
    "preferred_contact": "agent"
  },
  
  // Metadata
  "metadata": {
    "sources": ["a_speakers", "bigspeak", "speakerhub"],
    "primary_source": "a_speakers",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-20T15:30:00Z",
    "last_verified": "2024-01-20T15:30:00Z",
    "profile_score": 85,  // 0-100 completeness score
    "verification_status": "verified|partial|unverified",
    "merge_confidence": 0.95,  // Confidence in duplicate detection
    "data_quality": {
      "has_email": true,
      "has_fee": true,
      "has_video": true,
      "has_testimonials": true,
      "biography_length": 500
    }
  }
}
```

## Data Transformation Strategy

### 1. Deduplication Process
- **Primary Key**: Normalized name (lowercase, remove titles)
- **Matching Criteria**:
  - Exact name match (85%+ similarity)
  - Social media URL overlap
  - Location + similar name (70%+ similarity)
- **Merge Priority**: Most complete profile wins, then most recent

### 2. Data Normalization

#### Names
- Remove titles (Dr., Mr., Ms., etc.)
- Separate first/last names
- Preserve display name with titles

#### Locations
- Parse city, state, country from various formats
- Normalize country names to standard
- Add country codes and regions

#### Fees
- Extract numeric ranges from text
- Categorize into standard brackets
- Preserve original display text

#### Topics
- Map to normalized taxonomy
- Preserve original topics
- Generate searchable keywords

### 3. Quality Scoring
Profile completeness score (0-100) based on:
- Name and basic info: 20 points
- Biography content: 15 points
- Location data: 10 points
- Topics/expertise: 15 points
- Fee information: 10 points
- Media (images/videos): 10 points
- Contact information: 10 points
- Testimonials/ratings: 10 points

### 4. Search Optimization
- Full-text index on: name, title, biography, topics
- Faceted search on: location, topics, fee range, languages
- Sorting options: relevance, name, completeness, fee

## Benefits of Unified Structure

1. **Single Source of Truth**: No more checking multiple databases
2. **Comprehensive Profiles**: Combined data from all sources
3. **Better Search**: Consistent fields enable powerful queries
4. **Quality Metrics**: Know which profiles are most complete
5. **Duplicate Prevention**: Each speaker appears only once
6. **Scalability**: Easy to add new data sources
7. **API-Ready**: Consistent structure for applications

## Implementation Notes

1. **Run Time**: Full consolidation takes ~10-15 minutes
2. **Storage**: Unified database is ~30% smaller due to deduplication
3. **Updates**: Can be run incrementally to add new data
4. **Indexes**: Created on commonly searched fields for performance
5. **Backup**: Original databases remain untouched

## Future Enhancements

1. **Automated Updates**: Periodic re-scraping of source sites
2. **Manual Verification**: Admin interface for data quality
3. **Speaker Claiming**: Allow speakers to claim and update profiles
4. **Rich Media**: Store presentation slides, audio samples
5. **Availability Calendar**: Track speaker availability
6. **Price History**: Track fee changes over time
7. **Event Feedback**: Collect post-event reviews