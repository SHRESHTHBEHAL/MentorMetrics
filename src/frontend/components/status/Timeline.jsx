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

// Map backend status to which stages are completed
const STATUS_TO_COMPLETED_STAGES = {
    'pending': [],
    'uploaded': ['upload'],
    'processing_started': ['upload'],
    'processing': ['upload'],
    'processing_stt': ['upload'],
    'stt_completed': ['upload', 'stt'],
    'processing_audio': ['upload', 'stt'],
    'audio_completed': ['upload', 'stt', 'audio_analysis'],
    'processing_visual': ['upload', 'stt', 'audio_analysis'],
    'visual_completed': ['upload', 'stt', 'audio_analysis', 'visual_analysis'],
    'processing_text_eval': ['upload', 'stt', 'audio_analysis', 'visual_analysis'],
    'text_eval_completed': ['upload', 'stt', 'audio_analysis', 'visual_analysis', 'text_analysis'],
    'processing_fusion': ['upload', 'stt', 'audio_analysis', 'visual_analysis', 'text_analysis'],
    'fusion_completed': ['upload', 'stt', 'audio_analysis', 'visual_analysis', 'text_analysis', 'fusion'],
    'processing_report': ['upload', 'stt', 'audio_analysis', 'visual_analysis', 'text_analysis', 'fusion'],
    'report_completed': ['upload', 'stt', 'audio_analysis', 'visual_analysis', 'text_analysis', 'fusion', 'report'],
    'complete': ['upload', 'stt', 'audio_analysis', 'visual_analysis', 'text_analysis', 'fusion', 'report', 'complete'],
    'failed': [] // Will use metadata.stages_completed for failed sessions
};

// Map backend status to the currently in-progress stage
const STATUS_TO_CURRENT_STAGE = {
    'pending': null,
    'uploaded': null,
    'processing_started': 'stt',
    'processing': 'stt',
    'processing_stt': 'stt',
    'stt_completed': 'audio_analysis',
    'processing_audio': 'audio_analysis',
    'audio_completed': 'visual_analysis',
    'processing_visual': 'visual_analysis',
    'visual_completed': 'text_analysis',
    'processing_text_eval': 'text_analysis',
    'text_eval_completed': 'fusion',
    'processing_fusion': 'fusion',
    'fusion_completed': 'report',
    'processing_report': 'report',
    'report_completed': 'complete',
    'complete': null,
    'failed': null
};

const TimelineItem = ({ stage, status, isLast }) => {
    let Icon = Circle;
    let colorClass = 'text-gray-300 border-gray-300';
    let bgClass = 'bg-white';
    let lineClass = 'bg-gray-200';
    let textClass = 'text-gray-400';

    if (status === 'done') {
        Icon = CheckCircle;
        colorClass = 'text-green-600 border-green-600';
        bgClass = 'bg-green-50';
        lineClass = 'bg-green-500';
        textClass = 'text-gray-900';
    } else if (status === 'in-progress') {
        Icon = Loader2;
        colorClass = 'text-blue-600 border-blue-600';
        bgClass = 'bg-blue-50';
        lineClass = 'bg-gray-200';
        textClass = 'text-blue-800';
    } else if (status === 'pending') {
        Icon = Circle;
        colorClass = 'text-gray-300 border-gray-300';
        bgClass = 'bg-white';
        lineClass = 'bg-gray-200';
        textClass = 'text-gray-400';
    }

    return (
        <div className="relative flex gap-4 pb-6 last:pb-0">
            {!isLast && (
                <div
                    className={`absolute left-[15px] top-8 bottom-0 w-0.5 ${lineClass} transition-colors duration-300`}
                />
            )}

            <div className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 ${colorClass} ${bgClass} transition-all duration-300`}>
                <Icon className={`h-4 w-4 ${status === 'in-progress' ? 'animate-spin' : ''}`} />
            </div>

            <div className="flex flex-col pt-0.5 flex-1">
                <span className={`text-sm font-bold ${textClass} transition-colors duration-300`}>
                    {stage.label}
                    {status === 'done' && <span className="ml-2 text-green-600">✓</span>}
                </span>
                <p className={`text-xs ${status === 'pending' ? 'text-gray-400' : 'text-gray-500'} mt-0.5`}>
                    {stage.description}
                </p>
            </div>
        </div>
    );
};

const Timeline = ({ metadata, status }) => {
    // Get completed stages from mapping, with fallback to metadata
    const completedFromStatus = STATUS_TO_COMPLETED_STAGES[status] || [];
    const completedFromMetadata = metadata?.stages_completed || [];

    // Use whichever has more completed stages (in case metadata is more accurate)
    const completedStages = completedFromStatus.length >= completedFromMetadata.length
        ? completedFromStatus
        : completedFromMetadata;

    // Get the currently in-progress stage
    const currentStage = STATUS_TO_CURRENT_STAGE[status] || null;

    const getStageStatus = (stageId) => {
        // Upload is always done once we have status data
        if (stageId === 'upload' && status !== 'pending') {
            return 'done';
        }

        // Check if stage is completed
        if (completedStages.includes(stageId)) {
            return 'done';
        }

        // Check if stage is currently in progress
        if (currentStage === stageId) {
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
                            status={getStageStatus(stage.id)}
                            isLast={index === STAGES.length - 1}
                        />
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Timeline;

