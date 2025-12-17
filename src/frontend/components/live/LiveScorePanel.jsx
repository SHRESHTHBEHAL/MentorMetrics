import React from 'react';
import { Eye, Mic, Hand, Star, Clock, Play } from 'lucide-react';

const MetricBar = ({ label, value, icon: Icon, max = 100, suffix = '%' }) => {
    const percentage = Math.min((value / max) * 100, 100);

    const getColor = () => {
        if (percentage >= 70) return 'bg-green-500';
        if (percentage >= 40) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    return (
        <div className="mb-4">
            <div className="flex items-center justify-between mb-1">
                <div className="flex items-center">
                    <Icon className="w-4 h-4 mr-2" />
                    <span className="text-xs font-bold uppercase text-gray-600">{label}</span>
                </div>
                <span className="text-sm font-black">{value}{suffix}</span>
            </div>
            <div className="w-full h-3 bg-gray-200 border-2 border-black">
                <div
                    className={`h-full transition-all duration-300 ${getColor()}`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
};

const LiveScorePanel = ({ stats, isActive = false }) => {
    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // Show empty state when not recording
    if (!isActive) {
        return (
            <div className="bg-white border-4 border-black p-4 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                <h3 className="text-lg font-black uppercase mb-4 border-b-4 border-black pb-2 flex items-center">
                    <Star className="w-5 h-5 mr-2" />
                    Live Score
                </h3>
                <div className="text-center py-8 text-gray-400">
                    <Play className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    <p className="font-bold uppercase text-sm">Start Recording</p>
                    <p className="text-xs mt-2">Scores will appear once you begin</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white border-4 border-black p-4 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            <h3 className="text-lg font-black uppercase mb-4 border-b-4 border-black pb-2 flex items-center">
                <Star className="w-5 h-5 mr-2" />
                Live Score
            </h3>

            {/* Overall Score */}
            <div className="text-center mb-6 py-4 bg-gray-50 border-2 border-black">
                <div className="text-5xl font-black">{stats.overallScore.toFixed(1)}</div>
                <div className="text-xs font-bold uppercase text-gray-500">/ 10</div>
            </div>

            {/* Individual Metrics */}
            <MetricBar
                label="Eye Contact"
                value={Math.round(stats.eyeContactPercent)}
                icon={Eye}
            />
            <MetricBar
                label="Speaking"
                value={Math.round(stats.speakingPercent)}
                icon={Mic}
            />
            <MetricBar
                label="Gestures"
                value={stats.gestureCount}
                icon={Hand}
                max={10}
                suffix=""
            />

            {/* Session Duration */}
            <div className="mt-6 pt-4 border-t-2 border-black">
                <div className="flex items-center justify-between">
                    <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-2" />
                        <span className="text-xs font-bold uppercase text-gray-600">Duration</span>
                    </div>
                    <span className="text-lg font-black font-mono">
                        {formatTime(stats.sessionDuration)}
                    </span>
                </div>
            </div>
        </div>
    );
};

export default LiveScorePanel;
