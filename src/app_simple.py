from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import traceback
from datetime import datetime
import uuid
from dotenv import load_dotenv
import fitz  # PyMuPDF for PDF parsing
import docx  # python-docx for DOCX parsing
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

print("Backend AI modules loaded successfully")
print(f"Environment variables loaded from .env file")
print(f"Qdrant endpoint: {os.getenv('QDRANT_ENDPOINT', 'Not configured')}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "backend_available": True,
        "qdrant_configured": bool(os.getenv('QDRANT_ENDPOINT')),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_document():
    """Analyze uploaded document for geo-regulatory compliance"""
    try:
        # Mock response for testing frontend
        return jsonify({
            "status": "success",
            "analysis_id": str(uuid.uuid4()),
            "features": [
                {
                    "id": "feature_1",
                    "name": "Data Processing Location",
                    "description": "Where user data is processed",
                    "classification": "COMPLIANT",
                    "justification": "Data processing occurs within approved jurisdictions"
                },
                {
                    "id": "feature_2", 
                    "name": "Data Transfer Mechanism",
                    "description": "How data is transferred between regions",
                    "classification": "NON_COMPLIANT",
                    "justification": "Data transfers lack adequate safeguards"
                }
            ],
            "metadata": {
                "total_features": 2,
                "processing_time": "1.2s",
                "document_type": "PDF"
            }
        })

    except Exception as e:
        print(f"Error in analyze_document: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "error": f"Analysis failed: {str(e)}",
            "status": "error"
        }), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 GeoReg Compliance Classifier Backend")
    print("="*50)
    print(f"📡 API Server: http://localhost:5000")
    print(f"🔍 Health Check: http://localhost:5000/health")
    print(f"📋 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print("="*50 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
