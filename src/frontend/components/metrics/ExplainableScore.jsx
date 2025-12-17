import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Info, CheckCircle, AlertCircle, Lightbulb, Clock } from 'lucide-react';

const ExplainableScore = ({
    title,
    score,
    explanation,
    evidence = [],
    tips = [],
    rawData = {}
}) => {
    const [isExpanded, setIsExpanded] = useState(false);

    const getScoreColor = (score) => {
        if (score >= 8) return { bg: 'bg-green-500', text: 'text-green-700', light: 'bg-green-50' };
        if (score >= 6) return { bg: 'bg-yellow-500', text: 'text-yellow-700', light: 'bg-yellow-50' };
        return { bg: 'bg-red-500', text: 'text-red-700', light: 'bg-red-50' };
    };

    const colors = getScoreColor(score);
    const percentage = (score / 10) * 100;

    return (
        <div className="bg-white border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] overflow-hidden mb-4">
            {/* Header - Always Visible */}
            <div
                className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex items-center justify-between">
                    <div className="flex-1">
                        <div className="flex items-center mb-2">
                            <h4 className="font-black uppercase text-sm">{title}</h4>
                            <Info className="w-4 h-4 ml-2 text-gray-400" />
                        </div>

                        {/* Score Bar */}
                        <div className="flex items-center">
                            <div className="flex-1 h-4 bg-gray-200 border-2 border-black mr-4">
                                <div
                                    className={`h-full ${colors.bg} transition-all duration-500`}
                                    style={{ width: `${percentage}%` }}
                                />
                            </div>
                            <span className="text-2xl font-black w-16 text-right">
                                {score.toFixed(1)}
                            </span>
                        </div>
                    </div>

                    <div className="ml-4 text-gray-400">
                        {isExpanded ? <ChevronUp className="w-6 h-6" /> : <ChevronDown className="w-6 h-6" />}
                    </div>
                </div>

                {/* Brief Explanation - Always Visible */}
                {explanation && (
                    <p className="text-sm text-gray-600 mt-2 font-medium">
                        {explanation}
                    </p>
                )}
            </div>

            {/* Expanded Content */}
            {isExpanded && (
                <div className="border-t-4 border-black">
                    {/* Evidence Section */}
                    {evidence.length > 0 && (
                        <div className="p-4 bg-gray-50 border-b-2 border-black">
                            <h5 className="font-bold uppercase text-xs text-gray-500 mb-3 flex items-center">
                                <Clock className="w-4 h-4 mr-2" />
                                Evidence from Your Session
                            </h5>
                            <div className="space-y-2">
                                {evidence.map((item, idx) => (
                                    <div
                                        key={idx}
                                        className={`flex items-start p-2 border-2 border-black ${item.type === 'positive' ? 'bg-green-50' : 'bg-red-50'
                                            }`}
                                    >
                                        {item.type === 'positive' ? (
                                            <CheckCircle className="w-4 h-4 text-green-600 mr-2 mt-0.5 flex-shrink-0" />
                                        ) : (
                                            <AlertCircle className="w-4 h-4 text-red-600 mr-2 mt-0.5 flex-shrink-0" />
                                        )}
                                        <div className="flex-1">
                                            <span className="text-sm font-medium">{item.text}</span>
                                            {item.timestamp && (
                                                <span className="ml-2 text-xs text-gray-500 font-mono">
                                                    @ {Math.floor(item.timestamp / 60)}:{(item.timestamp % 60).toString().padStart(2, '0')}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Tips Section */}
                    {tips.length > 0 && (
                        <div className="p-4 bg-yellow-50">
                            <h5 className="font-bold uppercase text-xs text-yellow-700 mb-3 flex items-center">
                                <Lightbulb className="w-4 h-4 mr-2" />
                                How to Improve
                            </h5>
                            <ul className="space-y-2">
                                {tips.map((tip, idx) => (
                                    <li key={idx} className="flex items-start">
                                        <span className="bg-yellow-400 text-black rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold mr-2 flex-shrink-0">
                                            {idx + 1}
                                        </span>
                                        <span className="text-sm text-yellow-900 font-medium">{tip}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Raw Data (if available) */}
                    {Object.keys(rawData).length > 0 && (
                        <div className="p-4 bg-gray-100 border-t-2 border-black">
                            <h5 className="font-bold uppercase text-xs text-gray-500 mb-3">
                                Technical Details
                            </h5>
                            <div className="grid grid-cols-2 gap-2 text-xs">
                                {Object.entries(rawData).map(([key, value]) => {
                                    if (typeof value === 'object') return null;

                                    // Check if this item should be full width
                                    const isFullWidth =
                                        key.includes('summary') ||
                                        key.includes('feedback') ||
                                        key.includes('description') ||
                                        (typeof value === 'string' && value.length > 50);

                                    return (
                                        <div
                                            key={key}
                                            className={`flex ${isFullWidth ? 'flex-col col-span-2 gap-1' : 'justify-between items-center'} bg-white p-2 border border-black`}
                                        >
                                            <span className="text-gray-600 capitalize font-bold">{key.replace(/_/g, ' ')}</span>
                                            <span className={`${isFullWidth ? 'text-gray-900 mt-1 leading-relaxed' : 'font-mono font-bold'}`}>
                                                {typeof value === 'number' ? value.toFixed(2) : String(value)}
                                            </span>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ExplainableScore;
