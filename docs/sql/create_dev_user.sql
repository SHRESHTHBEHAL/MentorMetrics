-- Create mock development user for testing
-- This approach creates the user in auth.users first (using Supabase's auth schema)
-- Then creates the corresponding entry in public.users

-- Step 1: Insert into auth.users (Supabase's authentication table)
-- Note: This requires service_role permissions
INSERT INTO auth.users (
    id,
    instance_id,
    aud,
    role,
    email,
    encrypted_password,
    email_confirmed_at,
    created_at,
    updated_at,
    confirmation_token,
    raw_app_meta_data,
    raw_user_meta_data
)
VALUES (
    '00000000-0000-0000-0000-000000000001'::uuid,
    '00000000-0000-0000-0000-000000000000'::uuid,
    'authenticated',
    'authenticated',
    'dev@mentormetrics.local',
    crypt('dev-password-123', gen_salt('bf')),  -- Encrypted password
    NOW(),
    NOW(),
    NOW(),
    '',
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{}'::jsonb
)
ON CONFLICT (id) DO NOTHING;

-- Step 2: Insert into public.users (your application's user table)
INSERT INTO public.users (id, email, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'dev@mentormetrics.local',
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Verify both users were created
SELECT 'auth.users' as table_name, id, email FROM auth.users WHERE id = '00000000-0000-0000-0000-000000000001'
UNION ALL
SELECT 'public.users' as table_name, id, email FROM public.users WHERE id = '00000000-0000-0000-0000-000000000001';

