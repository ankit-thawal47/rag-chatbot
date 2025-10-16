import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Navbar from '../components/Navbar';
import { uploadFile, getFiles } from '../lib/api';

export default function Upload() {
  const router = useRouter();
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/');
      return;
    }
    loadFiles();
  }, [router]);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const data = await getFiles();
      setFiles(data.files || []);
    } catch (err) {
      console.error('Error loading files:', err);
      setError('Failed to load files. Please refresh the page.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Reset previous messages
    setError('');
    setSuccess('');

    // Validate file type
    const allowedExtensions = ['pdf', 'docx', 'pptx'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
      setError('Invalid file type. Please upload PDF, DOCX, or PPTX files only.');
      e.target.value = ''; // Clear the input
      return;
    }

    // Validate file size (10KB - 10MB)
    const minSize = 10 * 1024; // 10KB
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    if (file.size < minSize) {
      setError('File too small. Minimum size is 10KB.');
      e.target.value = '';
      return;
    }
    
    if (file.size > maxSize) {
      setError('File too large. Maximum size is 10MB.');
      e.target.value = '';
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      await uploadFile(file, (progress) => {
        setUploadProgress(progress);
      });
      
      setSuccess(`${file.name} uploaded successfully! Processing embeddings...`);
      setUploadProgress(100);
      
      // Reload files list
      await loadFiles();
      
      // Clear the input
      e.target.value = '';
      
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    };
    
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status) => {
    const icons = {
      pending: '⏳',
      processing: '🔄',
      completed: '✅',
      failed: '❌'
    };
    
    return icons[status] || '❓';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Documents</h1>
          <p className="text-gray-600">
            Upload PDF, DOCX, or PPTX files to make them searchable with AI
          </p>
        </div>
        
        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload New Document</h2>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <div className="space-y-4">
              <div className="text-4xl">📁</div>
              <div>
                <input
                  type="file"
                  accept=".pdf,.docx,.pptx"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
                />
              </div>
              <div className="text-sm text-gray-500">
                <p>Supported formats: PDF, DOCX, PPTX</p>
                <p>File size: 10KB - 10MB</p>
              </div>
            </div>
          </div>
          
          {/* Upload Progress */}
          {uploading && (
            <div className="mt-4">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Uploading...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}
          
          {/* Messages */}
          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
          
          {success && (
            <div className="mt-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
              {success}
            </div>
          )}
        </div>

        {/* Files List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Your Documents</h2>
          </div>
          
          <div className="p-6">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-500">Loading documents...</p>
              </div>
            ) : files.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📄</div>
                <p className="text-gray-500">No documents uploaded yet.</p>
                <p className="text-sm text-gray-400 mt-2">Upload your first document to get started!</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Document
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Size
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Uploaded
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {files.map((file) => (
                      <tr key={file.doc_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="text-2xl mr-3">
                              {file.filename.endsWith('.pdf') ? '📄' : 
                               file.filename.endsWith('.docx') ? '📝' : '📊'}
                            </div>
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {file.filename}
                              </div>
                              <div className="text-sm text-gray-500">
                                {file.file_type}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatFileSize(file.file_size)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(file.embedding_status)}`}>
                            <span className="mr-1">{getStatusIcon(file.embedding_status)}</span>
                            {file.embedding_status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(file.uploaded_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
        
        {/* Instructions */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">📋 Next Steps</h3>
          <div className="space-y-2 text-blue-800">
            <p>1. ✅ Upload your documents (PDF, DOCX, or PPTX files)</p>
            <p>2. ⏳ Wait for processing to complete (status will show "completed")</p>
            <p>3. 💬 Go to the Chat page to ask questions about your documents</p>
            <p>4. 🎯 Get AI-powered answers with source citations</p>
          </div>
        </div>
      </div>
    </div>
  );
}