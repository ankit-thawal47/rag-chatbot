from openai import OpenAI
from pinecone import Pinecone
import os
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from file_processor import extract_text_from_file
from storage import download_from_gcp
from database import update_embedding_status
import uuid

# Initialize OpenAI
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Pinecone
def initialize_pinecone():
    """Initialize Pinecone client with new API (v6+)"""
    api_key = os.getenv('PINECONE_API_KEY')
    
    if not api_key:
        print("Pinecone API key missing")
        return None
    
    try:
        # Use new Pinecone API
        pc = Pinecone(api_key=api_key)
        index_name = os.getenv('PINECONE_INDEX_NAME', 'rag-documents')
        
        # List indexes to verify connection
        indexes = pc.list_indexes()
        available_index_names = [idx.name for idx in indexes]
        print(f"Available Pinecone indexes: {available_index_names}")
        
        if index_name not in available_index_names:
            print(f"Warning: Pinecone index '{index_name}' not found.")
            print(f"Available indexes: {available_index_names}")
            print("Please check the index name matches exactly")
            return None
        
        # Connect to the index
        index = pc.Index(index_name)
        print(f"✅ Successfully connected to Pinecone index: {index_name}")
        
        # Test the connection
        stats = index.describe_index_stats()
        print(f"Index stats: {stats}")
        
        return index
    except Exception as e:
        print(f"Error initializing Pinecone: {e}")
        return None

# Initialize Pinecone index
pinecone_index = initialize_pinecone()

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI
    
    Args:
        text: Text to embed
    
    Returns:
        Embedding vector as list of floats
    """
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",  # This produces 1536 dimensions
            input=text
        )
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        raise

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split text into chunks for embedding
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    return chunks

def store_embeddings_in_pinecone(
    chunks: List[str],
    user_id: str,
    doc_id: str,
    filename: str
) -> None:
    """
    Generate embeddings for chunks and store them in Pinecone
    
    Args:
        chunks: List of text chunks
        user_id: User ID for namespace isolation
        doc_id: Document ID
        filename: Original filename
    """
    if not pinecone_index:
        raise Exception("Pinecone index not initialized")
    
    vectors = []
    
    for i, chunk in enumerate(chunks):
        try:
            # Generate embedding for the chunk
            embedding = generate_embedding(chunk)
            
            # Create vector with metadata
            vector = {
                "id": f"{doc_id}_chunk_{i}",
                "values": embedding,
                "metadata": {
                    "user_id": user_id,
                    "doc_id": doc_id,
                    "doc_name": filename,
                    "chunk_id": i,
                    "text": chunk[:1000],  # Store first 1000 chars for retrieval
                    "chunk_length": len(chunk)
                }
            }
            vectors.append(vector)
            
        except Exception as e:
            print(f"Error processing chunk {i}: {e}")
            continue
    
    if not vectors:
        raise Exception("No vectors generated from chunks")
    
    # Store vectors in Pinecone with user-specific namespace
    namespace = f"user_{user_id}"
    
    try:
        # Upsert vectors in batches (Pinecone has limits)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            pinecone_index.upsert(vectors=batch, namespace=namespace)
            
        print(f"Successfully stored {len(vectors)} vectors for document {doc_id}")
        
    except Exception as e:
        print(f"Error storing vectors in Pinecone: {e}")
        raise

def process_document_embeddings(
    user_id: str,
    doc_id: str,
    gcp_path: str,
    filename: str
) -> None:
    """
    Complete pipeline for processing document embeddings
    This function is called as a background task
    
    Args:
        user_id: User ID
        doc_id: Document ID
        gcp_path: Path to file in GCP Storage
        filename: Original filename
    """
    try:
        print(f"Starting embedding processing for document {doc_id}")
        
        # Update status to processing
        update_embedding_status(doc_id, 'processing')
        
        # Step 1: Download file from GCP
        print(f"Downloading file from GCP: {gcp_path}")
        file_content = download_from_gcp(gcp_path)
        
        # Step 2: Extract text from file
        print(f"Extracting text from {filename}")
        text = extract_text_from_file(file_content, filename)
        
        if not text.strip():
            raise Exception("No text extracted from file")
        
        print(f"Extracted {len(text)} characters of text")
        
        # Step 3: Chunk the text
        print("Chunking text...")
        chunks = chunk_text(text)
        print(f"Created {len(chunks)} chunks")
        
        if not chunks:
            raise Exception("No chunks created from text")
        
        # Step 4: Generate embeddings and store in Pinecone
        print("Generating and storing embeddings...")
        
        if pinecone_index:
            store_embeddings_in_pinecone(chunks, user_id, doc_id, filename)
        else:
            print("Pinecone not available - skipping embedding storage")
            print("File processed successfully but embeddings not stored")
        
        # Step 5: Update status to completed
        update_embedding_status(doc_id, 'completed')
        print(f"Successfully completed embedding processing for document {doc_id}")
        
    except Exception as e:
        print(f"Error processing embeddings for document {doc_id}: {e}")
        # Update status to failed
        update_embedding_status(doc_id, 'failed')
        raise

def delete_document_embeddings(user_id: str, doc_id: str) -> bool:
    """
    Delete all embeddings for a specific document
    
    Args:
        user_id: User ID
        doc_id: Document ID
    
    Returns:
        True if successful, False otherwise
    """
    if not pinecone_index:
        print("Pinecone index not initialized")
        return False
    
    try:
        namespace = f"user_{user_id}"
        
        # Query to find all vectors for this document
        query_response = pinecone_index.query(
            vector=[0.0] * 1536,  # Dummy vector for metadata filtering
            filter={"doc_id": doc_id},
            namespace=namespace,
            top_k=10000,  # Large number to get all matches
            include_metadata=False
        )
        
        # Extract vector IDs
        vector_ids = [match.id for match in query_response.matches]
        
        if vector_ids:
            # Delete vectors
            pinecone_index.delete(ids=vector_ids, namespace=namespace)
            print(f"Deleted {len(vector_ids)} vectors for document {doc_id}")
        
        return True
        
    except Exception as e:
        print(f"Error deleting embeddings for document {doc_id}: {e}")
        return False