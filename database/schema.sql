-- RAG Document Management System Database Schema
-- Execute this in your Supabase SQL editor

-- Create users table
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create documents table
CREATE TABLE documents (
    doc_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    gcp_path TEXT NOT NULL,
    embedding_status TEXT DEFAULT 'pending' CHECK (embedding_status IN ('pending', 'processing', 'completed', 'failed')),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_user_uploaded ON documents(user_id, uploaded_at DESC);
CREATE INDEX idx_documents_status ON documents(embedding_status);

-- Enable Row Level Security (RLS) for user isolation
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
-- Users can only see and update their own record
CREATE POLICY users_own_data ON users
    FOR ALL
    USING (user_id = current_setting('app.user_id', true)::TEXT);

-- RLS Policies for documents table
-- Users can only see and manage their own documents
CREATE POLICY documents_own_data ON documents
    FOR ALL
    USING (user_id = current_setting('app.user_id', true)::TEXT);

-- Function to set user context (call this from your application)
CREATE OR REPLACE FUNCTION set_user_context(p_user_id TEXT)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.user_id', p_user_id, TRUE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Optional: Create a view for document statistics
CREATE VIEW document_stats AS
SELECT 
    user_id,
    COUNT(*) as total_documents,
    COUNT(CASE WHEN embedding_status = 'completed' THEN 1 END) as completed_documents,
    COUNT(CASE WHEN embedding_status = 'pending' THEN 1 END) as pending_documents,
    COUNT(CASE WHEN embedding_status = 'processing' THEN 1 END) as processing_documents,
    COUNT(CASE WHEN embedding_status = 'failed' THEN 1 END) as failed_documents,
    SUM(file_size) as total_size_bytes,
    MIN(uploaded_at) as first_upload,
    MAX(uploaded_at) as last_upload
FROM documents
GROUP BY user_id;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Insert sample data (optional, for testing)
-- You can remove this section in production
INSERT INTO users (user_id, email, display_name) VALUES 
('test_user_123', 'test@example.com', 'Test User')
ON CONFLICT (user_id) DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE users IS 'User accounts with basic profile information';
COMMENT ON TABLE documents IS 'Document metadata and processing status';
COMMENT ON COLUMN documents.embedding_status IS 'Processing status: pending, processing, completed, failed';
COMMENT ON COLUMN documents.gcp_path IS 'Path to file in Google Cloud Storage';

-- Create a function to clean up old failed uploads (optional)
CREATE OR REPLACE FUNCTION cleanup_failed_documents()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete documents that have been in 'failed' status for more than 1 day
    DELETE FROM documents 
    WHERE embedding_status = 'failed' 
    AND uploaded_at < NOW() - INTERVAL '1 day';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get user document summary
CREATE OR REPLACE FUNCTION get_user_document_summary(p_user_id TEXT)
RETURNS TABLE(
    total_docs INTEGER,
    completed_docs INTEGER,
    pending_docs INTEGER,
    failed_docs INTEGER,
    total_size_mb NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_docs,
        COUNT(CASE WHEN embedding_status = 'completed' THEN 1 END)::INTEGER as completed_docs,
        COUNT(CASE WHEN embedding_status = 'pending' THEN 1 END)::INTEGER as pending_docs,
        COUNT(CASE WHEN embedding_status = 'failed' THEN 1 END)::INTEGER as failed_docs,
        ROUND((SUM(file_size) / 1024.0 / 1024.0)::NUMERIC, 2) as total_size_mb
    FROM documents
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;