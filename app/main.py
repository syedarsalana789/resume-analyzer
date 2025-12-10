import logging
from pathlib import Path
from typing import List
import io

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd

from .config import config
from .schemas import ResumeRecord, ExtractedData
from .services.file_service import FileService
from .services.resume_parser import ResumeParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Resume Analyzer",
    description="A web application for analyzing resumes and generating CSV reports",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Initialize services
file_service = FileService()
resume_parser = ResumeParser()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main HTML page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/download-csv")
async def download_csv(file: UploadFile = File(...)):
    """
    Process uploaded ZIP file and return CSV with resume data
    """
    try:
        # Validate the uploaded file
        file_service.validate_zip_file(file)
        
        # Read file content
        zip_content = await file.read()
        
        # Additional size check after reading
        if len(zip_content) > config.MAX_ZIP_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {config.MAX_ZIP_SIZE_MB}MB"
            )
        
        logger.info(f"Processing ZIP file: {file.filename} ({len(zip_content)} bytes)")
        
        # Extract resume files from ZIP
        resume_files = file_service.extract_resume_files(zip_content)
        
        logger.info(f"Found {len(resume_files)} resume files to process")
        
        # Process each resume file
        resume_records: List[ResumeRecord] = []
        
        for idx, (filename, file_content) in enumerate(resume_files, 1):
            logger.info(f"Processing resume {idx}/{len(resume_files)}: {filename}")
            
            try:
                # Parse the resume
                extracted_data = resume_parser.parse_resume(filename, file_content)
                
                # Create resume record
                record = ResumeRecord(
                    s_no=idx,
                    name=extracted_data.name,
                    address=extracted_data.address,
                    email=extracted_data.email,
                    contact_number=extracted_data.contact_number,
                    last_qualification=extracted_data.last_qualification,
                    last_institution=extracted_data.last_institution
                )
                
                resume_records.append(record)
                logger.info(f"Successfully processed {filename}")
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
                # Add empty record for failed processing
                record = ResumeRecord(s_no=idx)
                resume_records.append(record)
        
        # Convert to DataFrame
        df_data = []
        for record in resume_records:
            df_data.append({
                'S. No': record.s_no,
                'Name': record.name or '',
                'Address': record.address or '',
                'Email': record.email or '',
                'Contact Number': record.contact_number or '',
                'Last Qualification': record.last_qualification or '',
                'Last Institution Attended': record.last_institution or ''
            })
        
        df = pd.DataFrame(df_data)
        
        # Generate CSV content
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        logger.info(f"Generated CSV with {len(resume_records)} records")
        
        # Create streaming response
        def generate_csv():
            yield csv_content
        
        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=resume_report.csv"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the file"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "llm_enabled": config.is_llm_enabled(),
        "max_zip_size_mb": config.MAX_ZIP_SIZE_MB
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)