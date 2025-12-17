import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Pause, RotateCcw, Mic, Camera, AlertCircle, Zap, Eye, Hand, Volume2 } from 'lucide-react';
import ChallengeWheel, { ChallengeOverlay, ChallengeResult } from '../components/live/ChallengeWheel';
import LiveScorePanel from '../components/live/LiveScorePanel';
import FeedbackBubble from '../components/live/FeedbackBubble';
import { api } from '../utils/api';

const LivePractice = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [timer, setTimer] = useState(0);
    const [hasPermissions, setHasPermissions] = useState(false);
    const [stream, setStream] = useState(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);

    // Audio Analysis State
    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const dataArrayRef = useRef(null);

    // Challenge state
    const [isSpinning, setIsSpinning] = useState(false);
    const [activeChallenge, setActiveChallenge] = useState(null);
    const [challengeTimeRemaining, setChallengeTimeRemaining] = useState(0);
    const [challengeResult, setChallengeResult] = useState(null);
    const [completedChallenges, setCompletedChallenges] = useState(0);

    // Live metrics
    const [liveStats, setLiveStats] = useState({
        overallScore: 0,
        eyeContactPercent: 0,
        speakingPercent: 0,
        gestureCount: 0,
        sessionDuration: 0,
        eyeContactRatio: 0
    });

    // Detailed tracking for averaging
    const trackingRef = useRef({
        eyeContactFrames: 0,
        totalFrames: 0,
        speakingFrames: 0,
        totalAudioFrames: 0,
        gestureFrames: 0
    });

    // Feedback bubbles
    const [currentFeedback, setCurrentFeedback] = useState(null);

    // Timer for recording duration
    useEffect(() => {
        let interval;
        if (isRecording) {
            interval = setInterval(() => {
                setTimer(prev => prev + 1);
                setLiveStats(prev => ({
                    ...prev,
                    sessionDuration: prev.sessionDuration + 1
                }));
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isRecording]);

    // Challenge timer
    useEffect(() => {
        let interval;
        if (activeChallenge && challengeTimeRemaining > 0) {
            interval = setInterval(() => {
                setChallengeTimeRemaining(prev => prev - 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [activeChallenge, challengeTimeRemaining]);

    // REAL-TIME ANALYSIS LOOP
    useEffect(() => {
        let analysisInterval;
        let audioInterval;

        if (isRecording) {
            // Visual Analysis (Every 500ms)
            analysisInterval = setInterval(analyzeFrame, 500);

            // Audio Analysis (Every 100ms)
            audioInterval = setInterval(analyzeAudio, 100);
        }

        return () => {
            clearInterval(analysisInterval);
            clearInterval(audioInterval);
        };
    }, [isRecording]);

    const analyzeAudio = () => {
        if (!analyserRef.current || !dataArrayRef.current) return;

        analyserRef.current.getByteFrequencyData(dataArrayRef.current);
        const average = dataArrayRef.current.reduce((a, b) => a + b) / dataArrayRef.current.length;

        // Threshold for "Speaking"
        const isSpeaking = average > 10; // Adjust based on sensitivity

        trackingRef.current.totalAudioFrames++;
        if (isSpeaking) trackingRef.current.speakingFrames++;

        const speakingPct = (trackingRef.current.speakingFrames / Math.max(1, trackingRef.current.totalAudioFrames)) * 100;

        setLiveStats(prev => ({
            ...prev,
            speakingPercent: Math.round(speakingPct)
        }));
    };

    const analyzeFrame = async () => {
        if (!videoRef.current || !canvasRef.current) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        // Draw current video frame to canvas
        canvas.width = video.videoWidth / 4; // Downscale directly for speed
        canvas.height = video.videoHeight / 4;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert to base64
        const imageData = canvas.toDataURL('image/jpeg', 0.7);

        try {
            const response = await api.post('/live/analyze', { image: imageData });
            const result = response.data;

            // Update tracking stats
            trackingRef.current.totalFrames++;
            if (result.eye_contact) trackingRef.current.eyeContactFrames++;
            if (result.gestures > 0) trackingRef.current.gestureFrames++;

            // Calculate Metrics
            const eyeContactRatio = trackingRef.current.eyeContactFrames / Math.max(1, trackingRef.current.totalFrames);
            const gestureScore = Math.min(10, result.gestures * 2); // Instant gesture intensity

            // Calculate Overall Score (Simple weighted average of current performance)
            // 40% Eye Contact, 30% Speaking Consistency, 30% Gestures
            const speakingRatio = trackingRef.current.speakingFrames / Math.max(1, trackingRef.current.totalAudioFrames);
            const overall = (eyeContactRatio * 4) + (speakingRatio * 3) + (Math.min(1, trackingRef.current.gestureFrames / trackingRef.current.totalFrames) * 3 * 2);
            // Normalized roughly to 0-10

            setLiveStats(prev => ({
                ...prev,
                eyeContactPercent: Math.round(eyeContactRatio * 100),
                gestureCount: result.gestures, // Show CURRENT gestures count
                eyeContactRatio: eyeContactRatio,
                overallScore: Math.round(Math.min(10, Math.max(0, overall)) * 10) / 10
            }));

            // Generate Feedback Bubbles based on REAL data
            if (Math.random() > 0.8) { // Don't spam
                if (!result.eye_contact) showFeedback('warning', 'Look at camera', '📷');
                else if (result.gestures > 0) showFeedback('positive', 'Nice gestures!', '👋');
                else if (result.eye_contact) showFeedback('positive', 'Great eye contact!', '👀');
            }

        } catch (err) {
            console.error("Frame analysis failed:", err);
        }
    };

    const showFeedback = (type, message, icon) => {
        setCurrentFeedback({ type, message, icon });
        setTimeout(() => setCurrentFeedback(null), 3000);
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    useEffect(() => {
        if (videoRef.current && stream) {
            videoRef.current.srcObject = stream;
            videoRef.current.play().catch(e => console.error("Error playing video:", e));
        }
    }, [stream, hasPermissions]);

    const handleStartRecording = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            setStream(mediaStream);
            setHasPermissions(true);

            // Setup Audio Analysis
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const analyser = audioCtx.createAnalyser();
            const source = audioCtx.createMediaStreamSource(mediaStream);
            source.connect(analyser);
            analyser.fftSize = 256;
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);

            audioContextRef.current = audioCtx;
            analyserRef.current = analyser;
            dataArrayRef.current = dataArray;

            setIsRecording(true);

            // Reset tracking
            trackingRef.current = {
                eyeContactFrames: 0,
                totalFrames: 0,
                speakingFrames: 0,
                totalAudioFrames: 0,
                gestureFrames: 0
            };

        } catch (err) {
            console.error("Error accessing media devices:", err);
            alert('Please allow camera and microphone access to use Live Practice.');
        }
    };

    const handleStopRecording = () => {
        setIsRecording(false);
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
        if (audioContextRef.current) {
            audioContextRef.current.close();
        }
    };

    const handleReset = () => {
        handleStopRecording();
        setTimer(0);
        setLiveStats({
            overallScore: 0,
            eyeContactPercent: 0,
            speakingPercent: 0,
            gestureCount: 0,
            sessionDuration: 0,
            eyeContactRatio: 0
        });
        setCompletedChallenges(0);
        trackingRef.current = {
            eyeContactFrames: 0,
            totalFrames: 0,
            speakingFrames: 0,
            totalAudioFrames: 0,
            gestureFrames: 0
        };
    };

    const handleChallengeSelect = (challenge) => {
        setActiveChallenge(challenge);
        setChallengeTimeRemaining(challenge.duration);
    };

    const handleChallengeComplete = () => {
        setChallengeResult({ success: true, challenge: activeChallenge });
        setCompletedChallenges(prev => prev + 1);
        setActiveChallenge(null);
    };

    const handleChallengeFail = () => {
        setChallengeResult({ success: false, challenge: activeChallenge });
        setActiveChallenge(null);
    };

    const handleResultClose = () => {
        setChallengeResult(null);
    };

    return (
        <div className="min-h-screen bg-white text-black font-mono p-4 md:p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="border-4 border-black p-6 mb-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl md:text-4xl font-black uppercase mb-2 flex items-center">
                                <Zap className="w-8 h-8 mr-2 text-yellow-500" />
                                Live Practice
                            </h1>
                            <p className="text-lg font-bold text-gray-600">
                                Practice your teaching with real-time AI feedback.
                            </p>
                        </div>
                        {isRecording && (
                            <div className="text-right">
                                <div className="flex items-center justify-end mb-2">
                                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-2"></div>
                                    <span className="text-sm font-bold text-red-500 uppercase">Recording</span>
                                </div>
                                <div className="text-4xl font-black font-mono">{formatTime(timer)}</div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column - Video & Controls */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Video Preview */}
                        <div className="border-4 border-black bg-gray-900 aspect-video relative overflow-hidden">
                            {hasPermissions && stream ? (
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    muted
                                    playsInline
                                    className="w-full h-full object-cover scale-x-[-1]"
                                />
                            ) : (
                                <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
                                    <div className="text-center p-8">
                                        <Camera className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                                        <p className="font-bold text-gray-500">Camera Preview</p>
                                        <p className="text-sm text-gray-400 mt-2">Click Start to begin</p>
                                    </div>
                                </div>
                            )}

                            {/* Hidden canvas for frame capture */}
                            <canvas ref={canvasRef} className="hidden" />

                            {/* Recording indicator overlay */}
                            {isRecording && (
                                <div className="absolute top-4 left-4 flex items-center bg-red-500 text-white px-3 py-1 border-2 border-black">
                                    <div className="w-2 h-2 bg-white rounded-full animate-pulse mr-2"></div>
                                    <span className="text-sm font-bold">LIVE</span>
                                </div>
                            )}
                        </div>

                        {/* Controls */}
                        <div className="border-4 border-black p-6 bg-white">
                            <h3 className="font-black uppercase mb-4 border-b-4 border-black pb-2">Controls</h3>
                            <div className="flex gap-4">
                                {!isRecording ? (
                                    <button
                                        onClick={handleStartRecording}
                                        className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-black text-white font-bold border-4 border-black hover:bg-white hover:text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]"
                                    >
                                        <Play className="h-5 w-5" /> START
                                    </button>
                                ) : (
                                    <button
                                        onClick={handleStopRecording}
                                        className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-red-500 text-white font-bold border-4 border-black hover:bg-red-600 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]"
                                    >
                                        <Pause className="h-5 w-5" /> STOP
                                    </button>
                                )}
                                <button
                                    onClick={handleReset}
                                    className="px-6 py-4 bg-white text-black font-bold border-4 border-black hover:bg-gray-100 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]"
                                >
                                    <RotateCcw className="h-5 w-5" />
                                </button>
                            </div>
                        </div>

                        {/* Challenge Wheel */}
                        <div className="border-4 border-black p-6 bg-yellow-50">
                            <h3 className="font-black uppercase mb-6 border-b-4 border-black pb-2 flex items-center">
                                <Zap className="w-5 h-5 mr-2 text-yellow-500" />
                                Spin for a Challenge!
                            </h3>
                            <div className="flex flex-col items-center">
                                <ChallengeWheel
                                    onChallengeSelect={handleChallengeSelect}
                                    isSpinning={isSpinning}
                                    setIsSpinning={setIsSpinning}
                                />
                                {completedChallenges > 0 && (
                                    <div className="mt-4 text-center">
                                        <span className="text-sm font-bold text-gray-500 uppercase">Challenges Completed: </span>
                                        <span className="text-2xl font-black text-green-600">{completedChallenges}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Right Column - Live Stats & Tips */}
                    <div className="space-y-6">
                        {/* Live Score Panel */}
                        <LiveScorePanel stats={liveStats} isActive={isRecording} />

                        {/* Quick Tips */}
                        <div className="border-4 border-black p-6 bg-gray-50">
                            <h3 className="font-black uppercase mb-4 border-b-4 border-black pb-2">Quick Tips</h3>
                            <ul className="space-y-3 text-sm font-bold">
                                <li className="flex items-start gap-2">
                                    <Eye className="w-4 h-4 mt-1 text-blue-500 flex-shrink-0" />
                                    <span>Look directly at the camera for eye contact</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Hand className="w-4 h-4 mt-1 text-green-500 flex-shrink-0" />
                                    <span>Use natural hand gestures</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Volume2 className="w-4 h-4 mt-1 text-purple-500 flex-shrink-0" />
                                    <span>Speak at 120-150 words/minute</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Mic className="w-4 h-4 mt-1 text-red-500 flex-shrink-0" />
                                    <span>Pause for emphasis</span>
                                </li>
                            </ul>
                        </div>

                        {/* Session Stats */}
                        <div className="border-4 border-black p-6 bg-white">
                            <h3 className="font-black uppercase mb-4 border-b-4 border-black pb-2">Session Stats</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="text-center p-4 bg-gray-50 border-2 border-black">
                                    <div className="text-3xl font-black">{formatTime(timer)}</div>
                                    <div className="text-xs font-bold text-gray-500 uppercase">Duration</div>
                                </div>
                                <div className="text-center p-4 bg-gray-50 border-2 border-black">
                                    <div className="text-3xl font-black">{completedChallenges}</div>
                                    <div className="text-xs font-bold text-gray-500 uppercase">Challenges</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Feedback Bubble */}
            <FeedbackBubble feedback={currentFeedback} />

            {/* Challenge Overlay */}
            {activeChallenge && (
                <ChallengeOverlay
                    challenge={activeChallenge}
                    timeRemaining={challengeTimeRemaining}
                    onComplete={handleChallengeComplete}
                    onFail={handleChallengeFail}
                    stats={liveStats}
                />
            )}

            {/* Challenge Result */}
            {challengeResult && (
                <ChallengeResult
                    success={challengeResult.success}
                    challenge={challengeResult.challenge}
                    onClose={handleResultClose}
                />
            )}
        </div>
    );
};

export default LivePractice;
