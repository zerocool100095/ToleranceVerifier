# ToleranceVerifier

Automated system for verifying tolerance application in calibration certificates using AI.

## Overview

ToleranceVerifier is a comprehensive system that automates the verification of tolerances applied by technicians in calibration certificates. It combines PDF extraction, specification research, and AI analysis to determine if the correct tolerances were used during calibration.

## Key Components

### Core System
- **PDF Extraction**: Extracts structured data from calibration certificate PDFs
- **Specification Research**: Finds accurate specifications from manufacturer documentation
- **Tolerance Analysis**: Analyzes whether the correct tolerances were applied

### Interfaces
- **API Server**: RESTful API for processing certificates via HTTP requests
- **Tkinter Frontend**: Desktop application for easy user interaction

## Directory Structure

```
ToleranceVerifier/
├── api_server.py                  # FastAPI-based API server
├── tkinter_frontend.py            # Tkinter desktop application
├── run_system.bat                 # Windows batch file to start the system
├── requirements_api.txt           # Dependencies for the API server
├── README.md                      # Project documentation
├── .env                           # Environment variables (OpenAI API key)
│
├── pdf_extract/                   # PDF data extraction components
│   ├── CertificateParses.py       # Main PDF parsing module
│   ├── use_latest_api.py          # Updated API implementation
│   └── improved_parser.py         # Enhanced PDF parser
│
├── find_specifications/           # Specification research components
│   ├── spec_finder.py             # Main specification finder
│   ├── unified_spec_finder.py     # Combined multiple sources
│   ├── gemini_spec_finder.py      # Google Gemini implementation
│   └── prompts/                   # Prompts for AI models
│
├── final_analysis/                # Analysis components
│   ├── calibration_analyzer.py    # Main analysis module
│   └── test_o3mini.py             # Testing script for o3-mini model
│
├── prompts/                       # AI prompts for various components
│   ├── final_analysis/            # Analysis-related prompts
│   ├── specification_research/    # Specification research prompts
│   └── unified_analysis/          # Combined analysis prompts
│
└── scripts/                       # Utility scripts
    └── check_openai_api.py        # Verify OpenAI API usage
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/zerocool100095/ToleranceVerifier.git
cd ToleranceVerifier
```

2. Install dependencies:
```bash
pip install -r requirements_api.txt
```

3. Set up OpenAI API key:
Create a `.env` file in the root directory with your API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Starting the System

### Windows
Run the batch file to start both the API server and Tkinter frontend:
```
run_system.bat
```

### Manual Start
Start the API server:
```bash
python api_server.py
```

Start the Tkinter frontend in a separate terminal:
```bash
python tkinter_frontend.py
```

## Usage

1. Open the Tkinter frontend
2. Browse to select a PDF certificate file
3. Optionally, add custom instructions to refine the analysis
4. Click "Analyze Certificate"
5. View the results in the tabbed interface:
   - Verdict: See the PASS/FAIL result with confidence score
   - Specifications: View specifications used for the analysis
   - Calculations: See detailed tolerance calculations
   - Discrepancies: Review issues found during analysis
   - Full Response: View complete JSON output

## API Documentation

The API server provides OpenAPI documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

This project is available under the MIT License.