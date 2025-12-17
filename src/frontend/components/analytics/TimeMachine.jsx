import React, { useState, useEffect } from 'react';
import { Clock, TrendingUp, TrendingDown, Zap, Award, ArrowRight, Calendar, Star } from 'lucide-react';
import { api } from '../../utils/api';

const ScoreComparison = ({ label, firstScore, latestScore }) => {
    const improvement = latestScore - firstScore;
    const percentChange = firstScore > 0 ? ((improvement / firstScore) * 100).toFixed(0) : 0;
    const isImproved = improvement > 0;

    return (
        <div className="flex items-center justify-between py-2 border-b border-gray-200 last:border-0">
            <span className="font-bold text-sm uppercase text-gray-600">{label}</span>
            <div className="flex items-center gap-4">
                <span className="text-gray-400 font-mono">{firstScore?.toFixed(1) || '—'}</span>
                <ArrowRight className="w-4 h-4 text-gray-400" />
                <span className={`font-black ${isImproved ? 'text-green-600' : 'text-red-600'}`}>
                    {latestScore?.toFixed(1) || '—'}
                </span>
                {improvement !== 0 && (
                    <span className={`text-xs font-bold px-2 py-0.5 ${isImproved ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {isImproved ? '+' : ''}{percentChange}%
                    </span>
                )}
            </div>
        </div>
    );
};

const SessionCard = ({ session, label, isFirst }) => {
    const score = session?.mentor_score || session?.completion_metadata?.mentor_score || 0;
    const date = session?.created_at ? new Date(session.created_at).toLocaleDateString() : 'N/A';

    return (
        <div className={`border-4 border-black p-6 ${isFirst ? 'bg-gray-100' : 'bg-yellow-50'}`}>
            <div className="flex items-center justify-between mb-4">
                <span className={`text-xs font-black uppercase px-3 py-1 ${isFirst ? 'bg-gray-300 text-gray-700' : 'bg-yellow-400 text-black'}`}>
                    {label}
                </span>
                <div className="flex items-center text-xs text-gray-500">
                    <Calendar className="w-3 h-3 mr-1" />
                    {date}
                </div>
            </div>

            <div className="text-center py-6">
                <div className={`text-6xl font-black ${isFirst ? 'text-gray-500' : 'text-black'}`}>
                    {score.toFixed(1)}
                </div>
                <div className="text-sm font-bold text-gray-500 uppercase mt-2">Mentor Score</div>
            </div>

            <div className="text-xs text-gray-500 truncate">
                {session?.filename || 'Session'}
            </div>
        </div>
    );
};

const TimeMachine = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [firstSession, setFirstSession] = useState(null);
    const [latestSession, setLatestSession] = useState(null);
    const [improvement, setImprovement] = useState(0);

    useEffect(() => {
        fetchSessions();
    }, []);

    const fetchSessions = async () => {
        try {
            setLoading(true);
            const response = await api.get('/sessions/list');
            const sessions = response.data || [];

            // Filter completed sessions only
            const completedSessions = sessions.filter(s =>
                s.status === 'complete' &&
                (s.mentor_score || s.completion_metadata?.mentor_score)
            );

            if (completedSessions.length >= 2) {
                // Sort by date (oldest first)
                const sorted = [...completedSessions].sort(
                    (a, b) => new Date(a.created_at) - new Date(b.created_at)
                );

                const first = sorted[0];
                const latest = sorted[sorted.length - 1];

                setFirstSession(first);
                setLatestSession(latest);

                const firstScore = first.mentor_score || first.completion_metadata?.mentor_score || 0;
                const latestScore = latest.mentor_score || latest.completion_metadata?.mentor_score || 0;

                if (firstScore > 0) {
                    setImprovement(((latestScore - firstScore) / firstScore) * 100);
                }
            } else if (completedSessions.length === 1) {
                setFirstSession(completedSessions[0]);
                setLatestSession(null);
            }

            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch sessions:', err);
            setError('Failed to load progress data');
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="bg-white border-4 border-black p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                <div className="flex items-center justify-center py-12">
                    <Clock className="w-8 h-8 animate-spin text-gray-400" />
                </div>
            </div>
        );
    }

    if (!firstSession) {
        return (
            <div className="bg-white border-4 border-black p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                <div className="flex items-center mb-6 border-b-4 border-black pb-4">
                    <Clock className="w-6 h-6 mr-3" />
                    <h3 className="text-xl font-black uppercase">Time Machine</h3>
                </div>
                <div className="text-center py-12 text-gray-500">
                    <Clock className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <p className="font-bold uppercase mb-2">No Sessions Yet</p>
                    <p className="text-sm">Complete your first session to start tracking progress!</p>
                </div>
            </div>
        );
    }

    if (!latestSession) {
        return (
            <div className="bg-white border-4 border-black p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                <div className="flex items-center mb-6 border-b-4 border-black pb-4">
                    <Clock className="w-6 h-6 mr-3" />
                    <h3 className="text-xl font-black uppercase">Time Machine</h3>
                </div>
                <div className="text-center py-12">
                    <Star className="w-16 h-16 mx-auto mb-4 text-yellow-400" />
                    <p className="font-bold uppercase mb-2">Great Start!</p>
                    <p className="text-sm text-gray-500">Complete one more session to see your progress over time.</p>
                </div>
            </div>
        );
    }

    const isImproved = improvement > 0;

    return (
        <div className="bg-white border-4 border-black p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            {/* Header */}
            <div className="flex items-center justify-between mb-6 border-b-4 border-black pb-4">
                <div className="flex items-center">
                    <Clock className="w-6 h-6 mr-3" />
                    <h3 className="text-xl font-black uppercase">Time Machine</h3>
                </div>
                <div className="flex items-center">
                    {isImproved ? (
                        <TrendingUp className="w-5 h-5 text-green-500 mr-2" />
                    ) : (
                        <TrendingDown className="w-5 h-5 text-red-500 mr-2" />
                    )}
                    <span className="text-sm font-bold text-gray-500">Your Journey</span>
                </div>
            </div>

            {/* Improvement Banner */}
            <div className={`mb-8 p-6 border-4 border-black text-center relative overflow-hidden ${isImproved ? 'bg-gradient-to-r from-green-400 to-green-500' : 'bg-gradient-to-r from-yellow-400 to-yellow-500'}`}>
                <div className="absolute top-2 right-2">
                    <Zap className="w-8 h-8 text-white opacity-50" />
                </div>
                <div className="absolute bottom-2 left-2">
                    <Award className="w-8 h-8 text-white opacity-50" />
                </div>

                <p className="text-white text-sm font-bold uppercase mb-2">
                    {isImproved ? '🎉 Congratulations!' : '💪 Keep Going!'}
                </p>
                <p className="text-white text-4xl font-black">
                    {isImproved ? "You've improved by" : "Room to grow:"}
                </p>
                <p className="text-white text-7xl font-black my-4">
                    {Math.abs(improvement).toFixed(0)}%
                </p>
                <p className="text-white text-sm font-bold opacity-80">
                    From your first session to now
                </p>
            </div>

            {/* Side by Side Comparison */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <SessionCard session={firstSession} label="First Session" isFirst={true} />
                <SessionCard session={latestSession} label="Latest Session" isFirst={false} />
            </div>

            {/* Detailed Breakdown */}
            <div className="border-4 border-black p-4">
                <h4 className="font-black uppercase text-sm mb-4 text-gray-600">Score Breakdown</h4>
                <ScoreComparison
                    label="Overall"
                    firstScore={firstSession.mentor_score || firstSession.completion_metadata?.mentor_score}
                    latestScore={latestSession.mentor_score || latestSession.completion_metadata?.mentor_score}
                />
            </div>

            {/* Motivational Footer */}
            <div className="mt-6 text-center">
                <p className="text-xs text-gray-400 font-bold uppercase">
                    {isImproved
                        ? "Every practice session makes you better!"
                        : "Keep practicing - improvement takes time!"}
                </p>
            </div>
        </div>
    );
};

export default TimeMachine;
