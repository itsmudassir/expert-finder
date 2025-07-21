# Merge Summary: consolidate_speakers_v2_full.py

## Overview
Successfully merged enhancements from `consolidate_speakers_v2.py` into `consolidate_speakers_v2_full.py` to create a complete consolidation script that processes all 10 data sources.

## Key Changes Made

### 1. Updated Imports
- Added `from expertise_normalizer import ExpertiseNormalizer`

### 2. Class Name Change
- Changed from `SpeakerConsolidator` to `EnhancedSpeakerConsolidator`
- Added `self.expertise_normalizer = ExpertiseNormalizer()` to `__init__`

### 3. Enhanced Profile Structure
Added new fields to the profile structure:
- `professional_info['job_description']` - From llm_parsed_db
- Enhanced `expertise` section with:
  - `primary_categories`, `secondary_categories`, `parent_categories`
  - `keywords`, `original_terms`, `research_areas`
  - `legacy_topics` for backward compatibility
- New `education` section with degrees, institutions, fields_of_study
- `speaking_info['event_types']` - From llm_parsed_db
- `achievements['patents']` and `achievements['publications']`
- `engagement['case_studies']`
- `metadata['data_quality_tier']` - cat_1 through cat_4

### 4. New Methods Added
- `process_llm_parsed_db()` - Processes all 4 categories from llm_parsed_db
- `_merge_field()` - Helper method for merging fields
- Enhanced `merge_profiles()` with expertise normalization
- Enhanced `calculate_profile_score()` with new scoring logic

### 5. Updated Processing Methods
All process_* methods now:
- Store topics in both legacy format and as original terms
- Use the expertise normalizer to generate normalized categories
- Properly populate the new expertise structure

### 6. Enhanced MongoDB Operations
- Updated `save_to_mongodb()` with additional data quality flags
- Enhanced `create_indexes()` with new fields for better search

### 7. Updated Statistics
- `print_stats()` now includes llm_parsed_db category counts
- Shows "ENHANCED CONSOLIDATION STATISTICS" header

## Database Changes
- Target database changed from `expert_finder_unified` to `expert_finder_unified_v2`
- Collection remains `speakers`

## Processing Order
1. Original 9 databases (a_speakers through thespeakerhandbook)
2. New llm_parsed_db (cat_1 through cat_4)
3. Save to MongoDB with enhanced indexing

## Usage
```bash
python3 consolidate_speakers_v2_full.py
```

The script will process all 10 data sources and create a unified speaker database with advanced expertise normalization and enhanced data quality tracking.