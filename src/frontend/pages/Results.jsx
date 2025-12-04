import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { FileText, Download, ArrowLeft, AlertCircle, CheckCircle } from 'lucide-react';
import Button from '../components/Button';
import LoadingButton from '../components/ui/LoadingButton';
import { getResults } from '../utils/api';
import { useToast } from '../components/ui/ToastProvider';
import TranscriptViewer from '../components/transcript/TranscriptViewer';
import ParameterChart from '../components/charts/ParameterChart';
import MetricBlock from '../components/metrics/MetricBlock';
import EmptyState from '../components/ui/EmptyState';
import DownloadReportButton from '../components/report/DownloadReportButton';
import ExportRawButton from '../components/report/ExportRawButton';
import { recordEvent } from '../utils/analytics';

const ScoreCard = ({ title, score, description }) => {
    return (
        <div className={`p-6 border-4 border-black flex flex-col items-center justify-center text-center h-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] bg-white`}>
            <h3 className="text-sm font-bold uppercase tracking-widest mb-2">{title}</h3>
            <div className="text-5xl font-black mb-2">{score.toFixed(1)}</div>
            {description && <p className="text-xs font-bold text-gray-500 uppercase">{description}</p>}
        </div>
    );
};

const SimpleMetric = ({ label, value, subtext }) => (
    <div className="bg-white p-4 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <div className="text-xs font-bold text-gray-500 uppercase mb-1">{label}</div>
        <div className="text-xl font-black text-black">{value}</div>
        {subtext && <div className="text-xs font-bold text-gray-400 mt-1 uppercase">{subtext}</div>}
    </div>
);

