import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DailyChallenge from '../components/dashboard/DailyChallenge';
import QuoteOfTheDay from '../components/dashboard/QuoteOfTheDay';
import {
    BarChart2,
    Activity,
    Users,
    TrendingUp,
    TrendingDown,
    CheckCircle,
    Clock,
    AlertCircle,
    Loader2,
    FileVideo,
    ArrowRight,
    RefreshCw,
    Zap,
    Flame
} from 'lucide-react';
import { api } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import Achievements from '../components/gamification/Achievements';

import WeakAreasPanel from '../components/analytics/WeakAreasPanel';
import TimeMachine from '../components/analytics/TimeMachine';

import CertificateGenerator from '../components/gamification/CertificateGenerator';

const StatCard = ({ label, value, icon: Icon, subtitle, trend }) => (
    <div className="bg-white border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[4px] hover:translate-y-[4px] transition-all">
        <div className="flex items-center justify-between">
            <div className="flex items-center">
                <div className="flex-shrink-0 bg-black text-white p-3 border-2 border-black">
                    <Icon className="h-6 w-6" />
                </div>
                <div className="ml-5">
                    <p className="text-sm font-bold text-gray-500 uppercase truncate">{label}</p>
                    <p className="text-3xl font-black text-black">{value}</p>
                    {subtitle && (
                        <p className="text-xs font-bold text-gray-400 uppercase mt-1">{subtitle}</p>
                    )}
                </div>
            </div>
            {trend !== undefined && trend !== 0 && (
                <div className={`flex items-center ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {trend > 0 ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
                    <span className="ml-1 text-sm font-bold">{trend > 0 ? '+' : ''}{trend}%</span>
                </div>
            )}
        </div>
    </div>
);

const ScoreBar = ({ label, score, maxScore = 10 }) => {
    const percentage = (score / maxScore) * 100;
    const getColor = (score) => {
        if (score >= 7) return 'bg-green-500';
        if (score >= 4) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    return (
        <div className="mb-4">
            <div className="flex justify-between mb-1">
                <span className="text-sm font-bold uppercase text-gray-600">{label}</span>
                <span className="text-sm font-black text-black">{score.toFixed(1)}/10</span>
            </div>
            <div className="w-full bg-gray-200 h-3 border-2 border-black">
                <div
                    className={`h-full ${getColor(score)} transition-all duration-500`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
};

const RecentSessionCard = ({ session, onClick }) => {
    const getStatusIcon = (status) => {
        switch (status) {
            case 'complete': return <CheckCircle className="h-4 w-4 text-green-600" />;
            case 'processing': return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />;
            case 'failed': return <AlertCircle className="h-4 w-4 text-red-600" />;
            default: return <Clock className="h-4 w-4 text-gray-400" />;
        }
    };

    return (
        <div
            onClick={onClick}
            className="flex items-center justify-between p-4 border-2 border-black hover:bg-gray-50 cursor-pointer transition-all"
        >
            <div className="flex items-center space-x-3">
                <FileVideo className="h-5 w-5 text-black" />
                <div>
                    <p className="font-bold text-sm uppercase truncate max-w-[150px]">{session.filename}</p>
                    <p className="text-xs text-gray-500">{new Date(session.created_at).toLocaleDateString()}</p>
                </div>
            </div>
            <div className="flex items-center space-x-3">
                {session.mentor_score && (
                    <span className="text-lg font-black">{session.mentor_score.toFixed(1)}</span>
                )}
                {getStatusIcon(session.status)}
            </div>
        </div>
    );
};

const ScoreDistributionChart = ({ distribution }) => {
    const maxCount = Math.max(...Object.values(distribution), 1);
    const ranges = ['0-2', '2-4', '4-6', '6-8', '8-10'];
    const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-lime-500', 'bg-green-500'];

    return (
        <div className="flex items-end justify-between h-32 gap-2">
            {ranges.map((range, index) => {
                const count = distribution[range] || 0;
                const height = count > 0 ? (count / maxCount) * 100 : 5;
                return (
                    <div key={range} className="flex flex-col items-center flex-1">
                        <div
                            className={`w-full ${colors[index]} border-2 border-black transition-all duration-500`}
                            style={{ height: `${height}%`, minHeight: '8px' }}
                        />
                        <span className="text-xs font-bold mt-2 text-gray-600">{range}</span>
                        <span className="text-xs font-black">{count}</span>
                    </div>
                );
            })}
        </div>
    );
};

const ScoreTrendChart = ({ history }) => {
    if (!history || history.length === 0) {
        return (
            <div className="h-32 flex items-center justify-center text-gray-400 font-bold uppercase">
                No score history yet
            </div>
        );
    }

    const maxScore = 10;
    const minScore = 0;

    return (
        <div className="h-32 flex items-end gap-1">
            {history.map((item, index) => {
                const height = ((item.score - minScore) / (maxScore - minScore)) * 100;
                return (
                    <div key={index} className="flex flex-col items-center flex-1">
                        <div
                            className="w-full bg-black border-2 border-black transition-all duration-500"
                            style={{ height: `${height}%`, minHeight: '8px' }}
                        />
                        <span className="text-[10px] font-bold mt-1 text-gray-500 truncate w-full text-center">
                            {item.date.slice(5)}
                        </span>
                    </div>
                );
            })}
        </div>
    );
};

const Dashboard = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);
    const [refreshing, setRefreshing] = useState(false);

    const fetchDashboard = async () => {
        try {
            setError(null);
            const response = await api.get('/analytics/dashboard');
            setData(response.data);
        } catch (err) {
            console.error('Failed to fetch dashboard:', err);
            setError('Failed to load dashboard data');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchDashboard();
    }, []);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchDashboard();
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <Loader2 className="h-12 w-12 text-black animate-spin" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <AlertCircle className="mx-auto h-12 w-12 text-red-600 mb-4" />
                <p className="text-xl font-bold text-gray-600">{error}</p>
                <button
                    onClick={handleRefresh}
                    className="mt-4 px-6 py-2 bg-black text-white font-bold uppercase border-2 border-black hover:bg-white hover:text-black transition-all"
                >
                    Try Again
                </button>
            </div>
        );
    }

    const { summary, recent_sessions, score_distribution, score_history } = data || {};

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between border-b-4 border-black pb-4 gap-4">
                <div className="flex items-center gap-4">
                    <h2 className="text-4xl font-black uppercase tracking-tighter">Dashboard</h2>
                    {/* Streak Visualizer */}
                    <div className="hidden md:flex items-center space-x-2 bg-orange-500 text-white px-3 py-1 border-2 border-black transform rotate-2 animate-pulse">
                        <Flame className="w-5 h-5 fill-white" />
                        <span className="font-black uppercase tracking-wider">{summary?.streak || 0} Day Streak</span>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {/* Mobile Streak */}
                    <div className="md:hidden flex items-center space-x-1 bg-orange-500 text-white px-2 py-1 border-2 border-black text-xs">
                        <Flame className="w-3 h-3 fill-white" />
                        <span className="font-black uppercase">{summary?.streak || 0} Days</span>
                    </div>

                    <button
                        onClick={handleRefresh}
                        disabled={refreshing}
                        className="px-4 py-2 bg-white text-black border-2 border-black font-bold uppercase hover:bg-black hover:text-white transition-all flex items-center"
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* Daily Challenge & Motivation Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <DailyChallenge />
                <QuoteOfTheDay />
            </div>

            {/* Main Stats */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <StatCard
                    label="Total Sessions"
                    value={summary?.total_sessions || 0}
                    icon={BarChart2}
                    subtitle={`${summary?.completed_sessions || 0} completed`}
                />
                <StatCard
                    label="Avg. Score"
                    value={`${summary?.avg_mentor_score || 0}/10`}
                    icon={Activity}
                />
                <StatCard
                    label="Avg. Engagement"
                    value={`${summary?.avg_engagement || 0}/10`}
                    icon={Users}
                />
                <StatCard
                    label="Improvement"
                    value={`${summary?.improvement_percent > 0 ? '+' : ''}${summary?.improvement_percent || 0}%`}
                    icon={TrendingUp}
                    trend={summary?.improvement_percent}
                />
            </div>

            {/* Performance Breakdown & Recent Sessions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Performance Breakdown */}
                <div className="bg-white border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                    <h3 className="text-xl font-black uppercase mb-6 border-b-4 border-black pb-2">
                        Performance Breakdown
                    </h3>
                    <div className="space-y-4">
                        <ScoreBar label="Overall Score" score={summary?.avg_mentor_score || 0} />
                        <ScoreBar label="Engagement" score={summary?.avg_engagement || 0} />
                        <ScoreBar label="Communication" score={summary?.avg_communication || 0} />
                        <ScoreBar label="Technical" score={summary?.avg_technical || 0} />
                        <ScoreBar label="Pacing" score={summary?.avg_pacing || 0} />
                    </div>
                </div>

                {/* Recent Sessions */}
                <div className="bg-white border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                    <div className="flex items-center justify-between mb-6 border-b-4 border-black pb-2">
                        <h3 className="text-xl font-black uppercase">Recent Sessions</h3>
                        <button
                            onClick={() => navigate('/sessions')}
                            className="text-sm font-bold uppercase text-gray-600 hover:text-black flex items-center"
                        >
                            View All <ArrowRight className="h-4 w-4 ml-1" />
                        </button>
                    </div>
                    {recent_sessions && recent_sessions.length > 0 ? (
                        <div className="space-y-2">
                            {recent_sessions.map((session) => (
                                <RecentSessionCard
                                    key={session.id}
                                    session={session}
                                    onClick={() => navigate(
                                        session.status === 'complete'
                                            ? `/results?session_id=${session.id}`
                                            : `/status?session_id=${session.id}`
                                    )}
                                />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-400">
                            <FileVideo className="mx-auto h-12 w-12 mb-4" />
                            <p className="font-bold uppercase">No sessions yet</p>
                            <button
                                onClick={() => navigate('/upload')}
                                className="mt-4 px-4 py-2 bg-black text-white font-bold uppercase border-2 border-black hover:bg-white hover:text-black transition-all"
                            >
                                Upload Your First Video
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Score Distribution */}
                <div className="bg-white border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                    <h3 className="text-xl font-black uppercase mb-6 border-b-4 border-black pb-2">
                        Score Distribution
                    </h3>
                    {score_distribution && Object.values(score_distribution).some(v => v > 0) ? (
                        <ScoreDistributionChart distribution={score_distribution} />
                    ) : (
                        <div className="h-32 flex items-center justify-center text-gray-400 font-bold uppercase">
                            Complete more sessions to see distribution
                        </div>
                    )}
                </div>

                {/* Score Trend */}
                <div className="bg-white border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                    <h3 className="text-xl font-black uppercase mb-6 border-b-4 border-black pb-2">
                        Score Trend
                    </h3>
                    <ScoreTrendChart history={score_history} />
                </div>
            </div>

            {/* Achievements / Gamification */}
            <Achievements stats={{
                ...summary,
                highest_score: summary?.highest_score || summary?.avg_mentor_score || 0,
                total_duration_minutes: summary?.total_duration_minutes || 0,
                streak: summary?.streak || 0
            }} />

            {/* Certificate Generator */}
            <CertificateGenerator user={user} stats={summary} />



            {/* Time Machine - Progress Tracker */}
            <TimeMachine />

            {/* Comparative Analytics Row */}
            <div className="grid grid-cols-1 gap-8">
                <WeakAreasPanel
                    userScores={{
                        engagement: summary?.avg_engagement,
                        communication_clarity: summary?.avg_communication,
                        technical_correctness: summary?.avg_technical,
                        pacing_structure: summary?.avg_pacing,
                        interactive_quality: summary?.avg_engagement  // Use engagement as proxy
                    }}
                />
            </div>

            {/* Quick Actions */}
            <div className="bg-white border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                <h3 className="text-xl font-black uppercase mb-6 border-b-4 border-black pb-2">
                    Quick Actions
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                    <button
                        onClick={() => navigate('/live-practice')}
                        className="p-4 bg-yellow-400 text-black font-bold uppercase border-2 border-black hover:bg-yellow-500 transition-all flex items-center justify-center shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]"
                    >
                        <Zap className="h-5 w-5 mr-2" />
                        Live Practice
                    </button>
                    <button
                        onClick={() => navigate('/upload')}
                        className="p-4 bg-black text-white font-bold uppercase border-2 border-black hover:bg-white hover:text-black transition-all flex items-center justify-center"
                    >
                        <FileVideo className="h-5 w-5 mr-2" />
                        Upload New Video
                    </button>
                    <button
                        onClick={() => navigate('/sessions')}
                        className="p-4 bg-white text-black font-bold uppercase border-2 border-black hover:bg-black hover:text-white transition-all flex items-center justify-center"
                    >
                        <BarChart2 className="h-5 w-5 mr-2" />
                        View All Sessions
                    </button>
                    <button
                        onClick={() => recent_sessions?.[0] && navigate(`/results?session_id=${recent_sessions[0].id}`)}
                        disabled={!recent_sessions?.[0] || recent_sessions[0].status !== 'complete'}
                        className="p-4 bg-white text-black font-bold uppercase border-2 border-black hover:bg-black hover:text-white transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Activity className="h-5 w-5 mr-2" />
                        Latest Results
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
