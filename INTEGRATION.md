# 🔗 Frontend-Backend Integration Guide

This document explains the complete integration between frontend and backend in the GeoReg Compliance Classifier, including AI analysis with Ollama and Qdrant.

## 🏗️ Architecture Overview

```
┌─────────────────┐    HTTP/JSON     ┌─────────────────┐    Vector Search    ┌─────────────────┐
│                 │    API Calls     │                 │                     │                 │
│   Frontend      │◄────────────────►│   Backend       │◄───────────────────►│   Qdrant Cloud  │
│   (Lynx JS)     │                  │   (Flask API)   │                     │   Vector DB     │
│   Port: 3000    │                  │   Port: 5001    │                     │                 │
│                 │                  │                 │                     └─────────────────┘
└─────────────────┘                  └─────────────────┘
         │                                    │
         │                                    │
         ▼                                    ▼
┌─────────────────┐                  ┌─────────────────┐
│   Vite Dev      │                  │   Ollama AI     │
│   Server        │                  │   Local Models  │
│                 │                  │   - mxbai-embed │
└─────────────────┘                  │   - llama3.1:8b │
                                     └─────────────────┘
```

## Complete Setup Guide

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+ and pip
- Homebrew (macOS)
- Git

### 1. Repository Setup
```bash
git clone <repository-url>
cd toktative-techjam
```

### 2. Environment Configuration
Create `.env` file in root directory:
```env
QDRANT_API_KEY="your-qdrant-api-key"
QDRANT_ENDPOINT="your-qdrant-endpoint-url"
```

### 3. Install Dependencies

**Frontend:**
```bash
npm install
```

**Backend:**
```bash
pip3 install -r requirements.txt
```

### 4. Install AI Stack

**Install Ollama:**
```bash
brew install ollama
brew services start ollama
```

**Download AI Models:**
```bash
ollama pull mxbai-embed-large    # Embedding model
ollama pull llama3.1:8b          # Chat model
```

### 5. Start Services

**Option A: Automated Start**
```bash
chmod +x start.sh
./start.sh
```

**Option B: Manual Start**

Backend (Terminal 1):
```bash
cd src
nohup python3 app.py > backend.log 2>&1 &
```

Frontend (Terminal 2):
```bash
npm run dev
```

### 6. Verify Setup
- Frontend: http://localhost:3000
- Backend Health: http://localhost:5001/health
- Expected health response:
  ```json
  {
    "backend_available": true,
    "qdrant_configured": true,
    "status": "healthy",
    "timestamp": "2025-08-29T09:39:31.267346"
  }
  ```

## 📡 API Integration Details

### Backend API Endpoints

| Endpoint | Method | Description | Response |
|----------|---------|-------------|----------|
| `/health` | GET | Backend health check | Status, config info |
| `/api/analyze` | POST | Analyze feature for compliance | Full AI analysis |
| `/api/sources` | GET | Get available regulatory sources | Source list |

### Frontend-Backend Communication

The frontend (`app/api/realAdapter.js`) handles:
### Current Integration Features

- **Direct API calls** to Flask backend
- **Error handling** with proper user feedback
- **Real-time status** indication
- **No fallback to mock data** - real AI only

### API Request/Response Examples

#### Health Check
```bash
curl http://localhost:5001/health
```
```json
{
  "backend_available": true,
  "qdrant_configured": true,
  "status": "healthy",
  "timestamp": "2025-08-29T09:39:31.267346"
}
```

#### Feature Analysis
```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Teen Sleep Mode",
    "description": "Restrict app usage for under 18 during night hours",
    "prd_text": "Automatic restrictions 10 PM - 6 AM with parental override"
  }'
```

**Response:**
```json
{
  "success": true,
  "feature": {
    "id": "feat_abc123",
    "title": "Teen Sleep Mode",
    "description": "Restrict app usage for under 18 during night hours",
    "flag": "Maybe",
    "confidence": 0.65,
    "reasoning": "Feature meets requirements for protecting minors online...",
    "regulations": ["EU Privacy Directive"],
    "age": "Under 18",
    "regions_affected": ["European Union"],
    "risk_level": "Medium",
    "created_at": "2025-08-29T09:40:34.892961"
  },
  "raw_analysis": "Detailed AI analysis explanation...",
  "retrieved_documents": 3,
  "mode": "ai"
}
```

## 🧠 AI Analysis Pipeline

### 1. Document Embedding & Retrieval
```python
# Generate embedding for user's feature
query_embedding = get_embedding(feature_text)

# Search Qdrant for relevant regulatory passages
relevant_docs = qdrant_client.search(
    collection_name="eu_dsa_collection",
    query_vector=query_embedding,
    limit=5
)
```

### 2. AI Analysis Generation
```python
# Send context + query to Ollama
response = generate_response(
    context=relevant_regulatory_text,
    question=feature_description
)
```

### 3. Response Processing
```python
# Parse AI response into structured data
classification = {
    "flag": extract_compliance_flag(response),
    "confidence": calculate_confidence(response),
    "reasoning": extract_reasoning(response),
    "regulations": identify_regulations(response)
}
```

## 🔧 Configuration Details

