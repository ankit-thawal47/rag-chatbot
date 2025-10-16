from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from auth import verify_firebase_token, create_jwt_token, verify_jwt_token
from storage import upload_to_gcp
from database import (
    save_document_metadata, 
    get_user_documents, 
    save_or_update_user,
    get_document_by_id
)
from file_processor import validate_file_type, validate_file_size
from embedding_service import process_document_embeddings
from search_service import search_and_generate_response, get_document_statistics

# Initialize FastAPI app
app = FastAPI(
    title="RAG Document Management API",
    description="Secure document upload and AI-powered search system",
    version="1.0.0"
)

# CORS Configuration - Add your frontend URLs here
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Local development (alternative port)
        "https://your-vercel-app.vercel.app",  # Replace with your Vercel URL
        "https://*.vercel.app"  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models for request/response
class AuthRequest(BaseModel):
    firebase_token: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
    sources: list

class FileResponse(BaseModel):
    doc_id: str
    filename: str
    status: str
    message: str

# Dependency to get current user from JWT token
async def get_current_user(credentials = Depends(security)) -> str:
    """Extract user_id from JWT token"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    return payload["user_id"]

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "RAG Document Management API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.post("/auth", response_model=AuthResponse)
async def authenticate(auth_request: AuthRequest):
    """
    Authenticate user with Firebase token and return JWT
    """
    try:
        # Verify Firebase token
        decoded_token = verify_firebase_token(auth_request.firebase_token)
        user_id = decoded_token['uid']
        email = decoded_token.get('email', '')
        display_name = decoded_token.get('name', '')
        
        # Save/update user in database
        save_or_update_user(user_id, email)
        
        # Generate JWT token
        jwt_token = create_jwt_token(user_id, email)
        
        return AuthResponse(
            access_token=jwt_token,
            token_type="bearer",
            user_id=user_id,
            email=email
        )
        
    except Exception as e:
        print(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@app.post("/upload", response_model=FileResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """
    Upload document and trigger embedding generation
    """
    try:
        # Validate file type
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Supported formats: PDF, DOCX, PPTX"
            )
        
        # Read file content and validate size
        file_content = await file.read()
        file_size = len(file_content)
        
        if not validate_file_size(file_size):
            raise HTTPException(
                status_code=400,
                detail="File size must be between 10KB and 10MB"
            )
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Determine file type
        file_extension = file.filename.lower().split('.')[-1]
        content_type_map = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        }
        file_type = content_type_map.get(file_extension, 'application/octet-stream')
        
        # Upload file to GCP Storage
        gcp_path = f"{user_id}/{doc_id}/{file.filename}"
        upload_to_gcp(file_content, gcp_path)
        
        # Save metadata to database
        save_document_metadata(
            doc_id=doc_id,
            user_id=user_id,
            filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            gcp_path=gcp_path
        )
        
        # Trigger background embedding processing
        background_tasks.add_task(
            process_document_embeddings,
            user_id=user_id,
            doc_id=doc_id,
            gcp_path=gcp_path,
            filename=file.filename
        )
        
        return FileResponse(
            doc_id=doc_id,
            filename=file.filename,
            status="processing",
            message="File uploaded successfully. Embeddings are being generated."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/files")
async def list_files(user_id: str = Depends(get_current_user)):
    """
    Get list of user's uploaded documents
    """
    try:
        files = get_user_documents(user_id)
        return {"files": files}
        
    except Exception as e:
        print(f"Error fetching files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch files: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Query user's documents and get AI response
    """
    try:
        query = chat_request.query.strip()
        
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if len(query) > 1000:
            raise HTTPException(status_code=400, detail="Query too long (max 1000 characters)")
        
        # Search documents and generate response
        result = search_and_generate_response(query, user_id)
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.get("/stats")
async def get_stats(user_id: str = Depends(get_current_user)):
    """
    Get user's document statistics
    """
    try:
        # Get database stats
        user_documents = get_user_documents(user_id)
        
        # Get Pinecone stats
        pinecone_stats = get_document_statistics(user_id)
        
        # Calculate status distribution
        status_counts = {}
        for doc in user_documents:
            status = doc.get('embedding_status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_documents": len(user_documents),
            "status_distribution": status_counts,
            "vector_count": pinecone_stats.get("total_vectors", 0),
            "namespace": pinecone_stats.get("namespace", f"user_{user_id}")
        }
        
    except Exception as e:
        print(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Delete a document and its embeddings (placeholder for POC)
    """
    try:
        # Verify document belongs to user
        document = get_document_by_id(doc_id, user_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # For POC, we'll just return success
        # In production, you would:
        # 1. Delete from GCP Storage
        # 2. Delete embeddings from Pinecone
        # 3. Delete metadata from database
        
        return {"message": "Document deletion would be implemented here", "doc_id": doc_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

# Error handlers
from fastapi.responses import JSONResponse

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)