import React, { useState, useEffect } from 'react';
import {
    RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { Maximize2, Minimize2, BarChart2, Activity } from 'lucide-react';

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const ParameterChart = ({ scores }) => {
    const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
    const [chartType, setChartType] = useState('radar'); // 'radar' or 'bar'

    useEffect(() => {
        const handleResize = () => {
            const mobile = window.innerWidth < 768;
            setIsMobile(mobile);
            if (mobile) setChartType('bar');
            else setChartType('radar');
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const data = [
        { subject: 'Engagement', A: scores?.engagement || 0, fullMark: 10 },
        { subject: 'Clarity', A: scores?.communication_clarity || 0, fullMark: 10 },
        { subject: 'Technical', A: scores?.technical_correctness || 0, fullMark: 10 },
        { subject: 'Pacing', A: scores?.pacing_structure || 0, fullMark: 10 },
        { subject: 'Interactive', A: scores?.interactive_quality || 0, fullMark: 10 },
    ];

    const toggleChartType = () => {
        setChartType(prev => prev === 'radar' ? 'bar' : 'radar');
    };

    return (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 relative">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">Performance Metrics</h3>
                {!isMobile && (
                    <button
                        onClick={toggleChartType}
                        className="p-1.5 rounded-md hover:bg-gray-100 text-gray-500 transition-colors"
                        title={chartType === 'radar' ? "Switch to Bar Chart" : "Switch to Radar Chart"}
                    >
                        {chartType === 'radar' ? <BarChart2 className="w-5 h-5" /> : <Activity className="w-5 h-5" />}
                    </button>
                )}
            </div>

            <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    {chartType === 'radar' ? (
                        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12, fill: '#6b7280' }} />
                            <PolarRadiusAxis angle={30} domain={[0, 10]} tick={false} axisLine={false} />
                            <Radar
                                name="Score"
                                dataKey="A"
                                stroke="#4f46e5"
                                fill="#4f46e5"
                                fillOpacity={0.6}
                            />
                            <Tooltip
                                contentStyle={{ borderRadius: '0.375rem', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                                itemStyle={{ color: '#4f46e5', fontWeight: 600 }}
                            />
                        </RadarChart>
                    ) : (
                        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                            <XAxis type="number" domain={[0, 10]} hide />
                            <YAxis dataKey="subject" type="category" width={80} tick={{ fontSize: 12, fill: '#6b7280' }} />
                            <Tooltip
                                cursor={{ fill: 'transparent' }}
                                contentStyle={{ borderRadius: '0.375rem', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                            />
                            <Bar dataKey="A" radius={[0, 4, 4, 0]} barSize={20}>
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Bar>
                        </BarChart>
                    )}
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default ParameterChart;
