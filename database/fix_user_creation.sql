-- Fix RLS to allow user creation
-- Execute this in your Supabase SQL Editor

-- Drop existing restrictive policy
DROP POLICY IF EXISTS users_own_data ON users;

-- Create new policy that allows user registration
CREATE POLICY users_policy ON users
    FOR ALL
    USING (
        -- Allow users to access their own data OR allow inserts for new users
        user_id = current_setting('app.user_id', true)::TEXT
        OR current_setting('app.user_id', true) = ''
        OR current_setting('app.user_id', true) IS NULL
    );

-- Create separate insert policy for new user registration
CREATE POLICY users_insert_policy ON users
    FOR INSERT
    WITH CHECK (true);  -- Allow any new user to be created

-- Verify the policies
SELECT schemaname, tablename, policyname, permissive, cmd 
FROM pg_policies 
WHERE tablename = 'users';