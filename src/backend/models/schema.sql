CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id),
    file_url TEXT NOT NULL,
    filename TEXT NOT NULL,
    status TEXT DEFAULT 'uploaded',
    has_transcript BOOLEAN DEFAULT FALSE,
    stages_completed JSONB DEFAULT '[]'::jsonb,
    last_successful_stage TEXT,
    completed_at TIMESTAMP WITH TIME ZONE,
    completion_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.evaluations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.scores (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    score FLOAT NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.reports (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
    summary TEXT,
    recommendations JSONB,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.transcripts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
    raw_text TEXT,
    segments JSONB,
    word_timestamps JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

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

CREATE TABLE IF NOT EXISTS public.text_evaluations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE,
    clarity_score NUMERIC,
    structure_score NUMERIC,
    technical_correctness_score NUMERIC,
    explanation_quality_score NUMERIC,
    raw_llm_response JSONB,
    summary_feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

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

CREATE INDEX IF NOT EXISTS idx_audio_features_session_id ON public.audio_features(session_id);
CREATE INDEX IF NOT EXISTS idx_text_evaluations_session_id ON public.text_evaluations(session_id);
CREATE INDEX IF NOT EXISTS idx_visual_evaluations_session_id ON public.visual_evaluations(session_id);
CREATE INDEX IF NOT EXISTS idx_final_scores_session_id ON public.final_scores(session_id);
CREATE INDEX IF NOT EXISTS idx_reports_session_id ON public.reports(session_id);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audio_features ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.text_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.visual_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.final_scores ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own sessions" ON public.sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own sessions" ON public.sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own transcripts" ON public.transcripts
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );

CREATE POLICY "Users can insert own transcripts" ON public.transcripts
    FOR INSERT WITH CHECK (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );

CREATE POLICY "Users can view own audio features" ON public.audio_features
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );

CREATE POLICY "Users can insert own audio features" ON public.audio_features
    FOR INSERT WITH CHECK (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );

CREATE POLICY "Users can view own text evaluations" ON public.text_evaluations
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );

CREATE POLICY "Users can insert own text evaluations" ON public.text_evaluations
    FOR INSERT WITH CHECK (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );

CREATE POLICY "Users can view own visual evaluations" ON public.visual_evaluations
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );

CREATE POLICY "Users can insert own visual evaluations" ON public.visual_evaluations
    FOR INSERT WITH CHECK (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );

CREATE POLICY "Users can view own final scores" ON public.final_scores
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );

CREATE POLICY "Users can insert own final scores" ON public.final_scores
    FOR INSERT WITH CHECK (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );

CREATE POLICY "Users can view own reports" ON public.reports
    FOR SELECT USING (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );

CREATE POLICY "Users can insert own reports" ON public.reports
    FOR INSERT WITH CHECK (
        auth.uid() IN (
            SELECT user_id FROM public.sessions WHERE id = session_id
        )
    );
