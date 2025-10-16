import jwt
import firebase_admin
from firebase_admin import credentials, auth
from datetime import datetime, timedelta
from fastapi import HTTPException
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Firebase Admin SDK initialization
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        # Use individual Firebase environment variables
        private_key = os.getenv('FIREBASE_PRIVATE_KEY')
        project_id = os.getenv('FIREBASE_PROJECT_ID')
        client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
        
        if private_key and project_id and client_email:
            firebase_config = {
                "type": "service_account",
                "project_id": project_id,
                "private_key": private_key.replace('\\n', '\n'),
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
        else:
            raise Exception("Firebase credentials not found. Please set FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, and FIREBASE_CLIENT_EMAIL environment variables.")

# Initialize Firebase on module import
initialize_firebase()

def verify_firebase_token(firebase_token: str) -> Dict[str, Any]:
    """
    Verify Firebase ID token and return decoded claims
    """
    try:
        decoded_token = auth.verify_id_token(firebase_token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {str(e)}")

def create_jwt_token(user_id: str, email: str) -> str:
    """
    Create a JWT token for the authenticated user
    """
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 24))),
        "iat": datetime.utcnow()
    }
    
    secret_key = os.getenv('JWT_SECRET_KEY')
    algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
    
    if not secret_key:
        raise HTTPException(status_code=500, detail="JWT secret key not configured")
    
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and return payload
    """
    try:
        secret_key = os.getenv('JWT_SECRET_KEY')
        algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
        
        if not secret_key:
            raise HTTPException(status_code=500, detail="JWT secret key not configured")
        
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")