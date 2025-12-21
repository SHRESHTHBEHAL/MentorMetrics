import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, Timer, CheckCircle, XCircle, Skull, Hand, Volume2, Eye, Zap } from 'lucide-react';

// Challenge definitions
const CHALLENGES = [
    {
        id: 'no_i',
        title: "No 'I' Challenge",
        description: "Speak for 30 seconds WITHOUT using the word 'I'",
        duration: 30,
        icon: Skull,
        color: '#ef4444', // red
        detectType: 'forbidden_words'
    },
    {
        id: 'pirate',
        title: "Pirate Mode",
        description: "Explain your topic like you're a pirate! Arrr! 🏴‍☠️",
        duration: 45,
        icon: Sparkles,
        color: '#f59e0b', // amber
        detectType: 'bonus_words'
    },
    {
        id: 'gestures',
        title: "Gesture Master",
        description: "Use at least 5 visible hand gestures in 20 seconds!",
        duration: 20,
        icon: Hand,
        color: '#3b82f6', // blue
        targetGestures: 5,
        detectType: 'gesture_count'
    },
    {
        id: 'slow_motion',
        title: "Slow & Steady",
        description: "Speak at half your normal speed. Take. Your. Time.",
        duration: 30,
        icon: Timer,
        color: '#8b5cf6', // purple
        targetWPM: 80,
        detectType: 'pace'
    },
    {
        id: 'no_filler',
        title: "No Fillers",
        description: "No 'um', 'like', 'actually' for 45 seconds!",
        duration: 45,
        icon: Zap,
        color: '#22c55e', // green
        detectType: 'forbidden_words'
    },
    {
        id: 'eye_contact',
        title: "Stare Down",
        description: "Maintain eye contact for 30 seconds straight!",
        duration: 30,
        icon: Eye,
        color: '#ec4899', // pink
        targetEyeContact: 0.9,
        detectType: 'eye_contact'
    }
];

// Simple wheel using CSS conic gradient
const ChallengeWheel = ({ onChallengeSelect, isSpinning, setIsSpinning }) => {
    const [rotation, setRotation] = useState(0);
    const [selectedChallenge, setSelectedChallenge] = useState(null);

    const spinWheel = () => {
        if (isSpinning) return;

        setIsSpinning(true);
        setSelectedChallenge(null);

        // Random spin: 3-5 full rotations + random offset
        const fullRotations = (3 + Math.random() * 2) * 360;
        const randomOffset = Math.random() * 360;
        const finalRotation = rotation + fullRotations + randomOffset;

        setRotation(finalRotation);

        // Calculate which challenge was selected
        setTimeout(() => {
            const normalizedRotation = (360 - (finalRotation % 360) + 90) % 360; // +90 because pointer is at top
            const segmentAngle = 360 / CHALLENGES.length;
            const selectedIndex = Math.floor(normalizedRotation / segmentAngle);
            const challenge = CHALLENGES[selectedIndex % CHALLENGES.length];

            setSelectedChallenge(challenge);
            setIsSpinning(false);
            onChallengeSelect(challenge);
        }, 3000);
    };

    // Create conic gradient for wheel
    const segmentAngle = 360 / CHALLENGES.length;
    const gradientColors = CHALLENGES.map((c, i) => {
        const start = i * segmentAngle;
        const end = (i + 1) * segmentAngle;
        return `${c.color} ${start}deg ${end}deg`;
    }).join(', ');

    return (
        <div className="flex flex-col items-center">
            {/* Wheel Container */}
            <div className="relative w-56 h-56 sm:w-64 sm:h-64 mb-6">
                {/* Pointer */}
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-2 z-20">
                    <div className="w-0 h-0 border-l-[12px] border-r-[12px] border-t-[20px] border-l-transparent border-r-transparent border-t-black"></div>
                </div>

                {/* Wheel */}
                <div
                    className="w-full h-full rounded-full border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] relative"
                    style={{
                        background: `conic-gradient(${gradientColors})`,
                        transform: `rotate(${rotation}deg)`,
                        transition: isSpinning ? 'transform 3s cubic-bezier(0.17, 0.67, 0.12, 0.99)' : 'none'
                    }}
                >
                    {/* Segment Labels (Icons) */}
                    {CHALLENGES.map((challenge, index) => {
                        const angle = (index * segmentAngle) + (segmentAngle / 2);
                        const Icon = challenge.icon;
                        return (
                            <div
                                key={challenge.id}
                                className="absolute"
                                style={{
                                    top: '50%',
                                    left: '50%',
                                    transform: `rotate(${angle}deg) translateY(-70px) rotate(-${angle}deg)`,
                                    transformOrigin: 'center center',
                                    marginTop: '-12px',
                                    marginLeft: '-12px'
                                }}
                            >
                                <Icon className="w-6 h-6 text-white drop-shadow-md" />
                            </div>
                        );
                    })}

                    {/* Center Circle */}
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-14 h-14 rounded-full bg-black border-4 border-white flex items-center justify-center z-10">
                        <Sparkles className="w-6 h-6 text-yellow-400" />
                    </div>
                </div>
            </div>

            {/* Spin Button */}
            <button
                onClick={spinWheel}
                disabled={isSpinning}
                className={`px-6 py-3 font-black uppercase text-base border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all ${isSpinning
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-yellow-400 text-black hover:bg-yellow-500 hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]'
                    }`}
            >
                {isSpinning ? '🎲 SPINNING...' : '🎰 SPIN THE WHEEL!'}
            </button>
        </div>
    );
};

