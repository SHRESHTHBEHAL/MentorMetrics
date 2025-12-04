-- Comprehensive Schema Update Script
-- Run this in Supabase SQL Editor to ensure all tables and columns exist

-- 1. Update sessions table with missing columns
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sessions' AND column_name = 'last_successful_stage') THEN
        ALTER TABLE public.sessions ADD COLUMN last_successful_stage TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sessions' AND column_name = 'completed_at') THEN
        ALTER TABLE public.sessions ADD COLUMN completed_at TIMESTAMP WITH TIME ZONE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sessions' AND column_name = 'completion_metadata') THEN
        ALTER TABLE public.sessions ADD COLUMN completion_metadata JSONB;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sessions' AND column_name = 'stages_completed') THEN
        ALTER TABLE public.sessions ADD COLUMN stages_completed JSONB DEFAULT '[]'::jsonb;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sessions' AND column_name = 'has_transcript') THEN
        ALTER TABLE public.sessions ADD COLUMN has_transcript BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- 2. Create final_scores table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.final_scores (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
    engagement NUMERIC,
    communication_clarity NUMERIC,
    technical_correctness NUMERIC,
    pacing_structure NUMERIC,
    interactive_quality NUMERIC,
    mentor_score NUMERIC,
    raw_fusion_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Create reports table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.reports (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
    summary TEXT,
    strengths JSONB,
    improvements JSONB,
    actionable_tips JSONB,
    raw_llm_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Enable RLS and Policies for new tables
ALTER TABLE public.final_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'final_scores' AND policyname = 'Users can view own final scores') THEN
        CREATE POLICY "Users can view own final scores" ON public.final_scores
            FOR SELECT USING (auth.uid() IN (SELECT user_id FROM public.sessions WHERE id = session_id));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'final_scores' AND policyname = 'Users can insert own final scores') THEN
        CREATE POLICY "Users can insert own final scores" ON public.final_scores
            FOR INSERT WITH CHECK (auth.uid() IN (SELECT user_id FROM public.sessions WHERE id = session_id));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'reports' AND policyname = 'Users can view own reports') THEN
        CREATE POLICY "Users can view own reports" ON public.reports
            FOR SELECT USING (auth.uid() IN (SELECT user_id FROM public.sessions WHERE id = session_id));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'reports' AND policyname = 'Users can insert own reports') THEN
        CREATE POLICY "Users can insert own reports" ON public.reports
            FOR INSERT WITH CHECK (auth.uid() IN (SELECT user_id FROM public.sessions WHERE id = session_id));
    END IF;
END $$;

-- 5. Reload Schema Cache
NOTIFY pgrst, 'reload schema';
