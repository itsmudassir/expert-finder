# Expert Finder - Unified Speaker Database V4

A comprehensive solution for consolidating and normalizing speaker data from multiple sources into a unified, searchable database with advanced expertise categorization and market-standard filtering capabilities.

## 🚀 Overview

This project consolidates speaker profiles from 10 different databases with varying schemas into a single, normalized MongoDB database. Version 4 now includes comprehensive market-standard normalizations based on industry research, processing data into unique speaker profiles with:

- **Unified Schema**: Consistent structure across all sources with 75+ standardized fields
- **Multi-Dimensional Normalization**:
  - **Expertise**: 41 standardized categories from 34,000+ unique terms
  - **Industries**: 15 normalized industries from 274+ variations
  - **Languages**: ISO 639-1 standardization with proficiency levels
  - **Credentials**: Degrees, certifications, awards normalization
  - **Speaking Formats**: Session types, audience, duration standardization
  - **Demographics**: Sensitive handling of diversity data
- **Duplicate Detection**: Fuzzy name matching with 85% threshold
- **Enhanced Scoring**: Profile completeness, quality, and experience ratings
- **Advanced Search**: Full-text search with 50+ faceted filters

## 📊 Data Sources

The system consolidates data from:

1. **Original 9 Speaker Bureaus**:
   - a_speakers
   - allamericanspeakers
   - bigspeak_scraper
   - eventraptor
   - freespeakerbureau_scraper
   - leading_authorities
   - sessionize_scraper
   - speakerhub_scraper
   - thespeakerhandbook_scraper

2. **LLM Parsed Database**:
   - cat_1 (highest quality)
   - cat_2 (high quality)
   - cat_3 (medium quality)
   - cat_4 (lower quality)

## 🛠️ Key Features (V4 Enhanced)

### 1. Comprehensive Normalization Systems
- **Expertise Taxonomy**: 41 categories, 9 parent groups, hierarchical classification
- **Industry Normalization**: 15 standard industries (Healthcare, Technology, Finance, etc.)
- **Language Normalization**: ISO 639-1 codes with proficiency levels
- **Credential Standardization**: Degree mappings (PhD vs Ph.D.), certifications (PMP, CISSP)
- **Speaking Format Normalization**: Keynote, workshop, panel, webinar standardization
- **Demographics Normalization**: Gender, age brackets, diversity categories (sensitive handling)

### 2. Market-Standard Fields
- **Professional**: Leadership level, years experience, board memberships
- **Speaking Experience**: Years speaking, talks delivered, countries spoken
- **Commercial**: Fee ranges, pro bono acceptance, bureau commission
- **Availability**: Calendar links, lead time, blackout dates
- **Compliance**: Background checks, NDAs, insurance, industry compliance
- **Sustainability**: Carbon offset, virtual-first preferences
- **Engagement Metrics**: NPS scores, rebooking rates, testimonial counts

### 3. Enhanced Search Capabilities
- Full-text search across all fields
- 50+ filter dimensions matching industry standards
- Multi-faceted filtering (combine any filters)
- Scoring-based result ranking
- Quality tier filtering (cat_1-cat_4)

### 4. Data Quality & Scoring
- **Profile Completeness Score**: 0-100% based on filled fields
- **Experience Score**: Based on years, talks, ratings
- **Data Quality Tiers**: Source-based quality indicators
- **Verification Status**: Tracking data validation

## 📁 Project Structure

