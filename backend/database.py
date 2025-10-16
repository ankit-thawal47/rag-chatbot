from supabase import create_client, Client
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

# Initialize Supabase client
def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase configuration missing")
    
    return create_client(url, key)

supabase_client = get_supabase_client()

def save_document_metadata(
    doc_id: str,
    user_id: str,
    filename: str,
    file_type: str,
    file_size: int,
    gcp_path: str
) -> None:
    """
    Save document metadata to Supabase
    """
    try:
        # Set user context for RLS before inserting document
        try:
            supabase_client.rpc('set_user_context', {'p_user_id': user_id}).execute()
        except:
            pass  # Continue even if RLS context setting fails
        
        document_data = {
            'doc_id': doc_id,
            'user_id': user_id,
            'filename': filename,
            'file_type': file_type,
            'file_size': file_size,
            'gcp_path': gcp_path,
            'embedding_status': 'pending',
            'uploaded_at': datetime.now().isoformat()
        }
        
        result = supabase_client.table('documents').insert(document_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save document metadata")
            
    except Exception as e:
        print(f"Error saving document metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def get_user_documents(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all documents for a specific user
    """
    try:
        # Set user context for RLS
        supabase_client.rpc('set_user_context', {'p_user_id': user_id}).execute()
        
        result = supabase_client.table('documents') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('uploaded_at', desc=True) \
            .execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        print(f"Error fetching user documents: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def update_embedding_status(doc_id: str, status: str, processed_at: Optional[str] = None) -> None:
    """
    Update the embedding status of a document
    """
    try:
        update_data = {'embedding_status': status}
        
        if processed_at:
            update_data['processed_at'] = processed_at
        elif status == 'completed':
            update_data['processed_at'] = datetime.now().isoformat()
        
        result = supabase_client.table('documents') \
            .update(update_data) \
            .eq('doc_id', doc_id) \
            .execute()
        
        if not result.data:
            print(f"Warning: No document found with doc_id {doc_id}")
            
    except Exception as e:
        print(f"Error updating embedding status: {e}")

def save_or_update_user(user_id: str, email: str) -> None:
    """
    Save or update user information
    """
    try:
        # For user creation, we need to bypass RLS temporarily
        # Use a direct query without RLS
        user_data = {
            'user_id': user_id,
            'email': email,
            'last_login': datetime.now().isoformat()
        }
        
        # Use upsert which should work for both insert and update
        result = supabase_client.table('users').upsert(user_data).execute()
        
        # If upsert failed, try with RLS context
        if not result.data:
            try:
                # Set user context for RLS and retry
                supabase_client.rpc('set_user_context', {'p_user_id': user_id}).execute()
                result = supabase_client.table('users').upsert(user_data).execute()
            except:
                pass  # Continue with the original error
        
        print(f"User saved successfully: {user_id}")
            
    except Exception as e:
        print(f"Error saving user data: {e}")
        # Don't raise an exception for user save errors during auth
        # The auth can still proceed even if user save fails
        print(f"Continuing authentication despite user save error")

def get_document_by_id(doc_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific document by ID (with user validation)
    """
    try:
        result = supabase_client.table('documents') \
            .select('*') \
            .eq('doc_id', doc_id) \
            .eq('user_id', user_id) \
            .execute()
        
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"Error fetching document: {e}")
        return None