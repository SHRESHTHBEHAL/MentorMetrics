import React, { useState, useRef, useEffect } from 'react';
import {
    Play,
    Pause,
    Clock,
    AlertTriangle,
    Eye,
    MessageCircle,
    Hand,
    Volume2,
    ChevronRight,
    Lightbulb,
    Target
} from 'lucide-react';

// Moment types and their visual styles
const MOMENT_TYPES = {
    filler_word: {
        icon: MessageCircle,
        color: 'bg-red-500',
        label: 'Filler Word',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-300'
    },
    long_pause: {
        icon: Clock,
        color: 'bg-yellow-500',
        label: 'Long Pause',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-300'
    },
    eye_contact_lost: {
        icon: Eye,
        color: 'bg-purple-500',
        label: 'Eye Contact Lost',
        bgColor: 'bg-purple-50',
        borderColor: 'border-purple-300'
    },
    low_volume: {
        icon: Volume2,
        color: 'bg-orange-500',
        label: 'Low Volume',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-300'
    },
    no_gestures: {
        icon: Hand,
        color: 'bg-blue-500',
        label: 'Static Posture',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-300'
    },
    speaking_too_fast: {
        icon: AlertTriangle,
        color: 'bg-pink-500',
        label: 'Too Fast',
        bgColor: 'bg-pink-50',
        borderColor: 'border-pink-300'
    }
};

// Generate coaching insights from transcript and metrics
const generateCoachingMoments = (transcript, audioData, visualData) => {
    const moments = [];
    const segments = transcript?.segments || [];

    // Analyze transcript for filler words
    const fillerWords = ['um', 'uh', 'like', 'you know', 'actually', 'basically', 'literally', 'so'];

    segments.forEach((segment, idx) => {
        const text = (segment.text || '').toLowerCase();
        const timestamp = segment.start || idx * 5;

        // Check for filler words
        fillerWords.forEach(filler => {
            if (text.includes(filler)) {
                moments.push({
                    id: `filler-${idx}-${filler}`,
                    type: 'filler_word',
                    timestamp: timestamp,
                    duration: 2,
                    text: segment.text,
                    issue: `Used filler word: "${filler}"`,
                    explanation: `At ${formatTime(timestamp)}, you said "${filler}". This can make you sound less confident. Try replacing it with a brief pause instead.`,
                    tip: "Practice pausing silently instead of filling the void with words."
                });
            }
        });

        // Check for long pauses (if next segment starts much later)
        if (idx < segments.length - 1) {
            const gap = (segments[idx + 1].start || 0) - (segment.end || segment.start + 2);
            if (gap > 3) {
                moments.push({
                    id: `pause-${idx}`,
                    type: 'long_pause',
                    timestamp: segment.end || timestamp + 2,
                    duration: gap,
                    text: `${gap.toFixed(1)}s silence`,
                    issue: `${gap.toFixed(1)} second pause`,
                    explanation: `At ${formatTime(segment.end || timestamp)}, there was a ${gap.toFixed(1)} second pause. While strategic pauses are good, this one seemed unintentional.`,
                    tip: "If you need to think, acknowledge it: 'Let me think about that for a moment.'"
                });
            }
        }
    });

    // Add some visual-based moments if data available
    if (visualData?.low_eye_contact_moments) {
        visualData.low_eye_contact_moments.forEach((moment, idx) => {
            moments.push({
                id: `eye-${idx}`,
                type: 'eye_contact_lost',
                timestamp: moment.timestamp || idx * 15,
                duration: moment.duration || 3,
                text: 'Looking away from camera',
                issue: 'Eye contact broken',
                explanation: `At ${formatTime(moment.timestamp || idx * 15)}, you looked away from the camera for an extended period. This can reduce audience engagement.`,
                tip: "Imagine you're speaking to a friend through the camera lens."
            });
        });
    }

    // Sort by timestamp
    moments.sort((a, b) => a.timestamp - b.timestamp);

    // Limit to top 10 most impactful moments
    return moments.slice(0, 10);
};

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
};

