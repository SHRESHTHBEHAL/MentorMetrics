-- Create analytics_events table for tracking usage analytics
CREATE TABLE IF NOT EXISTS public.analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_name TEXT NOT NULL,
    session_id UUID,
    user_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on event_name for faster queries
CREATE INDEX IF NOT EXISTS idx_analytics_events_event_name ON public.analytics_events(event_name);

-- Create index on timestamp for time-based queries
CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON public.analytics_events(timestamp DESC);

-- Create index on session_id for session-based queries
CREATE INDEX IF NOT EXISTS idx_analytics_events_session_id ON public.analytics_events(session_id);

-- Create index on user_id for user-based queries
CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON public.analytics_events(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE public.analytics_events ENABLE ROW LEVEL SECURITY;

-- Create policy to allow service role to insert analytics events
CREATE POLICY "Allow service role to insert analytics"
ON public.analytics_events
FOR INSERT
TO service_role
WITH CHECK (true);

-- Create policy to allow service role to select analytics events
CREATE POLICY "Allow service role to select analytics"
ON public.analytics_events
FOR SELECT
TO service_role
USING (true);

-- Create policy to allow authenticated users to view their own analytics
CREATE POLICY "Allow users to view their own analytics"
ON public.analytics_events
FOR SELECT
TO authenticated
USING (user_id::text = auth.uid()::text);
