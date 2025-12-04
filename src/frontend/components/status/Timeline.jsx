import React from 'react';
import { CheckCircle, Circle, Loader2, Clock } from 'lucide-react';

const STAGES = [
    { id: 'upload', label: 'Video Uploaded', description: 'Video file received and stored.' },
    { id: 'stt', label: 'Transcript Extracted', description: 'Speech-to-text conversion complete.' },
    { id: 'audio_analysis', label: 'Audio Analysis', description: 'Tone, pitch, and clarity analyzed.' },
    { id: 'visual_analysis', label: 'Visual Analysis', description: 'Gestures and facial expressions analyzed.' },
    { id: 'text_analysis', label: 'Text Analysis', description: 'Content structure and quality evaluated.' },
    { id: 'fusion', label: 'Fusion & Scoring', description: 'Multimodal data combined for final score.' },
    { id: 'report', label: 'Report Generated', description: 'Detailed feedback report created.' },
    { id: 'complete', label: 'Session Complete', description: 'Ready for review.' }
];

const TimelineItem = ({ stage, status, timestamp, isLast }) => {
    let Icon = Circle;
    let colorClass = 'text-gray-300 border-gray-300';
    let bgClass = 'bg-white';
    let lineClass = 'bg-gray-200';

    if (status === 'done') {
        Icon = CheckCircle;
        colorClass = 'text-green-600 border-green-600';
        bgClass = 'bg-green-50';
        lineClass = 'bg-green-600';
    } else if (status === 'in-progress') {
        Icon = Loader2;
        colorClass = 'text-blue-600 border-blue-600';
        bgClass = 'bg-blue-50';
        lineClass = 'bg-gray-200'; // Line stays gray until next step starts
    } else if (status === 'pending') {
        Icon = Circle;
        colorClass = 'text-gray-300 border-gray-300';
        bgClass = 'bg-white';
        lineClass = 'bg-gray-200';
    }

    return (
        <div className="relative flex gap-4 pb-8 last:pb-0">
            {!isLast && (
                <div
                    className={`absolute left-[15px] top-8 bottom-0 w-0.5 ${lineClass} transition-colors duration-500`}
                />
            )}

            <div className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 ${colorClass} ${bgClass} transition-all duration-500`}>
                <Icon className={`h-5 w-5 ${status === 'in-progress' ? 'animate-spin' : ''}`} />
            </div>

            <div className="flex flex-col pt-0.5">
                <div className="flex items-center gap-2">
                    <span className={`text-sm font-medium ${status === 'pending' ? 'text-gray-500' : 'text-gray-900'}`}>
                        {stage.label}
                    </span>
                    {timestamp && (
                        <span className="flex items-center text-xs text-gray-400">
                            <Clock className="mr-1 h-3 w-3" />
                            {new Date(timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                    )}
                </div>
                <p className="text-xs text-gray-500 mt-1">{stage.description}</p>
            </div>
        </div>
    );
};

const Timeline = ({ metadata, status }) => {
    const completedStages = metadata?.stages_completed || [];
    const completionMetadata = metadata?.completion_metadata?.pipeline_stages || {};

    const getStageStatus = (stageId, index) => {
        if (stageId === 'upload' && status !== 'error' && status !== 'failed') {
            return 'done';
        }

        if (status === 'complete') return 'done';
        if (status === 'failed' && !completedStages.includes(stageId)) return 'pending';

        if (completedStages.includes(stageId)) return 'done';

        const prevStageId = index > 0 ? STAGES[index - 1].id : null;
        if (!prevStageId || completedStages.includes(prevStageId)) {
            return 'in-progress';
        }

        return 'pending';
    };

    return (
        <div className="flow-root">
            <ul role="list">
                {STAGES.map((stage, index) => (
                    <li key={stage.id}>
                        <TimelineItem
                            stage={stage}
                            status={getStageStatus(stage.id, index)}
                            timestamp={completionMetadata[`${stage.id}_time_sec`] ? null : null} // Timestamps are durations, not dates. We don't have exact completion times per stage in metadata yet.
                            isLast={index === STAGES.length - 1}
                        />
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Timeline;
