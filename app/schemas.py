from typing import Optional
from pydantic import BaseModel

class ResumeRecord(BaseModel):
    """Schema for a single resume record"""
    s_no: int
    name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    contact_number: Optional[str] = None
    last_qualification: Optional[str] = None
    last_institution: Optional[str] = None
    
    class Config:
        # Allow field names with underscores
        populate_by_name = True

class ExtractedData(BaseModel):
    """Schema for extracted resume data before CSV conversion"""
    name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    contact_number: Optional[str] = None
    last_qualification: Optional[str] = None
    last_institution: Optional[str] = None