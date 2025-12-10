import json
import logging
from typing import Optional
from openai import OpenAI

from ..config import config
from ..schemas import ExtractedData

logger = logging.getLogger(__name__)

class LLMExtractor:
    """Service for extracting resume data using OpenAI LLM"""
    
    def __init__(self):
        self.client = None
        if config.is_llm_enabled():
            try:
                self.client = OpenAI(api_key=config.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
    
    def extract_data(self, text: str) -> Optional[ExtractedData]:
        """
        Extract resume data using LLM
        Returns None if LLM is disabled or extraction fails
        """
        if not self.client:
            logger.info("LLM extraction disabled - no OpenAI API key configured")
            return None
        
        try:
            prompt = self._create_extraction_prompt(text)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a resume parsing assistant. Extract information from resumes and return ONLY valid JSON with the specified fields. Do not include any other text or explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Extract the response content
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                data = json.loads(content)
                
                # Validate required fields exist
                extracted_data = ExtractedData(
                    name=data.get('name'),
                    address=data.get('address'),
                    email=data.get('email'),
                    contact_number=data.get('contact_number'),
                    last_qualification=data.get('last_qualification'),
                    last_institution=data.get('last_institution')
                )
                
                logger.info("LLM extraction successful")
                return extracted_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {str(e)}")
                logger.error(f"Raw response: {content}")
                return None
        
        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}")
            return None
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create extraction prompt for the LLM"""
        return f"""
Extract the following information from this resume text and return ONLY a JSON object with these exact keys:

- name: Full name of the person
- address: Complete address or location
- email: Email address
- contact_number: Phone/contact number
- last_qualification: Most recent degree or qualification
- last_institution: Most recent educational institution attended

Resume text:
{text[:3000]}  

Return ONLY valid JSON with the above keys. Use null for missing information.
"""