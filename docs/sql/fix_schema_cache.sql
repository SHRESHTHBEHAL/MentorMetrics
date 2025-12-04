-- Reload the PostgREST schema cache
-- Run this in the Supabase SQL Editor to fix "Could not find column" errors
NOTIFY pgrst, 'reload schema';
