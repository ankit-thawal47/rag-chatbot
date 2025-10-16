# RAG Document Management System - POC

A secure, scalable document upload and AI-powered search system built with modern technologies.

## 🎯 Overview

This POC demonstrates a complete RAG (Retrieval Augmented Generation) system where users can:

- **Login** with Google (Firebase Auth)
- **Upload** documents (PDF, DOCX, PPTX | 10KB-10MB)
- **View** their uploaded files with processing status
- **Chat** with their documents using AI
- **Get answers** with source citations

**Key Feature**: Complete user isolation - users can only access their own documents.

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Backend   │    │   Storage   │
│  (Next.js)  │◄──►│  (FastAPI)  │◄──►│ (GCP/Supa) │
│   Vercel    │    │   Render    │    │   base)     │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   │
    Firebase            OpenAI              Pinecone
     Auth            Embeddings/Chat     Vector Database
```

### User Isolation Strategy

1. **JWT Tokens**: Contain `user_id`, validated on every request
2. **GCP Storage**: Files stored in `bucket/{user_id}/{doc_id}/filename`
3. **Supabase**: Row-Level Security filters by `user_id`
4. **Pinecone**: Each user has their own namespace (`user_{user_id}`)
5. **API Logic**: All queries explicitly filter by authenticated `user_id`

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- Firebase project
- Google Cloud project
- Supabase project
- Pinecone account
- OpenAI API key

### 1. Clone and Setup

```bash
git clone <your-repo>
cd rag-document-system
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and fill in values
cp .env.template .env
# Edit .env with your credentials

# Run the backend
uvicorn main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template and fill in values
cp .env.local.template .env.local
# Edit .env.local with your credentials

# Run the frontend
npm run dev
```

### 4. Database Setup

1. Go to your Supabase project
2. Open SQL Editor
3. Copy and run the contents of `database/schema.sql`
4. Verify tables are created

Visit `http://localhost:3000` to start using the application!

## 🔧 Environment Variables

### Backend (.env)

```bash
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# GCP Storage
GCP_PROJECT_ID=your-gcp-project
GCP_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key

# Pinecone
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east1-gcp
PINECONE_INDEX_NAME=rag-documents

# OpenAI
OPENAI_API_KEY=your-openai-key
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📦 Deployment

### Backend (Render)

1. Create new Web Service on [Render](https://render.com)
2. Connect GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Deploy

### Frontend (Vercel)

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `vercel --prod`
3. Configure environment variables in Vercel dashboard
4. Update `NEXT_PUBLIC_API_URL` to your Render backend URL

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Firebase Admin**: Authentication
- **PyJWT**: JWT token handling
- **Google Cloud Storage**: File storage
- **Supabase**: PostgreSQL database
- **Pinecone**: Vector database
- **OpenAI**: Embeddings and chat completion
- **LangChain**: Text processing utilities

### Frontend
- **Next.js**: React framework
- **Firebase SDK**: Google authentication
- **Axios**: HTTP client
- **Tailwind CSS**: Styling

### Infrastructure
- **Render**: Backend hosting
- **Vercel**: Frontend hosting
- **Supabase**: Database hosting
- **GCP**: File storage
- **Pinecone**: Vector storage

## 📁 Project Structure

```
rag-system/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── auth.py                 # Firebase/JWT auth
│   ├── database.py             # Supabase client
│   ├── storage.py              # GCP Storage client
│   ├── file_processor.py       # Text extraction
│   ├── embedding_service.py    # OpenAI embeddings
│   ├── search_service.py       # Pinecone search
│   ├── requirements.txt        # Dependencies
│   └── .env.template           # Environment template
│
├── frontend/
│   ├── pages/
│   │   ├── index.js            # Login page
│   │   ├── upload.js           # Upload page
│   │   └── chat.js             # Chat page
│   ├── components/
│   │   └── Navbar.js           # Navigation
│   ├── lib/
│   │   ├── firebase.js         # Firebase config
│   │   └── api.js              # API client
│   ├── package.json            # Dependencies
│   └── .env.local.template     # Environment template
│
├── database/
│   ├── schema.sql              # Database schema
│   └── setup_instructions.md   # Setup guide
│
└── README.md                   # This file
```

## 🔐 Security Features

- **Authentication**: Firebase Google OAuth
- **Authorization**: JWT tokens with user claims
- **User Isolation**: Multi-layer approach:
  - Database RLS (Row-Level Security)
  - Namespace isolation in Pinecone
  - Path-based isolation in GCP Storage
- **Input Validation**: File type, size, content validation
- **CORS Protection**: Configured allowed origins
- **Error Handling**: No sensitive data exposure

## 🧪 Testing

### Manual Testing Checklist

- [ ] Login with Google account
- [ ] Upload PDF file (should succeed)
- [ ] Upload invalid file type (should fail)
- [ ] Upload file too large (should fail)
- [ ] View file list with correct status
- [ ] Wait for processing to complete
- [ ] Ask questions in chat
- [ ] Verify source citations
- [ ] Test logout and re-login
- [ ] Verify user isolation (different accounts can't see each other's files)

### API Testing

```bash
# Test authentication
curl -X POST http://localhost:8000/auth \
  -H "Content-Type: application/json" \
  -d '{"firebase_token": "YOUR_TOKEN"}'

