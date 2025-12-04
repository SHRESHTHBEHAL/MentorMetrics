import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Info } from 'lucide-react';

const MetricBlock = ({ title, score, description, rawData }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    let colorClass = 'bg-gray-500';
    let barColorClass = 'bg-gray-500';

    if (typeof score === 'number') {
        if (score >= 8) {
            colorClass = 'text-green-700 bg-green-50 border-green-200';
            barColorClass = 'bg-green-500';
        } else if (score >= 5) {
            colorClass = 'text-yellow-700 bg-yellow-50 border-yellow-200';
            barColorClass = 'bg-yellow-500';
        } else {
            colorClass = 'text-red-700 bg-red-50 border-red-200';
            barColorClass = 'bg-red-500';
        }
    }

    const hasDetails = rawData && Object.keys(rawData).length > 0;

    return (
        <div className={`rounded-lg border transition-all duration-200 ${isExpanded ? 'shadow-md border-indigo-200' : 'border-gray-200 shadow-sm'} bg-white overflow-hidden`}>
            <div
                className={`p-4 flex items-center justify-between cursor-pointer ${hasDetails ? 'hover:bg-gray-50' : ''}`}
                onClick={() => hasDetails && setIsExpanded(!isExpanded)}
            >
                <div className="flex-1">
                    <div className="flex items-center mb-1">
                        <h4 className="text-sm font-medium text-gray-900 mr-2">{title}</h4>
                        {hasDetails && (
                            <Info className="w-3 h-3 text-gray-400" />
                        )}
                    </div>
                    <p className="text-xs text-gray-500 line-clamp-1">{description}</p>
                </div>

                <div className="flex items-center ml-4">
                    <div className="flex flex-col items-end mr-4 w-24">
                        <span className="text-lg font-bold text-gray-900">
                            {typeof score === 'number' ? score.toFixed(1) : score}
                            <span className="text-xs text-gray-400 font-normal ml-1">/ 10</span>
                        </span>
                        <div className="w-full h-1.5 bg-gray-100 rounded-full mt-1 overflow-hidden">
                            <div
                                className={`h-full rounded-full ${barColorClass}`}
                                style={{ width: `${Math.min(Math.max((score || 0) * 10, 0), 100)}%` }}
                            ></div>
                        </div>
                    </div>

                    {hasDetails && (
                        <div className="text-gray-400">
                            {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                        </div>
                    )}
                </div>
            </div>

            {/* Expanded Details */}
            {isExpanded && hasDetails && (
                <div className="px-4 pb-4 pt-0 bg-gray-50 border-t border-gray-100">
                    <div className="mt-3 grid grid-cols-1 gap-2">
                        {Object.entries(rawData).map(([key, value]) => {
                            if (typeof value === 'object' && value !== null) return null;

                            return (
                                <div key={key} className="flex justify-between text-xs py-1 border-b border-gray-200 last:border-0">
                                    <span className="text-gray-600 font-medium capitalize">
                                        {key.replace(/_/g, ' ')}
                                    </span>
                                    <span className="text-gray-800 font-mono">
                                        {typeof value === 'number' && !Number.isInteger(value)
                                            ? value.toFixed(2)
                                            : String(value)}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
};

export default MetricBlock;
