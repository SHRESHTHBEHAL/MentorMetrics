import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Calendar,
    CheckCircle,
    Clock,
    AlertCircle,
    Loader2,
    ArrowRight,
    RefreshCw,
    FileVideo,
    BarChart2
} from 'lucide-react';
import Button from '../components/Button';
import LoadingButton from '../components/ui/LoadingButton';
import { getSessions, restartSession } from '../utils/api';
import { useToast } from '../components/ui/ToastProvider';

const StatusBadge = ({ status }) => {
    const config = {
        pending: { icon: Clock, color: 'text-black', bg: 'bg-yellow-100', text: 'PENDING' },
        processing: { icon: Loader2, color: 'text-black', bg: 'bg-blue-100', text: 'PROCESSING', animate: true },
        complete: { icon: CheckCircle, color: 'text-white', bg: 'bg-black', text: 'COMPLETE' },
        failed: { icon: AlertCircle, color: 'text-white', bg: 'bg-red-600', text: 'FAILED' },
        uploaded: { icon: Clock, color: 'text-black', bg: 'bg-gray-200', text: 'UPLOADED' }
    };

    const current = config[status] || config.pending;
    const Icon = current.icon;

    return (
        <span className={`inline-flex items-center px-4 py-1 border-2 border-black text-xs font-bold uppercase ${current.bg} ${current.color} whitespace-nowrap`}>
            <Icon className={`w-3 h-3 mr-1.5 ${current.animate ? 'animate-spin' : ''}`} />
            {current.text}
        </span>
    );
};

const SessionCard = ({ session, onRestart }) => {
    const navigate = useNavigate();
    const [restarting, setRestarting] = useState(false);

    const handleRestart = async () => {
        setRestarting(true);
        await onRestart(session.id);
        setRestarting(false);
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="bg-white overflow-hidden border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[4px] hover:translate-y-[4px] transition-all duration-200">
            <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                            <div className="h-12 w-12 bg-black text-white flex items-center justify-center border-2 border-black">
                                <FileVideo className="h-6 w-6" />
                            </div>
                        </div>
                        <div>
                            <h3 className="text-lg font-black text-black truncate max-w-[200px] uppercase" title={session.filename}>
                                {session.filename}
                            </h3>
                            <div className="flex items-center text-xs font-bold text-gray-500 mt-1 uppercase">
                                <Calendar className="h-3 w-3 mr-1" />
                                {formatDate(session.created_at)}
                            </div>
                        </div>
                    </div>
                    <StatusBadge status={session.status} />
                </div>

                {session.status === 'complete' && session.mentor_score && (
                    <div className="mb-6 p-4 bg-gray-50 border-2 border-black flex items-center justify-between">
                        <span className="text-sm font-bold text-gray-600 uppercase">Mentor Score</span>
                        <span className="text-2xl font-black text-black">{session.mentor_score}/10</span>
                    </div>
                )}

                <div className="mt-4 flex space-x-3">
                    {session.status === 'complete' ? (
                        <button
                            onClick={() => navigate(`/results?session_id=${session.id}`)}
                            className="w-full flex items-center justify-center px-4 py-2 bg-black text-white border-2 border-black font-bold uppercase hover:bg-white hover:text-black transition-all"
                        >
                            <BarChart2 className="h-4 w-4 mr-2" />
                            View Results
                        </button>
                    ) : session.status === 'failed' ? (
                        <div className="flex space-x-2 w-full">
                            <button
                                onClick={handleRestart}
                                disabled={restarting}
                                className="flex-1 flex items-center justify-center px-4 py-2 bg-white text-black border-2 border-black font-bold uppercase hover:bg-gray-100 transition-all"
                            >
                                <RefreshCw className={`h-4 w-4 mr-2 ${restarting ? 'animate-spin' : ''}`} />
                                Restart
                            </button>
                            <button
                                onClick={() => navigate(`/status?session_id=${session.id}`)}
                                className="flex-1 flex items-center justify-center px-4 py-2 bg-white text-black border-2 border-black font-bold uppercase hover:bg-gray-100 transition-all"
                            >
                                Check Status
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={() => navigate(`/status?session_id=${session.id}`)}
                            className="w-full flex items-center justify-center px-4 py-2 bg-white text-black border-2 border-black font-bold uppercase hover:bg-gray-100 transition-all"
                        >
                            Check Status
                            <ArrowRight className="h-4 w-4 ml-2" />
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

const EmptyState = () => {
    const navigate = useNavigate();

    return (
        <div className="text-center py-12 bg-white border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <FileVideo className="mx-auto h-16 w-16 text-black mb-4" />
            <h3 className="text-xl font-black text-black uppercase">No sessions found</h3>
            <p className="mt-2 text-sm font-bold text-gray-500 uppercase">Get started by uploading a new video.</p>
            <div className="mt-8">
                <button
                    onClick={() => navigate('/upload')}
                    className="px-6 py-3 bg-black text-white border-4 border-black font-black uppercase hover:bg-white hover:text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]"
                >
                    <span className="flex items-center">
                        Upload Video <ArrowRight className="h-5 w-5 ml-2" />
                    </span>
                </button>
            </div>
        </div>
    );
};

const Sessions = () => {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const { showError, showSuccess } = useToast();

    const fetchSessions = async () => {
        try {
            setLoading(true);
            const data = await getSessions();
            setSessions(data);
        } catch (err) {
            console.error(err);
            showError('Failed to load sessions.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSessions();
    }, []);

    const handleRestartSession = async (sessionId) => {
        try {
            await restartSession(sessionId);
            showSuccess('Session restarted successfully.');
            fetchSessions(); // Refresh list
        } catch (err) {
            console.error(err);
            showError('Failed to restart session.');
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <Loader2 className="h-12 w-12 text-black animate-spin" />
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center mb-8 border-b-4 border-black pb-6">
                <div>
                    <h1 className="text-4xl font-black text-black uppercase tracking-tighter">Your Sessions</h1>
                    <p className="mt-2 text-lg font-bold text-gray-500 uppercase">
                        View and manage your teaching evaluation sessions
                    </p>
                </div>
                <button
                    onClick={fetchSessions}
                    className="px-4 py-2 bg-white text-black border-2 border-black font-bold uppercase hover:bg-black hover:text-white transition-all flex items-center"
                >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                </button>
            </div>

            {sessions.length === 0 ? (
                <EmptyState />
            ) : (
                <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
                    {sessions.map((session) => (
                        <SessionCard
                            key={session.id}
                            session={session}
                            onRestart={handleRestartSession}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default Sessions;
