# GeoReg Compliance Classifier

TikTok-styled Geo-Regulatory Compliance Classifier that analyzes documents for geography-specific regulatory requirements using AI.

## Features

- **Document Upload & Analysis**: Upload PRDs and get AI-powered compliance analysis
- **Regulatory Intelligence**: Analysis based on actual regulatory documents (EU DSA, FL Bill, Utah Act, etc.)
- **Upload & Classify**: Submit PRD/TRD documents for AI-powered compliance analysis
- **Results Dashboard**: View compliance classifications with AI confidence scores
- **Feature Detail**: Deep dive into AI analysis results with full reasoning
- **No Mock Data**: 100% real AI analysis - no hardcoded or fallback data
- **Modern UI**: Clean, TikTok-styled interface focused on AI insights

## 🛠 Tech Stack

### Frontend
- **Framework**: Lynx JS (React-style components), Vanilla JavaScript ES6+
- **Styling**: Custom CSS with TikTok brand colors (red #FF3361, cyan #25F4EE, teal #009995)
- **Build Tool**: Vite
- **Router**: Custom SPA router

### Backend
- **API**: Flask (Python)
- **AI Models**: Ollama (llama3.1:8b for chat, mxbai-embed-large for embeddings)
- **Vector Database**: Qdrant Cloud
- **Document Processing**: LangChain for text splitting and embedding
- **Environment**: .env configuration for secure credential management

### Regulatory Data Sources
- EU Digital Services Act (DSA)
- Florida Online Protection Bill
- Utah Social Media Regulation Act
- NCMEC Guidelines
- California POKSMAA

## 📁 Project Structure

```
/app                           # Frontend application
  /api
    realAdapter.js            # Real API adapter for backend integration
    api.js                    # API interface
  /pages
    Login.js                  # Authentication page
    Upload-simple.js          # Feature upload for classification
    Features.js               # Results dashboard (no hardcoded data)
    FeatureDetail.js          # Legacy component (not used)
  /components
    TopNav.ts                 # Navigation component
    FlagBadge.ts             # Compliance flag badges
    Toast.ts                 # Toast notifications
    ConfidenceMeter.ts       # Confidence visualization
    [Other components...]
  /lib
    router.js                # SPA routing
    utils.js                 # Utility functions
  /styles
    globals.css              # Global styles
  main-simple.js             # Main application entry point

/src                          # Backend application
  /api
    ollama_api.py            # Ollama AI integration
    qdrant_api.py            # Qdrant vector database integration
  /config
    collections.py           # Regulatory document collections mapping
  app.py                     # Flask API server
  main.py                    # Core analysis logic
  embed_documents.py        # Document embedding utilities
  chunk_documents.py        # Document chunking utilities

/data
  chunks_output.json         # Processed regulatory document chunks

.env                         # Environment variables (Qdrant credentials)
requirements.txt             # Python dependencies
package.json                 # Node.js dependencies
start.sh                     # Quick start script
INTEGRATION.md               # Integration guide
```

## Quick Start

### Prerequisites
- **Node.js** 16+ and npm
- **Python** 3.8+ and pip
- **Homebrew** (for macOS Ollama installation)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd toktative-techjam
```

### 2. Install Dependencies

**Frontend dependencies:**
```bash
npm install
```

**Backend dependencies:**
```bash
pip3 install -r requirements.txt
```

### 3. Setup Environment
Create a `.env` file in the root directory:
```env
QDRANT_API_KEY="your-qdrant-api-key"
QDRANT_ENDPOINT="your-qdrant-endpoint"
```

### 4. Install and Setup Ollama (AI Models)

**Install Ollama:**
```bash
# macOS
brew install ollama

# Start Ollama service
brew services start ollama
```

**Download required models:**
```bash
# Embedding model for document similarity
ollama pull mxbai-embed-large

# Chat model for analysis generation
ollama pull llama3.1:8b
```

### 5. Start the Application

**Option A: Use the provided script**
```bash
chmod +x start.sh
./start.sh
```

**Option B: Manual startup**

Start backend (Terminal 1):
```bash
cd src
nohup python3 app.py > backend.log 2>&1 &
```

Start frontend (Terminal 2):
```bash
npm run dev
```

### 6. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001
- **Health Check**: http://localhost:5001/health

## Usage Guide

### Login & Navigation
1. **Login**: Enter any name and email (demo authentication)
2. **Upload**: Navigate to upload page to submit features for analysis
3. **Features**: View analysis results and detailed AI insights

### Feature Analysis Workflow
1. **Upload Feature**:
   - Enter feature title and description
   - Provide detailed PRD/TRD requirements text
   - Submit for AI analysis

2. **AI Processing**:
   - System queries Qdrant vector database for relevant regulations
   - Ollama AI models analyze compliance requirements
   - Returns structured analysis with confidence scores

3. **View Results**:
   - See AI classification (Yes/No/Maybe for compliance risk)
   - Review detailed reasoning and identified regulations
   - Check confidence scores and risk levels
   - Access full raw AI analysis

### Features Dashboard
- **Clean Interface**: No search bars or filters - focus on AI insights
- **Real Data Only**: Shows only actual analyzed features (no mock data)
- **Detailed Views**: Click features to see comprehensive AI analysis
- **Rich Information**: Confidence meters, risk levels, regulation detection

## 🔧 Configuration

### Environment Variables
```env
QDRANT_API_KEY=<your-qdrant-api-key>
QDRANT_ENDPOINT=<your-qdrant-endpoint>
FLASK_ENV=production  # Optional: disable debug mode
```

### Available Regulatory Sources
- `eu_dsa.pdf` - EU Digital Services Act
- `fl_bill.pdf` - Florida Online Protection Bill  
- `utah_regulation_act.pdf` - Utah Social Media Regulation Act
- `ncmec.pdf` - NCMEC Guidelines
- `ca_poksmaa.pdf` - California POKSMAA

## 🧠 AI Analysis Pipeline

### 1. Document Retrieval
- Query embedding generated using mxbai-embed-large
- Qdrant vector search finds most relevant regulatory passages
- Typically retrieves 3-5 most relevant document chunks

### 2. AI Analysis
- llama3.1:8b model analyzes feature against retrieved regulations
- Generates structured compliance assessment
- Provides detailed reasoning and confidence scoring

### 3. Response Processing
- Extracts key information: flag, confidence, regulations, reasoning
- Classifies risk levels and age group targeting
- Returns structured JSON with full analysis details

## 📊 Analysis Output

Each AI analysis provides:
- **Compliance Flag**: Yes/No/Maybe for regulatory risk
- **Confidence Score**: 0-100% AI confidence in assessment
- **Risk Level**: High/Medium/Low classification
- **Target Age Group**: All Ages/Under 18/Adults Only
- **Identified Regulations**: Specific laws/guidelines triggered
- **Detailed Reasoning**: Full AI explanation of analysis
- **Retrieved Documents**: Number of regulatory docs consulted
- **Raw Analysis**: Complete unprocessed AI response

## 🛠 Development

### Frontend Development
```bash
npm run dev          # Start Vite dev server
npm run build        # Build for production
npm run preview      # Preview production build
```

### Backend Development
```bash
cd src
python3 app.py       # Start Flask development server
```

### Testing API Endpoints
```bash
# Health check
curl http://localhost:5001/health

# Analyze feature
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Feature Title",
    "description": "Feature description", 
    "prd_text": "Detailed requirements"
  }'
