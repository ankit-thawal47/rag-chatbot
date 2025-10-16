# Project Structure Overview

## 📁 Complete File Tree

```
rag-system/
├── README.md                      # Main project documentation
├── DEPLOYMENT.md                  # Deployment guide
├── PROJECT_STRUCTURE.md           # This file
├── setup.sh                      # Development setup script
│
├── backend/                       # FastAPI Backend
│   ├── main.py                    # Main FastAPI application
│   ├── auth.py                    # Firebase & JWT authentication
│   ├── database.py                # Supabase database client
│   ├── storage.py                 # Google Cloud Storage client
│   ├── file_processor.py          # PDF/DOCX/PPTX text extraction
│   ├── embedding_service.py       # OpenAI embeddings & Pinecone
│   ├── search_service.py          # Vector search & AI chat
│   ├── requirements.txt           # Python dependencies
│   ├── .env.template              # Environment variables template
│   └── render.yaml                # Render deployment config
│
├── frontend/                      # Next.js Frontend
│   ├── pages/
│   │   ├── _app.js                # Next.js app wrapper
│   │   ├── index.js               # Login page (Google Auth)
│   │   ├── upload.js              # File upload & management
│   │   └── chat.js                # Chat interface
│   ├── components/
│   │   └── Navbar.js              # Navigation component
│   ├── lib/
│   │   ├── firebase.js            # Firebase configuration
│   │   └── api.js                 # API client (Axios)
│   ├── styles/
│   │   └── globals.css            # Tailwind CSS styles
│   ├── package.json               # Node.js dependencies
│   ├── next.config.js             # Next.js configuration
│   ├── tailwind.config.js         # Tailwind CSS config
│   ├── postcss.config.js          # PostCSS config
│   ├── .env.local.template        # Environment template
│   └── vercel.json                # Vercel deployment config
│
└── database/                      # Database Setup
    ├── schema.sql                 # Complete Supabase schema
    └── setup_instructions.md      # Database setup guide
```

## 🏗️ Architecture Components

### Backend (FastAPI)
- **main.py**: Central FastAPI app with all endpoints
- **auth.py**: Firebase token validation, JWT generation
- **database.py**: Supabase client with RLS policies
- **storage.py**: Google Cloud Storage operations
- **file_processor.py**: Extract text from PDF/DOCX/PPTX
- **embedding_service.py**: Generate and store embeddings
- **search_service.py**: Vector search and AI responses

### Frontend (Next.js)
- **pages/index.js**: Google OAuth login page
- **pages/upload.js**: File upload with progress tracking
- **pages/chat.js**: Chat interface with source citations
- **components/Navbar.js**: Navigation with user info
- **lib/firebase.js**: Firebase authentication setup
- **lib/api.js**: Axios client with JWT interceptors

### Database (Supabase)
- **schema.sql**: Complete PostgreSQL schema
- Row-Level Security (RLS) for user isolation
- Indexes for performance optimization
- Helper functions for statistics

## 🔐 Security Architecture

### User Isolation Layers
1. **JWT Authentication**: User ID in token claims
2. **Database RLS**: Automatic row filtering by user_id
3. **GCP Storage**: User-specific folder paths
4. **Pinecone Namespaces**: Isolated vector storage
5. **API Validation**: Every endpoint checks user identity

### Security Flow
```
User Request → JWT Validation → User ID Extraction → RLS Policy → Data Access
```

## 📊 Data Flow

### Document Upload Flow
```
Frontend Upload → Backend Validation → GCP Storage → Database Metadata → Background Processing → Embedding Generation → Pinecone Storage → Status Update
```

### Chat Query Flow
```
User Question → Embedding Generation → Pinecone Search → Context Retrieval → OpenAI Chat → Response with Citations
```

## 🛠️ Development Workflow

### Local Development
1. Run `./setup.sh` for initial setup
2. Configure environment variables
3. Start backend: `uvicorn main:app --reload`
4. Start frontend: `npm run dev`
5. Access at `http://localhost:3000`

