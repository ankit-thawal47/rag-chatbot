# 🚀 RAG Document Management System - Deployment Guide

## 📋 Overview
This guide covers deploying the RAG system to:
- **Frontend**: Vercel (Next.js)
- **Backend**: Railway (FastAPI/Python)

## 🗂️ Repository Structure
```
filtr2/
├── frontend/          # Next.js application (deploy to Vercel)
├── backend/           # FastAPI application (deploy to Railway)
├── database/          # SQL scripts for Supabase
└── DEPLOYMENT_GUIDE.md
```

## 🔧 Prerequisites
Before deployment, ensure you have:
- [ ] GitHub account
- [ ] Vercel account (connected to GitHub)
- [ ] Railway account (connected to GitHub)
- [ ] All external services configured:
  - [ ] Firebase project with authentication
  - [ ] Google Cloud Storage bucket with service account
  - [ ] Supabase database with tables and RLS policies
  - [ ] Pinecone index (1536 dimensions, cosine metric)
  - [ ] OpenAI API key

## 📝 STEP-BY-STEP DEPLOYMENT

### **STEP 1: Prepare and Push to GitHub**

#### 1.1 Clean up sensitive files
```bash
# Remove sensitive files and temp files
rm -rf backend/venv/
rm -f backend/.env
rm -f frontend/.env.local
rm -f backend/debug_*.py
rm -f backend/test_*.py
rm -f backend/fix_*.py
rm -f backend/minimal_*.py
```

#### 1.2 Git setup and push
```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: RAG Document Management System

- FastAPI backend with Firebase auth, GCP Storage, Supabase, Pinecone
- Next.js frontend with Firebase OAuth
- Complete user isolation and security
- Background document processing and embedding generation"

# Create GitHub repository and push
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/rag-document-system.git
git branch -M main
git push -u origin main
```

### **STEP 2: Deploy Backend to Railway**

#### 2.1 Railway Setup
1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `rag-document-system` repository
5. Choose "Deploy from a folder" → Select `backend/`

#### 2.2 Configure Environment Variables
In Railway dashboard, add these environment variables:

**Firebase:**
```
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-key\n-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com
```

**JWT:**
```
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=48
```

**Google Cloud Storage:**
```
GCP_PROJECT_ID=your-gcp-project
GCP_BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS='{"type":"service_account",...}'
```

**Supabase:**
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

**Pinecone:**
```
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east1-gcp
PINECONE_INDEX_NAME=rag-documents
```

**OpenAI:**
```
OPENAI_API_KEY=your-openai-api-key
```

#### 2.3 Deploy
- Railway will automatically deploy
- Note your Railway backend URL: `https://your-app.railway.app`

### **STEP 3: Deploy Frontend to Vercel**

#### 3.1 Vercel Setup
1. Go to [Vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "New Project"
4. Import your `rag-document-system` repository
5. Set **Root Directory** to `frontend/`

#### 3.2 Configure Environment Variables
In Vercel dashboard, add these environment variables:

```
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-firebase-project
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your-measurement-id
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

#### 3.3 Deploy
- Vercel will automatically build and deploy
- Note your Vercel URL: `https://your-app.vercel.app`

### **STEP 4: Update CORS and Authentication**

#### 4.1 Update Backend CORS
Update `backend/main.py` CORS settings:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://your-app.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app"
    ],
    # ... rest of CORS config
)
```

#### 4.2 Update Firebase Auth Domain
Add your Vercel domain to Firebase:
1. Go to Firebase Console → Authentication → Settings
2. Add `your-app.vercel.app` to authorized domains

### **STEP 5: Test Deployment**

#### 5.1 Test Backend
```bash
curl https://your-backend.railway.app/
# Should return: {"message": "RAG Document Management API is running"}
```

#### 5.2 Test Frontend
1. Visit `https://your-app.vercel.app`
2. Test Google login
3. Upload a test document
4. Check embedding generation in Railway logs

## 🔍 Troubleshooting

### Common Issues:

**1. CORS Errors**
- Ensure your Vercel URL is in the CORS allow_origins list
- Push updated backend code to trigger Railway redeploy

**2. Environment Variables**
- Double-check all environment variables are set correctly
- Ensure no trailing spaces or quotes in Railway/Vercel dashboards

**3. Firebase Auth**
- Add your Vercel domain to Firebase authorized domains
- Check Firebase private key formatting (newlines as `\n`)

**4. Database Connection**
- Verify Supabase RLS policies allow user creation
- Check that all SQL scripts were executed

**5. File Upload Issues**
- Verify GCS service account has Storage Object Admin role
- Check bucket permissions and CORS settings

## 📊 Monitoring

### Railway (Backend)
- Monitor logs in Railway dashboard
- Check CPU/Memory usage
- Set up alerts for errors

### Vercel (Frontend)
- Monitor function logs in Vercel dashboard
- Check build logs for any issues
- Monitor performance metrics

## 🔄 Updates and Redeployment

### Backend Updates:
```bash
git add backend/
git commit -m "Update backend: description of changes"
git push origin main
# Railway auto-deploys on push
```

### Frontend Updates:
```bash
git add frontend/
git commit -m "Update frontend: description of changes"  
git push origin main
# Vercel auto-deploys on push
```

## 🔐 Security Checklist

- [ ] All `.env` files are in `.gitignore`
- [ ] No secrets committed to git
- [ ] Firebase rules properly configured
- [ ] Supabase RLS policies active
- [ ] GCS bucket permissions minimal
- [ ] CORS properly configured
- [ ] HTTPS enabled on all services

## 📞 Support

If you encounter issues:
1. Check Railway/Vercel logs
2. Verify all environment variables
3. Test external services (Firebase, Supabase, etc.)
4. Check network connectivity and CORS