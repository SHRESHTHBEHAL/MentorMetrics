-- Add all missing columns to reports table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'reports' AND column_name = 'summary') THEN
        ALTER TABLE public.reports ADD COLUMN summary TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'reports' AND column_name = 'strengths') THEN
        ALTER TABLE public.reports ADD COLUMN strengths JSONB;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'reports' AND column_name = 'improvements') THEN
        ALTER TABLE public.reports ADD COLUMN improvements JSONB;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'reports' AND column_name = 'actionable_tips') THEN
        ALTER TABLE public.reports ADD COLUMN actionable_tips JSONB;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'reports' AND column_name = 'raw_llm_response') THEN
        ALTER TABLE public.reports ADD COLUMN raw_llm_response JSONB;
    END IF;
END $$;

-- Reload Schema Cache
NOTIFY pgrst, 'reload schema';