### Code Organization

#### Backend Structure
- **Authentication**: Centralized in `auth.py`
- **Database**: All Supabase operations in `database.py`
- **Storage**: File operations isolated in `storage.py`
- **Processing**: Background tasks in `embedding_service.py`
- **Search**: AI logic contained in `search_service.py`

#### Frontend Structure
- **Pages**: One file per route
- **Components**: Reusable UI components
- **Lib**: Shared utilities and configurations
- **Styles**: Global CSS and Tailwind

## 🔧 Configuration Files

### Backend Configuration
- **requirements.txt**: Python dependencies
- **.env**: Environment variables (local)
- **render.yaml**: Deployment configuration

### Frontend Configuration
- **package.json**: Node.js dependencies and scripts
- **next.config.js**: Next.js framework settings
- **tailwind.config.js**: CSS framework configuration
- **vercel.json**: Deployment and security headers

## 📝 File Purposes

### Core Application Files

| File | Purpose | Key Features |
|------|---------|--------------|
| `main.py` | FastAPI app | All REST endpoints, CORS, error handling |
| `auth.py` | Authentication | Firebase validation, JWT creation/verification |
| `database.py` | Data persistence | Supabase client, RLS integration |
| `storage.py` | File storage | GCP Storage operations |
| `embedding_service.py` | AI processing | Text extraction, embedding generation |
| `search_service.py` | Search & chat | Vector search, AI response generation |

### Frontend Application Files

| File | Purpose | Key Features |
|------|---------|--------------|
| `index.js` | Login page | Google OAuth, authentication flow |
| `upload.js` | File management | Upload, progress, file list |
| `chat.js` | AI interface | Chat UI, source citations |
| `firebase.js` | Auth config | Firebase setup, Google provider |
| `api.js` | HTTP client | Axios with JWT interceptors |

### Configuration & Setup Files

| File | Purpose | Key Features |
|------|---------|--------------|
| `schema.sql` | Database setup | Tables, RLS policies, indexes |
| `setup.sh` | Development setup | Automated environment setup |
| `README.md` | Documentation | Overview, quick start, architecture |
| `DEPLOYMENT.md` | Deployment guide | Step-by-step production deployment |

## 🔍 Code Quality

### Best Practices Implemented
- **Separation of Concerns**: Each file has a single responsibility
- **Error Handling**: Comprehensive error handling throughout
- **Security**: Multiple layers of user isolation
- **Documentation**: Inline comments and external docs
- **Configuration**: Environment-based configuration
- **Validation**: Input validation and sanitization

### Code Standards
- **Python**: PEP 8 compliance, type hints where beneficial
- **JavaScript**: ES6+, consistent naming conventions
- **SQL**: Proper indexing, RLS policies, comments
- **Comments**: Focus on "why" not "what"

## 📦 Dependencies

### Backend Dependencies (Python)
- **fastapi**: Modern, fast web framework
- **uvicorn**: ASGI server
- **firebase-admin**: Authentication
- **PyJWT**: JWT token handling
- **google-cloud-storage**: File storage
- **supabase**: Database client
- **pinecone-client**: Vector database
- **openai**: AI embeddings and chat
- **langchain**: Text processing utilities

### Frontend Dependencies (JavaScript)
- **next**: React framework
- **react**: UI library
- **firebase**: Authentication SDK
- **axios**: HTTP client
- **tailwindcss**: CSS framework

## 🚀 Deployment Architecture

### Production Stack
- **Backend**: Render (FastAPI)
- **Frontend**: Vercel (Next.js)
- **Database**: Supabase (PostgreSQL)
- **Storage**: Google Cloud Storage
- **Vector DB**: Pinecone
- **Auth**: Firebase
- **AI**: OpenAI

### Environment Separation
- **Development**: Local with hot reload
- **Staging**: Preview deployments
- **Production**: Optimized builds with monitoring

This structure provides a clean, scalable foundation for the RAG document management system while maintaining security and user isolation throughout the stack.