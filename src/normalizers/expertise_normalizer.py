#!/usr/bin/env python3
"""
Enhanced expertise normalization with hierarchical taxonomy
"""

import re
from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict

class ExpertiseNormalizer:
    """Normalize and categorize expertise fields into unified taxonomy"""
    
    def __init__(self):
        # Define comprehensive taxonomy with synonyms and related terms
        self.taxonomy = {
            # Technology & Computer Science
            'artificial_intelligence': {
                'keywords': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 
                            'neural network', 'ml', 'reinforcement learning', 'nlp',
                            'natural language processing', 'computer vision', 'chatbot', 'llm',
                            'generative ai', 'predictive modeling', 'pattern recognition'],
                'parent': 'technology',
                'display_name': 'Artificial Intelligence & Machine Learning'
            },
            'data_science': {
                'keywords': ['data science', 'data analytics', 'big data', 'data mining', 
                            'data analysis', 'business intelligence', 'predictive analytics', 
                            'statistics', 'data visualization', 'data engineering', 'etl',
                            'data warehouse', 'tableau', 'power bi', 'sql'],
                'parent': 'technology',
                'display_name': 'Data Science & Analytics'
            },
            'software_development': {
                'keywords': ['software', 'programming', 'coding', 'software development', 
                            'web development', 'mobile development', 'app development', 
                            'full stack', 'backend', 'frontend', 'agile', 'scrum', 'devops',
                            'javascript', 'python', 'java', 'react', 'node.js'],
                'parent': 'technology',
                'display_name': 'Software Development'
            },
            'cybersecurity': {
                'keywords': ['cybersecurity', 'security', 'information security', 'network security', 
                            'data security', 'privacy', 'encryption', 'ethical hacking', 'penetration testing',
                            'compliance', 'risk management', 'incident response', 'soc', 'ciso'],
                'parent': 'technology',
                'display_name': 'Cybersecurity & Information Security'
            },
            'cloud_infrastructure': {
                'keywords': ['cloud', 'cloud computing', 'aws', 'azure', 'google cloud', 'gcp',
                            'infrastructure', 'saas', 'paas', 'iaas', 'kubernetes', 'docker',
                            'microservices', 'serverless', 'cloud migration', 'hybrid cloud'],
                'parent': 'technology',
                'display_name': 'Cloud Computing & Infrastructure'
            },
            'emerging_tech': {
                'keywords': ['blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'defi', 'web3', 
                            'nft', 'metaverse', 'iot', 'internet of things', 'embedded systems', 
                            'quantum computing', 'augmented reality', 'virtual reality', 'ar', 'vr'],
                'parent': 'technology',
                'display_name': 'Emerging Technologies'
            },
            
            # Business & Management
            'leadership': {
                'keywords': ['leadership', 'management', 'executive', 'ceo', 'team building', 
                            'organizational', 'team leadership', 'servant leadership', 'executive leadership',
                            'leading', 'manager', 'director', 'vp', 'c-suite', 'board'],
                'parent': 'business',
                'display_name': 'Leadership & Management'
            },
            'entrepreneurship': {
                'keywords': ['entrepreneur', 'startup', 'founder', 'business development', 'venture',
                            'innovation', 'business growth', 'small business', 'solopreneur',
                            'business owner', 'scale', 'pivot', 'lean startup', 'mvp'],
                'parent': 'business',
                'display_name': 'Entrepreneurship & Innovation'
            },
            'marketing': {
                'keywords': ['marketing', 'digital marketing', 'social media', 'branding', 'advertising',
                            'content marketing', 'seo', 'growth hacking', 'brand strategy', 'pr',
                            'public relations', 'influencer', 'email marketing', 'ppc', 'sem'],
                'parent': 'business',
                'display_name': 'Marketing & Branding'
            },
            'sales': {
                'keywords': ['sales', 'selling', 'revenue', 'customer acquisition', 'b2b', 'b2c',
                            'sales strategy', 'negotiation', 'closing', 'pipeline', 'crm',
                            'account management', 'business development', 'lead generation'],
                'parent': 'business',
                'display_name': 'Sales & Business Development'
            },
            'finance': {
                'keywords': ['finance', 'investment', 'banking', 'fintech', 'accounting', 'economics',
                            'financial planning', 'wealth management', 'private equity', 'venture capital',
                            'cfo', 'treasury', 'financial analysis', 'budgeting', 'forex', 'trading'],
                'parent': 'business',
                'display_name': 'Finance & Investment'
            },
            'strategy': {
                'keywords': ['strategy', 'business strategy', 'strategic planning', 'consulting', 
                            'transformation', 'change management', 'operations', 'process improvement',
                            'efficiency', 'optimization', 'restructuring', 'turnaround'],
                'parent': 'business',
                'display_name': 'Strategy & Consulting'
            },
            'human_resources': {
                'keywords': ['hr', 'human resources', 'talent', 'recruitment', 'hiring', 'people',
                            'culture', 'employee engagement', 'retention', 'compensation', 'benefits',
                            'diversity', 'inclusion', 'dei', 'workplace', 'organizational development'],
                'parent': 'business',
                'display_name': 'Human Resources & Culture'
            },
            
            # Healthcare & Life Sciences
            'healthcare': {
                'keywords': ['healthcare', 'medical', 'medicine', 'clinical', 'patient care', 
                            'telemedicine', 'hospital', 'physician', 'doctor', 'nurse', 'nursing',
                            'health system', 'healthcare delivery', 'patient experience'],
                'parent': 'health_sciences',
                'display_name': 'Healthcare & Medicine'
            },
            'biotechnology': {
                'keywords': ['biotech', 'biotechnology', 'genomics', 'bioinformatics', 'molecular biology',
                            'genetics', 'crispr', 'drug discovery', 'pharmaceutical', 'pharma',
                            'clinical trials', 'fda', 'therapeutics', 'diagnostics'],
                'parent': 'health_sciences',
                'display_name': 'Biotechnology & Pharmaceuticals'
            },
            'public_health': {
                'keywords': ['public health', 'epidemiology', 'health policy', 'global health', 
                            'pandemic', 'disease prevention', 'community health', 'health equity',
                            'vaccination', 'health education', 'population health'],
                'parent': 'health_sciences',
                'display_name': 'Public Health & Policy'
            },
            'wellness': {
                'keywords': ['wellness', 'mental health', 'psychology', 'psychiatry', 'mindfulness', 
                            'therapy', 'counseling', 'stress', 'anxiety', 'depression', 'wellbeing',
                            'meditation', 'yoga', 'fitness', 'nutrition', 'holistic health'],
                'parent': 'health_sciences',
                'display_name': 'Mental Health & Wellness'
            },
            
            # Science & Engineering
            'engineering': {
                'keywords': ['engineering', 'mechanical', 'electrical', 'civil', 'chemical', 'aerospace',
                            'biomedical', 'environmental', 'industrial', 'systems engineering',
                            'robotics', 'automation', 'manufacturing', '3d printing', 'cad'],
                'parent': 'stem',
                'display_name': 'Engineering'
            },
            'physical_sciences': {
                'keywords': ['physics', 'chemistry', 'materials science', 'nanotechnology', 'polymer',
                            'quantum', 'astrophysics', 'particle physics', 'theoretical physics',
                            'astronomy', 'geology', 'earth science', 'climate science'],
                'parent': 'stem',
                'display_name': 'Physical Sciences'
            },
            'life_sciences': {
                'keywords': ['biology', 'molecular biology', 'cell biology', 'ecology', 'evolution',
                            'microbiology', 'immunology', 'neuroscience', 'biochemistry',
                            'marine biology', 'botany', 'zoology', 'conservation'],
                'parent': 'stem',
                'display_name': 'Life Sciences'
            },
            'mathematics': {
                'keywords': ['mathematics', 'math', 'statistics', 'algorithms', 'computational',
                            'applied math', 'pure math', 'probability', 'calculus', 'algebra',
                            'geometry', 'topology', 'number theory', 'combinatorics'],
                'parent': 'stem',
                'display_name': 'Mathematics & Statistics'
            },
            
            # Law & Policy
            'law': {
                'keywords': ['law', 'legal', 'attorney', 'litigation', 'corporate law', 
                            'intellectual property', 'patent', 'trademark', 'copyright',
                            'compliance', 'regulation', 'contract', 'employment law',
                            'securities', 'tax law', 'criminal law', 'constitutional law'],
                'parent': 'legal_policy',
                'display_name': 'Law & Legal'
            },
            'policy': {
                'keywords': ['policy', 'public policy', 'government', 'politics', 'diplomacy', 
                            'international relations', 'foreign policy', 'legislative', 'regulatory',
                            'advocacy', 'lobbying', 'think tank', 'ngo', 'nonprofit'],
                'parent': 'legal_policy',
                'display_name': 'Policy & Government'
            },
            
            # Creative & Media
            'media': {
                'keywords': ['media', 'journalism', 'broadcasting', 'film', 'television', 'production',
                            'documentary', 'news', 'reporter', 'anchor', 'producer', 'director',
                            'cinematography', 'editing', 'multimedia', 'podcast'],
                'parent': 'creative',
                'display_name': 'Media & Entertainment'
            },
            'design': {
                'keywords': ['design', 'ux', 'ui', 'graphic design', 'product design', 'architecture',
                            'interior design', 'fashion', 'industrial design', 'web design',
                            'user experience', 'user interface', 'visual design', 'branding design'],
                'parent': 'creative',
                'display_name': 'Design & Creative'
            },
            'arts': {
                'keywords': ['art', 'music', 'theater', 'performance', 'creative', 'entertainment',
                            'artist', 'musician', 'actor', 'dancer', 'singer', 'composer',
                            'painting', 'sculpture', 'photography', 'gallery', 'museum'],
                'parent': 'creative',
                'display_name': 'Arts & Performance'
            },
            'writing': {
                'keywords': ['writing', 'author', 'content creation', 'copywriting', 'publishing',
                            'novelist', 'poet', 'screenwriter', 'blogger', 'editor', 'literary',
                            'book', 'manuscript', 'storytelling', 'narrative'],
                'parent': 'creative',
                'display_name': 'Writing & Publishing'
            },
            
            # Education & Research
            'education': {
                'keywords': ['education', 'teaching', 'learning', 'training', 'curriculum', 'e-learning',
                            'instructional design', 'academic', 'professor', 'teacher', 'educator',
                            'pedagogy', 'k-12', 'higher education', 'university', 'school'],
                'parent': 'education_research',
                'display_name': 'Education & Teaching'
            },
            'research': {
                'keywords': ['research', 'researcher', 'scientist', 'scholar', 'phd', 'postdoc',
                            'grant', 'publication', 'peer review', 'methodology', 'study',
                            'experiment', 'analysis', 'findings', 'hypothesis'],
                'parent': 'education_research',
                'display_name': 'Research & Academia'
            },
            
            # Social Impact
            'social_impact': {
                'keywords': ['social impact', 'nonprofit', 'charity', 'philanthropy', 'social enterprise',
                            'community', 'volunteer', 'humanitarian', 'development', 'sustainability',
                            'environment', 'climate', 'green', 'eco', 'conservation', 'renewable'],
                'parent': 'social',
                'display_name': 'Social Impact & Sustainability'
            },
            'diversity_inclusion': {
                'keywords': ['diversity', 'inclusion', 'dei', 'equity', 'equality', 'bias',
                            'gender', 'race', 'lgbtq', 'accessibility', 'belonging',
                            'multicultural', 'intersectionality', 'allyship'],
                'parent': 'social',
                'display_name': 'Diversity & Inclusion'
            },
            
            # Personal Development
            'personal_development': {
                'keywords': ['motivation', 'inspiration', 'resilience', 'mindset', 'growth',
                            'self improvement', 'personal growth', 'life coach', 'success',
                            'goal setting', 'productivity', 'time management', 'habits'],
                'parent': 'personal',
                'display_name': 'Personal Development'
            },
            'communication': {
                'keywords': ['communication', 'public speaking', 'presentation', 'storytelling',
                            'speech', 'rhetoric', 'persuasion', 'influence', 'negotiation',
                            'interpersonal', 'listening', 'conflict resolution'],
                'parent': 'personal',
                'display_name': 'Communication & Speaking'
            }
        }
        
        # Create reverse mapping for quick lookup
        self.keyword_to_category = {}
        for category, info in self.taxonomy.items():
            for keyword in info['keywords']:
                self.keyword_to_category[keyword.lower()] = category
        
        # Define parent categories
        self.parent_categories = {
            'technology': 'Technology & Innovation',
            'business': 'Business & Management',
            'health_sciences': 'Healthcare & Life Sciences',
            'stem': 'Science & Engineering',
            'legal_policy': 'Law & Policy',
            'creative': 'Creative & Media',
            'education_research': 'Education & Research',
            'social': 'Social Impact',
            'personal': 'Personal Development'
        }
    
    def normalize_expertise(self, expertise_list: List[str]) -> Dict[str, Any]:
        """
        Normalize a list of expertise terms into structured categories
        
        Returns:
            {
                'primary_categories': [...],  # Main category IDs
                'secondary_categories': [...],  # Additional matches
                'parent_categories': [...],  # Parent category IDs
                'keywords': [...],  # All normalized keywords
                'original_terms': [...],  # Original input terms
                'unmatched': [...]  # Terms that couldn't be categorized
            }
        """
        if not expertise_list:
            return {
                'primary_categories': [],
                'secondary_categories': [],
                'parent_categories': [],
                'keywords': [],
                'original_terms': [],
                'unmatched': []
            }
        
        primary_categories = set()
        secondary_categories = set()
        parent_categories = set()
        keywords = set()
        unmatched = []
        
        for term in expertise_list:
            if not term or term.lower() in ['none', 'n/a', '']:
                continue
                
            term_lower = term.lower().strip()
            matched = False
            
            # Direct keyword match
            if term_lower in self.keyword_to_category:
                category = self.keyword_to_category[term_lower]
                primary_categories.add(category)
                parent_categories.add(self.taxonomy[category]['parent'])
                keywords.add(term_lower)
                matched = True
            else:
                # Fuzzy matching - check if term contains or is contained in keywords
                for keyword, category in self.keyword_to_category.items():
                    if len(keyword) > 3:  # Avoid short word false matches
                        if keyword in term_lower or term_lower in keyword:
                            if category not in primary_categories:
                                secondary_categories.add(category)
                            parent_categories.add(self.taxonomy[category]['parent'])
                            keywords.add(term_lower)
                            matched = True
                            break
                
                # Multi-word phrase matching
                if not matched:
                    words = term_lower.split()
                    for word in words:
                        if word in self.keyword_to_category:
                            category = self.keyword_to_category[word]
                            secondary_categories.add(category)
                            parent_categories.add(self.taxonomy[category]['parent'])
                            keywords.add(term_lower)
                            matched = True
                            break
            
            if not matched:
                unmatched.append(term)
                keywords.add(term_lower)  # Still keep as keyword for search
        
        return {
            'primary_categories': list(primary_categories),
            'secondary_categories': list(secondary_categories),
            'parent_categories': list(parent_categories),
            'keywords': list(keywords),
            'original_terms': expertise_list,
            'unmatched': unmatched
        }
    
    def get_category_info(self, category_id: str) -> Dict[str, str]:
        """Get display information for a category"""
        if category_id in self.taxonomy:
            return {
                'id': category_id,
                'display_name': self.taxonomy[category_id]['display_name'],
                'parent': self.taxonomy[category_id]['parent'],
                'parent_display_name': self.parent_categories.get(self.taxonomy[category_id]['parent'])
            }
        return None
    
    def get_all_categories_hierarchy(self) -> Dict[str, List[Dict]]:
        """Get all categories organized by parent"""
        hierarchy = defaultdict(list)
        
        for category_id, info in self.taxonomy.items():
            parent = info['parent']
            hierarchy[parent].append({
                'id': category_id,
                'display_name': info['display_name'],
                'keyword_count': len(info['keywords'])
            })
        
        return dict(hierarchy)