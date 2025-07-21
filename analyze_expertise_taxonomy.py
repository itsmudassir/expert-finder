#!/usr/bin/env python3
"""
Analyze expertise fields across all databases to create unified taxonomy
"""

import pymongo
from pymongo import MongoClient
from collections import defaultdict, Counter
import json
import re

MONGO_URI = "mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin"

def analyze_expertise_fields():
    """Analyze all expertise-related fields across databases"""
    client = MongoClient(MONGO_URI)
    
    # Collect all expertise terms
    all_expertise = defaultdict(list)
    expertise_counts = Counter()
    
    print("Analyzing llm_parsed_db expertise fields...")
    
    # Analyze llm_parsed_db collections
    for cat in ['cat_1', 'cat_2', 'cat_3', 'cat_4']:
        db = client['llm_parsed_db']
        collection = db[cat]
        
        print(f"\nProcessing {cat}...")
        
        for doc in collection.find().limit(5000):  # Sample for analysis
            # Get field_of_expertise
            if doc.get('field_of_expertise'):
                for field in doc['field_of_expertise']:
                    if field and field != 'None':
                        all_expertise['llm_parsed'].append(field.lower().strip())
                        expertise_counts[field.lower().strip()] += 1
    
    # Analyze existing consolidated data
    print("\nAnalyzing existing consolidated speaker topics...")
    db = client['expert_finder_unified']
    collection = db['speakers']
    
    for doc in collection.find().limit(10000):
        # Get all topics
        topics = doc.get('expertise', {}).get('all_topics', [])
        for topic in topics:
            if topic:
                all_expertise['consolidated'].append(topic.lower().strip())
                expertise_counts[topic.lower().strip()] += 1
    
    # Find common patterns and create taxonomy
    print("\nAnalyzing patterns...")
    
    # Group similar terms
    expertise_groups = defaultdict(set)
    
    # Technology/Computer Science groups
    tech_patterns = {
        'artificial_intelligence': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 
                                   'neural network', 'ml', 'reinforcement learning', 'natural language processing',
                                   'nlp', 'computer vision', 'robotics', 'automation'],
        'data_science': ['data science', 'data analytics', 'big data', 'data mining', 'data analysis',
                        'business intelligence', 'predictive analytics', 'statistics', 'data visualization'],
        'software_engineering': ['software', 'programming', 'coding', 'software development', 'web development',
                                'mobile development', 'app development', 'full stack', 'backend', 'frontend'],
        'cybersecurity': ['cybersecurity', 'security', 'information security', 'network security', 
                         'data security', 'privacy', 'encryption', 'ethical hacking'],
        'cloud_computing': ['cloud', 'cloud computing', 'aws', 'azure', 'google cloud', 'devops', 
                           'infrastructure', 'saas', 'paas', 'iaas'],
        'blockchain': ['blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'defi', 'web3', 'nft'],
        'iot': ['iot', 'internet of things', 'embedded systems', 'sensors', 'smart devices']
    }
    
    # Business groups
    business_patterns = {
        'entrepreneurship': ['entrepreneur', 'startup', 'founder', 'business development', 'venture',
                           'innovation', 'business growth'],
        'leadership': ['leadership', 'management', 'executive', 'ceo', 'team building', 'organizational'],
        'marketing': ['marketing', 'digital marketing', 'social media', 'branding', 'advertising',
                     'content marketing', 'seo', 'growth hacking'],
        'sales': ['sales', 'business development', 'revenue', 'customer acquisition', 'b2b', 'b2c'],
        'finance': ['finance', 'investment', 'banking', 'fintech', 'accounting', 'economics',
                   'financial planning', 'wealth management'],
        'strategy': ['strategy', 'business strategy', 'strategic planning', 'consulting', 'transformation']
    }
    
    # Healthcare/Life Sciences
    healthcare_patterns = {
        'medicine': ['medicine', 'medical', 'healthcare', 'clinical', 'patient care', 'telemedicine'],
        'biotechnology': ['biotech', 'biotechnology', 'genomics', 'bioinformatics', 'molecular biology',
                         'genetics', 'crispr', 'drug discovery'],
        'public_health': ['public health', 'epidemiology', 'health policy', 'global health', 'pandemic'],
        'mental_health': ['mental health', 'psychology', 'psychiatry', 'wellness', 'mindfulness', 'therapy']
    }
    
    # Academic/Research fields
    academic_patterns = {
        'engineering': ['engineering', 'mechanical', 'electrical', 'civil', 'chemical', 'aerospace'],
        'physics': ['physics', 'quantum', 'astrophysics', 'particle physics', 'theoretical physics'],
        'chemistry': ['chemistry', 'materials science', 'nanotechnology', 'polymer'],
        'mathematics': ['mathematics', 'math', 'statistics', 'algorithms', 'computational'],
        'biology': ['biology', 'molecular biology', 'cell biology', 'ecology', 'evolution'],
        'social_sciences': ['sociology', 'anthropology', 'political science', 'economics', 'psychology']
    }
    
    # Legal/Policy
    legal_patterns = {
        'law': ['law', 'legal', 'attorney', 'litigation', 'corporate law', 'intellectual property',
               'patent', 'compliance', 'regulation'],
        'policy': ['policy', 'public policy', 'government', 'politics', 'diplomacy', 'international relations']
    }
    
    # Creative/Media
    creative_patterns = {
        'media': ['media', 'journalism', 'broadcasting', 'film', 'television', 'production'],
        'design': ['design', 'ux', 'ui', 'graphic design', 'product design', 'architecture'],
        'arts': ['art', 'music', 'theater', 'performance', 'creative', 'entertainment'],
        'writing': ['writing', 'author', 'content creation', 'copywriting', 'publishing']
    }
    
    # Education
    education_patterns = {
        'education': ['education', 'teaching', 'learning', 'training', 'curriculum', 'e-learning',
                     'instructional design', 'academic', 'research']
    }
    
    # Count matches for each pattern
    pattern_matches = defaultdict(int)
    unmatched = []
    
    for expertise, count in expertise_counts.most_common():
        matched = False
        
        # Check all pattern groups
        all_patterns = {
            **tech_patterns, **business_patterns, **healthcare_patterns,
            **academic_patterns, **legal_patterns, **creative_patterns, **education_patterns
        }
        
        for category, patterns in all_patterns.items():
            for pattern in patterns:
                if pattern in expertise or expertise in pattern:
                    pattern_matches[category] += count
                    expertise_groups[category].add(expertise)
                    matched = True
                    break
            if matched:
                break
        
        if not matched and count > 5:  # Only track common unmatched terms
            unmatched.append((expertise, count))
    
    # Save results
    results = {
        'total_unique_terms': len(expertise_counts),
        'top_expertise_terms': expertise_counts.most_common(100),
        'category_matches': dict(pattern_matches),
        'unmatched_common_terms': unmatched[:50],
        'taxonomy': {
            'technology': list(tech_patterns.keys()),
            'business': list(business_patterns.keys()),
            'healthcare': list(healthcare_patterns.keys()),
            'academic': list(academic_patterns.keys()),
            'legal_policy': list(legal_patterns.keys()),
            'creative_media': list(creative_patterns.keys()),
            'education': ['education']
        }
    }
    
    # Save detailed taxonomy
    taxonomy_detail = {}
    for category, terms in expertise_groups.items():
        taxonomy_detail[category] = list(terms)[:20]  # Top 20 terms per category
    
    with open('expertise_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    with open('expertise_taxonomy_mapping.json', 'w') as f:
        json.dump(taxonomy_detail, f, indent=2)
    
    print(f"\nTotal unique expertise terms: {len(expertise_counts)}")
    print(f"Top 10 expertise areas:")
    for term, count in expertise_counts.most_common(10):
        print(f"  {term}: {count}")
    
    print(f"\nCategory distribution:")
    for cat, count in sorted(pattern_matches.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
    
    client.close()
    return results

if __name__ == "__main__":
    analyze_expertise_fields()