-- Fix RLS policies to allow user registration
-- Execute this in your Supabase SQL editor

-- Drop existing policies
DROP POLICY IF EXISTS users_own_data ON users;
DROP POLICY IF EXISTS documents_own_data ON documents;

-- Create new policy for users table that allows registration
CREATE POLICY users_policy ON users
    FOR ALL
    USING (
        -- Allow access if user_id matches current user OR during registration
        user_id = current_setting('app.user_id', true)::TEXT
        OR current_setting('app.user_id', true) IS NULL
        OR current_setting('app.user_id', true) = ''
    );

-- Create policy for documents table (stricter)
CREATE POLICY documents_policy ON documents
    FOR ALL
    USING (user_id = current_setting('app.user_id', true)::TEXT);

-- Alternative: Create a separate policy for INSERT on users table
CREATE POLICY users_insert_policy ON users
    FOR INSERT
    WITH CHECK (true);  -- Allow any user to be inserted

-- Grant necessary permissions again
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;