# Expert Finder - Unified Speaker Database

A comprehensive solution for consolidating and normalizing speaker data from multiple sources into a unified, searchable database with advanced expertise categorization.

## 🚀 Overview

This project consolidates speaker profiles from 10 different databases with varying schemas into a single, normalized MongoDB database. It processes over 154,000 raw records into ~151,000 unique speaker profiles with:

- **Unified Schema**: Consistent structure across all sources
- **Expertise Normalization**: 41 standardized categories from 34,000+ unique terms
- **Duplicate Detection**: Fuzzy name matching with 85% threshold
- **Quality Scoring**: Profile completeness ratings (0-100%)
- **Advanced Search**: Full-text search with faceted filtering

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

## 🛠️ Key Features

### 1. Expertise Taxonomy
- 41 normalized expertise categories
- 9 parent category groups
- Hierarchical classification system
- Automatic keyword mapping

### 2. Data Normalization
- Name standardization
- Location normalization
- Fee range parsing
- Credential extraction
- Media consolidation

### 3. Quality Indicators
- Profile completeness scoring
- Data quality tiers (cat_1-cat_4)
- Source tracking
- Verification status

### 4. Search Capabilities
- Full-text search
- Filter by expertise category
- Filter by location
- Filter by quality tier
- Filter by profile features (video, email, education)

## 📁 Project Structure

```
expert_finder/
├── consolidate_speakers_v2_full.py  # Main consolidation script
├── expertise_normalizer.py          # Expertise taxonomy engine
├── query_speakers_v2.py            # Advanced query interface
├── explore_databases.py            # Initial database exploration
├── samples/                        # Sample data from each source
├── DATA_TRANSFORMATION_GUIDE.md    # User-friendly guide
├── DATA_CONSOLIDATION_GUIDE_V2.md  # Technical documentation
├── SPEAKER_DATA_NORMALIZATION_ANALYSIS.md  # Normalization opportunities
└── SPEAKER_DATA_NORMALIZATION_GUIDE.md     # Implementation guide
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

### Running the Consolidation

1. **Explore the databases** (optional):
   ```bash
   python3 explore_databases.py
   ```

2. **Run the consolidation**:
   ```bash
   python3 consolidate_speakers_v2_full.py
   ```

3. **Query the unified database**:
   ```bash
   # Search by text
   python3 query_speakers_v2.py --search "artificial intelligence"
   
   # Filter by expertise
   python3 query_speakers_v2.py --expertise artificial_intelligence
   
   # Filter by quality tier
   python3 query_speakers_v2.py --quality cat_1 --has-video
   
   # View statistics
   python3 query_speakers_v2.py --stats
   
   # Browse categories
   python3 query_speakers_v2.py --browse
   ```

## 📈 Statistics

Current database contains:
- **Total Speakers**: 151,088
- **With Categorized Expertise**: 45,772 (30.3%)
- **With Email**: 67,654 (44.8%)
- **With Video**: 2,451 (1.6%)
- **With Education**: 47,685 (31.6%)
- **Average Profile Score**: 51.4/100

### Top Expertise Categories
1. Leadership & Management: 14,435
2. Personal Development: 8,702
3. Communication & Speaking: 7,241
4. Social Impact & Sustainability: 5,814
5. Marketing & Branding: 4,731

## 🔄 Data Flow

```
Raw Databases → Extraction → Normalization → Deduplication → Unified Database
     ↓              ↓              ↓                ↓              ↓
10 sources    Profile data   Expertise      Name matching   MongoDB with
              extraction     categorization  & merging      indexes
```

## 🎯 Use Cases

1. **Event Planners**: Find speakers by expertise, location, and budget
2. **Speaker Bureaus**: Manage unified speaker inventory
3. **Conference Organizers**: Match speakers to event themes
4. **Research**: Analyze speaker market trends
5. **AI/ML Applications**: Build recommendation systems

## 📚 Documentation

- [Data Transformation Guide](DATA_TRANSFORMATION_GUIDE.md) - User-friendly overview
- [Technical Consolidation Guide](DATA_CONSOLIDATION_GUIDE_V2.md) - Implementation details
- [Normalization Analysis](SPEAKER_DATA_NORMALIZATION_ANALYSIS.md) - Deep dive into data variations
- [Normalization Guide](SPEAKER_DATA_NORMALIZATION_GUIDE.md) - Step-by-step implementation

## 🚧 Roadmap

See [ROADMAP.md](ROADMAP.md) for planned improvements including:
- Industry vertical normalization
- Event type standardization
- Enhanced duplicate detection
- API development
- Real-time updates

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

Built with MongoDB, Python, and expertise normalization powered by comprehensive taxonomy mapping.