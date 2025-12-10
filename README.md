# Resume Analyzer

A production-ready web application for analyzing resumes and generating structured CSV reports. The application accepts ZIP files containing multiple resumes in PDF and DOCX formats, extracts key information using AI/NLP techniques, and provides downloadable CSV reports.

## Features

- **Multi-format Support**: Processes PDF and DOCX resume files
- **AI-Powered Extraction**: Uses OpenAI LLM with spaCy NLP fallback for robust data extraction
- **Batch Processing**: Handles multiple resumes in a single ZIP upload
- **Structured Output**: Generates CSV reports with standardized columns
- **Clean Web Interface**: Modern, responsive single-page application
- **Production Architecture**: Clean layered design with proper error handling

## Extracted Information

The application extracts the following information from each resume:

1. **S. No** - Sequential number
2. **Name** - Full name of the candidate
3. **Address** - Complete address or location
4. **Email** - Email address
5. **Contact Number** - Phone/contact number
6. **Last Qualification** - Most recent degree or qualification
7. **Last Institution Attended** - Most recent educational institution

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

## Setup Instructions

### 1. Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd resume-analyzer

# Or extract the project files to a directory
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env file with your preferred settings
# Optional: Add your OpenAI API key for enhanced extraction
```

### 5. Run the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --reload
```

The application will be available at: **http://localhost:8000**

## Environment Variables

Configure the following variables in your `.env` file:

### MAX_ZIP_SIZE_MB
- **Description**: Maximum allowed ZIP file size in megabytes
- **Default**: 50
- **Example**: `MAX_ZIP_SIZE_MB=100`

### OPENAI_API_KEY
- **Description**: OpenAI API key for enhanced LLM-based extraction
- **Default**: Empty (uses spaCy-only extraction)
- **Example**: `OPENAI_API_KEY=sk-your-api-key-here`
- **Note**: If not provided, the application will use spaCy NER and regex-based extraction

## Usage

1. **Open the Application**: Navigate to `http://localhost:8000` in your web browser

2. **Upload ZIP File**: 
   - Click "Choose ZIP file" or drag and drop a ZIP file
   - Ensure the ZIP contains PDF and/or DOCX resume files
   - Maximum file size is configurable (default: 50MB)

3. **Process Resumes**: 
   - Click "Analyze & Download CSV"
   - The application will process all valid resume files
   - Progress will be shown in the status area

4. **Download Results**: 
   - A CSV file named `resume_report.csv` will be automatically downloaded
   - The CSV contains extracted information in a structured format

## Architecture

The application follows a clean layered architecture:

```
resume-analyzer/
├── app/
│   ├── main.py              # FastAPI application and routes
│   ├── config.py            # Configuration management
│   ├── schemas.py           # Pydantic data models
│   ├── services/            # Business logic layer
│   │   ├── file_service.py      # ZIP file handling
│   │   ├── resume_parser.py     # Resume parsing coordination
│   │   ├── text_extractors.py   # spaCy/regex extraction
│   │   └── llm_extractor.py     # OpenAI LLM extraction
│   ├── static/              # Frontend assets
│   │   ├── css/style.css        # Styling
│   │   └── js/app.js            # JavaScript functionality
│   └── templates/           # HTML templates
│       └── index.html           # Main page template
├── requirements.txt         # Python dependencies
├── .env.example            # Environment configuration template
└── README.md               # This file
```

## API Endpoints

### GET /
- **Description**: Serves the main HTML interface
- **Response**: HTML page for file upload and processing

### POST /api/download-csv
- **Description**: Processes ZIP file and returns CSV report
- **Request**: Multipart form data with `file` field containing ZIP
- **Response**: CSV file download with extracted resume data
- **Headers**: 
  - `Content-Type: text/csv`
  - `Content-Disposition: attachment; filename="resume_report.csv"`

### GET /health
- **Description**: Health check endpoint
- **Response**: JSON with application status and configuration

## Error Handling

The application includes comprehensive error handling:

- **File Validation**: Checks file type, size, and format
- **ZIP Processing**: Handles corrupted or invalid ZIP files
- **Resume Parsing**: Graceful handling of unreadable or corrupted resume files
- **Extraction Fallback**: Automatic fallback from LLM to spaCy extraction
- **User Feedback**: Clear error messages in the web interface

## Logging

The application logs important events and errors:

- File processing progress
- Extraction method used (LLM vs spaCy)
- Parsing errors for individual files
- Performance metrics

Logs are output to the console when running with `--reload`.

## Security Features

- **File Type Validation**: Only processes ZIP files
- **Content Filtering**: Only extracts PDF and DOCX files from ZIP
- **Directory Traversal Protection**: Prevents malicious ZIP files
- **Size Limits**: Configurable file size restrictions
- **Input Sanitization**: Proper handling of file content and names

## Performance Considerations

- **Model Loading**: spaCy model loaded once at startup
- **Streaming Response**: CSV generated and streamed without temporary files
- **Memory Management**: Efficient handling of large ZIP files
- **Concurrent Processing**: Designed for single-request processing with potential for scaling

## Troubleshooting

### Common Issues

1. **spaCy Model Not Found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **Port Already in Use**
   ```bash
   # Use a different port
   uvicorn app.main:app --reload --port 8001
   ```

3. **OpenAI API Errors**
   - Check your API key in `.env`
   - Ensure you have sufficient API credits
   - The application will fallback to spaCy extraction

4. **Large File Processing**
   - Increase `MAX_ZIP_SIZE_MB` in `.env`
   - Ensure sufficient system memory
   - Consider processing smaller batches

### Development Mode

For development with auto-reload:
```bash
uvicorn app.main:app --reload --log-level debug
```

## License

This project is provided as-is for educational and commercial use.

## Support

For issues and questions:
1. Check the logs for detailed error messages
2. Verify all dependencies are installed correctly
3. Ensure the spaCy model is downloaded
4. Check file formats and ZIP structure