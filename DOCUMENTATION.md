# From Guesswork to Governance: Automating Geo-Regulation with LLM

## Problem Statement

Global regulations such as the EU Digital Services Act, California SB 976 (Protecting Our Kids from Social Media Addiction Act), Florida House Bill 3 (Online Protections for Minors), and Utah Social Media Regulation Act require technology products to comply with strict, region-specific compliance standards. Traditionally, compliance verification has been a manual, expertise-heavy, and error-prone process that creates significant bottlenecks in product development cycles.

Our team has developed a comprehensive web application that allows employees to upload their Product Requirement Documents (PRDs) to automatically check for potential violations of geo-specific compliance requirements. The system transforms manual compliance review into an automated, AI-powered solution that provides instant, actionable insights.

To achieve this, we built a sophisticated pipeline that leverages a Retrieval-Augmented Generation (RAG) framework combined with Large Language Models (LLM). The system incorporates Reinforcement Learning with AI Feedback (RLAIF) using Gemini 2.0 for classification accuracy validation, while traditional Reinforcement Learning with Human Feedback (RLHF) is planned for future implementation to better capture human preferences in reasoning. The base model used is Meta Llama 3.1-8B-Instruct, with embeddings generated using mxbai-embed-large.

## Development Tools Used

**Frontend Development Stack:**
- **Vite** - Modern frontend build tool with fast development server and optimized production builds
- **Lynx JS** - Component-based frontend framework providing React-style modularity and state management
- **Modern CSS** - Responsive design with TikTok-styled interface elements

**Backend Development Stack:**
- **Flask** - Python web framework for RESTful API development with CORS support
- **Python 3.8+** - Core backend language with comprehensive library ecosystem

**AI/ML Development Tools:**
- **Ollama** - Local AI inference engine for running Llama models and embedding generation
- **AWS SageMaker** - Cloud platform for orchestrating reinforcement learning training jobs
- **Amazon S3** - Storage solution for datasets and trained model artifacts

**Database & Infrastructure:**
- **Qdrant** - High-performance vector database for storing and querying regulatory document embeddings
- **Git/GitHub** - Version control and collaborative development platform

**Development Environment:**
- **Node.js & npm** - JavaScript runtime and package management for frontend dependencies
- **pip** - Python package manager for backend dependencies
- **Docker** (planned) - Containerization for production deployment

## APIs Used in the Project

**Core Flask REST API Endpoints:**
- `GET /health` → System health check and configuration status
- `POST /api/analyze` → Feature compliance analysis with AI-powered classification
- `POST /api/parse` → Document parsing and structured data extraction from PDF/DOCX files
- `POST /api/send-email` → Email report delivery with HTML-formatted analysis reports
- `GET /api/sources` → Available regulatory source documents and collection mapping

**External AI/ML APIs:**
- **Ollama Client API** - Local inference with fine-tuned Meta Llama 3.1-8B-Instruct model for regulatory analysis
- **Ollama Embeddings API** - Text embedding generation using mxbai-embed-large model
- **Qdrant REST API** - Vector similarity search and document retrieval for RAG framework
- **Gemini 2.0 API** - AI feedback validation for RLAIF training pipeline and classification accuracy assessment

**Document Processing APIs:**
- **PyMuPDF API** - PDF text extraction and parsing with format preservation
- **python-docx API** - Microsoft Word document processing and structured content extraction

## Assets Used in the Project

**Legal Regulatory Documents (preprocessed & embedded):**
- **EU Digital Services Act (DSA)** - European Union digital platform regulations and content moderation requirements
- **California SB 976** - Protecting Our Kids from Social Media Addiction Act with youth protection provisions
- **Florida House Bill 3** - Online Protections for Minors with age verification and content filtering requirements
- **Utah Social Media Regulation Act** - State-level social media regulations and platform accountability measures
- **18 U.S.C. § 2258A** - Federal reporting requirements for providers regarding child sexual abuse content to NCMEC