const Results = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const sessionId = searchParams.get('session_id');
    const { showError, showSuccess } = useToast();

    useEffect(() => {
        if (sessionId) {
            recordEvent('page_view', { page: 'results', session_id: sessionId });
        }
    }, [sessionId]);

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!sessionId) {
            navigate('/upload');
            return;
        }

        const fetchData = async () => {
            try {
                const result = await getResults(sessionId);

                if (result.status === 'processing' || result.status === 'pending') {
                    navigate(`/status?session_id=${sessionId}`);
                    return;
                }

                if (result.status === 'failed') {
                    showError('Session processing failed.');
                    navigate(`/status?session_id=${sessionId}`);
                    return;
                }

                setData(result);
            } catch (err) {
                console.error(err);
                showError('Failed to load results.');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [sessionId, navigate, showError]);

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="max-w-7xl mx-auto py-12 px-4">
                <EmptyState
                    title="No Results Found"
                    description="We couldn't find any results for this session."
                    actionLabel="Go Back"
                    onAction={() => navigate('/dashboard')}
                />
            </div>
        );
    }

    const radarData = Object.entries(data.scores || {}).map(([key, value]) => ({
        subject: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        A: value,
        fullMark: 10,
    }));

    const durationSeconds = data.transcript?.segments?.length > 0
        ? data.transcript.segments[data.transcript.segments.length - 1].end
        : 0;
    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 border-b-4 border-black pb-6">
                <div>
                    <div className="flex items-center text-sm font-bold text-gray-500 mb-2 uppercase">
                        <button onClick={() => navigate('/dashboard')} className="hover:text-black flex items-center transition-colors">
                            <ArrowLeft className="h-4 w-4 mr-1" /> Back to Dashboard
                        </button>
                        <span className="mx-2">•</span>
                        <span>Session {sessionId.slice(0, 8)}...</span>
                    </div>
                    <h1 className="text-4xl font-black uppercase tracking-tighter text-black">Evaluation Results</h1>
                </div>
                <div className="mt-4 md:mt-0">
                    <DownloadReportButton sessionId={sessionId} />
                </div>
            </div>

            {/* Top Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="md:col-span-1">
                    <ScoreCard
                        title="Overall Mentor Score"
                        score={data.scores?.mentor_score || 0}
                        description="Weighted average across all metrics"
                    />
                </div>
                <div className="md:col-span-3 grid grid-cols-2 md:grid-cols-3 gap-4">
                    <SimpleMetric label="Duration" value={durationSeconds > 0 ? formatDuration(durationSeconds) : "N/A"} />
                    <SimpleMetric label="Words Spoken" value={data.transcript?.segments?.reduce((sum, seg) => sum + (seg.text?.split(' ').length || 0), 0) || "0"} />
                    <SimpleMetric label="WPM" value={data.audio?.wpm || "0"} subtext="Target: 130-150" />
                    <SimpleMetric label="Silence Ratio" value={`${(data.audio?.silence_ratio * 100 || 0).toFixed(1)}%`} />
                    <SimpleMetric label="Clarity" value={data.audio?.clarity_score?.toFixed(1) || "N/A"} />
                    <SimpleMetric label="Engagement" value={data.scores?.engagement?.toFixed(1) || "N/A"} />
                </div>
            </div>


            {/* Charts & Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Parameter Chart */}
                <div className="border-4 border-black p-4 bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                    <ParameterChart scores={data.scores} />
                </div>

                {/* Modality Breakdown */}
                <div className="space-y-4">
                    <h3 className="text-xl font-black uppercase text-black mb-4 border-l-4 border-black pl-4">Category Breakdown</h3>

                    <MetricBlock
                        title="Audio Analysis"
                        score={data.scores?.communication_clarity}
                        description="Clarity, tone, and pacing of speech"
                        rawData={data.audio}
                    />

                    <MetricBlock
                        title="Visual Analysis"
                        score={data.scores?.engagement}
                        description="Eye contact, gestures, and presence"
                        rawData={data.visual}
                    />

                    <MetricBlock
                        title="Content Analysis"
                        score={data.scores?.technical_correctness}
                        description="Accuracy and structure of content"
                        rawData={data.text}
                    />
                </div>
            </div>

            {/* Report Section */}
            <div className="bg-white border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] overflow-hidden mb-8">
                <div className="px-6 py-4 border-b-4 border-black bg-black text-white">
                    <h3 className="text-xl font-black uppercase flex items-center">
                        <FileText className="h-6 w-6 mr-3" />
                        Detailed Report
                    </h3>
                </div>
                <div className="p-8">
                    <div className="prose max-w-none font-mono">
                        <div className="mb-8">
                            <h4 className="text-lg font-black uppercase text-black mb-2 border-b-2 border-black inline-block">Executive Summary</h4>
                            <p className="text-gray-800 mt-2 leading-relaxed">{data.report?.summary || "No summary available."}</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                            <div className="border-2 border-black p-6 bg-gray-50">
                                <h4 className="text-lg font-black uppercase text-black mb-4 flex items-center">
                                    <CheckCircle className="h-5 w-5 mr-2" /> Strengths
                                </h4>
                                <ul className="list-disc pl-5 space-y-2 text-gray-800 font-bold">
                                    {data.report?.strengths?.map((item, i) => (
                                        <li key={i}>{item}</li>
                                    )) || <li>No specific strengths identified.</li>}
                                </ul>
                            </div>
                            <div className="border-2 border-black p-6 bg-gray-50">
                                <h4 className="text-lg font-black uppercase text-black mb-4 flex items-center">
                                    <AlertCircle className="h-5 w-5 mr-2" /> Areas for Improvement
                                </h4>
                                <ul className="list-disc pl-5 space-y-2 text-gray-800 font-bold">
                                    {data.report?.improvements?.map((item, i) => (
                                        <li key={i}>{item}</li>
                                    )) || <li>No specific improvements identified.</li>}
                                </ul>
                            </div>
                        </div>

                        {data.report?.actionable_tips && data.report.actionable_tips.length > 0 && (
                            <div className="border-4 border-black p-6 bg-yellow-50">
                                <h4 className="text-lg font-black uppercase text-black mb-4 flex items-center">
                                    <span className="bg-black text-white px-2 py-1 mr-3 text-sm">PRO TIPS</span>
                                    Actionable Advice
                                </h4>
                                <div className="grid grid-cols-1 gap-4">
                                    {data.report.actionable_tips.map((tip, i) => (
                                        <div key={i} className="flex items-start bg-white border-2 border-black p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                                            <div className="flex-shrink-0 bg-black text-white rounded-full w-6 h-6 flex items-center justify-center font-bold text-xs mt-1 mr-3">
                                                {i + 1}
                                            </div>
                                            <p className="text-gray-900 font-medium">{tip}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Transcript Viewer */}
            <div className="mb-8 border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                <TranscriptViewer
                    segments={data.transcript?.segments}
                    fullText={data.transcript?.text}
                />
            </div>

            {/* Developer Tools */}
            <div className="border-t-4 border-black pt-8 mt-12">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-black uppercase text-black">Developer Tools</h3>
                        <p className="text-sm font-bold text-gray-500 mt-1 uppercase">Export raw pipeline data for debugging and analysis.</p>
                    </div>
                    <ExportRawButton sessionId={sessionId} />
                </div>
            </div>
        </div>
    );
};

export default Results;
