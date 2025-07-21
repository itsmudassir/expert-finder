# 03. Speaker Data Normalization Implementation Guide

[← Previous: Normalization Analysis](02_NORMALIZATION_ANALYSIS.md) | [Next: Technical Consolidation V1 →](04_TECHNICAL_CONSOLIDATION_V1.md)

---
*A Step-by-Step Approach to Standardizing Speaker Information*

## 🎯 Goal
Transform messy, inconsistent speaker data from multiple sources into clean, standardized information that's easy to search and analyze.

## 📊 The Problem
We have speaker data from 7+ different sources, and they all describe the same things differently:
- One source says "Webinar", another says "Virtual event", another says "Webinar (Virtual event)"
- Fees are shown as "$10,000-$20,000" in one place and "10K to 20K" in another
- Same person might be "PhD" in one database and "Ph.D." in another

## 🔍 What We Found: Top 10 Normalization Opportunities

### 1. **Event Types** 🎤
**Current Chaos:**
```
"keynote" vs "Keynote Speaker" vs "Keynote Presentation"
"workshop" vs "Workshop (3+ hours)" vs "Training Workshop"
"webinar" vs "Virtual Event" vs "Online Presentation"
```
**Solution:** Create standard event types with aliases

### 2. **Speaking Fees** 💰
**Current Chaos:**
```
"$10,000 - $20,000"
"10K-20K"
"Please Inquire"
"Contact for rates"
null/empty
```
**Solution:** Convert to consistent numerical ranges

### 3. **Locations** 📍
**Current Chaos:**
```
"NYC" vs "New York City" vs "New York, NY, USA"
"UK" vs "United Kingdom" vs "Great Britain"
"Virtual" vs "Worldwide" vs "Online"
```
**Solution:** Standardize to City, State/Province, Country format

### 4. **Expertise Topics** 🎯
**Current Chaos:**
```
"AI" vs "Artificial Intelligence" vs "A.I." vs "Machine Learning & AI"
"Leadership" vs "Leadership Development" vs "Executive Leadership"
"HR" vs "Human Resources" vs "People & Culture"
```
**Solution:** Create topic taxonomy with preferred terms

### 5. **Professional Credentials** 🎓
**Current Chaos:**
```
"John Smith, PhD" vs "Dr. John Smith" vs "John Smith (PhD)"
"MBA" vs "M.B.A." vs "Master of Business Administration"
"Certified Coach" vs "ACC" vs "ICF Certified"
```
**Solution:** Extract and standardize credentials

### 6. **Virtual Capabilities** 💻
**Current Chaos:**
```
virtual_capable: true
"Available virtually"
Listed under event_types
Mentioned in biography only
```
**Solution:** Add explicit virtual_available boolean field

### 7. **Media Types** 📹
**Current Chaos:**
```
"Demo Reel" vs "Speaker Reel" vs "Sizzle Reel"
"Headshot" vs "Profile Photo" vs "Professional Photo"
Videos mixed with photos in same field
```
**Solution:** Separate media types with clear categories

### 8. **Audience Types** 👥
**Current Chaos:**
```
"C-Suite" vs "C-Level" vs "Executive"
"HR Professionals" vs "Human Resources" vs "People Teams"
"Entrepreneurs" vs "Startup Founders" vs "Business Owners"
```
**Solution:** Create audience taxonomy

### 9. **Languages** 🌍
**Current Chaos:**
```
"English" vs "EN" vs "English (Native)"
"Spanish" vs "Español" vs "ES"
Some list languages, others don't
```
**Solution:** Use ISO language codes with display names

### 10. **Time/Experience Fields** ⏰
**Current Chaos:**
```
"20 years experience" vs "Since 2004" vs "Two decades"
"Available immediately" vs "2 weeks notice" vs unspecified
Mixed formats for years in business
```
**Solution:** Convert to structured numerical fields

## 📋 Step-by-Step Normalization Process

### Phase 1: Quick Wins (Week 1)
✅ **Step 1:** Standardize Yes/No Fields
- Virtual capability → `virtual_available: true/false`
- International travel → `travels_internationally: true/false`

✅ **Step 2:** Clean Up Fee Ranges
- Extract min/max values from fee strings
- Convert "Please Inquire" → `fee_range: "CUSTOM"`
- Separate virtual vs in-person fees