**AI Model Assets:**
- **Meta Llama 3.1-8B-Instruct** - Base large language model fine-tuned for regulatory compliance classification
- **mxbai-embed-large** - Embedding model for semantic search and document retrieval in RAG pipeline
- **Fine-tuned Regulatory Classifier** - RLAIF-enhanced model for improved classification accuracy

**Frontend Assets:**
- **TikTok-styled UI Components** - Modern, responsive interface elements optimized for mobile and desktop
- **Custom CSS Framework** - Tailored styling system for compliance dashboard and analysis visualization
- **Interactive Navigation System** - Single-page application routing with real-time state management

**Infrastructure Assets:**
- **Vector Database Collections** - Pre-embedded regulatory document chunks stored in Qdrant cloud instance
- **Email Templates** - HTML-formatted report templates for compliance analysis delivery
- **Configuration Templates** - Environment setup files and deployment configurations

## Libraries Used in the Project

**Python Backend Libraries:**
- **Flask 3.0.3** - Web framework for API development
- **flask-cors 5.0.0** - Cross-origin resource sharing support
- **qdrant-client 1.15.1** - Vector database client for similarity search
- **PyMuPDF 1.26.4** - PDF document processing and text extraction
- **python-docx 1.1.2** - Microsoft Word document parsing
- **python-dotenv 1.1.1** - Environment variable management
- **requests 2.32.5** - HTTP client for external API communication
- **langchain 0.3.27** - Framework for document chunking and text processing
- **langchain-text-splitters 0.3.9** - Advanced text chunking algorithms
- **pandas 2.3.2** - Data manipulation and analysis
- **numpy 2.3.2** - Numerical computing and array operations
- **scikit-learn** - Machine learning utilities and similarity metrics
- **google-generativeai** - Gemini API integration for RLAIF validation
- **nltk** - Natural language processing for text analysis

**Frontend JavaScript Libraries:**
- **Lynx 0.2.0** - Component-based frontend framework
- **Vite 5.0.0** - Build tool and development server

**Development and Deployment Libraries:**
- **setuptools 80.9.0** - Python package building and distribution
- **wheel 0.45.1** - Binary package format for Python
- **typing-extensions 4.15.0** - Enhanced type hinting support

## Dataset(s) Used

**Primary Training Dataset:**
- **Provided Sample Dataset** - 30 labeled Product Requirement Document (PRD) features from the TechJam Information Document, serving as ground truth for model fine-tuning and validation

**Regulatory Knowledge Base:**
- **EU Digital Services Act Text Corpus** - Comprehensive legal document chunked into searchable segments
- **California State Law Corpus** - SB 976 legislative text with structured regulatory provisions
- **Florida State Law Corpus** - House Bill 3 with age protection and content moderation requirements
- **Utah State Law Corpus** - Social media regulation act with platform accountability measures
- **Federal Law Corpus** - 18 U.S.C. § 2258A reporting requirements and compliance standards

**Synthetic Enhancement Datasets:**
- **RLAIF Generated Labels** - Classification accuracy scores generated by Gemini 2.0 for training data augmentation
- **Regulatory Embedding Corpus** - Vector representations of legal texts for semantic similarity search
- **Entity Extraction Dataset** - Structured data extracted from regulatory documents for feature matching

**Notable Dataset Limitations:**
The primary constraint in our system is the limited size of the provided training dataset (30 samples). For production deployment, the system would benefit from:
- Expanded training corpus with 1000+ professionally labeled samples
- Domain expert validation of classification logic
- Multi-jurisdictional regulatory examples
- Real-world PRD samples across diverse product categories

**Data Processing Pipeline:**
- Document chunking using custom Python algorithms (no LangChain dependency for core processing)
- Embedding generation via mxbai-embed-large model through Ollama
- Vector storage optimization in Qdrant for sub-second retrieval performance
- Semantic search calibration for relevant regulatory passage identification
