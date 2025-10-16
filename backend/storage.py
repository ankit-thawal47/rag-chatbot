from google.cloud import storage
from google.oauth2 import service_account
import os
import json
from fastapi import HTTPException
from typing import Optional

def get_storage_client():
    """Get Google Cloud Storage client"""
    try:
        project_id = os.getenv('GCP_PROJECT_ID')
        credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if credentials_json and credentials_json.strip().startswith('{'):
            try:
                # Clean up the JSON string more thoroughly
                # Remove extra spaces that might have been introduced
                import re
                # Remove spaces that are breaking JSON structure
                credentials_json = re.sub(r'(?<=[a-zA-Z0-9])\s+(?=[a-zA-Z0-9])', '', credentials_json)
                # Fix common escape issues
                credentials_json = credentials_json.replace('\\n', '\n').replace('\\"', '"')
                
                credentials_dict = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(credentials_dict)
                client = storage.Client(project=project_id, credentials=credentials)
                print("✅ Successfully initialized GCS client with JSON credentials")
            except json.JSONDecodeError as json_err:
                print(f"JSON parsing error: {json_err}")
                print(f"Credentials string length: {len(credentials_json)}")
                print(f"First 200 chars: {credentials_json[:200]}")
                # Try one more time with aggressive cleaning
                try:
                    # Remove all extra whitespace within the JSON
                    cleaned = re.sub(r'\s+', ' ', credentials_json.strip())
                    cleaned = cleaned.replace('\\n', '\n').replace('\\"', '"')
                    credentials_dict = json.loads(cleaned)
                    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
                    client = storage.Client(project=project_id, credentials=credentials)
                    print("✅ Successfully initialized GCS client with cleaned JSON credentials")
                except Exception as cleanup_err:
                    print(f"Cleanup attempt failed: {cleanup_err}")
                    # Fallback to default credentials
                    client = storage.Client(project=project_id)
                    print("⚠️ Using default GCS credentials")
        else:
            # Use file path or default credentials
            client = storage.Client(project=project_id)
            print("⚠️ Using default GCS credentials (no JSON provided)")
        
        return client
    except Exception as e:
        print(f"Error initializing GCS client: {e}")
        print(f"Project ID: {project_id}")
        print(f"Credentials provided: {bool(credentials_json)}")
        raise HTTPException(status_code=500, detail="Failed to initialize cloud storage")

def upload_to_gcp(file_content: bytes, gcp_path: str) -> str:
    """
    Upload file to Google Cloud Storage
    
    Args:
        file_content: The file content as bytes
        gcp_path: The path in GCS bucket (user_id/doc_id/filename)
    
    Returns:
        The GCS URL of the uploaded file
    """
    try:
        client = get_storage_client()
        bucket_name = os.getenv('GCP_BUCKET_NAME')
        
        if not bucket_name:
            raise HTTPException(status_code=500, detail="GCS bucket name not configured")
        
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcp_path)
        
        # Upload the file content
        blob.upload_from_string(file_content)
        
        # Make the blob publicly readable (optional, for POC)
        # In production, you might want to keep files private and use signed URLs
        # blob.make_public()
        
        return f"gs://{bucket_name}/{gcp_path}"
        
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

def download_from_gcp(gcp_path: str) -> bytes:
    """
    Download file from Google Cloud Storage
    
    Args:
        gcp_path: The path in GCS bucket (user_id/doc_id/filename)
    
    Returns:
        The file content as bytes
    """
    try:
        client = get_storage_client()
        bucket_name = os.getenv('GCP_BUCKET_NAME')
        
        if not bucket_name:
            raise HTTPException(status_code=500, detail="GCS bucket name not configured")
        
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcp_path)
        
        # Download the file content
        file_content = blob.download_as_bytes()
        
        return file_content
        
    except Exception as e:
        print(f"Error downloading from GCS: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

def delete_from_gcp(gcp_path: str) -> bool:
    """
    Delete file from Google Cloud Storage
    
    Args:
        gcp_path: The path in GCS bucket (user_id/doc_id/filename)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_storage_client()
        bucket_name = os.getenv('GCP_BUCKET_NAME')
        
        if not bucket_name:
            print("GCS bucket name not configured")
            return False
        
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcp_path)
        
        # Delete the blob
        blob.delete()
        
        return True
        
    except Exception as e:
        print(f"Error deleting from GCS: {e}")
        return False

def file_exists_in_gcp(gcp_path: str) -> bool:
    """
    Check if file exists in Google Cloud Storage
    
    Args:
        gcp_path: The path in GCS bucket (user_id/doc_id/filename)
    
    Returns:
        True if file exists, False otherwise
    """
    try:
        client = get_storage_client()
        bucket_name = os.getenv('GCP_BUCKET_NAME')
        
        if not bucket_name:
            return False
        
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcp_path)
        
        return blob.exists()
        
    except Exception as e:
        print(f"Error checking file existence in GCS: {e}")
        return False