✅ **Step 3:** Basic Location Cleanup
- Map common abbreviations (NYC → New York City)
- Standardize country names (USA → United States)

### Phase 2: Core Standardization (Week 2-3)
✅ **Step 4:** Create Event Type Mapping
```python
event_type_map = {
    "keynote": "Keynote",
    "keynoter": "Keynote",
    "keynote speaker": "Keynote",
    "workshop": "Workshop",
    "breakout session": "Workshop",
    "webinar": "Virtual Event",
    "virtual presentation": "Virtual Event",
    # ... etc
}
```

✅ **Step 5:** Build Topic Taxonomy
- Create hierarchical topic structure
- Map variations to preferred terms
- Add topic categories (Business, Technology, Leadership, etc.)

✅ **Step 6:** Extract Professional Info
- Pull credentials from name fields
- Standardize credential abbreviations
- Create separate credential fields

### Phase 3: Advanced Normalization (Week 4)
✅ **Step 7:** Process Complex Fields
- Parse speaking history into structured format
- Separate media by type (video, photo, audio)
- Extract years of experience from bios

✅ **Step 8:** Create Cross-References
- Link similar topics
- Map audience types
- Connect related expertise areas

✅ **Step 9:** Add Calculated Fields
- `experience_years` from bio/history
- `topic_count` from expertise
- `avg_fee_range` from min/max

### Phase 4: Quality Control (Week 5)
✅ **Step 10:** Validate & Verify
- Run automated checks
- Flag suspicious mappings
- Manual review of edge cases

## 🎉 The Result: Clean, Searchable Data

### Before Normalization:
```json
{
  "name": "Dr. Jane Smith, MBA",
  "topics": ["AI", "Leadership development", "Digital transformation"],
  "location": "NYC",
  "fee": "10-20K",
  "events": ["keynotes", "workshop", "virtual"]
}
```

### After Normalization:
```json
{
  "name": "Jane Smith",
  "credentials": ["PhD", "MBA"],
  "topics": {
    "primary": ["Artificial Intelligence", "Leadership", "Digital Transformation"],
    "categories": ["Technology", "Business", "Leadership"]
  },
  "location": {
    "city": "New York City",
    "state": "NY",
    "country": "United States",
    "formatted": "New York City, NY, USA"
  },
  "fees": {
    "keynote": {"min": 10000, "max": 20000, "currency": "USD"},
    "workshop": {"min": 15000, "max": 25000, "currency": "USD"},
    "virtual": {"min": 5000, "max": 10000, "currency": "USD"}
  },
  "capabilities": {
    "virtual_available": true,
    "travels_internationally": true,
    "languages": ["en"]
  },
  "event_formats": ["Keynote", "Workshop", "Virtual Event"],
  "metadata": {
    "sources": ["bigspeak", "leading_authorities"],
    "last_normalized": "2024-01-15",
    "confidence_score": 0.95
  }
}
```

## 🚀 Quick Start Checklist

1. **[ ] Map your data sources** - List all fields from each source
2. **[ ] Identify common concepts** - Find fields that mean the same thing
3. **[ ] Create mapping tables** - Build translation dictionaries
4. **[ ] Write transformation scripts** - Automate the conversion
5. **[ ] Test with sample data** - Verify accuracy
6. **[ ] Process full dataset** - Run complete transformation
7. **[ ] Validate results** - Check for errors and edge cases
8. **[ ] Document decisions** - Record why you made specific choices

## 💡 Pro Tips

- **Start small**: Normalize one field type at a time
- **Keep originals**: Always preserve source data
- **Track confidence**: Flag automated vs verified mappings
- **Be consistent**: Once you pick a standard, stick to it
- **Think search**: Normalize for how users will search

## 📈 Success Metrics

After normalization, you should be able to:
- ✅ Search for "AI speakers" and find everyone who speaks about artificial intelligence (regardless of how it was originally written)
- ✅ Filter by fee range using numerical values
- ✅ Find all speakers in "New York" whether source said NYC, New York, or Manhattan
- ✅ Identify all virtual-capable speakers with one query
- ✅ Compare speakers across sources using standardized data

## 🎯 End Goal
Transform your speaker data from a confusing mess into a clean, searchable, analyzable resource that helps users find the perfect speaker every time!