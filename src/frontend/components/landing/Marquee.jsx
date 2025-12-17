import React from 'react';

const Marquee = ({ text = "ELEVATE YOUR TEACHING • DATA DRIVEN INSIGHTS • MASTER YOUR CRAFT •" }) => {
    return (
        <div className="bg-yellow-400 border-y-4 border-black py-4 overflow-hidden whitespace-nowrap relative">
            <div className="animate-marquee inline-block">
                <span className="text-2xl font-black uppercase tracking-widest mx-4">
                    {text}
                </span>
                <span className="text-2xl font-black uppercase tracking-widest mx-4">
                    {text}
                </span>
                <span className="text-2xl font-black uppercase tracking-widest mx-4">
                    {text}
                </span>
                <span className="text-2xl font-black uppercase tracking-widest mx-4">
                    {text}
                </span>
            </div>
            <div className="animate-marquee inline-block absolute top-4">
                <span className="text-2xl font-black uppercase tracking-widest mx-4">
                    {text}
                </span>
                <span className="text-2xl font-black uppercase tracking-widest mx-4">
                    {text}
                </span>
                <span className="text-2xl font-black uppercase tracking-widest mx-4">
                    {text}
                </span>
                <span className="text-2xl font-black uppercase tracking-widest mx-4">
                    {text}
                </span>
            </div>
            <style>{`
                .animate-marquee {
                    animation: marquee 20s linear infinite;
                }
                @keyframes marquee {
                    0% { transform: translateX(0); }
                    100% { transform: translateX(-100%); }
                }
            `}</style>
        </div>
    );
};

export default Marquee;
