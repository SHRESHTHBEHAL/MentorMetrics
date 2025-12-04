-- Delete audio_features for this session to force re-analysis with fixed WPM calculator
DELETE FROM public.audio_features WHERE session_id = '9ee297e4-ae4f-44d7-aaf0-0881078a3811';