// Individual Moment Card
const MomentCard = ({ moment, isSelected, onClick, onSeek }) => {
    const config = MOMENT_TYPES[moment.type] || MOMENT_TYPES.filler_word;
    const Icon = config.icon;

    return (
        <div
            onClick={onClick}
            className={`cursor-pointer border-2 p-4 transition-all ${isSelected
                    ? `${config.bgColor} ${config.borderColor} shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]`
                    : 'bg-white border-black hover:bg-gray-50'
                }`}
        >
            <div className="flex items-start justify-between">
                <div className="flex items-center">
                    <div className={`${config.color} p-2 mr-3`}>
                        <Icon className="w-4 h-4 text-white" />
                    </div>
                    <div>
                        <div className="font-bold text-sm uppercase">{config.label}</div>
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onSeek(moment.timestamp);
                            }}
                            className="text-xs text-gray-500 hover:text-black flex items-center"
                        >
                            <Clock className="w-3 h-3 mr-1" />
                            {formatTime(moment.timestamp)}
                            <ChevronRight className="w-3 h-3 ml-1" />
                        </button>
                    </div>
                </div>
            </div>

            {isSelected && (
                <div className="mt-4 space-y-3">
                    <div className="text-sm text-gray-700">
                        <strong>What happened:</strong> {moment.issue}
                    </div>
                    <div className="text-sm text-gray-600 italic">
                        "{moment.text}"
                    </div>
                    <div className={`p-3 ${config.bgColor} border ${config.borderColor}`}>
                        <div className="flex items-start">
                            <Lightbulb className="w-4 h-4 mr-2 mt-0.5 text-yellow-600" />
                            <div>
                                <div className="text-sm font-bold text-gray-800">AI Coach Says:</div>
                                <div className="text-sm text-gray-700 mt-1">{moment.explanation}</div>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center text-xs text-gray-500 bg-gray-100 p-2">
                        <Target className="w-3 h-3 mr-2" />
                        <strong>Quick Tip:</strong>&nbsp;{moment.tip}
                    </div>
                </div>
            )}
        </div>
    );
};

