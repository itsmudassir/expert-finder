#!/usr/bin/env python3
"""
Language normalization for speaker data
Maps language variations to ISO 639-1 codes and proficiency levels
"""

from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict

class LanguageNormalizer:
    """Normalize and categorize language information"""
    
    def __init__(self):
        # Language name to ISO 639-1 code mapping
        self.language_codes = {
            # Major languages
            'english': 'en',
            'spanish': 'es',
            'español': 'es',
            'french': 'fr',
            'français': 'fr',
            'german': 'de',
            'deutsch': 'de',
            'chinese': 'zh',
            'mandarin': 'zh',
            'mandarin chinese': 'zh',
            'cantonese': 'zh-yue',
            'japanese': 'ja',
            'korean': 'ko',
            'arabic': 'ar',
            'hindi': 'hi',
            'portuguese': 'pt',
            'português': 'pt',
            'russian': 'ru',
            'italian': 'it',
            'italiano': 'it',
            'dutch': 'nl',
            'nederlands': 'nl',
            'polish': 'pl',
            'turkish': 'tr',
            'swedish': 'sv',
            'norwegian': 'no',
            'danish': 'da',
            'finnish': 'fi',
            'greek': 'el',
            'hebrew': 'he',
            'thai': 'th',
            'vietnamese': 'vi',
            'indonesian': 'id',
            'malay': 'ms',
            'tagalog': 'tl',
            'filipino': 'tl',
            'bengali': 'bn',
            'urdu': 'ur',
            'punjabi': 'pa',
            'tamil': 'ta',
            'telugu': 'te',
            'marathi': 'mr',
            'gujarati': 'gu',
            'kannada': 'kn',
            'ukrainian': 'uk',
            'czech': 'cs',
            'hungarian': 'hu',
            'romanian': 'ro',
            'serbian': 'sr',
            'croatian': 'hr',
            'bulgarian': 'bg',
            'slovak': 'sk',
            'slovenian': 'sl',
            'lithuanian': 'lt',
            'latvian': 'lv',
            'estonian': 'et',
            'persian': 'fa',
            'farsi': 'fa',
            'swahili': 'sw',
            'zulu': 'zu',
            'afrikaans': 'af',
            'yoruba': 'yo',
            'igbo': 'ig',
            'amharic': 'am',
            'somali': 'so',
            'hausa': 'ha',
            # Variations and abbreviations
            'eng': 'en',
            'spa': 'es',
            'fra': 'fr',
            'deu': 'de',
            'chi': 'zh',
            'jpn': 'ja',
            'kor': 'ko',
            'ara': 'ar',
            'hin': 'hi',
            'por': 'pt',
            'rus': 'ru',
            'ita': 'it',
            # American/British variants
            'american english': 'en-US',
            'british english': 'en-GB',
            'canadian english': 'en-CA',
            'australian english': 'en-AU',
            'american spanish': 'es-US',
            'mexican spanish': 'es-MX',
            'european spanish': 'es-ES',
            'brazilian portuguese': 'pt-BR',
            'european portuguese': 'pt-PT',
            'simplified chinese': 'zh-CN',
            'traditional chinese': 'zh-TW'
        }
        
        # Proficiency levels normalization
        self.proficiency_levels = {
            # Native
            'native': 'native',
            'mother tongue': 'native',
            'first language': 'native',
            'l1': 'native',
            'native speaker': 'native',
            'native proficiency': 'native',
            
            # Fluent
            'fluent': 'fluent',
            'proficient': 'fluent',
            'advanced': 'fluent',
            'c2': 'fluent',
            'c1': 'fluent',
            'professional': 'fluent',
            'bilingual': 'fluent',
            'full professional': 'fluent',
            
            # Conversational
            'conversational': 'conversational',
            'intermediate': 'conversational',
            'b2': 'conversational',
            'b1': 'conversational',
            'working knowledge': 'conversational',
            'limited working': 'conversational',
            'functional': 'conversational',
            
            # Basic
            'basic': 'basic',
            'beginner': 'basic',
            'elementary': 'basic',
            'a2': 'basic',
            'a1': 'basic',
            'some': 'basic',
            'limited': 'basic'
        }
        
        # Create reverse mapping for display names
        self.code_to_language = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'it': 'Italian',
            'nl': 'Dutch',
            'pl': 'Polish',
            'tr': 'Turkish',
            'sv': 'Swedish',
            'no': 'Norwegian',
            'da': 'Danish',
            'fi': 'Finnish',
            'el': 'Greek',
            'he': 'Hebrew',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'id': 'Indonesian',
            'ms': 'Malay',
            'tl': 'Filipino',
            'bn': 'Bengali',
            'ur': 'Urdu',
            'pa': 'Punjabi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'fa': 'Persian',
            'sw': 'Swahili',
            'zu': 'Zulu',
            'af': 'Afrikaans'
        }
    
    def normalize_language(self, language_str: str) -> Dict[str, Any]:
        """
        Normalize a single language string
        Returns: {code, name, original}
        """
        if not language_str:
            return None
            
        lang_lower = language_str.lower().strip()
        
        # Check for proficiency level in string
        proficiency = None
        for prof_key, prof_value in self.proficiency_levels.items():
            if prof_key in lang_lower:
                proficiency = prof_value
                # Remove proficiency from language string
                lang_lower = lang_lower.replace(prof_key, '').strip()
                break
        
        # Get language code
        code = self.language_codes.get(lang_lower)
        if not code:
            # Try partial matching
            for lang_key, lang_code in self.language_codes.items():
                if lang_key in lang_lower or lang_lower in lang_key:
                    code = lang_code
                    break
        
        if code:
            # Handle regional variants
            base_code = code.split('-')[0]
            name = self.code_to_language.get(base_code, language_str.title())
            
            return {
                'code': code,
                'name': name,
                'proficiency': proficiency,
                'original': language_str
            }
        
        # Return original if not found
        return {
            'code': None,
            'name': language_str.title(),
            'proficiency': proficiency,
            'original': language_str
        }
    
    def normalize_language_list(self, languages: List[Any]) -> Dict[str, Any]:
        """
        Normalize a list of languages with proficiency levels
        
        Input formats supported:
        - ["English", "Spanish", "French"]
        - ["English (Native)", "Spanish (Fluent)"]
        - [{"language": "English", "proficiency": "Native"}]
        - "English, Spanish, French"
        
        Returns:
        {
            'languages': [
                {'code': 'en', 'name': 'English', 'proficiency': 'native'},
                {'code': 'es', 'name': 'Spanish', 'proficiency': 'fluent'}
            ],
            'codes': ['en', 'es'],
            'count': 2,
            'native': ['en'],
            'fluent': ['es'],
            'conversational': [],
            'display': 'English (Native), Spanish (Fluent)'
        }
        """
        normalized_languages = []
        
        # Handle string input
        if isinstance(languages, str):
            languages = [lang.strip() for lang in languages.split(',')]
        
        # Process each language
        for lang in languages:
            if not lang:
                continue
                
            # Handle dict format
            if isinstance(lang, dict):
                lang_str = lang.get('language', '')
                prof_str = lang.get('proficiency', '')
                
                norm_lang = self.normalize_language(lang_str)
                if norm_lang:
                    if prof_str and not norm_lang['proficiency']:
                        # Try to normalize proficiency
                        prof_lower = prof_str.lower()
                        norm_lang['proficiency'] = self.proficiency_levels.get(prof_lower, prof_lower)
                    normalized_languages.append(norm_lang)
            
            # Handle string format
            elif isinstance(lang, str):
                # Check for proficiency in parentheses
                if '(' in lang and ')' in lang:
                    lang_part = lang[:lang.index('(')].strip()
                    prof_part = lang[lang.index('(')+1:lang.index(')')].strip()
                    
                    norm_lang = self.normalize_language(lang_part)
                    if norm_lang:
                        prof_lower = prof_part.lower()
                        norm_lang['proficiency'] = self.proficiency_levels.get(prof_lower, prof_lower)
                        normalized_languages.append(norm_lang)
                else:
                    norm_lang = self.normalize_language(lang)
                    if norm_lang:
                        normalized_languages.append(norm_lang)
        
        # Group by proficiency
        by_proficiency = defaultdict(list)
        codes = []
        
        for lang in normalized_languages:
            if lang['code']:
                codes.append(lang['code'])
                if lang['proficiency']:
                    by_proficiency[lang['proficiency']].append(lang['code'])
        
        # Create display string
        display_parts = []
        for lang in normalized_languages:
            if lang['proficiency']:
                display_parts.append(f"{lang['name']} ({lang['proficiency'].title()})")
            else:
                display_parts.append(lang['name'])
        
        return {
            'languages': normalized_languages,
            'codes': list(set(codes)),
            'count': len(normalized_languages),
            'native': by_proficiency.get('native', []),
            'fluent': by_proficiency.get('fluent', []),
            'conversational': by_proficiency.get('conversational', []),
            'basic': by_proficiency.get('basic', []),
            'display': ', '.join(display_parts)
        }
    
    def get_language_info(self, code: str) -> Dict[str, str]:
        """Get display information for a language code"""
        base_code = code.split('-')[0]
        return {
            'code': code,
            'name': self.code_to_language.get(base_code, code.upper())
        }
    
    def search_speakers_by_language(self, languages: List[str], proficiency: str = None) -> Dict[str, Any]:
        """
        Create MongoDB query for language search
        
        Example:
        search_speakers_by_language(['en', 'es'], 'fluent')
        Returns query to find speakers fluent in English or Spanish
        """
        query = {}
        
        if proficiency:
            # Search for specific proficiency
            query['$or'] = [
                {f'languages.{proficiency}': {'$in': languages}}
            ]
        else:
            # Search for any proficiency
            query['languages.codes'] = {'$in': languages}
        
        return query