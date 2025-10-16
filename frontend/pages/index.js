import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { signInWithGoogle } from '../lib/firebase';
import { authenticateUser } from '../lib/api';

export default function Login() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Check if user is already logged in
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      router.push('/upload');
    }
  }, [router]);

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Step 1: Sign in with Google via Firebase
      const { user, idToken } = await signInWithGoogle();
      
      // Step 2: Authenticate with our backend
      const { access_token, user_id } = await authenticateUser(idToken);
      
      // Step 3: Store tokens and user info
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user_id', user_id);
      localStorage.setItem('user_email', user.email);
      localStorage.setItem('user_name', user.displayName || user.email);
      
      // Step 4: Redirect to upload page
      router.push('/upload');
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to login. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              RAG Document System
            </h1>
            <p className="text-gray-600">
              Upload documents and chat with them using AI
            </p>
          </div>
          
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-3 px-4 rounded-lg transition duration-200 flex items-center justify-center"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Signing in...
              </div>
            ) : (
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Sign in with Google
              </div>
            )}
          </button>
          
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500">
              Secure authentication powered by Firebase
            </p>
          </div>
        </div>
        
        <div className="mt-8 text-center text-sm text-gray-600">
          <p>✅ Upload PDF, DOCX, PPTX files</p>
          <p>✅ AI-powered document search</p>
          <p>✅ Secure user isolation</p>
        </div>
      </div>
    </div>
  );
}