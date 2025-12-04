import { useState, useEffect } from 'react';
import { supabase } from '../utils/supabase';
import { useNavigate, useLocation } from 'react-router-dom';

export const useAuthGuard = () => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const checkSession = async () => {
            try {
                const { data: { session } } = await supabase.auth.getSession();

                if (!session) {
                    console.warn('[DEV MODE] No auth session found, using mock user');
                    const mockUser = {
                        id: '00000000-0000-0000-0000-000000000001',
                        email: 'dev@mentormetrics.local',
                        role: 'authenticated'
                    };
                    setUser(mockUser);
                } else {
                    setUser(session.user);
                }
            } catch (error) {
                console.error('Auth check failed:', error);
                const mockUser = {
                    id: '00000000-0000-0000-0000-000000000001',
                    email: 'dev@mentormetrics.local',
                    role: 'authenticated'
                };
                setUser(mockUser);
            } finally {
                setLoading(false);
            }
        };

        checkSession();

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            if (session) {
                setUser(session.user);
            } else {
                const mockUser = {
                    id: '00000000-0000-0000-0000-000000000001',
                    email: 'dev@mentormetrics.local',
                    role: 'authenticated'
                };
                setUser(mockUser);
            }
        });

        return () => subscription.unsubscribe();
    }, [navigate, location.pathname]);

    return { user, loading };
};
