import React, { useState, useEffect } from 'react';
import { Check, Zap, Trophy, Flame } from 'lucide-react';
import confetti from 'canvas-confetti';

const CHALLENGES = [
    { id: 1, text: "Record a 1-min intro without any 'ums'", difficulty: "Hard" },
    { id: 2, text: "Maintain eye contact with the camera for 30s", difficulty: "Medium" },
    { id: 3, text: "Use 3 hand gestures in your next explanation", difficulty: "Easy" },
    { id: 4, text: "Vary your pitch to emphasize key points", difficulty: "Medium" },
    { id: 5, text: "Speak at a slower pace than usual for 1 min", difficulty: "Easy" }
];

const DailyChallenge = () => {
    // Persist completion state for the "day"
    const [completed, setCompleted] = useState(() => {
        const saved = localStorage.getItem('daily_challenge_completed');
        const date = localStorage.getItem('daily_challenge_date');
        const today = new Date().toDateString();
        return saved === 'true' && date === today;
    });

    const [challenge, setChallenge] = useState(() => {
        // Pick a consistent challenge for the day based on date
        const today = new Date().toDateString();
        const dateNum = new Date().getDate();
        return CHALLENGES[dateNum % CHALLENGES.length];
    });

    const handleComplete = () => {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#000000', '#FCD34D', '#FFFFFF'] // Black, Yellow, White
        });
        setCompleted(true);
        localStorage.setItem('daily_challenge_completed', 'true');
        localStorage.setItem('daily_challenge_date', new Date().toDateString());
    };

    return (
        <div className="bg-yellow-400 border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <Zap className="w-24 h-24 rotate-12" />
            </div>

            <div className="relative z-10">
                <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center space-x-2 bg-black text-white px-3 py-1 text-xs font-bold uppercase transform -rotate-1">
                        <Flame className="w-3 h-3 text-yellow-500" />
                        <span>Daily Challenge</span>
                    </div>
                    {completed && (
                        <div className="flex items-center space-x-1 text-black font-black uppercase text-sm animate-bounce">
                            <Trophy className="w-4 h-4" />
                            <span>Completed!</span>
                        </div>
                    )}
                </div>

                <h3 className="text-2xl font-black uppercase leading-tight mb-2 max-w-[90%]">
                    {challenge.text}
                </h3>

                <div className="flex items-center justify-between mt-6">
                    <div className="text-xs font-bold uppercase tracking-wider border-2 border-black px-2 py-1 bg-white">
                        Difficulty: {challenge.difficulty}
                    </div>

                    <button
                        onClick={handleComplete}
                        disabled={completed}
                        className={`
                            flex items-center space-x-2 px-6 py-2 border-4 border-black font-black uppercase transition-all
                            ${completed
                                ? 'bg-white text-black opacity-100 cursor-default'
                                : 'bg-black text-white hover:bg-white hover:text-black hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'
                            }
                        `}
                    >
                        {completed ? (
                            <>
                                <Check className="w-5 h-5" />
                                <span>Done</span>
                            </>
                        ) : (
                            <span>Mark Complete</span>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DailyChallenge;
