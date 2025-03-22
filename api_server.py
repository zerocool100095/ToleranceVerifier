import os
import tempfile
import uvicorn
import json
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import shutil
import logging
import sys
from pathlib import Path

# Add parent directory to path for importing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import the necessary modules
from pdf_extract.CertificateParses import process_pdf_with_openai
from find_specifications.spec_finder import research_specifications
from final_analysis.calibration_analyzer import perform_analysis

app = FastAPI(title="Calibration Analyzer API", 
              description="API for analyzing calibration certificates",
              version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    """Root endpoint to verify the API is running"""
    return {"message": "Calibration Analyzer API is running"}

@app.post("/analyze")
async def analyze_certificate(
    certificate_file: UploadFile = File(...),
    custom_instructions: Optional[str] = Form(None)
):
    """
    Analyze a calibration certificate PDF
    
    - **certificate_file**: The PDF certificate to analyze
    - **custom_instructions**: Optional custom instructions to append to the prompt
    
    Returns:
        JSON with analysis results including verdict, confidence, and detailed analysis
    """
    logger.info(f"Received file: {certificate_file.filename}")
    if custom_instructions:
        logger.info(f"Custom instructions provided: {custom_instructions}")
    
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            # Copy the uploaded file to the temporary file
            shutil.copyfileobj(certificate_file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Step 1: Extract data from certificate
        logger.info("Extracting data from certificate...")
        certificate_data = process_pdf_with_openai(temp_file_path)
        if not certificate_data or isinstance(certificate_data, list) and "error" in certificate_data[0]:
            logger.error(f"Error extracting certificate data: {certificate_data}")
            raise HTTPException(status_code=422, detail="Failed to extract data from certificate")
        
        # Step 2: Research specifications
        logger.info("Researching specifications...")
        specifications = research_specifications(certificate_data)
        if not specifications:
            logger.error("Failed to get specifications")
            raise HTTPException(status_code=422, detail="Failed to retrieve specifications for the equipment")
        
        # Extract metadata for response
        cert = certificate_data[0] if isinstance(certificate_data, list) and len(certificate_data) > 0 else certificate_data
        manufacturer = cert.get("Manufacturer", "Unknown Manufacturer")
        model = cert.get("Model", "Unknown Model")
        equipment_type = cert.get("EquipmentType", "Unknown Type")
        
        # Step 3: Perform analysis with custom instructions if provided
        logger.info("Performing analysis...")
        analysis_result = perform_analysis(certificate_data, specifications, custom_instructions)
        
        # Ensure we include raw specifications for reference
        if "specifications" not in analysis_result:
            analysis_result["specifications"] = specifications
            
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        # Log the analysis result verdict
        if "verdict" in analysis_result:
            logger.info(f"Analysis verdict: {analysis_result['verdict']}")
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        # Make sure to clean up temporary files in case of error
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Error processing certificate: {str(e)}")

if __name__ == "__main__":
    # Run the FastAPI server with uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)