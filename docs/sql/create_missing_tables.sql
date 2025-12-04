-- Create audio_features table
CREATE TABLE IF NOT EXISTS public.audio_features (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
    words_per_minute NUMERIC,
    silence_ratio NUMERIC,
    avg_volume NUMERIC,
    volume_variation NUMERIC,
    clarity_score NUMERIC,
    raw_features JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create visual_evaluations table
CREATE TABLE IF NOT EXISTS public.visual_evaluations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
    face_visibility_score NUMERIC,
    gaze_forward_score NUMERIC,
    gesture_score NUMERIC,
    movement_score NUMERIC,
    visual_overall NUMERIC,
    raw_visual_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS
ALTER TABLE public.audio_features ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.visual_evaluations ENABLE ROW LEVEL SECURITY;

-- Create Policies
DO $$
BEGIN
    -- Audio Features Policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'audio_features' AND policyname = 'Users can view own audio features') THEN
        CREATE POLICY "Users can view own audio features" ON public.audio_features
            FOR SELECT USING (auth.uid() IN (SELECT user_id FROM public.sessions WHERE id = session_id));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'audio_features' AND policyname = 'Users can insert own audio features') THEN
        CREATE POLICY "Users can insert own audio features" ON public.audio_features
            FOR INSERT WITH CHECK (auth.uid() IN (SELECT user_id FROM public.sessions WHERE id = session_id));
    END IF;

    -- Visual Evaluations Policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'visual_evaluations' AND policyname = 'Users can view own visual evaluations') THEN
        CREATE POLICY "Users can view own visual evaluations" ON public.visual_evaluations
            FOR SELECT USING (auth.uid() IN (SELECT user_id FROM public.sessions WHERE id = session_id));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'visual_evaluations' AND policyname = 'Users can insert own visual evaluations') THEN
        CREATE POLICY "Users can insert own visual evaluations" ON public.visual_evaluations
            FOR INSERT WITH CHECK (auth.uid() IN (SELECT user_id FROM public.sessions WHERE id = session_id));
    END IF;
END $$;

-- Reload Schema Cache
NOTIFY pgrst, 'reload schema';
