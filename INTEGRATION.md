# 🔗 Frontend-Backend Integration Guide

This document explains how the frontend and backend are now integrated in the GeoReg Compliance Classifier.

## 🏗️ Architecture Overview

```
┌─────────────────┐    HTTP/JSON     ┌─────────────────┐
│                 │    API Calls     │                 │
│   Frontend      │◄────────────────►│   Backend       │
│   (Lynx JS)     │                  │   (Flask API)   │
│   Port: 5173    │                  │   Port: 5000    │
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
         │                                    │
         │                                    │
         ▼                                    ▼
┌─────────────────┐                  ┌─────────────────┐
│   Vite Dev      │                  │   Qdrant +      │
│   Server        │                  │   Ollama AI     │
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
```

## 🚀 Quick Start

1. **Setup Dependencies:**
   ```bash
   ./start.sh
   ```

2. **Start Backend (Terminal 1):**
   ```bash
   cd src
   python3 app.py
   ```

3. **Start Frontend (Terminal 2):**
   ```bash
   npm run dev
   ```

4. **Open Browser:**
   ```
   http://localhost:5173
   ```

## 📡 API Integration Details

### Backend API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/health` | GET | Backend health check |
| `/api/analyze` | POST | Analyze feature for compliance |
| `/api/sources` | GET | Get available regulatory sources |

### Frontend Integration

The frontend automatically:
- ✅ **Detects backend status** (green/yellow indicator)
- ✅ **Falls back to mock data** if backend is unavailable
- ✅ **Sends real analysis requests** to Flask API
- ✅ **Displays AI-generated results** in the table

### Request/Response Flow

1. **User submits feature** → Upload page
2. **Frontend calls** → `/api/analyze` endpoint
3. **Backend processes** → Qdrant + Ollama AI analysis
4. **AI returns** → Structured compliance data
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

## 🎯 Features

### ✅ Real AI Analysis
- Document embedding and retrieval
- LLM-powered compliance reasoning
- Structured classification output

### ✅ Graceful Degradation
- Backend health monitoring
- Automatic fallback to mock data
- Clear status indicators

### ✅ User Experience
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
- 🟢 **Green**: AI Backend Online
- 🟡 **Yellow**: Backend Offline (Mock Mode)
- 🔴 **Red**: Critical error

## 📝 Development Notes

The integration provides:
- **Type safety** with structured API responses
- **Error handling** with graceful fallbacks
- **Real-time status** monitoring
- **Production ready** Flask API wrapper

Both frontend and backend can be developed independently while maintaining full integration capabilities.
