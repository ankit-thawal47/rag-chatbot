# Deployment Guide

Complete step-by-step guide to deploy the RAG Document Management System.

## 🚀 Overview

This guide covers deploying:
- **Backend**: FastAPI on Render
- **Frontend**: Next.js on Vercel
- **Database**: Supabase (already hosted)
- **Services**: Firebase, GCP, Pinecone, OpenAI (external)

## 📋 Pre-Deployment Checklist

### 1. External Services Setup

#### Firebase Authentication
```bash
1. Go to https://console.firebase.google.com
2. Create new project or use existing
3. Enable Authentication > Sign-in method > Google
4. Add authorized domains (your Vercel domain)
5. Download service account JSON for backend
6. Copy web config for frontend
```

#### Google Cloud Storage
```bash
1. Create GCP project at https://console.cloud.google.com
2. Enable Cloud Storage API
3. Create storage bucket (globally unique name)
4. Create service account with "Storage Admin" role
5. Download JSON key file
```

#### Supabase Database
```bash
1. Create project at https://supabase.com
2. Execute database/schema.sql in SQL Editor
3. Note project URL and anon key
```

#### Pinecone Vector Database
```bash
1. Sign up at https://pinecone.io
2. Create index:
   - Name: rag-documents
   - Dimensions: 1536 (for text-embedding-3-small)
   - Metric: cosine
3. Note API key and environment
```

#### OpenAI API
```bash
1. Get API key from https://platform.openai.com
2. Add payment method
3. Note API key
```

### 2. Environment Variables Preparation

Create a secure document with all these values:

```bash
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com

# JWT
JWT_SECRET_KEY=your-strong-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# GCP
GCP_PROJECT_ID=your-gcp-project
GCP_BUCKET_NAME=your-unique-bucket-name
GOOGLE_APPLICATION_CREDENTIALS={"type":"service_account",...} # Full JSON

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Pinecone
PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-east1-gcp
PINECONE_INDEX_NAME=rag-documents

# OpenAI
OPENAI_API_KEY=sk-...

# Frontend (Firebase config)
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSy...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
```

## 🖥️ Backend Deployment (Render)

### Step 1: Prepare Repository
```bash
# Ensure your code is pushed to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create Render Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub account and repository
4. Configure:
   - **Name**: `rag-backend` (or your choice)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables
In Render dashboard, go to Environment tab and add ALL backend variables:

⚠️ **Important**: For `FIREBASE_PRIVATE_KEY`, replace `\n` with actual newlines:
```
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----
```

⚠️ **Important**: For `GOOGLE_APPLICATION_CREDENTIALS`, paste the entire JSON object as a string.

### Step 4: Deploy
1. Click **Create Web Service**
2. Wait for build to complete (5-10 minutes)
3. Note your service URL: `https://your-service.onrender.com`

### Step 5: Test Backend
```bash
# Test health endpoint
curl https://your-service.onrender.com/

# Should return: {"message": "RAG Document Management API is running", ...}
```

## 🌐 Frontend Deployment (Vercel)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Deploy from Frontend Directory
```bash
cd frontend
vercel --prod
```

### Step 4: Configure Environment Variables
During deployment or in Vercel dashboard, add:

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSy...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### Step 5: Update CORS in Backend
Add your Vercel URL to the CORS configuration in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-vercel-app.vercel.app",  # Add this line
        "https://*.vercel.app"
    ],
    # ... rest of config
)
```

Redeploy backend after this change.

## 🔄 Post-Deployment Configuration

### 1. Update Firebase Authorized Domains
1. Go to Firebase Console → Authentication → Settings
2. Add your Vercel domain to "Authorized domains"
3. Example: `your-app.vercel.app`

### 2. Test End-to-End Flow
1. Visit your Vercel URL
2. Login with Google
3. Upload a small PDF
4. Wait for processing
5. Ask questions in chat
6. Verify source citations work

### 3. Set Up Monitoring (Optional)
- Enable Render metrics and logs
- Set up Vercel analytics
- Monitor Supabase usage
- Track OpenAI API usage

## 🔧 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs in Render dashboard
# Common issues:
- Missing environment variables
- Invalid JSON in GOOGLE_APPLICATION_CREDENTIALS
- Wrong Firebase private key format
```

#### CORS Errors
```bash
# Add your frontend URL to backend CORS settings
# Redeploy backend after changes
```

#### Firebase Auth Fails
```bash
# Check Firebase project settings
# Verify authorized domains include your Vercel URL
# Check API keys match
```

#### File Upload Fails
```bash
# Verify GCP service account has Storage Admin role
# Check bucket name and permissions
# Verify JSON credentials format
```

#### Embeddings Not Processing
```bash
# Check OpenAI API key and billing
# Verify Pinecone index exists and matches config
# Check background task logs in Render
```

### Debug Commands

```bash
# Test individual services
curl https://your-backend.onrender.com/
curl -X POST https://your-backend.onrender.com/auth \
  -H "Content-Type: application/json" \
  -d '{"firebase_token": "test"}'

# Check Render logs
# Go to Render Dashboard → Your Service → Logs

# Check Vercel logs  
vercel logs https://your-app.vercel.app
```

## 📊 Performance Optimization

### Backend (Render)
- Upgrade to Hobby plan for better performance
- Enable persistent disk for caching
- Consider using Redis for session storage

### Frontend (Vercel)
- Enable Vercel Analytics
- Optimize images and assets
- Use Vercel Edge Functions for better performance

### Database (Supabase)
- Monitor query performance
- Add indexes for frequently queried columns
- Consider upgrading plan for higher limits

## 🔒 Security Best Practices

### Environment Variables
- Never commit secrets to version control
- Use different keys for staging/production
- Rotate keys regularly

### API Security
- Enable rate limiting in production
- Add request validation middleware
- Monitor for suspicious activity

### Database Security
- Regularly audit RLS policies
- Monitor database access logs
- Keep dependencies updated

## 📈 Scaling Considerations

### Current Limitations (POC)
- Background tasks run on single instance
- No caching layer
- Basic error handling

### Production Improvements
1. **Replace BackgroundTasks with Pub/Sub**:
   ```bash
   # Google Cloud Pub/Sub for async processing
   # Separate worker instances
   # Better error handling and retries
   ```

2. **Add Redis Caching**:
   ```bash
   # Cache embeddings and frequent queries
   # Session storage
   # Rate limiting counters
   ```

3. **Implement Auto-Scaling**:
   ```bash
   # Horizontal pod autoscaling
   # Database read replicas
   # CDN for static assets
   ```

## 📝 Maintenance

### Regular Tasks
- Monitor API usage and costs
- Update dependencies
- Review logs for errors
- Backup database periodically

### Monthly Reviews
- Check service usage and optimize costs
- Review security practices
- Update documentation
- Performance analysis

---

## ✅ Deployment Checklist

- [ ] All external services configured
- [ ] Environment variables documented securely
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] CORS configured correctly
- [ ] Firebase authorized domains updated
- [ ] End-to-end flow tested
- [ ] Error monitoring set up
- [ ] Documentation updated with live URLs

**🎉 Your RAG Document Management System is now live!**