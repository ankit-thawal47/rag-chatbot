# Complete Step-by-Step Setup Guide

## 🎯 Overview

This guide will help you:
1. **Set up all external services** (Firebase, GCP, Supabase, Pinecone, OpenAI)
2. **Run locally** for development and testing
3. **Deploy to production** (Vercel + Railway)

## 📋 Prerequisites

Install these on your machine:
- **Node.js 18+**: [Download here](https://nodejs.org/)
- **Python 3.9+**: [Download here](https://python.org/)
- **Git**: [Download here](https://git-scm.com/)

## 🔧 Part 1: External Services Setup

### 1.1 Firebase Setup (Authentication)

#### Step 1: Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Create a project" or "Add project"
3. Enter project name: `rag-document-system` (or your choice)
4. Disable Google Analytics (not needed for this POC)
5. Click "Create project"

#### Step 2: Enable Google Authentication
1. In Firebase Console, go to **Authentication** → **Sign-in method**
2. Click on **Google** provider
3. Toggle "Enable"
4. Set project public-facing name: "RAG Document System"
5. Choose your support email
6. Click "Save"

#### Step 3: Add Authorized Domains
1. Still in **Authentication** → **Sign-in method**
2. Scroll down to "Authorized domains"
3. Click "Add domain"
4. Add: `localhost` (for local development)
5. We'll add Vercel domain later

#### Step 4: Get Web App Config
1. Go to **Project Settings** (gear icon) → **General**
2. Scroll down to "Your apps"
3. Click "Web app" icon (`</>`)
4. Register app name: "rag-frontend"
5. Don't check "Firebase Hosting"
6. Click "Register app"
7. **Copy the config object** - save this for later:
```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  // ... other fields
};
```

#### Step 5: Generate Service Account (for Backend)
1. Go to **Project Settings** → **Service accounts**
2. Click "Generate new private key"
3. Click "Generate key" - this downloads a JSON file
4. **Save this file securely** - you'll need it for backend

### 1.2 Google Cloud Storage Setup

#### Step 1: Create GCP Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Project name: `rag-documents-storage` (or your choice)
4. Click "Create"

#### Step 2: Enable Cloud Storage API
1. In GCP Console, go to **APIs & Services** → **Library**
2. Search for "Cloud Storage API"
3. Click on it and press "Enable"

#### Step 3: Create Storage Bucket
1. Go to **Cloud Storage** → **Buckets**
2. Click "Create bucket"
3. Bucket name: `your-unique-bucket-name` (must be globally unique)
4. Location: Choose region close to you
5. Storage class: Standard
6. Access control: Fine-grained
7. Click "Create"

#### Step 4: Create Service Account
1. Go to **IAM & Admin** → **Service accounts**
2. Click "Create service account"
3. Name: `rag-storage-service`
4. Description: "RAG document storage access"
5. Click "Create and continue"
6. Role: "Storage Admin"
7. Click "Continue" → "Done"

#### Step 5: Generate Service Account Key
1. Click on your newly created service account
2. Go to **Keys** tab
3. Click "Add key" → "Create new key"
4. Choose "JSON"
5. Click "Create" - this downloads a JSON file
6. **Save this file securely**

### 1.3 Supabase Setup (Database)

#### Step 1: Create Supabase Project
1. Go to [Supabase](https://supabase.com)
2. Sign up/login
3. Click "New project"
4. Organization: Create new or use existing
5. Project name: `rag-documents-db`
6. Database password: Generate strong password and **save it**
7. Region: Choose closest to you
8. Click "Create new project"
9. Wait 2-3 minutes for setup

#### Step 2: Execute Database Schema
1. In Supabase dashboard, go to **SQL Editor**
2. Open the file `/Users/ankit/workspace/filtr2/database/schema.sql`
3. Copy ALL the contents
4. Paste into Supabase SQL Editor
5. Click "Run" (green play button)
6. You should see "Success. No rows returned" message

#### Step 3: Verify Tables Created
1. Go to **Table Editor**
2. You should see two tables: `users` and `documents`
3. Click on each to verify structure

#### Step 4: Get Connection Details
1. Go to **Settings** → **API**
2. Copy and save these values:
   - **URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### 1.4 Pinecone Setup (Vector Database)

#### Step 1: Create Pinecone Account
1. Go to [Pinecone](https://pinecone.io)
2. Sign up for free account
3. Verify your email

#### Step 2: Create Index
1. In Pinecone dashboard, click "Create Index"
2. Index name: `rag-documents`
3. Dimensions: `1536` (for OpenAI text-embedding-3-small)
4. Metric: `cosine`
5. Pod type: `s1.x1` (free tier)
6. Click "Create Index"
7. Wait for index to be ready (shows "Ready")

#### Step 3: Get API Key
1. Click on your username (top right) → "API Keys"
2. Copy your API key
3. Note your environment (e.g., `us-east1-gcp`)

### 1.5 OpenAI Setup

#### Step 1: Create OpenAI Account
1. Go to [OpenAI](https://platform.openai.com)
2. Sign up/login
3. Add payment method (required for API access)

#### Step 2: Generate API Key
1. Go to **API keys** section
2. Click "Create new secret key"
3. Name: `rag-document-system`
4. Copy and save the key (starts with `sk-`)

## 🏠 Part 2: Local Development Setup

### 2.1 Prepare Project

#### Step 1: Navigate to Project
```bash
cd /Users/ankit/workspace/filtr2
```

#### Step 2: Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Check Python and Node.js
- Create virtual environment for backend
- Install Python dependencies
- Install Node.js dependencies
- Create environment files from templates

### 2.2 Configure Backend Environment

#### Step 1: Edit Backend Environment
```bash
cd backend
nano .env  # or use your preferred editor
```

#### Step 2: Fill in ALL values from services you set up:


**Important Notes:**
- For `FIREBASE_PRIVATE_KEY`: Copy from service account JSON, replace `\n` with actual newlines
- For `GOOGLE_APPLICATION_CREDENTIALS`: Copy the entire JSON object as a string
- For `JWT_SECRET_KEY`: Generate a random string (64+ characters)

### 2.3 Configure Frontend Environment

#### Step 1: Edit Frontend Environment
```bash
cd ../frontend
nano .env.local  # or use your preferred editor
```

#### Step 2: Fill in values from Firebase config:
```bash
```

### 2.4 Test Local Setup

#### Step 1: Start Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

#### Step 2: Test Backend Health
Open new terminal:
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "RAG Document Management API is running",
  "version": "1.0.0",
  "status": "healthy"
}
```

#### Step 3: Start Frontend
```bash
cd frontend
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

#### Step 4: Test Complete Flow
1. Open browser: `http://localhost:3000`
2. Click "Sign in with Google"
3. Complete Google OAuth flow
4. You should be redirected to upload page
5. Try uploading a small PDF file
6. Wait for processing to complete
7. Go to Chat page and ask a question

### 2.5 Troubleshooting Local Issues

#### Common Problems:

**Backend won't start:**
```bash
# Check if all environment variables are set
python -c "import os; print([k for k in ['FIREBASE_PROJECT_ID', 'OPENAI_API_KEY', 'PINECONE_API_KEY', 'SUPABASE_URL'] if not os.getenv(k)])"
```

**Firebase auth fails:**
```bash
# Test Firebase connection
python -c "from auth import verify_firebase_token; print('Firebase configured correctly')"
```

**File upload fails:**
```bash
# Test GCP Storage
python -c "from storage import get_storage_client; client = get_storage_client(); print('GCP Storage working')"
```

**Database connection fails:**
```bash
# Test Supabase
python -c "from database import supabase_client; print(supabase_client.table('users').select('*').limit(1).execute())"
```

## 🚀 Part 3: Production Deployment

### 3.1 Backend Deployment (Railway)

#### Step 1: Create Railway Account
1. Go to [Railway](https://railway.app)
2. Sign up with GitHub
3. Connect your GitHub account

#### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect to your repository
4. Select "Deploy Now"

#### Step 3: Configure Service
1. In Railway dashboard, click on your service
2. Go to **Settings** tab
3. Set **Root Directory**: `backend`
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Step 4: Add Environment Variables
1. Go to **Variables** tab
2. Add ALL backend environment variables:

#### Step 5: Deploy
1. Click "Deploy"
2. Wait for deployment (5-10 minutes)
3. Note your Railway URL: `https://your-service.railway.app`

#### Step 6: Test Backend
```bash
curl https://your-service.railway.app/
```

### 3.2 Frontend Deployment (Vercel)

#### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

#### Step 2: Login to Vercel
```bash
vercel login
```

#### Step 3: Deploy Frontend
```bash
cd frontend
vercel --prod
```

During deployment, Vercel will ask:
- **Set up and deploy?** → Yes
- **Which scope?** → Your account
- **Link to existing project?** → No
- **Project name?** → `rag-frontend` (or your choice)
- **Directory?** → `./` (current directory)

#### Step 4: Add Environment Variables
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your project
3. Go to **Settings** → **Environment Variables**
4. Add these variables:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSy...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_API_URL=https://your-service.railway.app
```

#### Step 5: Redeploy with Environment Variables
```bash
vercel --prod
```

#### Step 6: Note Your URLs
- **Frontend**: `https://your-frontend.vercel.app`
- **Backend**: `https://your-service.railway.app`

### 3.3 Update CORS and Firebase

#### Step 1: Update Backend CORS
1. Edit `backend/main.py`
2. Update CORS origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app"
    ],
    # ... rest of config
)
```

#### Step 2: Redeploy Backend
```bash
git add .
git commit -m "Update CORS for production"
git push origin main
```
Railway will auto-deploy the changes.

#### Step 3: Update Firebase Authorized Domains
1. Go to Firebase Console → Authentication → Settings
2. Scroll to "Authorized domains"
3. Click "Add domain"
4. Add: `your-frontend.vercel.app`
5. Save

### 3.4 Final Testing

#### Step 1: Test Production Flow
1. Visit your Vercel URL: `https://your-frontend.vercel.app`
2. Sign in with Google
3. Upload a test document
4. Wait for processing
5. Chat with your document
6. Verify source citations work

#### Step 2: Monitor Logs
- **Railway**: Check deployment logs in Railway dashboard
- **Vercel**: Check function logs in Vercel dashboard
- **Supabase**: Monitor database activity

## 🔍 Part 4: Verification & Troubleshooting

### 4.1 Verification Checklist

- [ ] Local development working
- [ ] Google OAuth login works
- [ ] File upload succeeds
- [ ] Document processing completes
- [ ] Chat responses include sources
- [ ] Backend deployed to Railway
- [ ] Frontend deployed to Vercel
- [ ] Production login works
- [ ] Production file upload works
- [ ] Production chat works

### 4.2 Common Production Issues

#### CORS Errors
```bash
# Check browser console for CORS errors
# Update backend CORS settings
# Ensure Railway backend URL is correct in Vercel env vars
```

#### Authentication Failures
```bash
# Check Firebase authorized domains
# Verify environment variables in Vercel
# Check browser network tab for 401 errors
```

#### File Upload Issues
```bash
# Check Railway logs for GCP errors
# Verify GCP service account permissions
# Check file size limits
```

#### Embedding Processing Fails
```bash
# Check Railway logs for OpenAI/Pinecone errors
# Verify API keys and quotas
# Check background task execution
```

### 4.3 Monitoring & Maintenance

#### Set Up Monitoring
1. **Railway**: Enable logging and metrics
2. **Vercel**: Set up analytics
3. **Supabase**: Monitor database usage
4. **OpenAI**: Track API usage and costs

#### Regular Maintenance
- Monitor API costs (OpenAI, Pinecone)
- Check storage usage (GCP)
- Review error logs
- Update dependencies

## 🎉 Success!

You now have a fully functional RAG Document Management System running in production!

**Your URLs:**
- **Production App**: `https://your-frontend.vercel.app`
- **API Docs**: `https://your-service.railway.app/docs`

**Next Steps:**
- Share with users for testing
- Monitor usage and performance
- Consider scaling optimizations
- Add additional features as needed

## 🆘 Getting Help

If you encounter issues:
1. Check browser console for frontend errors
2. Check Railway logs for backend errors
3. Verify all environment variables are set correctly
4. Test individual service connections
5. Review this guide step-by-step

The system is now ready for demonstration and real-world usage! 🚀