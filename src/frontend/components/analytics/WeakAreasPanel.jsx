import React from 'react';
import { AlertTriangle, Target, TrendingUp, ChevronRight } from 'lucide-react';

const WeakAreaCard = ({ area, userScore, platformAvg, tips }) => {
    const diff = userScore - platformAvg;
    const isWeak = diff < 0;
    const percentage = (userScore / 10) * 100;
    const avgPercentage = (platformAvg / 10) * 100;

    return (
        <div className={`p-4 border-2 border-black ${isWeak ? 'bg-red-50' : 'bg-green-50'}`}>
            <div className="flex items-center justify-between mb-2">
                <h4 className="font-bold uppercase text-sm">{area}</h4>
                <span className={`text-xs font-bold px-2 py-1 ${isWeak ? 'bg-red-200 text-red-800' : 'bg-green-200 text-green-800'
                    }`}>
                    {isWeak ? 'NEEDS WORK' : 'STRONG'}
                </span>
            </div>

            {/* Comparison Bars */}
            <div className="space-y-1 mb-3">
                <div className="flex items-center text-xs">
                    <span className="w-12 font-bold">You</span>
                    <div className="flex-1 h-3 bg-gray-200 border border-black mx-2">
                        <div
                            className={`h-full ${isWeak ? 'bg-red-400' : 'bg-green-400'}`}
                            style={{ width: `${percentage}%` }}
                        />
                    </div>
                    <span className="w-8 font-black text-right">{userScore.toFixed(1)}</span>
                </div>
                <div className="flex items-center text-xs">
                    <span className="w-12 text-gray-500">Avg</span>
                    <div className="flex-1 h-3 bg-gray-200 border border-black mx-2">
                        <div
                            className="h-full bg-gray-400"
                            style={{ width: `${avgPercentage}%` }}
                        />
                    </div>
                    <span className="w-8 text-gray-500 text-right">{platformAvg.toFixed(1)}</span>
                </div>
            </div>

            {/* Tips */}
            {tips && tips.length > 0 && (
                <div className="text-xs text-gray-600">
                    <ChevronRight className="w-3 h-3 inline mr-1" />
                    {tips[0]}
                </div>
            )}
        </div>
    );
};

const WeakAreasPanel = ({ userScores = {}, platformAverages = {} }) => {
    // Use actual data, no demo fallbacks
    const scores = {
        engagement: userScores.engagement ?? null,
        communication_clarity: userScores.communication_clarity ?? null,
        technical_correctness: userScores.technical_correctness ?? null,
        pacing_structure: userScores.pacing_structure ?? null,
        interactive_quality: userScores.interactive_quality ?? null,
    };

    // Check if we have any valid scores
    const hasValidScores = Object.values(scores).some(v => v !== null && v !== undefined && v !== 0);

    // Platform averages - These represent typical platform-wide scores
    // In production, fetch from /api/analytics/platform-averages
    const averages = {
        engagement: platformAverages.engagement || 7.5,
        communication_clarity: platformAverages.communication_clarity || 7.2,
        technical_correctness: platformAverages.technical_correctness || 7.0,
        pacing_structure: platformAverages.pacing_structure || 6.8,
        interactive_quality: platformAverages.interactive_quality || 6.5,
    };

    const tips = {
        engagement: ["Maintain more consistent eye contact throughout"],
        communication_clarity: ["Speak more clearly and reduce filler words"],
        technical_correctness: ["Great job! Keep providing accurate information"],
        pacing_structure: ["Work on varying your pace for emphasis"],
        interactive_quality: ["Use more hand gestures and rhetorical questions"],
    };

    const areaLabels = {
        engagement: "Engagement",
        communication_clarity: "Communication",
        technical_correctness: "Technical",
        pacing_structure: "Pacing",
        interactive_quality: "Interactive",
    };

    // If no valid scores, show empty state
    if (!hasValidScores) {
        return (
            <div className="bg-white border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                <div className="flex items-center mb-6 border-b-4 border-black pb-4">
                    <Target className="w-6 h-6 mr-3" />
                    <h3 className="text-xl font-black uppercase">Focus Areas</h3>
                </div>
                <div className="text-center py-8 text-gray-500">
                    <Target className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    <p className="font-bold">No sessions analyzed yet</p>
                    <p className="text-sm mt-2">Upload a teaching video to see your focus areas</p>
                </div>
            </div>
        );
    }

    // Sort areas by how much below average they are (only include valid scores)
    const sortedAreas = Object.entries(scores)
        .filter(([key, value]) => value !== null && value !== undefined)
        .map(([key, value]) => ({
            key,
            userScore: value,
            platformAvg: averages[key],
            diff: value - averages[key]
        }))
        .sort((a, b) => a.diff - b.diff);

    const weakAreas = sortedAreas.filter(a => a.diff < 0);
    const strongAreas = sortedAreas.filter(a => a.diff >= 0);

    return (
        <div className="bg-white border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            {/* Header */}
            <div className="flex items-center mb-6 border-b-4 border-black pb-4">
                <Target className="w-6 h-6 mr-3" />
                <h3 className="text-xl font-black uppercase">Focus Areas</h3>
            </div>

            {/* Weak Areas Section */}
            {weakAreas.length > 0 && (
                <div className="mb-6">
                    <div className="flex items-center mb-3">
                        <AlertTriangle className="w-4 h-4 mr-2 text-red-500" />
                        <h4 className="font-bold text-sm uppercase text-red-700">Needs Improvement</h4>
                    </div>
                    <div className="space-y-3">
                        {weakAreas.slice(0, 3).map(area => (
                            <WeakAreaCard
                                key={area.key}
                                area={areaLabels[area.key]}
                                userScore={area.userScore}
                                platformAvg={area.platformAvg}
                                tips={tips[area.key]}
                            />
                        ))}
                    </div>
                </div>
            )}

            {/* Strong Areas Section */}
            {strongAreas.length > 0 && (
                <div>
                    <div className="flex items-center mb-3">
                        <TrendingUp className="w-4 h-4 mr-2 text-green-500" />
                        <h4 className="font-bold text-sm uppercase text-green-700">Your Strengths</h4>
                    </div>
                    <div className="space-y-3">
                        {strongAreas.slice(0, 2).map(area => (
                            <WeakAreaCard
                                key={area.key}
                                area={areaLabels[area.key]}
                                userScore={area.userScore}
                                platformAvg={area.platformAvg}
                                tips={tips[area.key]}
                            />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default WeakAreasPanel;
