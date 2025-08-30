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
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

# Add src directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Add project root to sys.path for rl imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import backend modules
from main import retrieve_top_documents, formulate_response
from config.collections import SOURCE_COLLECTION_MAP
from rl.llama_reasoning_generation import extract_entities, retrieve_best_regulation_text, classify_stage

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

# File handler for general application logs
file_handler = RotatingFileHandler('../backend.log', maxBytes=10240000, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

# File handler for API access logs
api_handler = RotatingFileHandler('../api_access.log', maxBytes=10240000, backupCount=10)
api_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(method)s %(url)s - %(status_code)s - %(response_time)s ms'
))
api_handler.setLevel(logging.INFO)

app.logger.setLevel(logging.INFO)
app.logger.info('GeoReg Compliance API startup')

print("Backend AI modules loaded successfully")
print(f"Environment variables loaded from .env file")
print(f"Qdrant endpoint: {os.getenv('QDRANT_ENDPOINT', 'Not configured')}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    app.logger.info("Health check requested")
    return jsonify({
        "status": "healthy", 
        "backend_available": True,
        "qdrant_configured": bool(os.getenv('QDRANT_ENDPOINT')),
        "timestamp": datetime.now().isoformat()
    })

def parse_structured_feature_text(text):
    """
    Parse structured feature input that may contain formats like:
    Feature Title: Some title
    Description: Some description
    
    Or similar structured formats with colons as separators.
    """
    if not text or not isinstance(text, str):
        return None, None
    
    lines = text.strip().split('\n')
    title = None
    description = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for title patterns
        if line.lower().startswith(('feature title:', 'title:', 'feature name:', 'name:')):
            title_part = line.split(':', 1)
            if len(title_part) > 1:
                title = title_part[1].strip()
        
        # Look for description patterns
        elif line.lower().startswith(('description:', 'desc:', 'feature description:')):
            desc_part = line.split(':', 1)
            if len(desc_part) > 1:
                description = desc_part[1].strip()
    
    return title, description


@app.route('/analyze_feature', methods=['POST'])
def analyze_feature():
    """
    Analyze a feature for regulatory compliance.
    
    Expects JSON payload with:
    {
        "title": "Feature Title",
        "description": "Feature Description", 
        "prd_text": "Full PRD Text",
        "source_file": "eu_dsa.pdf" (optional, defaults to eu_dsa.pdf)
    }
    
    Also supports structured text input in prd_text with formats like:
    Feature Title: Some title
    Description: Some description
    """
    start_time = datetime.now()
    try:
        data = request.get_json()
        
        app.logger.info(f"NEW ANALYSIS REQUEST - Title: {data.get('title', 'Unknown') if data else 'No data'}")
        
        if not data:
            app.logger.error("No JSON payload provided")
            return jsonify({"error": "No JSON payload provided"}), 400
            
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        prd_text = data.get('prd_text', '').strip()
        source_file = data.get('source_file', 'eu_dsa.pdf')
        
        # If title or description is missing, try to parse from prd_text
        if prd_text and (not title or not description):
            parsed_title, parsed_description = parse_structured_feature_text(prd_text)
            if not title and parsed_title:
                title = parsed_title
                app.logger.info(f"Extracted title from structured text: {title}")
            if not description and parsed_description:
                description = parsed_description
                app.logger.info(f"Extracted description from structured text: {description}")
        
        if not title or not description:
            app.logger.error(f"Missing required fields - Title: {bool(title)}, Description: {bool(description)}")
            return jsonify({"error": "Title and description are required. Provide them directly or in structured format within prd_text."}), 400
            
        # Combine all text for analysis
        feature_desc = f"{title}\n{description}\n{prd_text}" if prd_text else f"{title}\n{description}"
        
        app.logger.info(f"Feature description length: {len(feature_desc)} characters")
        app.logger.info(f"Source file: {source_file}")

        # Step 1: Extract entities
        app.logger.info("Step 1: Extracting entities...")
        entities_json = extract_entities(title, description)
        try:
            entities = json.loads(entities_json)
            app.logger.info(f"Entities extracted: {list(entities.keys())}")
        except Exception:
            entities = {}
            app.logger.warning("Entity extraction failed, using empty entities")

        # Step 2: Retrieve best regulation text
        app.logger.info("Step 2: Searching vector database for relevant regulations...")
        regulation_results = retrieve_best_regulation_text(description, entities, top_k=3)
        if not regulation_results:
            regulation_context = ""
            related_regulation = ""
            regions_affected = []
            app.logger.warning("No relevant regulations found in vector search")
        else:
            regulation_context = "\n\n".join(
                "\n\n".join(r["texts"]) for r in regulation_results
            )
            related_regulation = ", ".join(r["source_file"] for r in regulation_results)
            regions_affected = [entities.get("location", "")] if entities.get("location", "") else []
            app.logger.info(f"Found {len(regulation_results)} relevant regulation sources: {related_regulation}")
            app.logger.info(f"Retrieved context length: {len(regulation_context)} characters")

        # Step 3: Classification and Reasoning (LLM)
        app.logger.info("Step 3: Generating AI classification and reasoning...")
        classification_json = classify_stage(entities, regulation_context)
        try:
            classification = json.loads(classification_json)
        except Exception:
            classification = {"classification": "Maybe", "reasoning": "LLM output not valid JSON", "related_regulation": ""}

        # Compose output for frontend
        result = {
            "id": f"feat_{uuid.uuid4().hex[:8]}",
            "title": title,
            "description": description,
            "flag": classification.get("classification", "Maybe"),
            "reasoning": classification.get("reasoning", ""),
            "age": ", ".join(entities.get("age", [])) if isinstance(entities.get("age", []), list) else entities.get("age", ""),
            "related_regulation": classification.get("related_regulation", ""),
            "regulations": [classification.get("related_regulation", "")] if classification.get("related_regulation", "") else [],
            "regions_affected": regions_affected,
            "created_at": datetime.now().isoformat()
        }

        # Log successful completion
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        app.logger.info(f"ANALYSIS COMPLETE - Classification: {result['flag']} - Duration: {duration:.0f}ms")
        app.logger.info(f"Final result: {result['title']} -> {result['flag']} ({len(result['reasoning'])} char reasoning)")

        return jsonify({
            "success": True,
            "feature": result,
            "raw_analysis": classification_json,
            "retrieved_documents": len(regulation_results),
            "mode": "ai"
        })
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        app.logger.error(f"ANALYSIS FAILED - Duration: {duration:.0f}ms - Error: {str(e)}")
        print(f"Error in analyze_feature: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

def parse_analysis_response(response_text, title, description):
    """
    Parse the AI response to extract structured classification information
    This is a simplified parser - in production you'd want more sophisticated NLP
    """
    response_lower = response_text.lower()
    
    # Determine flag based on response content
    if any(word in response_lower for word in ['violation', 'violates', 'non-compliant', 'illegal', 'prohibited']):
        flag = 'Yes'
    elif any(word in response_lower for word in ['compliant', 'legal', 'allowed', 'permitted', 'no violation']):
        flag = 'No' 
    else:
        flag = 'Maybe'
        
    # Extract mentioned regulations (simple keyword matching)
    regulations = []
    regulation_keywords = {
        'gdpr': 'GDPR Article 8',
        'digital services act': 'EU Digital Services Act',
        'dsa': 'EU Digital Services Act',
        'privacy': 'EU Privacy Directive',
        'data protection': 'Data Protection Regulation'
    }
    
    for keyword, regulation in regulation_keywords.items():
        if keyword in response_lower and regulation not in regulations:
            regulations.append(regulation)
    
    # Determine age group and reasoning
    age_group = 'All Ages'
    if any(word in response_lower for word in ['minor', 'child', 'under 18', 'teenager']):
        age_group = 'Under 18'
    elif any(word in response_lower for word in ['adult', 'over 18']):
        age_group = 'Adults Only'
        
    # Extract reasoning (first paragraph of response)
    reasoning_parts = response_text.split('\n\n')
    reasoning = reasoning_parts[0] if reasoning_parts else "Analysis indicates potential regulatory implications."
    
    return {
        "id": f"feat_{uuid.uuid4().hex[:8]}",
        "title": title,
        "description": description,
        "flag": flag,
        "regulations": regulations,
        "reasoning": reasoning[:300] + "..." if len(reasoning) > 300 else reasoning,
        "age": age_group,
        "regions_affected": ["European Union"],
        "created_at": datetime.now().isoformat()
    }

@app.route('/api/parse', methods=['POST'])
def parse_document():
    """
    Parse uploaded document and extract feature information
    """
    try:
        if 'document' not in request.files:
            return jsonify({"error": "No document file provided"}), 400
            
        file = request.files['document']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Check file type and parse accordingly
        filename = file.filename.lower()
        extracted_text = ""
        
        if filename.endswith('.pdf'):
            extracted_text = parse_pdf(file)
        elif filename.endswith(('.docx', '.doc')):
            extracted_text = parse_docx(file)
        else:
            return jsonify({"error": "Unsupported file type. Please upload PDF or DOCX files."}), 400
            
        if not extracted_text.strip():
            return jsonify({"error": "Could not extract text from document"}), 400
            
        # Extract structured information from text
        extracted_data = extract_feature_info(extracted_text)
        
        return jsonify({
            "success": True,
            "extracted_data": extracted_data,
            "raw_text": extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text
        })
        
    except Exception as e:
        print(f"Error parsing document: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Document parsing failed: {str(e)}"}), 500

def parse_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_data = file.read()
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        pdf_document.close()
        return text
    except Exception as e:
        raise Exception(f"PDF parsing error: {str(e)}")

def parse_docx(file):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise Exception(f"DOCX parsing error: {str(e)}")

def extract_feature_info(text):
    """
    Extract structured feature information from document text
    """
    # Clean up text - preserve structure but normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Initialize defaults
    title = "Extracted Feature"
    description = "Feature extracted from uploaded document"
    requirements = ""
    
    # Enhanced patterns to handle various formats including yours
    title_patterns = [
        r'(?:feature\s*title|title)\s*[:"]\s*([^,"\n]+?)(?:\s*[,"]|$)',  # Feature Title:" I WANNA SLEEP
        r'(?:feature\s*title|title):\s*([^\n,]+)',
        r'(?:feature\s*name|name):\s*([^\n,]+)',
        r'^([^:\n]{3,80})(?:\s*[,\n]|$)',  # First line if reasonable length
    ]
    
    description_patterns = [
        r'(?:description|desc)\s*[:"]\s*([^,"\n]+?)(?:\s*[,"]|(?:\s*"Requirements))',  # "Description:"SLAY,
        r'(?:description|summary|overview):\s*([^\n,]{3,300})',
        r'(?:brief|short\s+description):\s*([^\n,]{3,300})',
    ]
    
    requirements_patterns = [
        r'(?:requirements|reqs?)\s*[:"]\s*([^,"\n]+?)(?:\s*[,"]|$)',  # "Requirements:" UNSLAY
        r'(?:requirements|reqs?):\s*([^\n,]{3,500})',
    ]
    
    # Extract title
    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            extracted_title = match.group(1).strip().strip('"').strip()
            if len(extracted_title) >= 3:  # Minimum meaningful length
                title = extracted_title[:100]  # Limit title length
                break
    
    # Extract description
    for pattern in description_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted_desc = match.group(1).strip().strip('"').strip()
            if len(extracted_desc) >= 3:  # Minimum meaningful length
                description = extracted_desc[:300]
                break
    
    # Extract requirements
    for pattern in requirements_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted_reqs = match.group(1).strip().strip('"').strip()
            if len(extracted_reqs) >= 3:  # Minimum meaningful length
                requirements = extracted_reqs[:500]
                break
    
    # If no specific description found, try to get meaningful content
    if description == "Feature extracted from uploaded document":
        # Look for sentences that aren't the title
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and sentence.lower() != title.lower():
                description = sentence[:300]
                break
    
    # Build comprehensive content
    content_parts = []
    if title and title != "Extracted Feature":
        content_parts.append(f"Title: {title}")
    if description and description != "Feature extracted from uploaded document":
        content_parts.append(f"Description: {description}")
    if requirements:
        content_parts.append(f"Requirements: {requirements}")
    
    # If we have structured parts, use them; otherwise fall back to raw text
    if content_parts:
        content = "\n\n".join(content_parts)
    else:
        content = text[:2000] + "..." if len(text) > 2000 else text
    
    return {
        "title": title,
        "description": description,
        "content": content
    }

@app.route('/api/send-email', methods=['POST'])
def send_email():
    """
    Send analysis report via email
    Expected payload: {
        "to": "user@example.com",
        "subject": "Analysis Report",
        "feature": {...},
        "raw_analysis": "..."
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400
            
        to_email = data.get('to', '').strip()
        subject = data.get('subject', 'Regulatory Analysis Report')
        feature = data.get('feature', {})
        raw_analysis = data.get('raw_analysis', '')
        
        if not to_email:
            return jsonify({"error": "Recipient email is required"}), 400
            
        # Basic email validation
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, to_email):
            return jsonify({"error": "Invalid email address"}), 400
            
        # Create email content
        email_body = create_email_body(feature, raw_analysis)
        
        # For demo purposes, we'll simulate sending email
        # In production, you would configure SMTP settings
        success = send_email_smtp(to_email, subject, email_body)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Analysis report sent to {to_email}"
            })
        else:
            return jsonify({"error": "Failed to send email"}), 500
            
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Email sending failed: {str(e)}"}), 500

def create_email_body(feature, raw_analysis):
    """Create formatted email body with analysis report"""
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background: #009995; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .section {{ margin-bottom: 20px; }}
            .label {{ font-weight: bold; color: #009995; }}
            .value {{ margin-left: 10px; }}
            .flag-yes {{ color: #ef4444; font-weight: bold; }}
            .flag-no {{ color: #22c55e; font-weight: bold; }}
            .flag-maybe {{ color: #f59e0b; font-weight: bold; }}
            .analysis {{ background: #f9fafb; padding: 15px; border-radius: 8px; border-left: 4px solid #009995; }}
            .footer {{ background: #f3f4f6; padding: 15px; text-align: center; font-size: 0.9em; color: #6b7280; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>GeoReg Compliance Analysis Report</h1>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>Feature Summary</h2>
                <p><span class="label">Title:</span><span class="value">{feature.get('title', 'N/A')}</span></p>
                <p><span class="label">Description:</span><span class="value">{feature.get('description', 'N/A')}</span></p>
                <p><span class="label">Analysis Date:</span><span class="value">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</span></p>
            </div>
            
            <div class="section">
                <h2>Compliance Assessment</h2>
                <p><span class="label">Regulatory Flag:</span><span class="value flag-{feature.get('flag', 'maybe').lower()}">{feature.get('flag', 'N/A')}</span></p>
                <p><span class="label">Age Group:</span><span class="value">{feature.get('age', 'N/A')}</span></p>
            </div>
            
            <div class="section">
                <h2>Analysis Details</h2>
                <p><span class="label">Reasoning:</span></p>
                <div class="analysis">{feature.get('reasoning', 'No reasoning provided')}</div>
            </div>
            
            <div class="section">
                <h2>Regulatory Context</h2>
                <p><span class="label">Affected Regulations:</span><span class="value">{', '.join(feature.get('regulations', []) or ['None specified'])}</span></p>
                <p><span class="label">Regions Affected:</span><span class="value">{', '.join(feature.get('regions_affected', []) or ['None specified'])}</span></p>
            </div>
        </div>
        
        <div class="footer">
            <p>This report was generated by the GeoReg Compliance Classifier system.</p>
            <p>For questions about this analysis, please contact your compliance team.</p>
        </div>
    </body>
    </html>
    """
    
    return html_body

def send_email_smtp(to_email, subject, html_body):
    """
    Send email using SMTP (demo version)
    In production, configure with real SMTP settings
    """
    try:
        # For demo purposes, we'll just simulate successful email sending
        # In production, you would use real SMTP settings like this:
        
        # SMTP Configuration (example - replace with your settings)
        # smtp_server = "smtp.gmail.com"
        # smtp_port = 587
        # sender_email = "your-app@company.com"
        # sender_password = "your-app-password"
        
        # msg = MIMEMultipart('alternative')
        # msg['Subject'] = subject
        # msg['From'] = sender_email
        # msg['To'] = to_email
        # 
        # html_part = MIMEText(html_body, 'html')
        # msg.attach(html_part)
        # 
        # server = smtplib.SMTP(smtp_server, smtp_port)
        # server.starttls()
        # server.login(sender_email, sender_password)
        # server.send_message(msg)
        # server.quit()
        
        # For demo, we'll just log and return success
        print(f"DEMO: Email would be sent to {to_email}")
        print(f"Subject: {subject}")
        print("Email content prepared successfully")
        
        return True
        
    except Exception as e:
        print(f"SMTP Error: {str(e)}")
        return False

@app.route('/api/sources', methods=['GET'])
def get_available_sources():
    """Get list of available regulatory source documents"""
    return jsonify({
        "sources": list(SOURCE_COLLECTION_MAP.keys()),
        "collections": SOURCE_COLLECTION_MAP
    })

if __name__ == '__main__':
    print("Starting GeoReg Compliance API...")
    print("Available sources:", list(SOURCE_COLLECTION_MAP.keys()))
    app.run(debug=False, host='0.0.0.0', port=5001)