```

## 📁 Key Files

- **`app/main-simple.js`**: Frontend application entry point
- **`src/app.py`**: Flask API server with analysis endpoints
- **`src/main.py`**: Core AI analysis logic
- **`.env`**: Environment configuration (create this file)
- **`start.sh`**: Quick start script for both servers
- **`INTEGRATION.md`**: Detailed integration guide

## 🚨 Troubleshooting

### Backend Issues
- **Connection refused**: Ensure backend is running on port 5001
- **Ollama errors**: Check if `brew services list | grep ollama` shows "started"
- **Model issues**: Re-run `ollama pull mxbai-embed-large` and `ollama pull llama3.1:8b`

### Frontend Issues  
- **Build errors**: Run `npm install` to ensure dependencies
- **API errors**: Check backend health at http://localhost:5001/health

### Environment Issues
- **Missing .env**: Create file with Qdrant credentials
- **Wrong directory**: Ensure backend runs from `src/` directory

## 🏗 Architecture

### Frontend Architecture
- **Lynx JS**: Component-based architecture similar to React
- **Real API Integration**: Direct communication with Flask backend
- **No Mock Data**: 100% real AI analysis results
- **Responsive Design**: TikTok-styled modern interface

### Backend Architecture
- **Flask API**: RESTful endpoints for health and analysis
- **Ollama Integration**: Local AI models for embeddings and chat
- **Qdrant Vector DB**: Cloud-hosted regulatory document search
- **Document Processing**: LangChain for text chunking and embedding

### Data Flow
1. User submits feature via frontend form
2. Frontend sends POST request to `/api/analyze`
3. Backend generates embedding for user's feature description
4. Qdrant vector search retrieves relevant regulatory passages
5. Ollama chat model analyzes feature against regulations
6. Backend returns structured analysis to frontend
7. Frontend displays results with confidence and reasoning

## API Reference

### Endpoints

#### `GET /health`
Returns backend health status and configuration

#### `POST /api/analyze`
Analyzes feature for regulatory compliance

**Request Body:**
```json
{
  "title": "Feature Title",
  "description": "Feature description",
  "prd_text": "Detailed PRD/TRD text",
  "source_file": "eu_dsa.pdf"  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "feature": {
    "id": "feat_abc123",
    "title": "Feature Title",
    "flag": "Yes|No|Maybe",
    "confidence": 0.85,
    "reasoning": "AI analysis explanation...",
    "regulations": ["EU Digital Services Act"],
    "age": "Under 18|All Ages",
    "risk_level": "High|Medium|Low"
  },
  "raw_analysis": "Full AI response...",
  "retrieved_documents": 3,
  "mode": "ai"
}
```

## Troubleshooting

## Project Status

### Completed Features
- Full-stack AI integration with Ollama + Qdrant
- Real regulatory document analysis
- Clean UI without hardcoded data
- Confidence scoring and risk assessment
- Full analysis viewing capability
- Environment-based configuration
- Health monitoring and error handling

### Future Enhancements
- User authentication and session management
- Feature history and persistence
- Additional regulatory jurisdictions
- Batch analysis capabilities
- Advanced filtering and search
- PDF document upload and parsing
- Email notifications and sharing
- Audit trail and compliance reporting

---

**Built with ❤️ for TikTok TechJam 2025**

The app comes with 3 pre-loaded examples:

1. **Teen sleep mode (US)** → Yes (youth protection regulations)
2. **Geofence US rollout for market testing** → No (business decision)
3. **Filter available globally except KR** → Maybe (unclear requirements)

## Mobile Support

- Responsive design for mobile devices
- Touch-friendly navigation
- Collapsible filters and sections
- Optimized table layouts

## Future Backend Integration

To connect a real backend:

1. Replace `createApi('mock')` with `createApi('http')` in components
2. Update `HttpAdapter` base URL to point to your API
3. No UI changes required - same interface contracts

## Browser Support

- Modern browsers with ES6+ support
- Chrome, Firefox, Safari, Edge
- Mobile Safari, Chrome Mobile

## License

MIT License