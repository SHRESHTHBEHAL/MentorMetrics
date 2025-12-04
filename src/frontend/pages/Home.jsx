import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckSquare, Terminal, Cpu } from 'lucide-react';

const Home = () => {
    return (
        <div className="min-h-screen bg-white text-black font-mono">
            {/* Hero Section */}
            <div className="border-b-4 border-black">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
                    <div className="max-w-4xl">
                        <h1 className="text-4xl sm:text-6xl md:text-8xl font-black tracking-tighter mb-8 uppercase leading-none">
                            Elevate Your <span className="bg-black text-white px-4">Teaching</span>
                        </h1>
                        <p className="text-xl md:text-2xl font-bold mb-12 border-l-4 border-black pl-6 py-2">
                            AI-POWERED INSIGHTS FOR THE MODERN EDUCATOR.
                            <br />
                            NO FLUFF. JUST DATA.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-6">
                            <Link to="/upload">
                                <button className="w-full sm:w-auto px-8 py-4 bg-black text-white text-xl font-bold border-4 border-black hover:bg-white hover:text-black transition-all duration-200 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[4px] hover:translate-y-[4px] flex items-center justify-center gap-3">
                                    GET STARTED <ArrowRight className="h-6 w-6" />
                                </button>
                            </Link>
                            {/* View Demo Removed */}
                        </div>
                    </div>
                </div>
            </div>

            {/* Features Grid */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {[
                        {
                            title: 'MULTIMODAL ANALYSIS',
                            description: 'AUDIO. TEXT. VISUAL. WE ANALYZE IT ALL.',
                            icon: <Cpu className="h-12 w-12 mb-4" />
                        },
                        {
                            title: 'INSTANT FEEDBACK',
                            description: 'DETAILED REPORTS IN MINUTES. NOT DAYS.',
                            icon: <Terminal className="h-12 w-12 mb-4" />
                        },
                        {
                            title: 'PROGRESS TRACKING',
                            description: 'WATCH YOUR METRICS CLIMB. DATA DOESN\'T LIE.',
                            icon: <CheckSquare className="h-12 w-12 mb-4" />
                        }
                    ].map((feature, index) => (
                        <div key={index} className="border-4 border-black p-8 hover:bg-black hover:text-white transition-colors duration-300 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                            {feature.icon}
                            <h3 className="text-2xl font-black mb-4 uppercase">{feature.title}</h3>
                            <p className="text-lg font-bold">{feature.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Home;
