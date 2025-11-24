import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/Button';
import { ArrowRight, CheckCircle } from 'lucide-react';

const Home = () => {
    return (
        <div className="space-y-16">
            <div className="text-center space-y-8 py-12">
                <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
                    <span className="block">Elevate Your Teaching</span>
                    <span className="block text-indigo-600">With AI-Powered Insights</span>
                </h1>
                <p className="max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
                    MentorMetrics analyzes your teaching videos using advanced multimodal AI to provide actionable feedback on clarity, engagement, and effectiveness.
                </p>
                <div className="flex justify-center gap-4">
                    <Link to="/upload">
                        <Button className="px-8 py-3 text-lg">
                            Get Started <ArrowRight className="ml-2 h-5 w-5" />
                        </Button>
                    </Link>
                    <Link to="/dashboard">
                        <Button variant="outline" className="px-8 py-3 text-lg">
                            View Demo
                        </Button>
                    </Link>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
                    {[
                        {
                            title: 'Multimodal Analysis',
                            description: 'Combines audio, text, and visual cues for holistic evaluation.'
                        },
                        {
                            title: 'Instant Feedback',
                            description: 'Get detailed reports and scoring within minutes of upload.'
                        },
                        {
                            title: 'Progress Tracking',
                            description: 'Monitor your improvement over time with intuitive dashboards.'
                        }
                    ].map((feature, index) => (
                        <div key={index} className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                            <div className="h-10 w-10 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
                                <CheckCircle className="h-6 w-6 text-indigo-600" />
                            </div>
                            <h3 className="text-lg font-medium text-gray-900">{feature.title}</h3>
                            <p className="mt-2 text-gray-500">{feature.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Home;