# Test file upload
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer YOUR_JWT" \
  -F "file=@test.pdf"

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}'
```

## 🚧 Production Considerations

### Current POC Limitations

- **Background Tasks**: Using FastAPI BackgroundTasks (should be Pub/Sub)
- **Error Handling**: Basic (should have retries, monitoring)
- **Caching**: None (should add Redis)
- **Rate Limiting**: None (should add rate limiting)
- **Monitoring**: Basic logging (should add comprehensive monitoring)

### Production Improvements

1. **Scalability**:
   - Replace BackgroundTasks with Google Pub/Sub
   - Add Redis caching for embeddings
   - Implement horizontal scaling

2. **Reliability**:
   - Add retry logic with exponential backoff
   - Implement circuit breakers
   - Add health checks

3. **Monitoring**:
   - Add structured logging
   - Implement metrics collection
   - Set up alerting

4. **Security**:
   - Add rate limiting
   - Implement API key rotation
   - Add WAF protection

## 📊 Performance

### Expected Metrics (POC)

- **File Upload**: ~2-5 seconds for 1MB file
- **Text Extraction**: ~1-3 seconds for typical documents
- **Embedding Generation**: ~2-10 seconds depending on content
- **Search Query**: ~1-2 seconds
- **Chat Response**: ~3-8 seconds

### Optimization Opportunities

- Parallel embedding generation
- Caching frequent queries
- Optimized text chunking
- Connection pooling

## 🤝 Demo Script

### For Interview/Presentation (5-7 minutes)

1. **Introduction** (1 min)
   - Explain the RAG concept
   - Highlight user isolation

2. **Architecture Overview** (1 min)
   - Show the system diagram
   - Explain component responsibilities

3. **Live Demo** (3-4 min)
   - Login with Google
   - Upload a document
   - Show processing status
   - Ask questions in chat
   - Highlight source citations

4. **Technical Deep Dive** (1-2 min)
   - Explain user isolation strategy
   - Show code examples of security measures
   - Discuss production considerations

## 🐛 Troubleshooting

### Common Issues

1. **Firebase Token Invalid**: Check Firebase configuration
2. **File Upload Fails**: Verify GCP Storage setup
3. **Embeddings Not Processing**: Check OpenAI API key
4. **Search Returns No Results**: Verify Pinecone setup
5. **CORS Errors**: Update allowed origins in backend

### Debug Commands

```bash
# Check backend health
curl http://localhost:8000/

# Test database connection
python -c "from database import supabase_client; print(supabase_client.table('users').select('*').limit(1).execute())"

# Test Pinecone connection
python -c "from embedding_service import pinecone_index; print(pinecone_index.describe_index_stats())"
```

## 📞 Support

For issues or questions:

1. Check this README
2. Review the setup instructions in `database/setup_instructions.md`
3. Check the browser console for frontend errors
4. Check the backend logs for API errors

## 📄 License

This is a POC/demo project. Adapt as needed for your use case.

---

**Built with ❤️ for demonstrating modern RAG architecture**