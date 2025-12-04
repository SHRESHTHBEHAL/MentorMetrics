import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { CheckCircle, Clock, AlertCircle, Loader2, ArrowRight, RefreshCw, Play } from 'lucide-react';
import Button from '../components/Button';
import LoadingButton from '../components/ui/LoadingButton';
import { checkStatus, restartSession } from '../utils/api';
import { useToast } from '../components/ui/ToastProvider';
import RetryBox from '../components/ui/RetryBox';
import Timeline from '../components/status/Timeline';
import { recordEvent } from '../utils/analytics';
import { POLLING_INTERVAL_MS } from '../config/appConfig';

const StatusIndicator = ({ status }) => {
    const config = {
        pending: { icon: Clock, color: 'text-black', bg: 'bg-yellow-100', text: 'PENDING' },
        uploaded: { icon: Clock, color: 'text-black', bg: 'bg-yellow-100', text: 'UPLOADED' },
        processing: { icon: Loader2, color: 'text-black', bg: 'bg-blue-100', text: 'PROCESSING', animate: true },
        processing_started: { icon: Loader2, color: 'text-black', bg: 'bg-blue-100', text: 'STARTING...', animate: true },
        processing_stt: { icon: Loader2, color: 'text-black', bg: 'bg-blue-100', text: 'TRANSCRIBING...', animate: true },
        stt_completed: { icon: Loader2, color: 'text-black', bg: 'bg-blue-100', text: 'ANALYZING AUDIO...', animate: true },
        processing_text_eval: { icon: Loader2, color: 'text-black', bg: 'bg-blue-100', text: 'ANALYZING TEXT...', animate: true },
        text_eval_completed: { icon: Loader2, color: 'text-black', bg: 'bg-blue-100', text: 'FINALIZING...', animate: true },
        complete: { icon: CheckCircle, color: 'text-white', bg: 'bg-black', text: 'COMPLETE' },
        failed: { icon: AlertCircle, color: 'text-white', bg: 'bg-red-600', text: 'FAILED' }
    };

    const current = config[status] || config.pending;
    const Icon = current.icon;

    return (
        <div className={`flex items-center p-4 border-4 border-black ${current.bg}`}>
            <Icon className={`h-8 w-8 mr-4 ${current.color} ${current.animate ? 'animate-spin' : ''}`} />
            <span className={`font-black text-xl uppercase ${current.color}`}>{current.text}</span>
        </div>
    );
};

const Status = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const sessionId = searchParams.get('session_id');
    const { showError, showSuccess } = useToast();

    const [statusData, setStatusData] = useState(null);
    const [error, setError] = useState(null);
    const [retrying, setRetrying] = useState(false);
    const [starting, setStarting] = useState(false);
    const pollTimerRef = useRef(null);

    const fetchStatus = async () => {
        try {
            const data = await checkStatus(sessionId);
            setStatusData(data);

            if (data.status === 'complete') {
                showSuccess('Processing complete!');
                setTimeout(() => {
                    navigate(`/results?session_id=${sessionId}`);
                }, 2000); // Increased delay to let user see "Complete" state
            }
        } catch (err) {
            console.error("Status check failed:", err);
            if (err.response && (err.response.status === 404 || err.response.status === 500)) {
                setError('Could not fetch session status.');
                showError('Could not fetch session status.');
            }
        }
    };

    const handleStartProcessing = async () => {
        setStarting(true);
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/process/${sessionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-ID': localStorage.getItem('user_id') || sessionStorage.getItem('user_id') || ''
                }
            });

            if (!response.ok) {
                throw new Error('Failed to start processing');
            }

            showSuccess('Processing started!');
            await fetchStatus();
        } catch (err) {
            console.error('Failed to start processing:', err);
            showError('Failed to start processing. Please try again.');
        } finally {
            setStarting(false);
        }
    };

    useEffect(() => {
        if (!sessionId) {
            setError('No session ID provided.');
            return;
        }

        recordEvent('page_view', { page: 'status', session_id: sessionId });

        fetchStatus();

        pollTimerRef.current = setInterval(() => {
            if (statusData?.status !== 'complete' && statusData?.status !== 'failed') {
                fetchStatus();
            }
        }, POLLING_INTERVAL_MS);

        return () => {
            if (pollTimerRef.current) {
                clearInterval(pollTimerRef.current);
            }
        };
    }, [sessionId]);

    const handleRetry = async () => {
        setRetrying(true);
        try {
            await restartSession(sessionId);
            showSuccess('Session restarted! Processing will begin shortly.');
            await fetchStatus();
        } catch (err) {
            showError('Failed to restart session. Please try again.');
        } finally {
            setRetrying(false);
        }
    };

    if (error) {
        return (
            <div className="max-w-xl mx-auto mt-12 px-4">
                <RetryBox
                    message={error}
                    onRetry={() => navigate('/upload')}
                    retryLabel="Back to Upload"
                />
            </div>
        );
    }

    if (!statusData) {
        return (
            <div className="flex justify-center items-center h-64">
                <Loader2 className="h-12 w-12 text-black animate-spin" />
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-10">
                <h2 className="text-4xl font-black uppercase text-black tracking-tighter">Processing Session</h2>
                <p className="mt-2 text-lg font-bold text-gray-500 uppercase">ID: {sessionId}</p>
            </div>

            <div className="bg-white border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] overflow-hidden mb-8">
                <div className="p-8">
                    <StatusIndicator status={statusData.status} />

                    <div className="mt-8 pl-4 pr-4">
                        <h3 className="text-lg font-black text-black uppercase tracking-wider mb-6 border-b-4 border-black inline-block">
                            Pipeline Progress
                        </h3>
                        <Timeline
                            metadata={statusData.metadata}
                            status={statusData.status}
                        />
                    </div>

                    {(statusData.status === 'uploaded' || statusData.status === 'pending') && (
                        <div className="mt-8 flex justify-center">
                            <button
                                onClick={handleStartProcessing}
                                disabled={starting}
                                className="px-8 py-4 bg-black text-white border-4 border-black font-black uppercase hover:bg-white hover:text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px] flex items-center"
                            >
                                <Play className="h-6 w-6 mr-3" />
                                {starting ? 'STARTING...' : 'START PROCESSING'}
                            </button>
                        </div>
                    )}

                    {statusData.status === 'failed' && (
                        <div className="mt-8 flex justify-center">
                            <button
                                onClick={handleRetry}
                                disabled={retrying}
                                className="px-8 py-4 bg-white text-black border-4 border-black font-black uppercase hover:bg-black hover:text-white transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px] flex items-center"
                            >
                                <RefreshCw className={`h-6 w-6 mr-3 ${retrying ? 'animate-spin' : ''}`} />
                                {retrying ? 'RESTARTING...' : 'RETRY PROCESSING'}
                            </button>
                        </div>
                    )}

                    {statusData.status === 'complete' && (
                        <div className="mt-8 flex justify-center">
                            <button
                                onClick={() => navigate(`/results?session_id=${sessionId}`)}
                                className="px-8 py-4 bg-black text-white border-4 border-black font-black uppercase hover:bg-white hover:text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px] flex items-center"
                            >
                                VIEW RESULTS
                                <ArrowRight className="ml-3 h-6 w-6" />
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Status;
