import React from 'react';
import { Shield, AlertTriangle, CheckCircle, Info } from 'lucide-react';

const ConfidenceIndicator = ({
    confidence = 0.85,
    interval = [7.2, 7.8],
    showDetails = true
}) => {
    const getConfidenceLevel = (conf) => {
        if (conf >= 0.9) return { label: 'Very High', color: 'text-green-600', bg: 'bg-green-100' };
        if (conf >= 0.8) return { label: 'High', color: 'text-green-600', bg: 'bg-green-50' };
        if (conf >= 0.7) return { label: 'Moderate', color: 'text-yellow-600', bg: 'bg-yellow-50' };
        if (conf >= 0.6) return { label: 'Low', color: 'text-orange-600', bg: 'bg-orange-50' };
        return { label: 'Very Low', color: 'text-red-600', bg: 'bg-red-50' };
    };

    const level = getConfidenceLevel(confidence);
    const percentConfidence = Math.round(confidence * 100);

    return (
        <div className={`p-3 border-2 border-black ${level.bg}`}>
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center">
                    <Shield className={`w-4 h-4 mr-2 ${level.color}`} />
                    <span className="text-xs font-bold uppercase text-gray-600">
                        Confidence Level
                    </span>
                </div>
                <span className={`font-black ${level.color}`}>
                    {level.label}
                </span>
            </div>

            {/* Confidence Bar */}
            <div className="h-2 bg-gray-200 border border-black mb-2">
                <div
                    className={`h-full transition-all ${confidence >= 0.8 ? 'bg-green-500' :
                            confidence >= 0.6 ? 'bg-yellow-500' :
                                'bg-red-500'
                        }`}
                    style={{ width: `${percentConfidence}%` }}
                />
            </div>

            {showDetails && (
                <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center text-gray-500">
                        <CheckCircle className="w-3 h-3 mr-1 text-green-500" />
                        <span>Bias mitigation applied</span>
                    </div>
                    {interval && (
                        <div className="font-mono text-gray-600">
                            Score range: {interval[0]} - {interval[1]}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ConfidenceIndicator;
