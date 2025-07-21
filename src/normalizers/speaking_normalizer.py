#!/usr/bin/env python3
"""
Speaking-specific normalizations: formats, audience types, etc.
"""

from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict
import re

class SpeakingNormalizer:
    """Normalize speaking formats, audience types, and engagement parameters"""
    
    def __init__(self):
        # Session format mappings
        self.format_mappings = {
            # Keynotes
            'keynote': 'keynote',
            'keynoter': 'keynote',
            'keynote speaker': 'keynote',
            'keynote speech': 'keynote',
            'keynote address': 'keynote',
            'opening keynote': 'keynote',
            'closing keynote': 'keynote',
            'plenary': 'keynote',
            'general session': 'keynote',
            
            # Workshops
            'workshop': 'workshop',
            'training': 'workshop',
            'training session': 'workshop',
            'hands-on': 'workshop',
            'hands on': 'workshop',
            'interactive session': 'workshop',
            'breakout': 'workshop',
            'breakout session': 'workshop',
            'concurrent session': 'workshop',
            'seminar': 'workshop',
            'masterclass': 'workshop',
            'bootcamp': 'workshop',
            
            # Panels
            'panel': 'panel',
            'panelist': 'panel',
            'panel discussion': 'panel',
            'roundtable': 'panel',
            'round table': 'panel',
            'forum': 'panel',
            'town hall': 'panel',
            
            # Fireside chats
            'fireside': 'fireside',
            'fireside chat': 'fireside',
            'conversation': 'fireside',
            'interview': 'fireside',
            'moderated discussion': 'fireside',
            'dialogue': 'fireside',
            
            # Virtual formats
            'webinar': 'webinar',
            'virtual': 'webinar',
            'online session': 'webinar',
            'virtual event': 'webinar',
            'zoom': 'webinar',
            'livestream': 'webinar',
            'live stream': 'webinar',
            
            # MC/Host
            'mc': 'emcee',
            'master of ceremonies': 'emcee',
            'emcee': 'emcee',
            'host': 'emcee',
            'moderator': 'emcee',
            'facilitator': 'emcee',
            
            # Other
            'presentation': 'presentation',
            'talk': 'presentation',
            'speech': 'presentation',
            'lecture': 'presentation',
            'demo': 'demonstration',
            'demonstration': 'demonstration',
            'performance': 'performance'
        }
        
        # Audience type mappings
        self.audience_mappings = {
            # Executive level
            'c-suite': 'executives',
            'csuite': 'executives',
            'c-level': 'executives',
            'executive': 'executives',
            'executives': 'executives',
            'ceo': 'executives',
            'cfo': 'executives',
            'cto': 'executives',
            'cio': 'executives',
            'board': 'executives',
            'board of directors': 'executives',
            'leadership': 'executives',
            'senior leadership': 'executives',
            'vp': 'executives',
            'vice president': 'executives',
            
            # Management
            'management': 'management',
            'managers': 'management',
            'middle management': 'management',
            'directors': 'management',
            'supervisors': 'management',
            'team leads': 'management',
            
            # Sales
            'sales': 'sales_teams',
            'sales team': 'sales_teams',
            'sales force': 'sales_teams',
            'salespeople': 'sales_teams',
            'business development': 'sales_teams',
            'account managers': 'sales_teams',
            
            # HR
            'hr': 'hr_professionals',
            'human resources': 'hr_professionals',
            'people team': 'hr_professionals',
            'talent': 'hr_professionals',
            'recruiting': 'hr_professionals',
            'l&d': 'hr_professionals',
            'learning and development': 'hr_professionals',
            
            # Technical
            'technical': 'technical_teams',
            'developers': 'technical_teams',
            'engineers': 'technical_teams',
            'it': 'technical_teams',
            'tech teams': 'technical_teams',
            'programmers': 'technical_teams',
            'data scientists': 'technical_teams',
            
            # Healthcare
            'healthcare': 'healthcare_professionals',
            'medical': 'healthcare_professionals',
            'doctors': 'healthcare_professionals',
            'physicians': 'healthcare_professionals',
            'nurses': 'healthcare_professionals',
            'clinicians': 'healthcare_professionals',
            'healthcare workers': 'healthcare_professionals',
            
            # Education
            'educators': 'educators',
            'teachers': 'educators',
            'faculty': 'educators',
            'professors': 'educators',
            'academic': 'educators',
            'students': 'students',
            'university': 'students',
            'college': 'students',
            'graduate students': 'students',
            
            # General
            'general audience': 'general_public',
            'public': 'general_public',
            'mixed': 'general_public',
            'all employees': 'all_staff',
            'all staff': 'all_staff',
            'company-wide': 'all_staff',
            'organization-wide': 'all_staff',
            
            # Specialized
            'entrepreneurs': 'entrepreneurs',
            'startups': 'entrepreneurs',
            'founders': 'entrepreneurs',
            'investors': 'investors',
            'vcs': 'investors',
            'venture capitalists': 'investors',
            'nonprofit': 'nonprofit',
            'non-profit': 'nonprofit',
            'association': 'associations',
            'government': 'government',
            'public sector': 'government'
        }
        
        # Audience size brackets
        self.audience_sizes = {
            'small': {'min': 1, 'max': 50, 'display': 'Small (1-50)'},
            'medium': {'min': 51, 'max': 500, 'display': 'Medium (51-500)'},
            'large': {'min': 501, 'max': 5000, 'display': 'Large (501-5000)'},
            'xlarge': {'min': 5001, 'max': None, 'display': 'Extra Large (5000+)'}
        }
        
        # Session duration mappings (in minutes)
        self.duration_mappings = {
            '15 min': 15,
            '15 minutes': 15,
            'lightning': 15,
            'ted talk': 18,
            'tedx': 18,
            '20 min': 20,
            '20 minutes': 20,
            '30 min': 30,
            '30 minutes': 30,
            'half hour': 30,
            '45 min': 45,
            '45 minutes': 45,
            '60 min': 60,
            '60 minutes': 60,
            '1 hour': 60,
            'one hour': 60,
            '90 min': 90,
            '90 minutes': 90,
            '1.5 hours': 90,
            '2 hours': 120,
            'two hours': 120,
            'half day': 240,
            'full day': 480,
            'multi-day': 960
        }
        
        # Engagement style
        self.engagement_styles = {
            'interactive': ['interactive', 'hands-on', 'participatory', 'workshop-style'],
            'lecture': ['lecture', 'presentation', 'talk', 'speech'],
            'discussion': ['discussion', 'q&a', 'dialogue', 'conversation'],
            'demonstration': ['demo', 'demonstration', 'show and tell'],
            'performance': ['performance', 'entertainment', 'musical', 'theatrical']
        }
    
    def normalize_formats(self, formats: List[str]) -> Dict[str, Any]:
        """
        Normalize speaking formats
        
        Returns:
        {
            'formats': ['keynote', 'workshop', 'panel'],
            'primary_format': 'keynote',
            'virtual_capable': True,
            'can_emcee': False,
            'original': ['Keynote Speaker', 'Workshop Leader']
        }
        """
        normalized_formats = set()
        original_formats = []
        
        for format_str in formats:
            if not format_str:
                continue
                
            format_lower = format_str.lower().strip()
            original_formats.append(format_str)
            
            # Find matching format
            for fmt_key, fmt_value in self.format_mappings.items():
                if fmt_key in format_lower:
                    normalized_formats.add(fmt_value)
                    break
        
        # Determine capabilities
        virtual_capable = 'webinar' in normalized_formats
        can_emcee = 'emcee' in normalized_formats
        
        # Primary format (prioritize keynote > workshop > panel > others)
        format_priority = ['keynote', 'workshop', 'panel', 'fireside', 'webinar', 'presentation']
        primary_format = None
        for fmt in format_priority:
            if fmt in normalized_formats:
                primary_format = fmt
                break
        
        return {
            'formats': list(normalized_formats),
            'primary_format': primary_format,
            'virtual_capable': virtual_capable,
            'can_emcee': can_emcee,
            'original': original_formats
        }
    
    def normalize_audiences(self, audiences: List[str]) -> Dict[str, Any]:
        """
        Normalize audience types
        
        Returns:
        {
            'audience_types': ['executives', 'management'],
            'primary_audience': 'executives',
            'sectors': ['corporate', 'nonprofit'],
            'original': ['C-Suite', 'Senior Management']
        }
        """
        normalized_audiences = set()
        sectors = set()
        original_audiences = []
        
        for audience_str in audiences:
            if not audience_str:
                continue
                
            aud_lower = audience_str.lower().strip()
            original_audiences.append(audience_str)
            
            # Find matching audience
            for aud_key, aud_value in self.audience_mappings.items():
                if aud_key in aud_lower:
                    normalized_audiences.add(aud_value)
                    
                    # Determine sector
                    if aud_value in ['executives', 'management', 'sales_teams', 'hr_professionals', 'technical_teams', 'all_staff']:
                        sectors.add('corporate')
                    elif aud_value in ['healthcare_professionals']:
                        sectors.add('healthcare')
                    elif aud_value in ['educators', 'students']:
                        sectors.add('education')
                    elif aud_value == 'nonprofit':
                        sectors.add('nonprofit')
                    elif aud_value == 'government':
                        sectors.add('government')
                    break
        
        # Primary audience (prioritize executives > management > specialized > general)
        audience_priority = ['executives', 'management', 'healthcare_professionals', 
                           'educators', 'sales_teams', 'hr_professionals', 'general_public']
        primary_audience = None
        for aud in audience_priority:
            if aud in normalized_audiences:
                primary_audience = aud
                break
        
        return {
            'audience_types': list(normalized_audiences),
            'primary_audience': primary_audience,
            'sectors': list(sectors),
            'original': original_audiences
        }
    
    def normalize_audience_size(self, size_input: Any) -> Dict[str, Any]:
        """
        Normalize audience size
        
        Input: "100-500", "Large", 250, "500+"
        Returns: {
            'bracket': 'medium',
            'min': 100,
            'max': 500,
            'display': 'Medium (51-500)',
            'comfortable_with_large': True
        }
        """
        if not size_input:
            return None
        
        # Handle numeric input
        if isinstance(size_input, (int, float)):
            size_num = int(size_input)
            for bracket, info in self.audience_sizes.items():
                if size_num >= info['min'] and (info['max'] is None or size_num <= info['max']):
                    return {
                        'bracket': bracket,
                        'min': info['min'],
                        'max': info['max'],
                        'display': info['display'],
                        'comfortable_with_large': bracket in ['large', 'xlarge']
                    }
        
        # Handle string input
        size_str = str(size_input).lower()
        
        # Check for bracket names
        for bracket, info in self.audience_sizes.items():
            if bracket in size_str:
                return {
                    'bracket': bracket,
                    'min': info['min'],
                    'max': info['max'],
                    'display': info['display'],
                    'comfortable_with_large': bracket in ['large', 'xlarge']
                }
        
        # Extract numbers from range
        numbers = re.findall(r'\d+', size_str)
        if numbers:
            min_size = int(numbers[0])
            max_size = int(numbers[-1]) if len(numbers) > 1 else min_size
            
            # Find appropriate bracket
            avg_size = (min_size + max_size) / 2
            for bracket, info in self.audience_sizes.items():
                if avg_size >= info['min'] and (info['max'] is None or avg_size <= info['max']):
                    return {
                        'bracket': bracket,
                        'min': min_size,
                        'max': max_size,
                        'display': f"{min_size}-{max_size}",
                        'comfortable_with_large': max_size > 500
                    }
        
        return {
            'bracket': 'unknown',
            'display': str(size_input),
            'comfortable_with_large': 'large' in size_str or 'any' in size_str
        }
    
    def normalize_duration(self, duration_str: str) -> Dict[str, Any]:
        """
        Normalize session duration
        
        Returns:
        {
            'minutes': 60,
            'display': '1 hour',
            'category': 'standard',  # lightning, standard, extended, workshop
            'flexible': False
        }
        """
        if not duration_str:
            return None
            
        dur_lower = duration_str.lower().strip()
        
        # Check for mapped durations
        for dur_key, dur_minutes in self.duration_mappings.items():
            if dur_key in dur_lower:
                category = 'lightning' if dur_minutes <= 20 else \
                          'standard' if dur_minutes <= 90 else \
                          'extended' if dur_minutes <= 240 else 'workshop'
                
                return {
                    'minutes': dur_minutes,
                    'display': dur_key,
                    'category': category,
                    'flexible': 'flexible' in dur_lower or 'adjustable' in dur_lower
                }
        
        # Extract numbers
        numbers = re.findall(r'\d+', dur_lower)
        if numbers:
            minutes = int(numbers[0])
            if 'hour' in dur_lower:
                minutes *= 60
            
            category = 'lightning' if minutes <= 20 else \
                      'standard' if minutes <= 90 else \
                      'extended' if minutes <= 240 else 'workshop'
            
            return {
                'minutes': minutes,
                'display': duration_str,
                'category': category,
                'flexible': 'flexible' in dur_lower or 'adjustable' in dur_lower
            }
        
        return {
            'display': duration_str,
            'flexible': True
        }
    
    def calculate_experience_score(self, speaking_info: Dict[str, Any]) -> int:
        """
        Calculate speaking experience score (0-100)
        
        Based on:
        - Years of experience
        - Number of talks delivered
        - Format diversity
        - Audience size comfort
        - Average ratings
        """
        score = 0
        
        # Years of experience (0-20 points)
        years = speaking_info.get('years_speaking', 0)
        if years and years >= 20:
            score += 20
        elif years and years >= 10:
            score += 15
        elif years and years >= 5:
            score += 10
        elif years and years >= 2:
            score += 5
        
        # Number of talks (0-20 points)
        talks = speaking_info.get('talks_delivered', 0)
        if talks and talks >= 500:
            score += 20
        elif talks and talks >= 200:
            score += 15
        elif talks and talks >= 100:
            score += 10
        elif talks and talks >= 50:
            score += 5
        
        # Format diversity (0-20 points)
        formats = len(speaking_info.get('formats', []))
        score += min(formats * 4, 20)
        
        # Audience comfort (0-20 points)
        audience_sizes = speaking_info.get('audience_sizes', {})
        if audience_sizes.get('comfortable_with_large'):
            score += 20
        elif audience_sizes.get('max') and audience_sizes.get('max') > 500:
            score += 10
        
        # Ratings (0-20 points)
        avg_rating = speaking_info.get('average_rating', 0)
        if avg_rating and avg_rating >= 4.8:
            score += 20
        elif avg_rating and avg_rating >= 4.5:
            score += 15
        elif avg_rating and avg_rating >= 4.0:
            score += 10
        elif avg_rating and avg_rating >= 3.5:
            score += 5
        
        return min(score, 100)