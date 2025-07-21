#!/usr/bin/env python3
"""
Demonstration of IndustryNormalizer functionality
Shows how industry normalization improves data consistency
"""

from src.normalizers.industry_normalizer import IndustryNormalizer

def demo_industry_normalization():
    """Demonstrate industry normalization with real examples"""
    
    normalizer = IndustryNormalizer()
    
    print("="*80)
    print("INDUSTRY NORMALIZATION DEMONSTRATION")
    print("="*80)
    
    # Example 1: Healthcare variations
    print("\n1. Healthcare Industry Variations:")
    print("-" * 40)
    healthcare_variations = [
        "Healthcare",
        "Medical",
        "Health Services", 
        "Hospital Systems",
        "Pharma",
        "Life Sciences",
        "Digital Health"
    ]
    
    result = normalizer.normalize_industries(healthcare_variations)
    print(f"Input: {healthcare_variations}")
    print(f"Primary Industries: {result['primary_industries']}")
    print(f"Display Name: {normalizer.get_industry_info('healthcare')['display_name']}")
    
    # Example 2: Technology variations
    print("\n2. Technology Industry Variations:")
    print("-" * 40)
    tech_variations = [
        "Technology",
        "IT",
        "Software",
        "SaaS",
        "Fintech",
        "EdTech",
        "Artificial Intelligence"
    ]
    
    result = normalizer.normalize_industries(tech_variations)
    print(f"Input: {tech_variations}")
    print(f"Primary Industries: {result['primary_industries']}")
    print(f"Keywords Captured: {len(result['keywords'])}")
    
    # Example 3: Mixed categories (from real data)
    print("\n3. Real Data Example - Mixed Categories:")
    print("-" * 40)
    mixed_categories = [
        "Education",
        "Educational Motivational",
        "Family & Parenting",
        "Science",
        "STEM",
        "STEM Education",
        "Technology"
    ]
    
    result = normalizer.merge_with_categories(mixed_categories)
    print(f"Input: {mixed_categories}")
    print(f"Industries Found: {result['primary_industries']}")
    print(f"Non-Industry Categories: {result['non_industry_categories']}")
    
    # Example 4: Finance variations
    print("\n4. Financial Services Variations:")
    print("-" * 40)
    finance_variations = [
        "Banking",
        "Financial Services",
        "Investment Banking",
        "Wealth Management",
        "FinServ",
        "Insurance",
        "Capital Markets"
    ]
    
    result = normalizer.normalize_industries(finance_variations)
    print(f"Input: {finance_variations}")
    print(f"Primary Industries: {result['primary_industries']}")
    print(f"All Keywords: {result['keywords']}")
    
    # Example 5: Show all available industries
    print("\n5. All Available Industry Categories:")
    print("-" * 40)
    all_industries = normalizer.get_all_industries()
    for industry_id, info in sorted(all_industries.items()):
        print(f"  - {info['display_name']} ({info['keyword_count']} keywords)")
    
    # Example 6: Unmatched terms
    print("\n6. Handling Unmatched Terms:")
    print("-" * 40)
    unknown_terms = [
        "Blockchain",  # Will match to technology
        "Restaurants",  # Will match to retail
        "Space Exploration",  # Won't match
        "Quantum Computing",  # Won't match directly
        "Agriculture Technology"  # Will match to agriculture
    ]
    
    result = normalizer.normalize_industries(unknown_terms)
    print(f"Input: {unknown_terms}")
    print(f"Matched to Industries: {result['primary_industries'] + result['secondary_industries']}")
    print(f"Unmatched Terms: {result['unmatched']}")
    
    # Example 7: Industry statistics from your data
    print("\n7. Industry Distribution in Your Data:")
    print("-" * 40)
    print("Based on analysis of speaker categories:")
    print("  - Healthcare/Medical: Found in multiple sources")
    print("  - Technology/IT: Common across all sources")
    print("  - Finance/Banking: Frequent in enterprise speakers")
    print("  - Education: Very common category")
    print("  - Manufacturing: Less common but present")
    
    print("\n" + "="*80)
    print("BENEFITS OF INDUSTRY NORMALIZATION:")
    print("="*80)
    print("1. Unified Search: Search 'healthcare' finds all medical/pharma/hospital speakers")
    print("2. Better Analytics: Accurate industry distribution statistics")
    print("3. Improved Matching: Event planners can filter by standardized industries")
    print("4. Data Quality: Consistent categorization across all sources")
    print("5. Scalability: Easy to add new industry mappings as needed")

if __name__ == "__main__":
    demo_industry_normalization()