#!/usr/bin/env python3
"""
Industry normalization for speaker data
Maps various industry terms to standardized categories
"""

import re
from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict

class IndustryNormalizer:
    """Normalize and categorize industry fields into unified taxonomy"""
    
    def __init__(self):
        # Define comprehensive industry taxonomy with synonyms
        self.taxonomy = {
            'healthcare': {
                'keywords': ['healthcare', 'medical', 'medicine', 'health care', 'hospital',
                            'clinical', 'patient care', 'health system', 'nursing', 'pharma',
                            'pharmaceutical', 'biotech', 'biotechnology', 'life sciences',
                            'health services', 'wellness', 'mental health', 'public health',
                            'telemedicine', 'digital health', 'medtech', 'medical device'],
                'display_name': 'Healthcare & Life Sciences',
                'subcategories': ['hospitals', 'pharmaceuticals', 'biotechnology', 'medical_devices', 'digital_health']
            },
            'technology': {
                'keywords': ['technology', 'tech', 'it', 'information technology', 'software',
                            'hardware', 'computer', 'digital', 'internet', 'web', 'mobile',
                            'app', 'saas', 'cloud', 'data', 'ai', 'artificial intelligence',
                            'machine learning', 'cybersecurity', 'fintech', 'edtech', 'martech'],
                'display_name': 'Technology & Software',
                'subcategories': ['software', 'hardware', 'saas', 'fintech', 'cybersecurity']
            },
            'finance': {
                'keywords': ['finance', 'financial', 'banking', 'bank', 'investment', 'insurance',
                            'finserv', 'financial services', 'wealth management', 'asset management',
                            'private equity', 'venture capital', 'hedge fund', 'trading', 'capital markets',
                            'payments', 'lending', 'credit', 'mortgage', 'real estate finance'],
                'display_name': 'Financial Services',
                'subcategories': ['banking', 'investment', 'insurance', 'fintech', 'real_estate']
            },
            'manufacturing': {
                'keywords': ['manufacturing', 'industrial', 'factory', 'production', 'assembly',
                            'automotive', 'aerospace', 'defense', 'chemicals', 'materials',
                            'supply chain', 'logistics', 'distribution', 'warehouse', 'operations',
                            'lean', 'six sigma', 'quality', 'engineering', 'machinery'],
                'display_name': 'Manufacturing & Industrial',
                'subcategories': ['automotive', 'aerospace', 'chemicals', 'machinery', 'logistics']
            },
            'retail': {
                'keywords': ['retail', 'ecommerce', 'e-commerce', 'online retail', 'store',
                            'shopping', 'consumer goods', 'cpg', 'fmcg', 'fashion', 'apparel',
                            'grocery', 'restaurant', 'hospitality', 'food service', 'qsr',
                            'customer experience', 'omnichannel', 'marketplace'],
                'display_name': 'Retail & E-commerce',
                'subcategories': ['ecommerce', 'brick_mortar', 'fashion', 'grocery', 'hospitality']
            },
            'education': {
                'keywords': ['education', 'academic', 'university', 'college', 'school', 'k-12',
                            'k12', 'higher education', 'edtech', 'e-learning', 'online education',
                            'training', 'professional development', 'curriculum', 'teaching',
                            'student', 'research', 'library', 'educational technology'],
                'display_name': 'Education & Academia',
                'subcategories': ['k12', 'higher_ed', 'edtech', 'training', 'research']
            },
            'government': {
                'keywords': ['government', 'federal', 'state', 'local', 'municipal', 'public sector',
                            'public service', 'military', 'defense', 'intelligence', 'policy',
                            'regulation', 'compliance', 'politics', 'political', 'diplomatic',
                            'international relations', 'ngo', 'nonprofit', 'non-profit'],
                'display_name': 'Government & Public Sector',
                'subcategories': ['federal', 'state_local', 'military', 'nonprofit', 'international']
            },
            'media': {
                'keywords': ['media', 'entertainment', 'broadcast', 'television', 'tv', 'film',
                            'movie', 'music', 'publishing', 'news', 'journalism', 'advertising',
                            'marketing', 'pr', 'public relations', 'digital media', 'social media',
                            'content', 'streaming', 'gaming', 'sports', 'creative'],
                'display_name': 'Media & Entertainment',
                'subcategories': ['broadcast', 'publishing', 'digital_media', 'advertising', 'gaming']
            },
            'energy': {
                'keywords': ['energy', 'oil', 'gas', 'petroleum', 'renewable', 'solar', 'wind',
                            'utilities', 'power', 'electricity', 'nuclear', 'coal', 'natural gas',
                            'sustainability', 'clean energy', 'green energy', 'environmental',
                            'climate', 'carbon', 'emissions', 'mining', 'resources'],
                'display_name': 'Energy & Utilities',
                'subcategories': ['oil_gas', 'renewable', 'utilities', 'mining', 'environmental']
            },
            'professional_services': {
                'keywords': ['consulting', 'professional services', 'legal', 'law', 'accounting',
                            'audit', 'tax', 'advisory', 'management consulting', 'strategy consulting',
                            'hr', 'human resources', 'recruiting', 'staffing', 'real estate',
                            'architecture', 'engineering services', 'design'],
                'display_name': 'Professional Services',
                'subcategories': ['consulting', 'legal', 'accounting', 'hr_services', 'real_estate']
            },
            'telecommunications': {
                'keywords': ['telecom', 'telecommunications', 'wireless', 'mobile', '5g', 'broadband',
                            'cable', 'satellite', 'network', 'carrier', 'isp', 'internet service',
                            'communication', 'connectivity', 'infrastructure'],
                'display_name': 'Telecommunications',
                'subcategories': ['wireless', 'broadband', 'infrastructure', 'satellite']
            },
            'transportation': {
                'keywords': ['transportation', 'transport', 'logistics', 'shipping', 'freight',
                            'airline', 'aviation', 'rail', 'railroad', 'trucking', 'maritime',
                            'delivery', 'courier', 'postal', 'mobility', 'autonomous', 'vehicle'],
                'display_name': 'Transportation & Logistics',
                'subcategories': ['aviation', 'ground_transport', 'maritime', 'logistics', 'delivery']
            },
            'agriculture': {
                'keywords': ['agriculture', 'farming', 'agtech', 'agribusiness', 'food production',
                            'crop', 'livestock', 'dairy', 'ranch', 'agricultural technology',
                            'precision farming', 'sustainable agriculture', 'organic', 'food processing'],
                'display_name': 'Agriculture & Food',
                'subcategories': ['farming', 'agtech', 'food_processing', 'sustainability']
            },
            'construction': {
                'keywords': ['construction', 'building', 'contractor', 'architecture', 'engineering',
                            'real estate development', 'infrastructure', 'civil engineering',
                            'commercial construction', 'residential construction', 'heavy construction'],
                'display_name': 'Construction & Real Estate',
                'subcategories': ['commercial', 'residential', 'infrastructure', 'architecture']
            },
            'pharmaceutical': {
                'keywords': ['pharmaceutical', 'pharma', 'drug', 'medication', 'clinical trial',
                            'fda', 'regulatory', 'drug development', 'biopharmaceutical',
                            'generic', 'specialty pharma', 'vaccine', 'therapeutic'],
                'display_name': 'Pharmaceuticals',
                'subcategories': ['research', 'manufacturing', 'distribution', 'clinical_trials']
            }
        }
        
        # Create reverse mapping for quick lookup
        self.keyword_to_industry = {}
        for industry, info in self.taxonomy.items():
            for keyword in info['keywords']:
                self.keyword_to_industry[keyword.lower()] = industry
    
    def normalize_industries(self, industry_list: List[str]) -> Dict[str, Any]:
        """
        Normalize a list of industry terms into structured categories
        
        Returns:
            {
                'primary_industries': [...],      # Main industry categories
                'secondary_industries': [...],    # Additional matches
                'subcategories': [...],          # Specific subcategories
                'keywords': [...],               # All normalized keywords
                'original_terms': [...],         # Original input terms
                'unmatched': [...]              # Terms that couldn't be categorized
            }
        """
        if not industry_list:
            return {
                'primary_industries': [],
                'secondary_industries': [],
                'subcategories': [],
                'keywords': [],
                'original_terms': [],
                'unmatched': []
            }
        
        primary_industries = set()
        secondary_industries = set()
        subcategories = set()
        keywords = set()
        unmatched = []
        
        for term in industry_list:
            if not term or term.lower() in ['none', 'n/a', '']:
                continue
                
            term_lower = term.lower().strip()
            matched = False
            
            # Direct keyword match
            if term_lower in self.keyword_to_industry:
                industry = self.keyword_to_industry[term_lower]
                primary_industries.add(industry)
                keywords.add(term_lower)
                matched = True
            else:
                # Fuzzy matching - check if term contains or is contained in keywords
                for keyword, industry in self.keyword_to_industry.items():
                    if len(keyword) > 3:  # Avoid short word false matches
                        if keyword in term_lower or term_lower in keyword:
                            if industry not in primary_industries:
                                secondary_industries.add(industry)
                            keywords.add(term_lower)
                            matched = True
                            break
                
                # Multi-word phrase matching
                if not matched:
                    words = term_lower.split()
                    for word in words:
                        if word in self.keyword_to_industry:
                            industry = self.keyword_to_industry[word]
                            secondary_industries.add(industry)
                            keywords.add(term_lower)
                            matched = True
                            break
            
            if not matched:
                unmatched.append(term)
                keywords.add(term_lower)  # Still keep as keyword for search
        
        # Identify subcategories based on matched industries
        all_industries = primary_industries.union(secondary_industries)
        for industry in all_industries:
            # Simple subcategory detection based on keywords
            if 'fintech' in ' '.join(keywords) and industry == 'technology':
                subcategories.add('fintech')
            elif 'edtech' in ' '.join(keywords) and industry == 'technology':
                subcategories.add('edtech')
            # Add more subcategory logic as needed
        
        return {
            'primary_industries': list(primary_industries),
            'secondary_industries': list(secondary_industries),
            'subcategories': list(subcategories),
            'keywords': list(keywords),
            'original_terms': industry_list,
            'unmatched': unmatched
        }
    
    def get_industry_info(self, industry_id: str) -> Dict[str, str]:
        """Get display information for an industry"""
        if industry_id in self.taxonomy:
            return {
                'id': industry_id,
                'display_name': self.taxonomy[industry_id]['display_name'],
                'subcategories': self.taxonomy[industry_id]['subcategories']
            }
        return None
    
    def get_all_industries(self) -> Dict[str, Dict]:
        """Get all industries with their info"""
        industries = {}
        for industry_id, info in self.taxonomy.items():
            industries[industry_id] = {
                'display_name': info['display_name'],
                'keyword_count': len(info['keywords']),
                'subcategories': info['subcategories']
            }
        return industries
    
    def merge_with_categories(self, categories: List[str]) -> Dict[str, Any]:
        """
        Merge general categories with industry normalization
        Used for sources that mix topics and industries
        """
        industry_terms = []
        non_industry_terms = []
        
        # Separate industry-related terms from general categories
        for category in categories:
            if not category:
                continue
            
            category_lower = category.lower()
            is_industry = False
            
            # Check if it matches any industry keyword
            for keyword in self.keyword_to_industry:
                if keyword in category_lower or category_lower in keyword:
                    industry_terms.append(category)
                    is_industry = True
                    break
            
            if not is_industry:
                non_industry_terms.append(category)
        
        # Normalize the industry terms
        normalized = self.normalize_industries(industry_terms)
        normalized['non_industry_categories'] = non_industry_terms
        
        return normalized