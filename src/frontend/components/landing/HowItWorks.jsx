import React from 'react';
import { Upload, Cpu, FileText, ArrowRight } from 'lucide-react';

const StepCard = ({ number, icon: Icon, title, description }) => (
    <div className="relative group">
        <div className="absolute -top-6 -left-6 text-8xl font-black text-gray-100 select-none z-0 group-hover:text-yellow-100 transition-colors">
            {number}
        </div>
        <div className="relative z-10 bg-white border-4 border-black p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] h-full hover:translate-x-[-4px] hover:translate-y-[-4px] hover:shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] transition-all">
            <div className="bg-black text-white p-3 inline-block mb-6 border-2 border-black">
                <Icon className="h-8 w-8" />
            </div>
            <h3 className="text-2xl font-black uppercase mb-4">{title}</h3>
            <p className="text-lg font-bold text-gray-600">{description}</p>
        </div>
    </div>
);

const HowItWorks = () => {
    return (
        <div className="py-24 bg-gray-50 border-t-4 border-black">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-16">
                    <span className="bg-black text-white px-4 py-1 text-sm font-bold uppercase tracking-widest">Process</span>
                    <h2 className="text-5xl md:text-6xl font-black uppercase mt-4 mb-6">
                        How It Works
                    </h2>
                    <p className="text-xl font-bold text-gray-500 max-w-2xl mx-auto">
                        Three simple steps to transform your teaching delivery.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-12 pt-8">
                    <StepCard
                        number="01"
                        icon={Upload}
                        title="Upload Video"
                        description="Drag & drop your lecture or presentation recording. We handle the rest securely."
                    />
                    <StepCard
                        number="02"
                        icon={Cpu}
                        title="AI Analysis"
                        description="Our multi-modal engine analyzes speech, body language, and content simultaneously."
                    />
                    <StepCard
                        number="03"
                        icon={FileText}
                        title="Get Insights"
                        description="Receive a comprehensive brutalist report with actionable scoring and feedback."
                    />
                </div>
            </div>
        </div>
    );
};

export default HowItWorks;
