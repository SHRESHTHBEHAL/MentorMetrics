import React, { useState, useMemo } from 'react';
import { Search, ChevronDown, ChevronUp, Clock, FileText, Download } from 'lucide-react';

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const TranscriptSegment = ({ segment, searchTerm }) => {
    const [isExpanded, setIsExpanded] = useState(true);

    const highlightText = (text, term) => {
        if (!term) return text;
        const parts = text.split(new RegExp(`(${term})`, 'gi'));
        return parts.map((part, index) =>
            part.toLowerCase() === term.toLowerCase() ? (
                <span key={index} className="bg-yellow-200 font-medium">{part}</span>
            ) : part
        );
    };

    return (
        <div className="border-b border-gray-100 last:border-0 hover:bg-gray-50 transition-colors duration-150">
            <div
                className="flex items-start p-3 cursor-pointer group"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex-shrink-0 w-24 text-xs text-gray-500 font-mono mt-1 flex items-center">
                    <Clock className="w-3 h-3 mr-1 opacity-50" />
                    {formatTime(segment.start)} - {formatTime(segment.end)}
                </div>

                <div className="flex-grow min-w-0 ml-4">
                    <div className={`text-sm text-gray-800 leading-relaxed ${!isExpanded ? 'truncate' : ''}`}>
                        {highlightText(segment.text, searchTerm)}
                    </div>
                </div>

                <div className="flex-shrink-0 ml-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
            </div>
        </div>
    );
};

const TranscriptViewer = ({ segments = [], fullText = "" }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [isMobileCollapsed, setIsMobileCollapsed] = useState(true);

    const filteredSegments = useMemo(() => {
        if (!searchTerm) return segments;
        return segments.filter(seg =>
            seg.text.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [segments, searchTerm]);

    const handleDownload = (e) => {
        e.stopPropagation();
        const element = document.createElement("a");
        const file = new Blob([fullText || segments.map(s => s.text).join('\n')], { type: 'text/plain' });
        element.href = URL.createObjectURL(file);
        element.download = "transcript.txt";
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    if (!segments || segments.length === 0) {
        return (
            <div className="p-8 text-center text-gray-500 bg-gray-50 border-4 border-black">
                <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="font-bold uppercase">No transcript segments available.</p>
                {fullText && (
                    <div className="mt-4 p-4 bg-white border-2 border-black text-left text-sm max-h-48 overflow-y-auto font-mono">
                        {fullText}
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className={`bg-white border-4 border-black flex flex-col ${isMobileCollapsed ? 'h-auto' : 'h-[500px]'} sm:h-[500px] transition-all duration-300`}>
            {/* Header */}
            <div
                className="px-4 py-3 border-b-4 border-black flex flex-col sm:flex-row sm:items-center justify-between bg-black text-white sticky top-0 z-10 cursor-pointer sm:cursor-default"
                onClick={() => window.innerWidth < 640 && setIsMobileCollapsed(!isMobileCollapsed)}
            >
                <div className="flex items-center justify-between w-full sm:w-auto mb-2 sm:mb-0">
                    <h3 className="font-black uppercase flex items-center tracking-wider">
                        <FileText className="w-4 h-4 mr-2" />
                        Transcript
                        <span className="ml-2 text-xs font-bold text-black bg-white px-2 py-0.5">
                            {filteredSegments.length} SEGMENTS
                        </span>
                    </h3>
                    <div className="sm:hidden text-white">
                        {isMobileCollapsed ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
                    </div>
                </div>

                <div className="flex items-center space-x-2 w-full sm:w-auto">
                    <div className={`relative flex-grow sm:w-64 ${isMobileCollapsed ? 'hidden sm:block' : 'block'}`} onClick={(e) => e.stopPropagation()}>
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Search className="h-4 w-4 text-gray-500" />
                        </div>
                        <input
                            type="text"
                            className="block w-full pl-10 pr-3 py-1.5 border-2 border-white bg-black text-white placeholder-gray-400 focus:outline-none focus:border-gray-300 sm:text-sm font-bold uppercase transition duration-150 ease-in-out"
                            placeholder="SEARCH TRANSCRIPT..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button
                        onClick={handleDownload}
                        className="p-1.5 bg-white text-black border-2 border-white hover:bg-gray-200 transition-colors"
                        title="Download Transcript"
                    >
                        <Download className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Content */}
            <div className={`flex-grow overflow-y-auto scroll-smooth ${isMobileCollapsed ? 'hidden sm:block' : 'block'}`}>
                {filteredSegments.length > 0 ? (
                    <div className="divide-y-2 divide-gray-100">
                        {filteredSegments.map((segment, index) => (
                            <TranscriptSegment
                                key={index}
                                segment={segment}
                                searchTerm={searchTerm}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="p-8 text-center text-gray-500 font-bold uppercase">
                        <p>No matching segments found.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TranscriptViewer;
