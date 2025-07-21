#!/usr/bin/env python3
"""
Demographics normalization: gender, age, diversity flags
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional

class DemographicsNormalizer:
    """Normalize demographic information with sensitivity and privacy in mind"""
    
    def __init__(self):
        # Gender mappings (inclusive)
        self.gender_mappings = {
            # Traditional
            'male': 'male',
            'm': 'male',
            'man': 'male',
            'he': 'male',
            'his': 'male',
            'him': 'male',
            
            'female': 'female',
            'f': 'female',
            'woman': 'female',
            'she': 'female',
            'her': 'female',
            'hers': 'female',
            
            # Non-binary
            'non-binary': 'non-binary',
            'nonbinary': 'non-binary',
            'nb': 'non-binary',
            'enby': 'non-binary',
            'genderqueer': 'non-binary',
            'genderfluid': 'non-binary',
            'they': 'non-binary',
            'them': 'non-binary',
            
            # Other
            'other': 'other',
            'prefer not to say': 'prefer_not_to_say',
            'not specified': 'not_specified'
        }
        
        # Pronoun mappings
        self.pronoun_mappings = {
            'he/him': 'he/him',
            'he/him/his': 'he/him',
            'she/her': 'she/her',
            'she/her/hers': 'she/her',
            'they/them': 'they/them',
            'they/them/theirs': 'they/them',
            'ze/zir': 'ze/zir',
            'ze/hir': 'ze/hir',
            'xe/xem': 'xe/xem',
            'any pronouns': 'any',
            'all pronouns': 'any',
            'name only': 'name_only'
        }
        
        # Age bracket definitions
        self.age_brackets = {
            'gen_z': {'min': 18, 'max': 27, 'display': 'Gen Z (18-27)'},
            'millennial': {'min': 28, 'max': 43, 'display': 'Millennial (28-43)'},
            'gen_x': {'min': 44, 'max': 59, 'display': 'Gen X (44-59)'},
            'boomer': {'min': 60, 'max': 78, 'display': 'Baby Boomer (60-78)'},
            'silent': {'min': 79, 'max': 99, 'display': 'Silent Gen (79+)'}
        }
        
        # Diversity categories (sensitive - handle with care)
        self.diversity_categories = {
            # Ethnicity/Race (US categories)
            'african_american': ['african american', 'black', 'afro-american', 'afro american'],
            'asian': ['asian', 'asian american', 'aapi'],
            'hispanic_latino': ['hispanic', 'latino', 'latina', 'latinx', 'latine'],
            'native_american': ['native american', 'indigenous', 'american indian', 'alaska native'],
            'pacific_islander': ['pacific islander', 'hawaiian', 'polynesian'],
            'middle_eastern': ['middle eastern', 'arab', 'persian'],
            'white': ['white', 'caucasian', 'european'],
            'multiracial': ['multiracial', 'mixed race', 'biracial', 'multiethnic'],
            
            # LGBTQ+
            'lgbtq': ['lgbtq', 'lgbt', 'lgbtq+', 'lgbtqia', 'lgbtqia+'],
            'gay': ['gay', 'homosexual'],
            'lesbian': ['lesbian'],
            'bisexual': ['bisexual', 'bi'],
            'transgender': ['transgender', 'trans'],
            'queer': ['queer'],
            
            # Other diversity dimensions
            'veteran': ['veteran', 'military', 'armed forces'],
            'disability': ['disabled', 'disability', 'differently abled', 'special needs'],
            'first_gen': ['first generation', 'first gen', 'first-generation'],
            'immigrant': ['immigrant', 'refugee', 'asylum'],
            
            # Women/Gender diversity
            'woman': ['woman', 'female'],
            'woman_in_tech': ['women in tech', 'woman in technology', 'female in tech'],
            'woman_in_stem': ['women in stem', 'woman in stem', 'female in stem'],
            'woman_leader': ['women leader', 'female leader', 'woman executive']
        }
        
        # Generation keywords for bio extraction
        self.generation_keywords = {
            'gen_z': ['gen z', 'generation z', 'zoomer', 'born after 1996'],
            'millennial': ['millennial', 'generation y', 'gen y', 'born 198', 'born 199'],
            'gen_x': ['gen x', 'generation x', 'born 196', 'born 197'],
            'boomer': ['baby boomer', 'boomer', 'born 194', 'born 195', 'born 196'],
            'silent': ['silent generation', 'born 192', 'born 193']
        }
    
    def normalize_gender(self, gender_input: str) -> Dict[str, Any]:
        """
        Normalize gender information
        
        Returns:
        {
            'gender': 'female',
            'pronouns': 'she/her',
            'display': 'Female',
            'original': 'Woman (she/her)'
        }
        """
        if not gender_input:
            return {
                'gender': 'not_specified',
                'pronouns': None,
                'display': 'Not Specified'
            }
        
        gender_lower = gender_input.lower().strip()
        
        # Extract pronouns if in parentheses
        pronouns = None
        if '(' in gender_lower and ')' in gender_lower:
            pronoun_part = gender_lower[gender_lower.index('(')+1:gender_lower.index(')')].strip()
            pronouns = self.pronoun_mappings.get(pronoun_part, pronoun_part)
            gender_lower = gender_lower[:gender_lower.index('(')].strip()
        
        # Map gender
        gender = 'not_specified'
        for gender_key, gender_value in self.gender_mappings.items():
            if gender_key in gender_lower:
                gender = gender_value
                break
        
        # If pronouns not found, infer from gender
        if not pronouns and gender in ['male', 'female']:
            pronouns = 'he/him' if gender == 'male' else 'she/her'
        
        display_map = {
            'male': 'Male',
            'female': 'Female',
            'non-binary': 'Non-binary',
            'other': 'Other',
            'prefer_not_to_say': 'Prefer not to say',
            'not_specified': 'Not Specified'
        }
        
        return {
            'gender': gender,
            'pronouns': pronouns,
            'display': display_map.get(gender, 'Not Specified'),
            'original': gender_input
        }
    
    def normalize_age(self, age_input: Any) -> Dict[str, Any]:
        """
        Normalize age information
        
        Input: 45, "45", "45-54", "millennial", "born 1978"
        Returns:
        {
            'age': 45,
            'bracket': 'gen_x',
            'generation': 'Gen X',
            'display': 'Gen X (44-59)',
            'birth_year': 1978
        }
        """
        current_year = datetime.now().year
        
        # Handle numeric age
        if isinstance(age_input, (int, float)):
            age = int(age_input)
            birth_year = current_year - age
            
            # Find bracket
            for bracket_key, bracket_info in self.age_brackets.items():
                if age is not None and age >= bracket_info['min'] and age <= bracket_info['max']:
                    return {
                        'age': age,
                        'bracket': bracket_key,
                        'generation': bracket_info['display'].split(' (')[0],
                        'display': bracket_info['display'],
                        'birth_year': birth_year
                    }
        
        # Handle string input
        if isinstance(age_input, str):
            age_lower = age_input.lower()
            
            # Extract birth year
            year_match = re.search(r'(19\d{2}|20\d{2})', age_lower)
            if year_match:
                birth_year = int(year_match.group(1))
                age = current_year - birth_year
                
                # Find bracket
                for bracket_key, bracket_info in self.age_brackets.items():
                    if age >= bracket_info['min'] and age <= bracket_info['max']:
                        return {
                            'age': age,
                            'bracket': bracket_key,
                            'generation': bracket_info['display'].split(' (')[0],
                            'display': bracket_info['display'],
                            'birth_year': birth_year
                        }
            
            # Check for generation keywords
            for gen_key, gen_keywords in self.generation_keywords.items():
                for keyword in gen_keywords:
                    if keyword in age_lower:
                        bracket_info = self.age_brackets[gen_key]
                        avg_age = (bracket_info['min'] + bracket_info['max']) // 2
                        return {
                            'age': avg_age,
                            'bracket': gen_key,
                            'generation': bracket_info['display'].split(' (')[0],
                            'display': bracket_info['display'],
                            'birth_year': current_year - avg_age
                        }
            
            # Extract age range
            numbers = re.findall(r'\d+', age_lower)
            if numbers:
                age = int(numbers[0])
                for bracket_key, bracket_info in self.age_brackets.items():
                    if age >= bracket_info['min'] and age <= bracket_info['max']:
                        return {
                            'age': age,
                            'bracket': bracket_key,
                            'generation': bracket_info['display'].split(' (')[0],
                            'display': bracket_info['display'],
                            'birth_year': current_year - age
                        }
        
        return {
            'display': str(age_input),
            'original': age_input
        }
    
    def normalize_diversity(self, diversity_inputs: List[str]) -> Dict[str, Any]:
        """
        Normalize diversity categories
        
        IMPORTANT: Handle with extreme sensitivity
        Only use self-identified information
        Never infer or assume
        
        Returns:
        {
            'categories': ['woman', 'asian', 'first_gen'],
            'flags': {
                'bipoc': True,
                'woman_in_tech': True,
                'first_generation': True
            },
            'display': ['Woman', 'Asian American', 'First Generation'],
            'dei_speaker': True
        }
        """
        categories = set()
        flags = {}
        display = []
        
        for diversity_str in diversity_inputs:
            if not diversity_str:
                continue
                
            div_lower = diversity_str.lower().strip()
            
            # Match categories
            for cat_key, cat_keywords in self.diversity_categories.items():
                for keyword in cat_keywords:
                    if keyword in div_lower:
                        categories.add(cat_key)
                        
                        # Set relevant flags
                        if cat_key in ['african_american', 'asian', 'hispanic_latino', 
                                      'native_american', 'pacific_islander', 'middle_eastern']:
                            flags['bipoc'] = True
                        
                        if cat_key in ['woman', 'woman_in_tech', 'woman_in_stem', 'woman_leader']:
                            flags['woman'] = True
                            if 'tech' in cat_key:
                                flags['woman_in_tech'] = True
                            if 'stem' in cat_key:
                                flags['woman_in_stem'] = True
                        
                        if cat_key == 'lgbtq' or cat_key in ['gay', 'lesbian', 'bisexual', 
                                                             'transgender', 'queer']:
                            flags['lgbtq'] = True
                        
                        if cat_key == 'veteran':
                            flags['veteran'] = True
                        
                        if cat_key == 'disability':
                            flags['disability'] = True
                        
                        if cat_key == 'first_gen':
                            flags['first_generation'] = True
                        
                        # Add display name
                        display_name = diversity_str if diversity_str else cat_key.replace('_', ' ').title()
                        display.append(display_name)
                        break
        
        # Determine if DEI speaker
        dei_speaker = bool(categories) or any(flags.values())
        
        return {
            'categories': list(categories),
            'flags': flags,
            'display': list(set(display)),
            'dei_speaker': dei_speaker,
            'original': diversity_inputs
        }
    
    def extract_demographics_from_bio(self, bio_text: str) -> Dict[str, Any]:
        """
        Carefully extract demographic information from biography
        
        IMPORTANT: Only extract explicitly stated information
        Never infer or assume demographics
        
        Returns found demographics or empty values
        """
        if not bio_text:
            return {
                'gender': None,
                'age_bracket': None,
                'diversity': []
            }
        
        bio_lower = bio_text.lower()
        
        # Extract pronouns (most reliable gender indicator)
        pronouns = None
        gender = None
        for pronoun_key, pronoun_value in self.pronoun_mappings.items():
            if f'({pronoun_key})' in bio_lower or f'pronouns: {pronoun_key}' in bio_lower:
                pronouns = pronoun_value
                if pronoun_value == 'he/him':
                    gender = 'male'
                elif pronoun_value == 'she/her':
                    gender = 'female'
                elif pronoun_value == 'they/them':
                    gender = 'non-binary'
                break
        
        # Extract age/generation if explicitly stated
        age_bracket = None
        for gen_key, gen_keywords in self.generation_keywords.items():
            for keyword in gen_keywords:
                if keyword in bio_lower:
                    age_bracket = gen_key
                    break
        
        # Extract explicitly stated diversity (very careful)
        diversity = []
        # Only if they explicitly self-identify
        if 'i am a' in bio_lower or 'as a' in bio_lower:
            for cat_key, cat_keywords in self.diversity_categories.items():
                for keyword in cat_keywords:
                    if f'i am a {keyword}' in bio_lower or f'as a {keyword}' in bio_lower:
                        diversity.append(cat_key)
                        break
        
        return {
            'gender': gender,
            'pronouns': pronouns,
            'age_bracket': age_bracket,
            'diversity': diversity
        }