import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || 'dummy-api-key',
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || 'dummy.firebaseapp.com',
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || 'dummy-project',
};

// Initialize Firebase only if we have valid config
let app;
let auth;

try {
  if (process.env.NEXT_PUBLIC_FIREBASE_API_KEY && 
      process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN && 
      process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID) {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
  } else {
    console.warn('Firebase environment variables not set. Authentication will not work.');
    // Create dummy app for build time
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
  }
} catch (error) {
  console.error('Firebase initialization error:', error);
  // Fallback for build time
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
}

export { auth };

// Google Auth Provider
export const googleProvider = new GoogleAuthProvider();

// Helper function to sign in with Google
export const signInWithGoogle = async () => {
  try {
    if (!process.env.NEXT_PUBLIC_FIREBASE_API_KEY) {
      throw new Error('Firebase not configured. Please set environment variables.');
    }
    const result = await signInWithPopup(auth, googleProvider);
    const idToken = await result.user.getIdToken();
    return { user: result.user, idToken };
  } catch (error) {
    console.error("Error signing in with Google:", error);
    throw error;
  }
};

// Helper function to sign out
export const signOutUser = async () => {
  try {
    if (!process.env.NEXT_PUBLIC_FIREBASE_API_KEY) {
      throw new Error('Firebase not configured. Please set environment variables.');
    }
    await signOut(auth);
  } catch (error) {
    console.error("Error signing out:", error);
    throw error;
  }
};