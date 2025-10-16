# Supabase Database Setup Instructions

## 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up/login and create a new project
3. Choose a database password and region
4. Wait for project to be ready (2-3 minutes)

## 2. Execute Database Schema

1. In your Supabase dashboard, go to the **SQL Editor**
2. Copy the contents of `schema.sql` and paste it into the editor
3. Click **Run** to execute the schema
4. Verify tables were created in the **Table Editor**

## 3. Get Connection Details

1. Go to **Settings** > **API**
2. Copy the following values:
   - **Project URL** (for SUPABASE_URL)
   - **anon public** key (for SUPABASE_KEY)

## 4. Update Environment Variables

Add these to your backend `.env` file:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

## 5. Test Database Connection

You can test the connection using the backend:

```bash
cd backend
python -c "
from database import supabase_client
result = supabase_client.table('users').select('*').limit(1).execute()
print('Database connection successful!' if result else 'Connection failed')
"
```

## 6. Row Level Security (RLS) Explanation

The database uses RLS to ensure user isolation:

- **Users table**: Users can only access their own user record
- **Documents table**: Users can only access documents they uploaded
- **Policy enforcement**: Happens automatically at the database level

## 7. Important Notes

### User Context Setting
Before performing any database operations, set the user context:

```python
# In your Python code
supabase_client.rpc('set_user_context', {'p_user_id': user_id})
```

### Security Features
- All queries are automatically filtered by user_id
- No additional WHERE clauses needed in application code
- Database-level security prevents data leaks

### Monitoring
- Use the Supabase dashboard to monitor:
  - Database performance
  - Active connections
  - Query logs
  - User activity

## 8. Optional: Sample Queries

Test your setup with these queries in the SQL Editor:

```sql
-- Check if tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'documents');

-- View RLS policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename IN ('users', 'documents');

-- Check document statistics
SELECT * FROM document_stats;
```

## 9. Troubleshooting

### Common Issues:

1. **RLS blocks all queries**
   - Make sure to call `set_user_context()` before queries
   - Check that user_id exists in the users table

2. **Connection errors**
   - Verify SUPABASE_URL and SUPABASE_KEY are correct
   - Check network connectivity

3. **Permission denied**
   - Ensure RLS policies are correctly applied
   - Verify user has proper authentication

### Debug Commands:

```sql
-- Check current user context
SELECT current_setting('app.user_id', true);

-- Disable RLS temporarily (for testing only)
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;

-- Re-enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
```

## 10. Production Considerations

For production deployment:

1. **Environment Variables**: Store securely (not in code)
2. **Database Backups**: Enable automatic backups in Supabase
3. **Monitoring**: Set up alerts for database performance
4. **Scaling**: Monitor usage and upgrade plan as needed
5. **Security**: Regularly audit RLS policies and permissions