### Environment Variables
```env
# Required for Qdrant vector database
QDRANT_API_KEY="your-api-key"
QDRANT_ENDPOINT="https://your-cluster.qdrant.io"

# Optional Flask settings
FLASK_ENV=production
FLASK_DEBUG=false
```

### Regulatory Document Collections
- **eu_dsa.pdf** → `eu_dsa_collection`
- **fl_bill.pdf** → `fl_bill_collection`  
- **utah_regulation_act.pdf** → `utah_regulation_collection`
- **ncmec.pdf** → `ncmec_collection`
- **ca_poksmaa.pdf** → `ca_poksmaa_collection`

## 🔄 Data Flow Architecture

```
User Input (Feature) 
       ↓
Frontend Form Submission
       ↓
realAdapter.analyzeFeature()
       ↓
POST /api/analyze
       ↓
Flask API Handler
       ↓
main.retrieve_top_documents()
       ↓
Qdrant Vector Search
       ↓
main.formulate_response()
       ↓
Ollama AI Analysis
       ↓
parse_analysis_response()
       ↓
Structured JSON Response
       ↓
Frontend Result Display
```

## 🚨 Troubleshooting Integration

### Backend Connection Issues
```bash
# Check if backend is running
curl http://localhost:5001/health

# Check backend logs
tail -f src/backend.log

# Verify Ollama is running
brew services list | grep ollama
```

### AI Model Issues
```bash
# Restart Ollama service
brew services restart ollama

# Re-download models if corrupted
ollama pull mxbai-embed-large
ollama pull llama3.1:8b

# Test Ollama directly
ollama run llama3.1:8b "Hello, test message"
```

### Frontend API Issues
```bash
# Check if frontend can reach backend
curl -v http://localhost:5001/health

# Verify CORS is enabled
# Should see Access-Control-Allow-Origin headers
```

### Environment Issues
```bash
# Verify .env file exists
ls -la .env

# Check environment loading
cd src && python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print(f'Qdrant: {os.getenv(\"QDRANT_ENDPOINT\")}')"
```

## ⚡ Performance Considerations

- **Analysis Speed**: ~10-15 seconds per feature (normal for AI processing)
- **Qdrant Queries**: 3-5 document chunks retrieved per analysis
- **Model Performance**: llama3.1:8b provides good balance of speed/quality
- **Memory Usage**: Ollama models require ~8GB RAM minimum

## 🔐 Security Notes

- **API Keys**: Stored in .env file (never commit to git)
- **CORS**: Enabled for localhost development only
- **Rate Limiting**: None implemented (add for production)
- **Authentication**: Demo mode only (implement for production)

## Deployment

## Production Deployment

For production deployment:

1. **Use production WSGI server**: Replace Flask dev server with Gunicorn
2. **Enable HTTPS**: SSL certificates for API endpoints  
3. **Add authentication**: User sessions and API authentication
4. **Scale Ollama**: Consider GPU acceleration for faster inference
5. **Monitor performance**: Add logging and metrics collection
6. **Backup strategy**: Regular Qdrant collection backups

## 📈 Future Enhancements

- **Batch Processing**: Analyze multiple features simultaneously
- **Document Upload**: PDF parsing and direct document analysis
- **Advanced Search**: Natural language queries for regulatory lookup
- **Audit Trail**: Complete compliance decision history
- **Multi-language**: Support for non-English regulatory documents
- **Custom Models**: Fine-tuned models for specific regulatory domains
5. **Frontend displays** → Results in Features table

## 🔧 Configuration

### Backend Settings
- **Flask API**: `src/app.py`
- **Ollama URL**: `http://localhost:11434`
- **Qdrant**: Vector database for document retrieval
- **Models**: `mxbai-embed-large`, `llama3.1:8b`

### Frontend Settings
- **API Base URL**: `http://localhost:5000/api`
- **Real API Adapter**: `app/api/realAdapter.js`
- **Auto-fallback**: Mock mode when backend unavailable

## Future Enhancements

## Features

### Real AI Analysis
- Document embedding and retrieval
- LLM-powered compliance reasoning
- Structured classification output

- Real document analysis using Ollama and Qdrant

### Graceful Degradation
- Backend health monitoring
- Automatic fallback to mock data
- Clear status indicators

- Clear error messages and user feedback

### User Experience
- Loading states during analysis
- Toast notifications for feedback
- Seamless integration flow

## 🐛 Troubleshooting

### Backend Issues
- **Ollama not running**: Start Ollama service
- **Qdrant connection**: Check vector database
- **Dependencies**: Run `pip install -r requirements.txt`

### Frontend Issues
- **CORS errors**: Backend includes CORS headers
- **API timeout**: Check backend logs
- **Mock mode**: Backend automatically switches

### Status Indicators
- **Green**: AI Backend Online
- **Yellow**: Backend Offline (Mock Mode)
- 🔴 **Red**: Critical error

## 📝 Development Notes

The integration provides:
- **Type safety** with structured API responses
- **Error handling** with graceful fallbacks
- **Real-time status** monitoring
- **Production ready** Flask API wrapper

Both frontend and backend can be developed independently while maintaining full integration capabilities.
