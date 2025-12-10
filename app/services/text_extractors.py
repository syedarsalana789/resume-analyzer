import re
import spacy
from typing import Optional, List, Set
import logging

from ..schemas import ExtractedData

logger = logging.getLogger(__name__)

class TextExtractor:
    """Service for extracting structured data from resume text using spaCy and regex"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.error("spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm")
            raise
    
    # Degree keywords for qualification detection
    DEGREE_KEYWORDS = {
        'bs', 'bsc', 'ba', 'be', 'btech', 'btec', 'bachelor',
        'ms', 'msc', 'ma', 'me', 'mtech', 'master', 'masters',
        'mba', 'bba', 'mphil', 'phd', 'doctorate',
        'intermediate', 'fsc', 'fa', 'hssc', 'hsc',
        'diploma', 'certificate', 'degree'
    }
    
    # Institution keywords
    INSTITUTION_KEYWORDS = {
        'university', 'college', 'institute', 'school', 'academy',
        'campus', 'polytechnic', 'technical', 'engineering'
    }
    
    def extract_data(self, text: str) -> ExtractedData:
        """Extract structured data from resume text"""
        # Normalize text
        text = self._normalize_text(text)
        
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract each field
        name = self._extract_name(doc, text)
        email = self._extract_email(text)
        contact_number = self._extract_contact_number(text)
        address = self._extract_address(doc, text)
        last_qualification = self._extract_last_qualification(text)
        last_institution = self._extract_last_institution(doc, text)
        
        return ExtractedData(
            name=name,
            address=address,
            email=email,
            contact_number=contact_number,
            last_qualification=last_qualification,
            last_institution=last_institution
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for processing"""
        # Remove extra whitespace and normalize line endings
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'\n+', '\n', text)
        return text
    
    def _extract_name(self, doc, text: str) -> Optional[str]:
        """Extract person name using spaCy NER"""
        # Look for PERSON entities
        persons = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
        
        if persons:
            # Return the first person name found (usually at the top of resume)
            return persons[0]
        
        # Fallback: look for name patterns in first few lines
        lines = text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            # Simple heuristic: line with 2-4 words, mostly alphabetic
            words = line.split()
            if 2 <= len(words) <= 4 and all(word.replace('.', '').isalpha() for word in words):
                return line
        
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None
    
    def _extract_contact_number(self, text: str) -> Optional[str]:
        """Extract contact number using regex"""
        # Pattern for various phone number formats
        phone_patterns = [
            r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\d{10,15}',  # Simple digit sequence
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Return the first valid-looking phone number
                for match in matches:
                    # Clean up the match
                    cleaned = re.sub(r'[^\d+]', '', match)
                    if 7 <= len(cleaned) <= 15:  # Reasonable phone number length
                        return match.strip()
        
        return None
    
    def _extract_address(self, doc, text: str) -> Optional[str]:
        """Extract address using spaCy entities and heuristics"""
        # Look for GPE (Geopolitical entities) and LOC (Locations)
        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
        
        if locations:
            # Try to find a line containing location information
            lines = text.split('\n')
            for line in lines:
                for location in locations:
                    if location.lower() in line.lower():
                        # Return the line containing location info
                        return line.strip()
        
        # Fallback: look for address keywords
        address_keywords = ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'city', 'state']
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in address_keywords):
                return line.strip()
        
        return None
    
    def _extract_last_qualification(self, text: str) -> Optional[str]:
        """Extract last qualification using keyword matching"""
        lines = text.split('\n')
        
        # Look for degree keywords in reverse order (bottom-up)
        for line in reversed(lines):
            line_lower = line.lower()
            for degree in self.DEGREE_KEYWORDS:
                if degree in line_lower:
                    return line.strip()
        
        return None
    
    def _extract_last_institution(self, doc, text: str) -> Optional[str]:
        """Extract last institution using spaCy ORG entities and keywords"""
        # Get organization entities
        organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        
        lines = text.split('\n')
        
        # First, try to find organizations that contain institution keywords
        for line in reversed(lines):  # Bottom-up search
            line_lower = line.lower()
            
            # Check if line contains institution keywords
            if any(keyword in line_lower for keyword in self.INSTITUTION_KEYWORDS):
                # Check if any organization is in this line
                for org in organizations:
                    if org.lower() in line_lower:
                        return line.strip()
                # If no org found but has institution keywords, return the line
                return line.strip()
        
        # Fallback: return the last organization found
        if organizations:
            return organizations[-1]
        
        return None