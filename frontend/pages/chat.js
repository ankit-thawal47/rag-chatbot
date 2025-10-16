import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import Navbar from '../components/Navbar';
import { chatQuery, getFiles } from '../lib/api';

export default function Chat() {
  const router = useRouter();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [documentsCount, setDocumentsCount] = useState(0);
  const [completedCount, setCompletedCount] = useState(0);
  const messagesEndRef = useRef(null);

  // Check authentication and load initial data
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/');
      return;
    }
    
    loadDocumentStats();
    
    // Add welcome message
    setMessages([{
      role: 'assistant',
      content: 'Hello! I\'m here to help you find information in your uploaded documents. Ask me anything about the content of your files.',
      timestamp: new Date()
    }]);
  }, [router]);

  // Auto scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadDocumentStats = async () => {
    try {
      const data = await getFiles();
      const files = data.files || [];
      setDocumentsCount(files.length);
      setCompletedCount(files.filter(file => file.embedding_status === 'completed').length);
    } catch (err) {
      console.error('Error loading document stats:', err);
    }
  };

  const handleSend = async () => {
    const query = input.trim();
    if (!query || loading) return;

    // Check if user has any completed documents
    if (completedCount === 0) {
      alert('Please upload and process some documents first before asking questions.');
      return;
    }

    const userMessage = {
      role: 'user',
      content: query,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatQuery(query);
      
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        sources: response.sources,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (err) {
      console.error('Chat error:', err);
      
      let errorMessage = 'Sorry, I encountered an error while processing your question.';
      
      if (err.response?.status === 400) {
        errorMessage = err.response.data.detail || 'Invalid question format.';
      } else if (err.response?.status === 500) {
        errorMessage = 'Server error. Please try again in a moment.';
      }
      
      const errorResponse = {
        role: 'assistant',
        content: errorMessage,
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const exampleQuestions = [
    "Where is XYZ?"
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <div className="flex-1 max-w-4xl w-full mx-auto py-8 px-4 sm:px-6 lg:px-8 flex flex-col">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Chat with Your Documents</h1>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <span>📄 {documentsCount} document{documentsCount !== 1 ? 's' : ''} uploaded</span>
            <span>✅ {completedCount} ready for search</span>
            {completedCount === 0 && documentsCount > 0 && (
              <span className="text-amber-600">⏳ Processing in progress...</span>
            )}
          </div>
        </div>
        
        {/* Messages Container */}
        <div className="flex-1 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-1' : 'order-2'}`}>
                  {/* Message bubble */}
                  <div className={`px-4 py-3 rounded-lg ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : msg.isError
                        ? 'bg-red-50 text-red-800 border border-red-200'
                        : 'bg-gray-100 text-gray-900'
                  }`}>
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                  
                  {/* Sources */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm font-semibold text-blue-900 mb-1">📚 Sources:</p>
                      <div className="space-y-1">
                        {msg.sources.map((source, i) => (
                          <div key={i} className="text-sm text-blue-800 flex items-center justify-between">
                            <span className="flex items-center">
                              <span className="mr-1">•</span>
                              {source.doc_name}
                            </span>
                            <span className="text-xs bg-blue-200 px-2 py-0.5 rounded">
                              {Math.round(source.relevance_score * 100)}% match
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Timestamp */}
                  <div className={`text-xs text-gray-500 mt-1 ${
                    msg.role === 'user' ? 'text-right' : 'text-left'
                  }`}>
                    {formatTime(msg.timestamp)}
                  </div>
                </div>
              </div>
            ))}
            
            {/* Loading indicator */}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 px-4 py-3 rounded-lg">
                  <div className="flex items-center space-x-2 text-gray-600">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                    <span>Searching documents...</span>
                  </div>
                </div>
              </div>
            )}
            
            {/* Empty state */}
            {messages.length === 1 && completedCount === 0 && (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">🤖</div>
                <p className="text-gray-600 mb-4">No documents ready for search yet.</p>
                <button
                  onClick={() => router.push('/upload')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium"
                >
                  Upload Documents
                </button>
              </div>
            )}
            
            {/* Example questions */}
            {messages.length === 1 && completedCount > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">💡 Try asking:</h3>
                <div className="space-y-2">
                  {exampleQuestions.map((question, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInput(question)}
                      className="block w-full text-left text-sm text-blue-700 hover:text-blue-900 hover:bg-blue-100 px-2 py-1 rounded transition duration-200"
                    >
                      "{question}"
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-2">
              <div className="flex-1">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={
                    completedCount === 0 
                      ? "Upload and process documents first..." 
                      : "Ask a question about your documents..."
                  }
                  disabled={loading || completedCount === 0}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:bg-gray-100 disabled:cursor-not-allowed"
                  rows="2"
                  maxLength="1000"
                />
                <div className="text-xs text-gray-500 mt-1 text-right">
                  {input.length}/1000 characters
                </div>
              </div>
              <button
                onClick={handleSend}
                disabled={loading || !input.trim() || completedCount === 0}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg font-medium transition duration-200 h-fit"
              >
                {loading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Sending
                  </div>
                ) : (
                  'Send'
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}