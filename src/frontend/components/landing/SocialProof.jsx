import React from 'react';

const Metric = ({ value, label }) => (
    <div className="text-center group">
        <div className="text-5xl md:text-6xl font-black mb-2 group-hover:scale-110 transition-transform duration-300">
            {value}
        </div>
        <div className="text-sm font-bold uppercase tracking-widest text-gray-500 group-hover:text-black transition-colors">
            {label}
        </div>
    </div>
);

const SocialProof = () => {
    return (
        <div className="bg-white border-y-4 border-black py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                    <Metric value="10k+" label="Educators" />
                    <Metric value="500+" label="Universities" />
                    <Metric value="1M+" label="Minutes Analyzed" />
                    <Metric value="98%" label="Improvement Rate" />
                </div>
            </div>
        </div>
    );
};

export default SocialProof;
