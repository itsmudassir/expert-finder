# Expert Speaker Database Schema Analysis Report

## Overview
This report analyzes 9 MongoDB databases containing expert speaker profiles from different websites. The goal is to consolidate these into a unified data source with comprehensive querying capabilities.

## Database Summary

### 1. a_speakers (3,592 speakers)
- **Source**: A-Speakers website
- **Key Fields**: name, location, description, job_title, fee_range, topics, keynotes, reviews, average_rating, image_url, videos
- **Unique Features**: Has structured keynotes array, why_book_points, average rating with reviews

### 2. allamericanspeakers (11,081 speakers)
- **Source**: All American Speakers Bureau
- **Key Fields**: name, speaker_id, location, job_title, biography, categories, fee_range (object), speaking_topics, videos
- **Unique Features**: Detailed fee_range as object, categories array

### 3. bigspeak_scraper (2,178 speakers + detailed profiles)
- **Collections**: speakers, speaker_profiles
- **Key Fields**: name, speaker_id, biography, fee_range, topics, keynote_topics, books, testimonials, awards
- **Unique Features**: Two-level data structure with basic info and detailed profiles

### 4. eventraptor (2,986 speakers)
- **Source**: Event Raptor platform
- **Key Fields**: name, tagline, biography, credentials, business_areas, events, social_media, email
- **Unique Features**: Has direct email contact, credentials field, event history

### 5. freespeakerbureau_scraper (436 speakers)
- **Source**: Free Speaker Bureau
- **Key Fields**: name, location (city/state/country), company, role, speaking_topics, areas_of_expertise, awards, contact_info
- **Unique Features**: Most detailed contact info, speaker onesheet URLs, member levels

### 6. leading_authorities (1,230 speakers)
- **Source**: Leading Authorities
- **Key Fields**: name, job_title, description, topics, speaker_fees, books_and_publications, client_testimonials, social_media
- **Unique Features**: Download profile/topics links, recent news, structured fee information

### 7. sessionize_scraper (12,827 speakers)
- **Collections**: speakers, speaker_profiles, categories
- **Key Fields**: username, name, location, tagline, events_count, sessions_count, categories
- **Unique Features**: Event/session statistics, username-based system

### 8. speakerhub_scraper (20,548 speakers)
- **Source**: Speaker Hub
- **Key Fields**: name, location (city/state/country), company, job_title, bio_summary, topics, languages, event_types
- **Unique Features**: Multiple language support, available_regions, speaker_type

### 9. thespeakerhandbook_scraper (3,510 speakers)
- **Collections**: speakers, speaker_profiles
- **Key Fields**: name, location, strapline, topics, notability, engagement_types, event_types, fee_types
- **Unique Features**: Gender field, notability array, testimonials with detailed structure

## Common Fields Across Databases

### Core Identity Fields
- **name** (all databases)
- **location** (varies: string vs object)
- **job_title/role** (most databases)
- **company** (some databases)

### Professional Information
- **biography/bio/description** (all databases)
- **topics/speaking_topics** (all databases)
- **fee_range/speaker_fees** (most databases)
- **credentials** (eventraptor, freespeakerbureau)

### Media & Social
- **image_url/profile_picture** (all databases)
- **videos** (most databases)
- **social_media** (several databases)

### Engagement Data
- **reviews/testimonials** (several databases)
- **ratings** (a_speakers, allamericanspeakers)
- **events/speaking_history** (eventraptor, sessionize)

## Schema Variations & Challenges

1. **Location Format**:
   - Simple string: "Australia", "UK"
   - Detailed: city, state, country as separate fields
   - Mixed formats within same database

2. **Fee Information**:
   - String: "$40,001 - $50,000", "Please Inquire"
   - Object with structured data
   - Missing in some databases

3. **Topics/Categories**:
   - Array of strings
   - Array of objects
   - Different naming conventions

4. **Contact Information**:
   - Direct email (rare)
   - Contact objects
   - Website URLs only

5. **Ratings/Reviews**:
   - Numeric ratings
   - Review arrays with text
   - Testimonial objects

## Recommended Unified Schema

```json
{
  "_id": "unique_speaker_id",
  "source_ids": {
    "a_speakers": "url_or_id",
    "allamericanspeakers": "speaker_id",
    // ... other sources
  },
  "basic_info": {
    "full_name": "string",
    "first_name": "string",
    "last_name": "string",
    "gender": "string",
    "pronouns": "string"
  },
  "professional_info": {
    "job_title": "string",
    "company": "string",
    "tagline": "string",
    "credentials": ["array"],
    "years_experience": "number"
  },
  "location": {
    "city": "string",
    "state_province": "string",
    "country": "string",
    "country_code": "string",
    "timezone": "string",
    "available_regions": ["array"]
  },
  "biography": {
    "short": "string (< 200 chars)",
    "medium": "string (< 500 chars)",
    "full": "string"
  },
  "expertise": {
    "topics": ["array of normalized topics"],
    "categories": ["array of normalized categories"],
    "industries": ["array"],
    "keywords": ["array for search"]
  },
  "speaking_info": {
    "fee_range": {
      "min": "number",
      "max": "number",
      "currency": "string",
      "display": "string",
      "negotiable": "boolean"
    },
    "languages": ["array"],
    "event_types": ["array"],
    "engagement_types": ["array"],
    "keynote_topics": ["array of objects"]
  },
  "media": {
    "profile_images": ["array of image URLs"],
    "videos": ["array of video objects"],
    "speaker_reel_url": "string"
  },
  "social_media": {
    "website": "string",
    "linkedin": "string",
    "twitter": "string",
    "facebook": "string",
    "instagram": "string",
    "youtube": "string"
  },
  "publications": {
    "books": ["array of book objects"],
    "articles": ["array"],
    "awards": ["array"]
  },
  "engagement_history": {
    "total_events": "number",
    "notable_clients": ["array"],
    "testimonials": ["array of testimonial objects"],
    "ratings": {
      "average": "number",
      "count": "number",
      "distribution": "object"
    }
  },
  "contact_info": {
    "email": "string",
    "phone": "string",
    "booking_url": "string",
    "agent_info": "object"
  },
  "metadata": {
    "sources": ["array of source databases"],
    "last_updated": "datetime",
    "verification_status": "string",
    "profile_completeness": "number (0-100)"
  }
}
```

## Data Quality Issues

1. **Duplicate Speakers**: Same person appears in multiple databases
2. **Name Variations**: "Bob Smith" vs "Robert Smith"
3. **Missing Data**: Many optional fields are empty
4. **Inconsistent Formats**: Especially for fees and locations
5. **Stale Data**: Some profiles haven't been updated recently

## Consolidation Strategy

1. **Entity Resolution**: Match speakers across databases using:
   - Exact name matches
   - Fuzzy name matching
   - Location + name combination
   - Social media URLs

2. **Data Merging**: Priority order for conflicting data:
   - Most recent update
   - Most complete information
   - Trusted sources first

3. **Normalization**:
   - Standardize location formats
   - Convert fee ranges to numeric values
   - Normalize topic categories
   - Clean and validate URLs

4. **Search Optimization**:
   - Create search indexes on all text fields
   - Generate keyword arrays
   - Build topic taxonomy
   - Location-based search capabilities