from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import traceback
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Import backend modules
from main import retrieve_top_documents, formulate_response
from config.collections import SOURCE_COLLECTION_MAP

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
def analyze_feature():
    """
    Analyze a feature for geo-regulatory compliance
    Expected payload: {
        "title": "Feature Title",
        "description": "Feature Description", 
        "prd_text": "Full PRD Text",
        "source_file": "eu_dsa.pdf" (optional, defaults to eu_dsa.pdf)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400
            
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        prd_text = data.get('prd_text', '').strip()
        source_file = data.get('source_file', 'eu_dsa.pdf')
        
        if not title or not description:
            return jsonify({"error": "Title and description are required"}), 400
            
        # Combine all text for analysis
        query_text = f"Feature: {title}\nDescription: {description}"
        if prd_text:
            query_text += f"\nDetailed Requirements: {prd_text}"
            
        # Use real AI backend
        try:
            # Retrieve relevant documents
            top_results = retrieve_top_documents(query_text, source_file, top_k=5)
            
            # Generate compliance analysis
            analysis_response = formulate_response(top_results, query_text)
            
            # Parse response to extract classification info
            classification_result = parse_analysis_response(analysis_response, title, description)
            
            return jsonify({
                "success": True,
                "feature": classification_result,
                "raw_analysis": analysis_response,
                "retrieved_documents": len(top_results),
                "mode": "ai"
            })
        except Exception as ai_error:
            print(f"AI backend error: {ai_error}")
            traceback.print_exc()
            return jsonify({"error": f"AI analysis failed: {str(ai_error)}"}), 500
        
    except Exception as e:
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
        confidence = 0.85
    elif any(word in response_lower for word in ['compliant', 'legal', 'allowed', 'permitted', 'no violation']):
        flag = 'No' 
        confidence = 0.90
    else:
        flag = 'Maybe'
        confidence = 0.65
        
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
        "confidence": confidence,
        "regulations": regulations,
        "reasoning": reasoning[:300] + "..." if len(reasoning) > 300 else reasoning,
        "age": age_group,
        "regions_affected": ["European Union"],
        "created_at": datetime.now().isoformat(),
        "review_status": "none",
        "impact_assessment": f"Analysis suggests {flag.lower()} regulatory risk",
        "business_impact": "Requires legal review for compliance",
        "technical_complexity": "Medium - May require implementation changes",
        "rollout_timeline": "4-6 weeks including compliance review",
        "stakeholders": ["Legal Team", "Compliance", "Product Team"],
        "risk_level": "High" if flag == "Yes" else "Medium" if flag == "Maybe" else "Low"
    }

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
