import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { signOutUser } from '../lib/firebase';

export default function Navbar() {
  const router = useRouter();
  const [userEmail, setUserEmail] = useState('');
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const email = localStorage.getItem('user_email');
    const name = localStorage.getItem('user_name');
    setUserEmail(email || '');
    setUserName(name || email || '');
  }, []);

  const handleLogout = async () => {
    try {
      await signOutUser();
      localStorage.clear();
      router.push('/');
    } catch (error) {
      console.error('Logout error:', error);
      // Clear localStorage anyway
      localStorage.clear();
      router.push('/');
    }
  };

  const isUploadPage = router.pathname === '/upload';
  const isChatPage = router.pathname === '/chat';

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo/Title */}
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-gray-900">RAG Documents</h1>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center space-x-1">
            <button
              onClick={() => router.push('/upload')}
              className={`px-4 py-2 rounded-lg font-medium transition duration-200 ${
                isUploadPage
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              📄 Upload
            </button>
            <button
              onClick={() => router.push('/chat')}
              className={`px-4 py-2 rounded-lg font-medium transition duration-200 ${
                isChatPage
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              💬 Chat
            </button>
          </div>

          {/* User Info and Logout */}
          <div className="flex items-center space-x-4">
            <div className="hidden sm:block text-right">
              <p className="text-sm font-medium text-gray-900">{userName}</p>
              <p className="text-xs text-gray-500">{userEmail}</p>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-50 hover:bg-red-100 text-red-700 px-4 py-2 rounded-lg font-medium transition duration-200"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}