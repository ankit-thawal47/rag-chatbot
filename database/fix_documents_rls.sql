-- Fix documents table RLS policy to allow document creation
-- Execute this in your Supabase SQL Editor

-- Drop existing restrictive policy for documents
DROP POLICY IF EXISTS documents_policy ON documents;
DROP POLICY IF EXISTS documents_own_data ON documents;

-- Create new policy for documents that allows creation
CREATE POLICY documents_policy ON documents
    FOR ALL
    USING (
        -- Allow access to own documents OR during document creation
        user_id = current_setting('app.user_id', true)::TEXT
        OR current_setting('app.user_id', true) IS NULL
        OR current_setting('app.user_id', true) = ''
    );

-- Create separate insert policy for documents
CREATE POLICY documents_insert_policy ON documents
    FOR INSERT
    WITH CHECK (true);  -- Allow any document to be created

-- Verify the policies
SELECT schemaname, tablename, policyname, permissive, cmd 
FROM pg_policies 
WHERE tablename = 'documents';