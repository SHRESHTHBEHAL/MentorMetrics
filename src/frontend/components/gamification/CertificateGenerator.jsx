import React, { useRef, useState } from 'react';
import html2canvas from 'html2canvas';
import { Award, Download, Share2, Shield, Star, Crown } from 'lucide-react';
import Button from '../Button';

const CertificateGenerator = ({ user, stats }) => {
    const certificateRef = useRef(null);
    const [generating, setGenerating] = useState(false);
    const [customName, setCustomName] = useState('');

    const generateCertificate = async () => {
        // Ask for name, defaulting to email name or "Hackathon Judge"
        const defaultName = user?.email?.includes('judge') ? 'Honorable Judge' : (user?.email?.split('@')[0] || 'Master Communicator');
        const nameInput = window.prompt("Enter the name for the certificate:", defaultName);

        if (!nameInput) return; // Cancelled

        setCustomName(nameInput);
        setGenerating(true);

        // Wait for state to update and render
        setTimeout(async () => {
            try {
                if (certificateRef.current) {
                    const canvas = await html2canvas(certificateRef.current, {
                        scale: 2, // Higher quality
                        backgroundColor: '#ffffff',
                        useCORS: true
                    });

                    const image = canvas.toDataURL('image/png');
                    const link = document.createElement('a');
                    link.href = image;
                    link.download = `MentorMetrics_Certificate_${nameInput.replace(/\s+/g, '_')}.png`;
                    link.click();
                }
            } catch (err) {
                console.error("Certificate generation failed:", err);
            } finally {
                setGenerating(false);
                setCustomName(''); // Reset
            }
        }, 100);
    };

    const currentDate = new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    // Determine rank based on score
    const score = stats?.highest_score || 0;
    let rank = "MENTOR";
    let rankColor = "text-black";

    if (score >= 9) { rank = "MASTER MENTOR"; rankColor = "text-yellow-600"; }
    else if (score >= 8) { rank = "EXPERT COACH"; rankColor = "text-blue-600"; }
    else if (score >= 7) { rank = "SKILLED GUIDE"; rankColor = "text-green-600"; }

    return (
        <div className="mt-8">
            <Button
                onClick={generateCertificate}
                className="w-full bg-yellow-400 text-black border-2 border-black font-black uppercase tracking-wider hover:bg-yellow-500 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px] transition-all flex items-center justify-center p-4 text-lg"
                disabled={generating}
            >
                {generating ? 'Printing...' : '🏅 DOWNLOAD OFFICIAL CERTIFICATE'}
            </Button>

            {/* Hidden Certificate Template */}
            <div style={{ position: 'absolute', left: '-9999px', top: 0 }}>
                <div
                    ref={certificateRef}
                    className="w-[1000px] h-[700px] bg-white border-[20px] border-double border-black p-12 flex flex-col items-center justify-between relative"
                    style={{ fontFamily: 'monospace' }}
                >
                    {/* Decorative Corners */}
                    <div className="absolute top-4 left-4 w-16 h-16 border-t-8 border-l-8 border-black"></div>
                    <div className="absolute top-4 right-4 w-16 h-16 border-t-8 border-r-8 border-black"></div>
                    <div className="absolute bottom-4 left-4 w-16 h-16 border-b-8 border-l-8 border-black"></div>
                    <div className="absolute bottom-4 right-4 w-16 h-16 border-b-8 border-r-8 border-black"></div>

                    {/* Header */}
                    <div className="text-center mt-8">
                        <div className="flex items-center justify-center mb-4">
                            <Crown className="w-16 h-16 text-yellow-500 mr-4" />
                            <h1 className="text-6xl font-black uppercase tracking-tighter">MentorMetrics</h1>
                            <Crown className="w-16 h-16 text-yellow-500 ml-4" />
                        </div>
                        <div className="w-64 h-2 bg-black mx-auto my-6"></div>
                        <h2 className="text-3xl font-bold uppercase tracking-widest text-gray-600">Certificate of Excellence</h2>
                    </div>

                    {/* Content */}
                    <div className="text-center flex-1 flex flex-col justify-center">
                        <p className="text-xl text-gray-500 uppercase font-bold mb-4">This certifies that</p>
                        <h3 className="text-5xl font-black uppercase mb-8 border-b-4 border-black inline-block pb-2 px-8">
                            {customName || user?.email || 'Valued User'}
                        </h3>
                        <p className="text-xl text-gray-500 uppercase font-bold mb-6">Has achieved the rank of</p>
                        <h2 className={`text-6xl font-black uppercase tracking-tight mb-8 ${rankColor}`}>
                            {rank}
                        </h2>

                        <div className="flex justify-center items-center gap-12 mt-8">
                            <div className="text-center p-4 border-4 border-black bg-gray-50">
                                <p className="text-sm font-bold text-gray-500 uppercase">Highest Score</p>
                                <p className="text-5xl font-black">{score.toFixed(1)}</p>
                            </div>
                            <div className="text-center p-4 border-4 border-black bg-gray-50">
                                <p className="text-sm font-bold text-gray-500 uppercase">Sessions</p>
                                <p className="text-5xl font-black">{stats?.total_sessions || 0}</p>
                            </div>
                            <div className="text-center p-4 border-4 border-black bg-gray-50">
                                <p className="text-sm font-bold text-gray-500 uppercase">Level</p>
                                <p className="text-5xl font-black">{Math.floor(score)}</p>
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="w-full flex justify-between items-end border-t-4 border-black pt-8 mt-8">
                        <div className="text-left">
                            <p className="text-lg font-bold uppercase">Date Awarded</p>
                            <p className="text-2xl font-mono">{currentDate}</p>
                        </div>
                        <div className="flex flex-col items-center">
                            <Shield className="w-16 h-16 text-black mb-2" />
                            <p className="text-xs font-bold uppercase tracking-widest">Verified by AI</p>
                        </div>
                        <div className="text-right">
                            <p className="text-lg font-bold uppercase">Signature</p>
                            <p className="text-2xl font-script italic">MentorMetrics AI</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CertificateGenerator;
