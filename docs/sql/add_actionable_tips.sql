-- Add actionable_tips column to reports table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'reports' AND column_name = 'actionable_tips') THEN
        ALTER TABLE public.reports ADD COLUMN actionable_tips JSONB;
    END IF;
END $$;

-- Reload Schema Cache
NOTIFY pgrst, 'reload schema';
