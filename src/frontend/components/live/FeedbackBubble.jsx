import React from 'react';

const FeedbackBubble = ({ feedback }) => {
    if (!feedback) return null;

    const getTypeStyles = (type) => {
        switch (type) {
            case 'positive':
                return 'bg-green-100 border-green-500 text-green-800';
            case 'warning':
                return 'bg-red-100 border-red-500 text-red-800';
            case 'neutral':
            default:
                return 'bg-yellow-100 border-yellow-500 text-yellow-800';
        }
    };

    return (
        <div
            className={`
                fixed top-24 left-1/2 transform -translate-x-1/2 z-50
                px-6 py-4 rounded-none border-4 border-black
                shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]
                animate-bounce-in
                ${getTypeStyles(feedback.type)}
            `}
            style={{
                animation: 'slideInBounce 0.5s ease-out forwards'
            }}
        >
            <div className="flex items-center space-x-3">
                <span className="text-3xl">{feedback.icon}</span>
                <span className="text-xl font-black uppercase tracking-wide">
                    {feedback.message}
                </span>
            </div>

            {/* Progress bar for auto-dismiss */}
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/20">
                <div
                    className="h-full bg-black/40"
                    style={{
                        animation: 'shrink 3s linear forwards'
                    }}
                />
            </div>

            <style jsx>{`
                @keyframes slideInBounce {
                    0% {
                        opacity: 0;
                        transform: translate(-50%, -100px) scale(0.8);
                    }
                    50% {
                        transform: translate(-50%, 10px) scale(1.05);
                    }
                    100% {
                        opacity: 1;
                        transform: translate(-50%, 0) scale(1);
                    }
                }
                
                @keyframes shrink {
                    from {
                        width: 100%;
                    }
                    to {
                        width: 0%;
                    }
                }
            `}</style>
        </div>
    );
};

export default FeedbackBubble;