```
expert_finder/
├── src/
│   └── normalizers/           # All normalization modules
│       ├── __init__.py
│       ├── expertise_normalizer.py      # 41 expertise categories
│       ├── industry_normalizer.py       # 15 industry categories
│       ├── language_normalizer.py       # ISO language codes
│       ├── credential_normalizer.py     # Degrees, certs, awards
│       ├── speaking_normalizer.py       # Formats, audiences, duration
│       └── demographics_normalizer.py   # Gender, age, diversity
├── consolidate_speakers_v4_enhanced.py  # V4 consolidation with all normalizers
├── query_speakers_v4_enhanced.py        # Advanced query interface
├── docs/                                # Comprehensive documentation
│   ├── 00_START_HERE.md
│   ├── 01_PROJECT_OVERVIEW.md
│   ├── 02_DATA_TRANSFORMATION_GUIDE.md
│   ├── 03_NORMALIZATION_DEEP_DIVE.md
│   ├── 04_IMPLEMENTATION_GUIDE.md
│   ├── 05_QUERYING_GUIDE.md
│   ├── 06_ROADMAP.md
│   └── 07_MARKET_COMPARISON_ANALYSIS.md
└── samples/                             # Sample data from each source
```

## 🚦 Getting Started

### Prerequisites

- Python 3.8+
- MongoDB access
- Required Python packages:
  ```bash
  pip install pymongo python-dateutil
  ```

### Configuration

Set your MongoDB connection string in the scripts:
```python
MONGO_URI = "mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin"
```

### Running the V4 Consolidation

1. **Run the enhanced consolidation**:
   ```bash
   python3 consolidate_speakers_v4_enhanced.py
   ```

2. **Query with enhanced filters**:
   ```bash
   # Search with multiple filters
   python3 query_speakers_v4_enhanced.py \
     --expertise artificial_intelligence \
     --industry healthcare \
     --language en \
     --has-video \
     --min-rating 4.5
   
   # Filter by speaking format and audience
   python3 query_speakers_v4_enhanced.py \
     --format keynote \
     --audience executives \
     --fee-range "10000-20000"
   
   # Find diverse speakers
   python3 query_speakers_v4_enhanced.py \
     --diversity woman \
     --expertise technology \
     --has-degree PhD
   ```

## 📈 V4 Database Statistics

Current enhanced database contains:
- **Total Unique Profiles**: 11,043+ 
- **With Normalized Expertise**: 95%+
- **With Industry Classification**: 90%+
- **With Credentials Extracted**: 95%+
- **Average Profile Completeness**: 75%+

### Normalization Coverage
- **Expertise Categories**: 41 standardized from 34,000+ terms
- **Industries**: 15 standardized from 274+ variations  
- **Languages**: ISO 639-1 codes for all language data
- **Degrees**: Standardized format for all academic credentials
- **Speaking Formats**: 8 primary formats normalized
- **Audience Types**: 15 standardized audience categories

## 🔄 V4 Data Processing Pipeline

```
Raw Databases → Enhanced Extraction → Multi-Dimensional Normalization → 
     ↓                   ↓                        ↓
10 sources      75+ field extraction      6 normalization systems
                                                 ↓
                                    Deduplication & Scoring →
                                                 ↓
                                    MongoDB with 50+ indexes
```

## 🎯 Use Cases

1. **Event Planners**: Find speakers with 50+ filter combinations
2. **Diversity & Inclusion**: Search for underrepresented speakers
3. **Virtual Events**: Filter by virtual platform experience
4. **Budget Planning**: Detailed fee range and pro bono filters
5. **International Events**: Language and travel requirement matching
6. **Compliance Requirements**: Background check and certification filters
7. **Sustainability**: Find carbon-neutral speakers

## 📚 Documentation

Start with [00_START_HERE.md](docs/00_START_HERE.md) for the complete documentation guide.

Key documents:
- [Project Overview](docs/01_PROJECT_OVERVIEW.md) - System architecture
- [Market Comparison Analysis](docs/07_MARKET_COMPARISON_ANALYSIS.md) - Industry research
- [Implementation Guide](docs/04_IMPLEMENTATION_GUIDE.md) - Technical details
- [Querying Guide](docs/05_QUERYING_GUIDE.md) - Using all 50+ filters

## 🚧 Future Enhancements

- Real-time availability integration
- Video transcription and topic extraction
- AI-powered speaker recommendations
- Multi-language interface support
- Speaking engagement outcome tracking
- Dynamic pricing models

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

Built with MongoDB, Python, and comprehensive normalization systems based on extensive market research of leading speaker platforms.