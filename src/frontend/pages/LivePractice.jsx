import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Play, Pause, RotateCcw, Mic, Camera, AlertCircle, Zap, Eye, Hand, Volume2,
    CheckCircle, XCircle, TrendingUp, Clock, Award, ArrowLeft
} from 'lucide-react';
import ChallengeWheel, { ChallengeOverlay, ChallengeResult } from '../components/live/ChallengeWheel';
import LiveScorePanel from '../components/live/LiveScorePanel';
import FeedbackBubble from '../components/live/FeedbackBubble';
import { api } from '../utils/api';

const LivePractice = () => {
    const navigate = useNavigate();
    const [isRecording, setIsRecording] = useState(false);
    const [timer, setTimer] = useState(0);
    const [hasPermissions, setHasPermissions] = useState(false);
    const [permissionError, setPermissionError] = useState(null);
    const [stream, setStream] = useState(null);
    const [showSummary, setShowSummary] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState('idle'); // idle, connecting, connected, error
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

    // Session summary (for end screen)
    const [sessionSummary, setSessionSummary] = useState(null);

    // Detailed tracking for averaging
    const trackingRef = useRef({
        eyeContactFrames: 0,
        totalFrames: 0,
        speakingFrames: 0,
        totalAudioFrames: 0,
        gestureFrames: 0,
        analysisErrors: 0,
        lastGestureTime: 0 // Cooldown to avoid counting same gesture repeatedly
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

        // Higher threshold to ignore background noise - only active speech
        const isSpeaking = average > 30;

        trackingRef.current.totalAudioFrames++;
        if (isSpeaking) trackingRef.current.speakingFrames++;

        const speakingPct = (trackingRef.current.speakingFrames / Math.max(1, trackingRef.current.totalAudioFrames)) * 100;

        setLiveStats(prev => ({
            ...prev,
            speakingPercent: Math.round(speakingPct)
        }));
    };

    const analyzeFrame = async () => {
        if (!videoRef.current || !canvasRef.current || !isRecording) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        // Check if video is ready
        if (video.readyState < 2) return;

        // Draw current video frame to canvas
        canvas.width = Math.floor(video.videoWidth / 4); // Downscale for speed
        canvas.height = Math.floor(video.videoHeight / 4);
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert to base64
        const imageData = canvas.toDataURL('image/jpeg', 0.6);

        try {
            setConnectionStatus('connected');
            const response = await api.post('/live/analyze', { image: imageData });
            const result = response.data;

            // Update tracking stats
            trackingRef.current.totalFrames++;
            if (result.eye_contact) trackingRef.current.eyeContactFrames++;

            // Count gestures immediately (no cooldown - gestures are already filtered by backend)
            if (result.gestures > 0) {
                trackingRef.current.gestureFrames += result.gestures;
            }

            // Calculate Metrics
            const eyeContactRatio = trackingRef.current.eyeContactFrames / Math.max(1, trackingRef.current.totalFrames);
            const speakingRatio = trackingRef.current.speakingFrames / Math.max(1, trackingRef.current.totalAudioFrames);
            // Gesture score based on cumulative gestures (more gestures = better, capped at 1.0 ratio)
            const gestureRatio = Math.min(1, trackingRef.current.gestureFrames / 10); // 10+ gestures = full score

            // Calculate Overall Score (weighted)
            // 40% Eye Contact, 30% Speaking, 30% Gestures
            const overall = (eyeContactRatio * 4) + (speakingRatio * 3) + (gestureRatio * 3);

            setLiveStats(prev => ({
                ...prev,
                eyeContactPercent: Math.round(eyeContactRatio * 100),
                gestureCount: trackingRef.current.gestureFrames, // Show TOTAL cumulative gestures
                eyeContactRatio: eyeContactRatio,
                overallScore: Math.round(Math.min(10, Math.max(0, overall)) * 10) / 10
            }));

            // Generate Feedback Bubbles based on REAL data (less frequently)
            if (Math.random() > 0.85) {
                if (!result.eye_contact && result.face_detected) {
                    showFeedback('warning', 'Look at the camera!', '📷');
                } else if (result.gestures > 0) {
                    showFeedback('positive', 'Great gestures!', '👋');
                } else if (result.eye_contact) {
                    showFeedback('positive', 'Excellent eye contact!', '👀');
                } else if (!result.face_detected) {
                    showFeedback('warning', 'Stay in frame!', '🖼️');
                }
            }

        } catch (err) {
            trackingRef.current.analysisErrors++;
            if (trackingRef.current.analysisErrors > 5) {
                setConnectionStatus('error');
            }
            console.error("Frame analysis failed:", err);
        }
    };

    const showFeedback = (type, message, icon) => {
        setCurrentFeedback({ type, message, icon });
        setTimeout(() => setCurrentFeedback(null), 2500);
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
            setPermissionError(null);
            setConnectionStatus('connecting');

            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
                audio: true
            });
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
            setShowSummary(false);
            setConnectionStatus('connected');

            // Reset tracking
            trackingRef.current = {
                eyeContactFrames: 0,
                totalFrames: 0,
                speakingFrames: 0,
                totalAudioFrames: 0,
                gestureFrames: 0,
                analysisErrors: 0
            };

        } catch (err) {
            console.error("Error accessing media devices:", err);
            setConnectionStatus('error');
            if (err.name === 'NotAllowedError') {
                setPermissionError('Camera and microphone access denied. Please allow access in your browser settings.');
            } else if (err.name === 'NotFoundError') {
                setPermissionError('No camera or microphone found. Please connect a device.');
            } else {
                setPermissionError('Failed to access camera/microphone. Please try again.');
            }
        }
    };

    const handleStopRecording = () => {
        // Calculate session summary before stopping
        const summary = {
            duration: timer,
            eyeContactPercent: liveStats.eyeContactPercent,
            speakingPercent: liveStats.speakingPercent,
            overallScore: liveStats.overallScore,
            challengesCompleted: completedChallenges,
            totalGestures: trackingRef.current.gestureFrames,
            grade: getGrade(liveStats.overallScore)
        };
        setSessionSummary(summary);
        setShowSummary(true);

        setIsRecording(false);
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
        if (audioContextRef.current) {
            audioContextRef.current.close();
        }
        setConnectionStatus('idle');
    };

    const getGrade = (score) => {
        if (score >= 9) return { letter: 'A+', color: 'text-green-600' };
        if (score >= 8) return { letter: 'A', color: 'text-green-600' };
        if (score >= 7) return { letter: 'B+', color: 'text-blue-600' };
        if (score >= 6) return { letter: 'B', color: 'text-blue-600' };
        if (score >= 5) return { letter: 'C', color: 'text-yellow-600' };
        return { letter: 'D', color: 'text-orange-600' };
    };

    const handleReset = () => {
        if (isRecording) {
            handleStopRecording();
        }
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
        setShowSummary(false);
        setSessionSummary(null);
        setHasPermissions(false);
        trackingRef.current = {
            eyeContactFrames: 0,
            totalFrames: 0,
            speakingFrames: 0,
            totalAudioFrames: 0,
            gestureFrames: 0,
            analysisErrors: 0
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

    // Session Summary Screen
    if (showSummary && sessionSummary) {
        return (
            <div className="min-h-screen bg-white text-black font-mono p-4 md:p-8">
                <div className="max-w-2xl mx-auto">
                    <div className="border-4 border-black p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                        <div className="text-center mb-8">
                            <Award className="w-16 h-16 mx-auto mb-4 text-yellow-500" />
                            <h1 className="text-4xl font-black uppercase mb-2">Practice Complete!</h1>
                            <p className="text-gray-600 font-bold">Here's how you did:</p>
                        </div>

                        {/* Big Score */}
                        <div className="text-center mb-8 p-6 bg-gray-50 border-4 border-black">
                            <p className="text-sm font-bold text-gray-500 uppercase mb-2">Overall Score</p>
                            <p className="text-7xl font-black">{sessionSummary.overallScore.toFixed(1)}</p>
                            <p className={`text-3xl font-black ${sessionSummary.grade.color}`}>
                                Grade: {sessionSummary.grade.letter}
                            </p>
                        </div>

                        {/* Stats Grid */}
                        <div className="grid grid-cols-2 gap-4 mb-8">
                            <div className="p-4 bg-blue-50 border-2 border-black text-center">
                                <Eye className="w-6 h-6 mx-auto mb-2 text-blue-600" />
                                <p className="text-2xl font-black">{sessionSummary.eyeContactPercent}%</p>
                                <p className="text-xs font-bold text-gray-500 uppercase">Eye Contact</p>
                            </div>
                            <div className="p-4 bg-purple-50 border-2 border-black text-center">
                                <Volume2 className="w-6 h-6 mx-auto mb-2 text-purple-600" />
                                <p className="text-2xl font-black">{sessionSummary.speakingPercent}%</p>
                                <p className="text-xs font-bold text-gray-500 uppercase">Speaking Time</p>
                            </div>
                            <div className="p-4 bg-green-50 border-2 border-black text-center">
                                <Clock className="w-6 h-6 mx-auto mb-2 text-green-600" />
                                <p className="text-2xl font-black">{formatTime(sessionSummary.duration)}</p>
                                <p className="text-xs font-bold text-gray-500 uppercase">Duration</p>
                            </div>
                            <div className="p-4 bg-yellow-50 border-2 border-black text-center">
                                <Zap className="w-6 h-6 mx-auto mb-2 text-yellow-600" />
                                <p className="text-2xl font-black">{sessionSummary.challengesCompleted}</p>
                                <p className="text-xs font-bold text-gray-500 uppercase">Challenges</p>
                            </div>
                        </div>

                        {/* Tips based on performance */}
                        <div className="p-4 bg-gray-100 border-2 border-black mb-8">
                            <h3 className="font-black uppercase mb-3">💡 Tips for Improvement</h3>
                            <ul className="space-y-2 text-sm font-bold">
                                {sessionSummary.eyeContactPercent < 60 && (
                                    <li className="flex items-start gap-2">
                                        <XCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                                        Practice looking directly at the camera more often
                                    </li>
                                )}
                                {sessionSummary.speakingPercent < 50 && (
                                    <li className="flex items-start gap-2">
                                        <XCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                                        Try to speak more - aim for 60%+ speaking time
                                    </li>
                                )}
                                {sessionSummary.eyeContactPercent >= 60 && (
                                    <li className="flex items-start gap-2">
                                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                        Great eye contact! Keep it up!
                                    </li>
                                )}
                                {sessionSummary.overallScore >= 7 && (
                                    <li className="flex items-start gap-2">
                                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                        Excellent performance! You're ready to teach!
                                    </li>
                                )}
                            </ul>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex gap-4">
                            <button
                                onClick={handleReset}
                                className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-black text-white font-bold border-4 border-black hover:bg-white hover:text-black transition-all"
                            >
                                <RotateCcw className="w-5 h-5" />
                                Practice Again
                            </button>
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-white text-black font-bold border-4 border-black hover:bg-gray-100 transition-all"
                            >
                                <ArrowLeft className="w-5 h-5" />
                                Dashboard
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

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

                {/* Permission Error */}
                {permissionError && (
                    <div className="mb-8 p-4 bg-red-100 border-4 border-red-500 flex items-center gap-4">
                        <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0" />
                        <div>
                            <p className="font-bold text-red-700">{permissionError}</p>
                            <button
                                onClick={() => setPermissionError(null)}
                                className="text-sm underline text-red-600 mt-1"
                            >
                                Dismiss
                            </button>
                        </div>
                    </div>
                )}

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

                            {/* Connection Status */}
                            {isRecording && connectionStatus === 'error' && (
                                <div className="absolute bottom-4 left-4 flex items-center bg-orange-500 text-white px-3 py-1 border-2 border-black">
                                    <AlertCircle className="w-4 h-4 mr-2" />
                                    <span className="text-sm font-bold">Connection Issues</span>
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
                                        disabled={connectionStatus === 'connecting'}
                                        className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-black text-white font-bold border-4 border-black hover:bg-white hover:text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px] disabled:opacity-50"
                                    >
                                        <Play className="h-5 w-5" />
                                        {connectionStatus === 'connecting' ? 'CONNECTING...' : 'START'}
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

                        {/* Challenge Wheel - Only show when recording */}
                        {isRecording && (
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
                        )}
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
                                    <span>Use natural hand gestures while explaining</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Volume2 className="w-4 h-4 mt-1 text-purple-500 flex-shrink-0" />
                                    <span>Speak clearly at 120-150 words/minute</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Mic className="w-4 h-4 mt-1 text-red-500 flex-shrink-0" />
                                    <span>Use pauses for emphasis and clarity</span>
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
