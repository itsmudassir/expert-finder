# 02. Speaker Data Normalization Analysis

[← Previous: Data Transformation](01_DATA_TRANSFORMATION_OVERVIEW.md) | [Next: Implementation Guide →](03_NORMALIZATION_IMPLEMENTATION.md)

---

## Executive Summary
After analyzing speaker data from 7 different sources (A-Speakers, BigSpeak, Leading Authorities, Sessionize, SpeakerHub, AllAmericanSpeakers, EventRaptor, and The Speaker Handbook), I've identified extensive normalization opportunities across multiple dimensions. The data shows significant inconsistencies in field naming, value formatting, and concept representation that would benefit from standardization.

## Sources Analyzed
1. **A-Speakers** - Traditional speaker bureau format
2. **BigSpeak** - Corporate speaker bureau with structured data
3. **Leading Authorities** - High-end bureau with detailed profiles
4. **Sessionize** - Tech/conference speaker platform
5. **SpeakerHub** - Community-driven speaker marketplace
6. **AllAmericanSpeakers** - Entertainment-focused bureau
7. **EventRaptor** - Event platform with speaker profiles
8. **The Speaker Handbook** - UK-based speaker directory

## Major Normalization Opportunities

### 1. Event Types and Formats

#### Field Name Variations
- `event_types` (SpeakerHub, EventRaptor)
- `engagement_types` (The Speaker Handbook)
- `speaking_programs` (BigSpeak)
- `keynote_topics` (BigSpeak)
- `talks` (The Speaker Handbook)
- `presentations` (SpeakerHub)

#### Value Variations
- **Conference Formats:**
  - "Conference" vs "Conference (Full-day Event)"
  - "keynote" vs "Keynote" vs "Speaking"
  - "Workshop" vs "Workshop (3+ hour event)" vs "Workshops"
  - "Webinar" vs "Webinar (Virtual event)" vs "Virtual event"
  - "Panel" vs "Panel Participation" vs "Panel Discussion"
  
- **MC/Host Roles:**
  - "Emcee" vs "Moderator" vs "Host/Emcee Speakers" vs "Moderating And Emcee" vs "Event Hosting"
  - "Moderator" vs "Moderating" vs "Moderation"

- **Educational Formats:**
  - "School (incl. charity)" vs "Educational Motivational"
  - "Certificate Program" vs "Coaching" vs "Training"
  - "Meetup" vs "Meeting" vs "Session"

### 2. Fee Range Representations

#### Field Name Variations
- `fee_range` (A-Speakers, BigSpeak)
- `speaker_fees` (SpeakerHub, Leading Authorities)
- `fees` (The Speaker Handbook)

#### Value Format Variations
- **Text Descriptions:**
  - "Request price and availability"
  - "Please Inquire"
  - "$10,001 - $20,000"
  - "$10,000 - $20,000"
  
- **Structure Variations:**
  - Simple string: "$50,000 - $100,000"
  - Object with event types: `{"live_event": "$100,000 - $200,000", "virtual_event": "$100,000 - $200,000"}`
  - Regional pricing: `{"Local": "$20,001 - $35,000*", "US East": "$35,001 - $55,000*"}`
  - Null/empty values

### 3. Location and Geography

#### Field Name Variations
- `location` (most sources)
- `city`, `country`, `state_province` (SpeakerHub - separated)
- `travels_from` (The Speaker Handbook)
- `nationality` (The Speaker Handbook)

#### Value Format Variations
- Full format: "San Francisco, CA, USA"
- City only: "London"
- Country only: "Canada"
- State/Province: "California"
- Special cases: "nationwide", "Worldwide", "an undisclosed location"
- Mixed separators: "New York City" vs "New York, NY"

### 4. Expertise Areas and Topics

#### Field Name Variations
- `topics` (A-Speakers, Leading Authorities, The Speaker Handbook)
- `topic_categories` (SpeakerHub)
- `expertise_areas` (Sessionize)
- `business_areas` (EventRaptor)
- `categories` (AllAmericanSpeakers)
- `keynote_topics` (BigSpeak)
- `knows_about` (The Speaker Handbook)

#### Value Variations
- **Leadership Topics:**
  - "Leadership" vs "Leadership & Management" vs "Leadership and Change"
  - "Leadership development" vs "Leadership Development"
  - "Corporate Leadership" vs "Business Leadership"

