import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../../utils/api';
import { useToast } from '../../components/ui/ToastProvider';
import JsonViewer from '../../components/debug/JsonViewer';
import { ChevronDown, ChevronRight, Activity, FileText, Video, Cpu, Database, ArrowLeft } from 'lucide-react';

const DebugPanel = ({ title, icon: Icon, data, defaultOpen = false }) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    return (
        <div className="border border-gray-200 rounded-lg mb-4 overflow-hidden bg-white shadow-sm">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
            >
                <div className="flex items-center gap-3">
                    {Icon && <Icon className="h-5 w-5 text-indigo-600" />}
                    <span className="font-medium text-gray-900">{title}</span>
                </div>
                {isOpen ? <ChevronDown className="h-5 w-5 text-gray-500" /> : <ChevronRight className="h-5 w-5 text-gray-500" />}
            </button>
            {isOpen && (
                <div className="p-4 border-t border-gray-200">
                    <JsonViewer data={data} />
                </div>
            )}
        </div>
    );
};

const SessionDebug = () => {
    const [searchParams] = useSearchParams();
    const sessionId = searchParams.get('session_id');
    const navigate = useNavigate();
    const { showError } = useToast();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!sessionId) {
            navigate('/admin/logs');
            return;
        }

        const fetchDebugData = async () => {
            try {
                const response = await api.get(`/debug/${sessionId}`);
                setData(response.data);
            } catch (err) {
                console.error(err);
                showError('Failed to fetch debug data');
            } finally {
                setLoading(false);
            }
        };

        fetchDebugData();
    }, [sessionId, navigate, showError]);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center mb-8">
                <button onClick={() => navigate(-1)} className="mr-4 p-2 hover:bg-gray-100 rounded-full transition-colors">
                    <ArrowLeft className="h-5 w-5 text-gray-600" />
                </button>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <Cpu className="h-6 w-6 text-indigo-600" />
                        Diagnostic Mode
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">Session: {sessionId}</p>
                </div>
            </div>

            <div className="space-y-2">
                <DebugPanel
                    title="Session Metadata"
                    icon={Database}
                    data={data.session_metadata}
                    defaultOpen={true}
                />

                <DebugPanel
                    title="Raw Transcript"
                    icon={FileText}
                    data={data.transcript}
                />

                <DebugPanel
                    title="Text Analysis (LLM Output)"
                    icon={Activity}
                    data={data.text_evaluation}
                />

                <DebugPanel
                    title="Visual Analysis Metrics"
                    icon={Video}
                    data={data.visual_evaluation}
                />

                <DebugPanel
                    title="Audio Analysis Metrics"
                    icon={Activity}
                    data={data.audio_features}
                />

                <DebugPanel
                    title="Fusion & Final Scores"
                    icon={Cpu}
                    data={data.final_scores}
                />

                <DebugPanel
                    title="Generated Report"
                    icon={FileText}
                    data={data.report}
                />
            </div>
        </div>
    );
};

export default SessionDebug;