// Challenge Overlay (shows active challenge)
export const ChallengeOverlay = ({ challenge, timeRemaining, onComplete, onFail, stats }) => {
    const [violations, setViolations] = useState(0);
    const [successes, setSuccesses] = useState(0);
    const [completed, setCompleted] = useState(false);
    const [startGestureCount, setStartGestureCount] = useState(null);
    const [startEyeContactFrames, setStartEyeContactFrames] = useState(null);

    const progress = ((challenge.duration - timeRemaining) / challenge.duration) * 100;
    const isTimerDone = timeRemaining <= 0;

    // Capture starting stats when challenge begins
    useEffect(() => {
        if (startGestureCount === null && stats?.gestureCount !== undefined) {
            setStartGestureCount(stats.gestureCount);
        }
    }, [stats?.gestureCount, startGestureCount]);

    // Calculate gestures DURING this challenge
    const gesturesDuringChallenge = (stats?.gestureCount || 0) - (startGestureCount || 0);

    // Check for early completion or violations
    useEffect(() => {
        if (completed) return;

        // Check if gesture goal is met
        if (challenge.detectType === 'gesture_count' &&
            gesturesDuringChallenge >= challenge.targetGestures) {
            setCompleted(true);
            onComplete();
            return;
        }

        // Track eye contact violations (each frame without eye contact when needed)
        if (challenge.detectType === 'eye_contact') {
            if (stats?.eyeContactPercent < 50) {
                // Not looking at camera - increment violations
                setViolations(v => v + 1);
            }
        }
    }, [stats, challenge, completed, onComplete, gesturesDuringChallenge]);

    // Handle timer completion
    useEffect(() => {
        if (isTimerDone && !completed) {
            setCompleted(true);
            let success = false;

            switch (challenge.detectType) {
                case 'forbidden_words':
                    success = violations < 3;
                    break;
                case 'bonus_words':
                    success = successes >= 2;
                    break;
                case 'gesture_count':
                    success = gesturesDuringChallenge >= challenge.targetGestures;
                    break;
                case 'eye_contact':
                    // Calculate average eye contact during challenge
                    const avgEyeContact = (stats?.eyeContactPercent || 0) / 100;
                    success = avgEyeContact >= challenge.targetEyeContact;
                    break;
                case 'pace':
                    success = true; // Default to success for pace
                    break;
                default:
                    success = true;
            }

            if (success) {
                onComplete();
            } else {
                onFail();
            }
        }
    }, [isTimerDone, completed, violations, successes, stats, challenge, onComplete, onFail, gesturesDuringChallenge]);


    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-white border-4 border-black p-6 max-w-md w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                {/* Challenge Header */}
                <div
                    className="-m-6 mb-6 p-4 border-b-4 border-black"
                    style={{ backgroundColor: challenge.color }}
                >
                    <div className="flex items-center justify-between text-white">
                        <div className="flex items-center">
                            <challenge.icon className="w-6 h-6 mr-2" />
                            <h2 className="text-lg font-black uppercase">{challenge.title}</h2>
                        </div>
                        <div className="text-4xl font-black">
                            {timeRemaining}s
                        </div>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="h-4 bg-gray-200 border-2 border-black mb-4">
                    <div
                        className="h-full transition-all duration-1000"
                        style={{
                            width: `${progress}%`,
                            backgroundColor: challenge.color
                        }}
                    />
                </div>

                {/* Challenge Description */}
                <p className="text-center text-base font-bold mb-4">
                    {challenge.description}
                </p>

                {/* Stats */}
                {challenge.detectType === 'forbidden_words' && (
                    <div className="text-center p-4 bg-red-50 border-2 border-red-300">
                        <p className="text-sm font-bold text-red-700 uppercase">Violations</p>
                        <p className="text-4xl font-black text-red-600">{violations}</p>
                        <p className="text-xs text-red-500">Keep it under 3 to win!</p>
                    </div>
                )}

                {challenge.detectType === 'bonus_words' && (
                    <div className="text-center p-4 bg-amber-50 border-2 border-amber-300">
                        <p className="text-sm font-bold text-amber-700 uppercase">Pirate Words!</p>
                        <p className="text-4xl font-black text-amber-600">{successes}</p>
                        <p className="text-xs text-amber-500">Say arrr, matey, ahoy to win!</p>
                    </div>
                )}

                {challenge.detectType === 'gesture_count' && (
                    <div className="text-center p-4 bg-blue-50 border-2 border-blue-300">
                        <p className="text-sm font-bold text-blue-700 uppercase">Gestures This Challenge</p>
                        <p className="text-4xl font-black text-blue-600">
                            {gesturesDuringChallenge} / {challenge.targetGestures}
                        </p>
                        {gesturesDuringChallenge >= challenge.targetGestures && (
                            <p className="text-xs text-green-600 font-bold">✓ Goal reached!</p>
                        )}
                    </div>
                )}

                {challenge.detectType === 'eye_contact' && (
                    <div className="text-center p-4 bg-pink-50 border-2 border-pink-300">
                        <p className="text-sm font-bold text-pink-700 uppercase">Eye Contact</p>
                        <p className="text-4xl font-black text-pink-600">
                            {((stats?.eyeContactRatio || 0) * 100).toFixed(0)}%
                        </p>
                        <p className="text-xs text-pink-500">Need 90% to win!</p>
                    </div>
                )}

                {challenge.detectType === 'pace' && (
                    <div className="text-center p-4 bg-purple-50 border-2 border-purple-300">
                        <p className="text-sm font-bold text-purple-700 uppercase">Take it slow!</p>
                        <p className="text-2xl font-black text-purple-600">🐢 Slow & Steady</p>
                        <p className="text-xs text-purple-500">Breathe. Pause. Speak clearly.</p>
                    </div>
                )}

                {/* Cancel Button */}
                <button
                    onClick={onFail}
                    className="mt-4 w-full py-2 text-sm font-bold text-gray-500 hover:text-gray-700 uppercase"
                >
                    Give Up
                </button>
            </div>
        </div>
    );
};

// Result Modal (shows after challenge)
export const ChallengeResult = ({ success, challenge, onClose }) => {
    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className={`border-4 border-black p-8 max-w-md w-full shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] ${success ? 'bg-green-400' : 'bg-red-400'
                }`}>
                <div className="text-center text-white">
                    {success ? (
                        <>
                            <CheckCircle className="w-20 h-20 mx-auto mb-4" />
                            <h2 className="text-4xl font-black uppercase mb-2">NAILED IT!</h2>
                            <p className="text-lg font-bold mb-6">
                                You completed the {challenge.title}!
                            </p>
                        </>
                    ) : (
                        <>
                            <XCircle className="w-20 h-20 mx-auto mb-4" />
                            <h2 className="text-4xl font-black uppercase mb-2">SO CLOSE!</h2>
                            <p className="text-lg font-bold mb-6">
                                Better luck next time!
                            </p>
                        </>
                    )}

                    <button
                        onClick={onClose}
                        className="px-8 py-3 bg-white text-black font-black uppercase border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px] transition-all"
                    >
                        Continue
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChallengeWheel;
export { CHALLENGES };
