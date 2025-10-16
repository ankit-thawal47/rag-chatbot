# Quick Setup Checklist

## 🔧 External Services (Do First)

### Firebase
- [ ] Create Firebase project
- [ ] Enable Google Authentication  
- [ ] Add localhost to authorized domains
- [ ] Get web app config (for frontend)
- [ ] Download service account JSON (for backend)

### Google Cloud Storage
- [ ] Create GCP project
- [ ] Enable Cloud Storage API
- [ ] Create storage bucket (unique name)
- [ ] Create service account with Storage Admin role
- [ ] Download service account JSON key

### Supabase
- [ ] Create Supabase project
- [ ] Run `database/schema.sql` in SQL Editor
- [ ] Get project URL and anon key

### Pinecone
- [ ] Create account
- [ ] Create index: `rag-documents`, 1536 dimensions, cosine metric
- [ ] Get API key and environment

### OpenAI
- [ ] Create account and add payment method
- [ ] Generate API key

## 🏠 Local Development

- [ ] Run `./setup.sh`
- [ ] Fill `backend/.env` with all service credentials
- [ ] Fill `frontend/.env.local` with Firebase config
- [ ] Start backend: `cd backend && source venv/bin/activate && uvicorn main:app --reload`
- [ ] Start frontend: `cd frontend && npm run dev`
- [ ] Test at `http://localhost:3000`

## 🚀 Production Deployment

### Railway (Backend)
- [ ] Create Railway account
- [ ] Deploy from GitHub repo
- [ ] Set root directory: `backend`
- [ ] Add ALL environment variables
- [ ] Note Railway URL

### Vercel (Frontend)
- [ ] Install Vercel CLI: `npm install -g vercel`
- [ ] Deploy: `cd frontend && vercel --prod`
- [ ] Add environment variables in Vercel dashboard
- [ ] Note Vercel URL

### Final Configuration
- [ ] Update CORS in `backend/main.py` with Vercel URL
- [ ] Add Vercel domain to Firebase authorized domains
- [ ] Test production flow end-to-end

## 🧪 Testing Checklist

- [ ] Google login works
- [ ] File upload (PDF/DOCX/PPTX) succeeds
- [ ] Document status shows "completed"
- [ ] Chat responds with relevant answers
- [ ] Source citations appear correctly
- [ ] User can logout and login again
- [ ] Different users see only their own documents

## 🔍 Troubleshooting

**If something doesn't work:**
1. Check browser console for frontend errors
2. Check Railway/backend logs for API errors  
3. Verify all environment variables are set
4. Test individual service connections
5. Review `STEP_BY_STEP_SETUP.md` for detailed instructions

## 📱 Quick Commands

```bash
# Local development
./setup.sh
cd backend && source venv/bin/activate && uvicorn main:app --reload
cd frontend && npm run dev

# Test backend health
curl http://localhost:8000/

# Deploy to production
cd frontend && vercel --prod

# Test production
curl https://your-service.railway.app/
```

## 🎯 Environment Variables Summary

**Backend (.env):**
```
FIREBASE_PROJECT_ID=
FIREBASE_PRIVATE_KEY=
FIREBASE_CLIENT_EMAIL=
JWT_SECRET_KEY=
GCP_PROJECT_ID=
GCP_BUCKET_NAME=
GOOGLE_APPLICATION_CREDENTIALS=
SUPABASE_URL=
SUPABASE_KEY=
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=
PINECONE_INDEX_NAME=
OPENAI_API_KEY=
```

**Frontend (.env.local):**
```
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_API_URL=
```