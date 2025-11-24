import React from 'react';
import { BarChart2, Activity, Users } from 'lucide-react';

const Dashboard = () => {
    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                    Week 3 Preview
                </span>
            </div>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
                {[
                    { label: 'Total Sessions', value: '12', icon: BarChart2 },
                    { label: 'Avg. Engagement', value: '85%', icon: Users },
                    { label: 'Improvement', value: '+15%', icon: Activity },
                ].map((stat, index) => (
                    <div key={index} className="bg-white overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <stat.icon className="h-6 w-6 text-gray-400" />
                                </div>
                                <div className="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt className="text-sm font-medium text-gray-500 truncate">{stat.label}</dt>
                                        <dd className="text-lg font-medium text-gray-900">{stat.value}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="bg-white shadow rounded-lg p-6">
                <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
                    <p className="text-gray-500">Detailed analytics and charts will be implemented in Week 3.</p>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