// Timeline visualization
const Timeline = ({ moments, duration, onSeek, currentTime }) => {
    if (!duration) duration = 120; // Default 2 min

    return (
        <div className="relative h-12 bg-gray-200 border-2 border-black mb-4">
            {/* Progress bar */}
            <div
                className="absolute top-0 left-0 h-full bg-gray-300"
                style={{ width: `${(currentTime / duration) * 100}%` }}
            />

            {/* Moment markers */}
            {moments.map((moment) => {
                const config = MOMENT_TYPES[moment.type];
                const position = (moment.timestamp / duration) * 100;

                return (
                    <button
                        key={moment.id}
                        onClick={() => onSeek(moment.timestamp)}
                        className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 ${config.color} border-2 border-white shadow-md hover:scale-125 transition-transform cursor-pointer`}
                        style={{ left: `${Math.min(position, 97)}%` }}
                        title={`${config.label} at ${formatTime(moment.timestamp)}`}
                    />
                );
            })}

            {/* Current time indicator */}
            <div
                className="absolute top-0 h-full w-0.5 bg-black"
                style={{ left: `${(currentTime / duration) * 100}%` }}
            />
        </div>
    );
};

// Main Coaching Timeline Component
const CoachingTimeline = ({ transcript, audioData, visualData, videoUrl, videoDuration }) => {
    const videoRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [selectedMoment, setSelectedMoment] = useState(null);
    const [moments, setMoments] = useState([]);

    useEffect(() => {
        const generatedMoments = generateCoachingMoments(transcript, audioData, visualData);
        setMoments(generatedMoments);
        if (generatedMoments.length > 0) {
            setSelectedMoment(generatedMoments[0].id);
        }
    }, [transcript, audioData, visualData]);

    const handleSeek = (timestamp) => {
        if (videoRef.current) {
            videoRef.current.currentTime = timestamp;
            setCurrentTime(timestamp);
        }
    };

    const handleTimeUpdate = () => {
        if (videoRef.current) {
            setCurrentTime(videoRef.current.currentTime);
        }
    };

    const togglePlay = () => {
        if (videoRef.current) {
            if (isPlaying) {
                videoRef.current.pause();
            } else {
                videoRef.current.play();
            }
            setIsPlaying(!isPlaying);
        }
    };

    if (moments.length === 0) {
        return (
            <div className="bg-white border-4 border-black p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                <div className="flex items-center mb-4">
                    <Target className="w-6 h-6 mr-3 text-green-600" />
                    <h3 className="text-xl font-black uppercase">AI Coach Review</h3>
                </div>
                <div className="text-center py-8">
                    <div className="text-6xl mb-4">🎉</div>
                    <h4 className="text-xl font-black uppercase text-green-600 mb-2">Great Job!</h4>
                    <p className="text-gray-600">No major issues detected in this session.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            {/* Header */}
            <div className="flex items-center justify-between mb-6 border-b-4 border-black pb-4">
                <div className="flex items-center">
                    <Target className="w-6 h-6 mr-3 text-purple-600" />
                    <div>
                        <h3 className="text-xl font-black uppercase">AI Coach Review</h3>
                        <p className="text-xs text-gray-500 font-bold">Click any moment to learn more</p>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-2xl font-black text-red-600">{moments.length}</div>
                    <div className="text-xs font-bold text-gray-500 uppercase">Areas to Improve</div>
                </div>
            </div>

            {/* Video Player (if URL available) */}
            {videoUrl && (
                <div className="mb-6">
                    <div className="relative bg-black border-4 border-black">
                        <video
                            ref={videoRef}
                            src={videoUrl}
                            className="w-full aspect-video"
                            onTimeUpdate={handleTimeUpdate}
                            onPlay={() => setIsPlaying(true)}
                            onPause={() => setIsPlaying(false)}
                        />
                        <button
                            onClick={togglePlay}
                            className="absolute bottom-4 left-4 p-2 bg-white border-2 border-black"
                        >
                            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                        </button>
                        <div className="absolute bottom-4 right-4 px-3 py-1 bg-black text-white font-mono text-sm">
                            {formatTime(currentTime)}
                        </div>
                    </div>

                    {/* Timeline */}
                    <Timeline
                        moments={moments}
                        duration={videoDuration || 120}
                        onSeek={handleSeek}
                        currentTime={currentTime}
                    />
                </div>
            )}

            {/* Moment Cards */}
            <div className="space-y-3">
                <h4 className="font-black uppercase text-sm text-gray-600 mb-2">
                    Coaching Moments ({moments.length})
                </h4>
                {moments.map((moment) => (
                    <MomentCard
                        key={moment.id}
                        moment={moment}
                        isSelected={selectedMoment === moment.id}
                        onClick={() => setSelectedMoment(
                            selectedMoment === moment.id ? null : moment.id
                        )}
                        onSeek={handleSeek}
                    />
                ))}
            </div>

            {/* Summary */}
            <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200">
                <div className="flex items-center mb-2">
                    <Lightbulb className="w-5 h-5 mr-2 text-purple-600" />
                    <span className="font-black uppercase text-sm text-purple-800">Focus Areas</span>
                </div>
                <p className="text-sm text-purple-700">
                    {moments.filter(m => m.type === 'filler_word').length > 2 &&
                        "Work on reducing filler words. "
                    }
                    {moments.filter(m => m.type === 'long_pause').length > 1 &&
                        "Practice smoother transitions between thoughts. "
                    }
                    {moments.filter(m => m.type === 'eye_contact_lost').length > 1 &&
                        "Try to maintain more consistent eye contact. "
                    }
                    {moments.length <= 3 && "You're doing great! Just a few minor areas to polish."}
                </p>
            </div>
        </div>
    );
};

export default CoachingTimeline;
