#!/usr/bin/env python3
"""
Credential normalization for degrees, certifications, and awards
"""

import re
from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict

class CredentialNormalizer:
    """Normalize academic degrees, professional certifications, and awards"""
    
    def __init__(self):
        # Academic degree mappings
        self.degree_mappings = {
            # Doctoral degrees
            'phd': 'PhD',
            'ph.d.': 'PhD',
            'ph.d': 'PhD',
            'doctor of philosophy': 'PhD',
            'dphil': 'DPhil',
            'd.phil': 'DPhil',
            'edd': 'EdD',
            'ed.d.': 'EdD',
            'doctor of education': 'EdD',
            'md': 'MD',
            'm.d.': 'MD',
            'doctor of medicine': 'MD',
            'jd': 'JD',
            'j.d.': 'JD',
            'juris doctor': 'JD',
            'dba': 'DBA',
            'd.b.a.': 'DBA',
            'doctor of business administration': 'DBA',
            'psyd': 'PsyD',
            'psy.d.': 'PsyD',
            'doctor of psychology': 'PsyD',
            'dsc': 'DSc',
            'd.sc.': 'DSc',
            'doctor of science': 'DSc',
            
            # Master's degrees
            'mba': 'MBA',
            'm.b.a.': 'MBA',
            'master of business administration': 'MBA',
            'ms': 'MS',
            'm.s.': 'MS',
            'master of science': 'MS',
            'msc': 'MSc',
            'm.sc.': 'MSc',
            'ma': 'MA',
            'm.a.': 'MA',
            'master of arts': 'MA',
            'med': 'MEd',
            'm.ed.': 'MEd',
            'master of education': 'MEd',
            'meng': 'MEng',
            'm.eng.': 'MEng',
            'master of engineering': 'MEng',
            'mph': 'MPH',
            'm.p.h.': 'MPH',
            'master of public health': 'MPH',
            'mpa': 'MPA',
            'm.p.a.': 'MPA',
            'master of public administration': 'MPA',
            'mfa': 'MFA',
            'm.f.a.': 'MFA',
            'master of fine arts': 'MFA',
            'llm': 'LLM',
            'll.m.': 'LLM',
            'master of laws': 'LLM',
            'msw': 'MSW',
            'm.s.w.': 'MSW',
            'master of social work': 'MSW',
            
            # Bachelor's degrees
            'ba': 'BA',
            'b.a.': 'BA',
            'bachelor of arts': 'BA',
            'bs': 'BS',
            'b.s.': 'BS',
            'bachelor of science': 'BS',
            'bsc': 'BSc',
            'b.sc.': 'BSc',
            'beng': 'BEng',
            'b.eng.': 'BEng',
            'bachelor of engineering': 'BEng',
            'bba': 'BBA',
            'b.b.a.': 'BBA',
            'bachelor of business administration': 'BBA',
            'bed': 'BEd',
            'b.ed.': 'BEd',
            'bachelor of education': 'BEd',
            'llb': 'LLB',
            'll.b.': 'LLB',
            'bachelor of laws': 'LLB',
            'bfa': 'BFA',
            'b.f.a.': 'BFA',
            'bachelor of fine arts': 'BFA'
        }
        
        # Professional certifications
        self.certification_mappings = {
            # Project Management
            'pmp': 'PMP',
            'project management professional': 'PMP',
            'prince2': 'PRINCE2',
            'prince 2': 'PRINCE2',
            'capm': 'CAPM',
            'agile': 'Agile',
            'scrum master': 'CSM',
            'csm': 'CSM',
            'psm': 'PSM',
            'safe': 'SAFe',
            
            # IT/Security
            'cissp': 'CISSP',
            'cisa': 'CISA',
            'cism': 'CISM',
            'ccna': 'CCNA',
            'ccnp': 'CCNP',
            'ccie': 'CCIE',
            'mcse': 'MCSE',
            'mcsa': 'MCSA',
            'aws certified': 'AWS',
            'aws solutions architect': 'AWS-SA',
            'azure': 'Azure',
            'gcp': 'GCP',
            'comptia': 'CompTIA',
            'ceh': 'CEH',
            'oscp': 'OSCP',
            
            # Finance/Accounting
            'cpa': 'CPA',
            'c.p.a.': 'CPA',
            'certified public accountant': 'CPA',
            'cfa': 'CFA',
            'c.f.a.': 'CFA',
            'chartered financial analyst': 'CFA',
            'frm': 'FRM',
            'cma': 'CMA',
            'certified management accountant': 'CMA',
            'cia': 'CIA',
            'certified internal auditor': 'CIA',
            'acca': 'ACCA',
            'caia': 'CAIA',
            
            # Quality/Process
            'six sigma': 'Six Sigma',
            'black belt': 'Six Sigma Black Belt',
            'green belt': 'Six Sigma Green Belt',
            'lean': 'Lean',
            'iso': 'ISO',
            
            # HR
            'shrm': 'SHRM',
            'shrm-cp': 'SHRM-CP',
            'shrm-scp': 'SHRM-SCP',
            'phr': 'PHR',
            'sphr': 'SPHR',
            'gphr': 'GPHR',
            
            # Medical
            'board certified': 'Board Certified',
            'bcps': 'BCPS',
            'facc': 'FACC',
            'facs': 'FACS',
            'facep': 'FACEP',
            
            # Speaking
            'csp': 'CSP',
            'certified speaking professional': 'CSP',
            'cpae': 'CPAE',
            'dtm': 'DTM',
            'distinguished toastmaster': 'DTM'
        }
        
        # Award categories
        self.award_categories = {
            'nobel': 'Nobel Prize',
            'pulitzer': 'Pulitzer Prize',
            'emmy': 'Emmy Award',
            'grammy': 'Grammy Award',
            'oscar': 'Academy Award',
            'tony': 'Tony Award',
            'forbes': 'Forbes Recognition',
            'ted': 'TED',
            'tedx': 'TEDx',
            'bestseller': 'Bestselling Author',
            'inc': 'Inc. Magazine',
            'entrepreneur': 'Entrepreneur Magazine',
            'fast company': 'Fast Company',
            '40 under 40': '40 Under 40',
            '30 under 30': '30 Under 30'
        }
        
        # Degree levels for sorting
        self.degree_levels = {
            'PhD': 5, 'DPhil': 5, 'EdD': 5, 'MD': 5, 'JD': 5, 'DBA': 5, 'PsyD': 5, 'DSc': 5,
            'MBA': 4, 'MS': 4, 'MSc': 4, 'MA': 4, 'MEd': 4, 'MEng': 4, 'MPH': 4, 'MPA': 4,
            'MFA': 4, 'LLM': 4, 'MSW': 4,
            'BA': 3, 'BS': 3, 'BSc': 3, 'BEng': 3, 'BBA': 3, 'BEd': 3, 'LLB': 3, 'BFA': 3,
            'AA': 2, 'AS': 2,
            'HS': 1
        }
    
    def normalize_degree(self, degree_str: str) -> Dict[str, Any]:
        """
        Normalize a single degree string
        
        Input: "ph.d. computer science from MIT"
        Output: {
            'degree': 'PhD',
            'field': 'Computer Science',
            'institution': 'MIT',
            'level': 5,
            'original': 'ph.d. computer science from MIT'
        }
        """
        if not degree_str:
            return None
            
        degree_lower = degree_str.lower().strip()
        
        # Extract degree type
        degree_type = None
        for deg_key, deg_value in self.degree_mappings.items():
            if deg_key in degree_lower:
                degree_type = deg_value
                break
        
        # Extract institution (after "from", "at", "-")
        institution = None
        for separator in [' from ', ' at ', ' - ', ', ']:
            if separator in degree_lower:
                parts = degree_lower.split(separator)
                if len(parts) > 1:
                    institution = parts[-1].strip().title()
                    break
        
        # Extract field of study (between degree and institution)
        field = None
        if degree_type:
            # Remove degree type and institution from string
            field_str = degree_lower
            for deg_key in self.degree_mappings:
                field_str = field_str.replace(deg_key, '')
            if institution:
                field_str = field_str.replace(institution.lower(), '')
            for sep in [' from ', ' at ', ' - ', ', ', ' in ']:
                field_str = field_str.replace(sep, ' ')
            field_str = field_str.strip()
            if field_str:
                field = field_str.title()
        
        if degree_type:
            return {
                'degree': degree_type,
                'field': field,
                'institution': institution,
                'level': self.degree_levels.get(degree_type, 0),
                'original': degree_str
            }
        
        # Return original if not recognized
        return {
            'degree': degree_str,
            'field': None,
            'institution': None,
            'level': 0,
            'original': degree_str
        }
    
    def normalize_certification(self, cert_str: str) -> Dict[str, Any]:
        """Normalize a certification string"""
        if not cert_str:
            return None
            
        cert_lower = cert_str.lower().strip()
        
        # Find matching certification
        cert_type = None
        for cert_key, cert_value in self.certification_mappings.items():
            if cert_key in cert_lower:
                cert_type = cert_value
                break
        
        # Extract year if present
        year_match = re.search(r'(\d{4})', cert_str)
        year = year_match.group(1) if year_match else None
        
        # Extract issuer
        issuer = None
        for separator in [' by ', ' from ', ' - ']:
            if separator in cert_lower:
                parts = cert_lower.split(separator)
                if len(parts) > 1:
                    issuer = parts[-1].strip().title()
                    break
        
        if cert_type:
            return {
                'certification': cert_type,
                'issuer': issuer,
                'year': year,
                'original': cert_str
            }
        
        return {
            'certification': cert_str,
            'issuer': None,
            'year': year,
            'original': cert_str
        }
    
    def normalize_awards(self, awards_list: List[str]) -> Dict[str, Any]:
        """
        Normalize a list of awards
        
        Returns:
        {
            'awards': [normalized award objects],
            'categories': ['Nobel Prize', 'TED'],
            'prestigious_count': 2,
            'speaker_awards': ['CSP'],
            'media_awards': ['Emmy Award']
        }
        """
        normalized_awards = []
        categories = set()
        prestigious = []
        speaker_awards = []
        media_awards = []
        
        for award in awards_list:
            if not award:
                continue
                
            award_lower = award.lower()
            
            # Check award categories
            category = None
            for award_key, award_cat in self.award_categories.items():
                if award_key in award_lower:
                    category = award_cat
                    categories.add(award_cat)
                    
                    # Categorize
                    if award_cat in ['Nobel Prize', 'Pulitzer Prize', 'MacArthur Fellowship']:
                        prestigious.append(award_cat)
                    elif award_cat in ['CSP', 'CPAE', 'DTM']:
                        speaker_awards.append(award_cat)
                    elif award_cat in ['Emmy Award', 'Grammy Award', 'Oscar', 'Tony Award']:
                        media_awards.append(award_cat)
                    break
            
            # Extract year
            year_match = re.search(r'(\d{4})', award)
            year = year_match.group(1) if year_match else None
            
            normalized_awards.append({
                'award': award,
                'category': category,
                'year': year
            })
        
        return {
            'awards': normalized_awards,
            'categories': list(categories),
            'prestigious_count': len(set(prestigious)),
            'speaker_awards': list(set(speaker_awards)),
            'media_awards': list(set(media_awards))
        }
    
    def extract_credentials_from_bio(self, bio_text: str) -> Dict[str, Any]:
        """
        Extract degrees, certifications, and awards from biography text
        
        Returns combined credentials found in text
        """
        if not bio_text:
            return {
                'degrees': [],
                'certifications': [],
                'awards': []
            }
        
        bio_lower = bio_text.lower()
        
        # Extract degrees
        degrees = []
        for deg_key, deg_value in self.degree_mappings.items():
            if deg_key in bio_lower:
                # Try to extract context around degree
                pattern = rf'\b{re.escape(deg_key)}[\w\s,.-]*(?:from|at)?\s*[\w\s]*'
                matches = re.finditer(pattern, bio_lower)
                for match in matches:
                    degree_context = match.group(0)
                    normalized = self.normalize_degree(degree_context)
                    if normalized:
                        degrees.append(normalized)
        
        # Extract certifications
        certifications = []
        for cert_key, cert_value in self.certification_mappings.items():
            if cert_key in bio_lower:
                certifications.append({
                    'certification': cert_value,
                    'found_in_bio': True
                })
        
        # Extract awards
        awards = []
        for award_key, award_cat in self.award_categories.items():
            if award_key in bio_lower:
                awards.append({
                    'category': award_cat,
                    'found_in_bio': True
                })
        
        return {
            'degrees': degrees,
            'certifications': certifications,
            'awards': awards
        }