- **Technology Topics:**
  - "Technology" vs "Technology & AI" vs "Emerging Technologies"
  - "AI" vs "Artificial Intelligence" vs "AI & Machine Learning"
  - "Digital Transformation" vs "Digital Disruption" vs "Digitalization"

- **Business Topics:**
  - "Business" vs "Business & Management" vs "Business Success"
  - "Entrepreneurship" vs "Entrepreneurial" vs "Startups"
  - "Marketing" vs "Media & Marketing" vs "Brand Marketing"

### 5. Credentials and Qualifications

#### Field Name Variations
- `credentials` (EventRaptor, SpeakerHub)
- `professional_title` (SpeakerHub)
- `certifications` (SpeakerHub)
- `awards` (Multiple sources)

#### Value Format Variations
- Embedded in name: "John Smith, PhD" vs separate field
- Abbreviations: "PhD" vs "Ph.D." vs "Doctor"
- "MBA" vs "M.B.A." vs "Masters in Business Administration"
- "CLC" vs "Certified Life Coach"

### 6. Media and Assets

#### Field Name Variations
- `videos` (most sources)
- `video_categories` (The Speaker Handbook)
- `profile_picture_url` vs `image_url` vs `speaker_image_url`
- `images` vs `image_gallery`

#### Structure Variations
- Simple URL list
- Objects with metadata: `{url, title, description, platform, thumbnail}`
- Categorized videos: `{"Showreels": [...], "Media appearances": [...]}`

### 7. Biography and Description

#### Field Name Variations
- `bio_summary` vs `biography` vs `full_bio`
- `description` vs `job_title` vs `tagline`
- `why_choose_me` (SpeakerHub specific)

### 8. Speaking History

#### Field Name Variations
- `past_talks` (SpeakerHub)
- `events` (Sessionize, EventRaptor)
- `speaking_history` (Sessionize)

#### Structure Variations
- Simple list of event names
- Detailed objects with date, location, title
- Mixed with session information

### 9. Social Media

#### Field Name Variations
- `social_media` (most sources)
- `social_links` (Sessionize, The Speaker Handbook)

#### Structure Variations
- URL only: `{"twitter": "https://twitter.com/username"}`
- Handle included: `{"twitter": {"url": "...", "handle": "@username"}}`
- Platform variations: "twitter" vs "Twitter" vs "X"

### 10. Availability Indicators

#### Value Variations for Virtual Capability
- `virtual_capable: true` (BigSpeak)
- Embedded in fee structure
- Listed as event type option
- "Available: In person, Virtually" (The Speaker Handbook)

## Recommended Normalization Strategy

### 1. Standardize Field Names
Create a unified schema with consistent field naming:
```
- event_formats (instead of event_types, engagement_types, etc.)
- fee_ranges (with sub-structure for different event types)
- expertise_topics (unified topic taxonomy)
- location_base (for primary location)
- travel_availability (for travel willingness)
```

### 2. Create Controlled Vocabularies
Develop standardized lists for:
- Event formats (with aliases mapping)
- Topic categories (hierarchical taxonomy)
- Credential abbreviations
- Country/Region codes
- Language codes (ISO standards)

### 3. Implement Data Transformation Rules
- Standardize fee range formats to numerical min/max
- Normalize location strings to structured format
- Extract and standardize credentials from names
- Map topic variations to canonical terms

### 4. Handle Special Cases
- Create "Unknown" or "By Request" categories for missing data
- Maintain source-specific fields as metadata
- Implement confidence scores for automated mappings

### 5. Quality Assurance
- Validation rules for each field type
- Automated testing for transformation accuracy
- Manual review process for ambiguous mappings

## Implementation Priority
1. **High Priority**: Fee ranges, event formats, core topics
2. **Medium Priority**: Locations, credentials, media assets  
3. **Low Priority**: Speaking history, social media, auxiliary fields

## Conclusion
The speaker data ecosystem shows significant fragmentation in how similar concepts are represented. A comprehensive normalization effort would greatly improve data quality, searchability, and cross-platform compatibility. The variations identified here provide a roadmap for creating a unified speaker data standard that preserves source-specific nuances while enabling consistent analysis and search capabilities.

---

[← Previous: Data Transformation](01_DATA_TRANSFORMATION_OVERVIEW.md) | [Next: Implementation Guide →](03_NORMALIZATION_IMPLEMENTATION.md)
