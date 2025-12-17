import React from 'react';
import {
    Eye,
    Mic,
    Zap,
    Target,
    Award,
    Star,
    TrendingUp,
    Clock,
    Users,
    Flame
} from 'lucide-react';

// Badge definitions with unlock criteria
const BADGE_DEFINITIONS = [
    {
        id: 'eye_contact_pro',
        name: 'Eye Contact Pro',
        description: 'Maintained excellent eye contact (8+)',
        icon: Eye,
        color: 'from-blue-500 to-cyan-400',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-400',
        check: (stats) => stats.avg_engagement >= 8
    },
    {
        id: 'clear_communicator',
        name: 'Clear Communicator',
        description: 'Achieved clarity score above 8',
        icon: Mic,
        color: 'from-purple-500 to-pink-400',
        bgColor: 'bg-purple-50',
        borderColor: 'border-purple-400',
        check: (stats) => stats.avg_communication >= 8
    },
    {
        id: 'speed_demon',
        name: 'Speed Demon',
        description: 'Completed 5+ sessions',
        icon: Zap,
        color: 'from-yellow-500 to-orange-400',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-400',
        check: (stats) => stats.total_sessions >= 5
    },
    {
        id: 'perfectionist',
        name: 'Perfectionist',
        description: 'Scored 9+ on any session',
        icon: Target,
        color: 'from-red-500 to-rose-400',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-400',
        check: (stats) => stats.highest_score >= 9
    },
    {
        id: 'rising_star',
        name: 'Rising Star',
        description: 'Improved score by 10%+',
        icon: TrendingUp,
        color: 'from-green-500 to-emerald-400',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-400',
        check: (stats) => stats.improvement_percent >= 10
    },
    {
        id: 'consistent',
        name: 'Consistency King',
        description: 'Maintained 7+ average score',
        icon: Award,
        color: 'from-indigo-500 to-violet-400',
        bgColor: 'bg-indigo-50',
        borderColor: 'border-indigo-400',
        check: (stats) => stats.avg_mentor_score >= 7
    },
    {
        id: 'tech_guru',
        name: 'Tech Guru',
        description: 'Technical accuracy above 8',
        icon: Star,
        color: 'from-amber-500 to-yellow-400',
        bgColor: 'bg-amber-50',
        borderColor: 'border-amber-400',
        check: (stats) => stats.avg_technical >= 8
    },
    {
        id: 'marathon',
        name: 'Marathon Mentor',
        description: 'Analyzed 30+ minutes of content',
        icon: Clock,
        color: 'from-teal-500 to-cyan-400',
        bgColor: 'bg-teal-50',
        borderColor: 'border-teal-400',
        check: (stats) => stats.total_duration_minutes >= 30
    },
    {
        id: 'first_session',
        name: 'First Steps',
        description: 'Completed your first session',
        icon: Users,
        color: 'from-slate-500 to-gray-400',
        bgColor: 'bg-slate-50',
        borderColor: 'border-slate-400',
        check: (stats) => stats.completed_sessions >= 1
    },
    {
        id: 'on_fire',
        name: 'On Fire',
        description: '3 sessions in a row above 7',
        icon: Flame,
        color: 'from-orange-500 to-red-500',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-400',
        check: (stats) => stats.streak >= 3
    }
];

const Badge = ({ badge, unlocked }) => {
    const Icon = badge.icon;

    return (
        <div
            className={`
                relative p-4 border-4 transition-all duration-300
                ${unlocked
                    ? `${badge.bgColor} ${badge.borderColor} shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]`
                    : 'bg-gray-100 border-gray-300 opacity-50 grayscale'
                }
            `}
        >
            {/* Glow effect for unlocked badges */}
            {unlocked && (
                <div className={`absolute inset-0 bg-gradient-to-br ${badge.color} opacity-10`}></div>
            )}

            <div className="relative flex flex-col items-center text-center">
                <div className={`
                    w-12 h-12 rounded-full flex items-center justify-center mb-2
                    ${unlocked
                        ? `bg-gradient-to-br ${badge.color} text-white shadow-lg`
                        : 'bg-gray-300 text-gray-500'
                    }
                `}>
                    <Icon className="w-6 h-6" />
                </div>

                <h4 className={`font-black text-xs uppercase tracking-wide ${unlocked ? 'text-black' : 'text-gray-500'}`}>
                    {badge.name}
                </h4>

                <p className={`text-[10px] mt-1 font-medium ${unlocked ? 'text-gray-600' : 'text-gray-400'}`}>
                    {badge.description}
                </p>

                {unlocked && (
                    <div className="absolute -top-2 -right-2 bg-green-500 text-white rounded-full w-5 h-5 flex items-center justify-center">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                    </div>
                )}
            </div>
        </div>
    );
};

const Achievements = ({ stats = {} }) => {
    // Calculate which badges are unlocked based on stats
    const badges = BADGE_DEFINITIONS.map(badge => ({
        ...badge,
        unlocked: badge.check(stats)
    }));

    const unlockedCount = badges.filter(b => b.unlocked).length;
    const totalCount = badges.length;
    const progressPercent = (unlockedCount / totalCount) * 100;

    return (
        <div className="bg-white border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
            {/* Header with progress */}
            <div className="flex items-center justify-between mb-6 border-b-4 border-black pb-4">
                <div className="flex items-center">
                    <Award className="w-6 h-6 mr-3" />
                    <h3 className="text-xl font-black uppercase">Achievements</h3>
                </div>
                <div className="flex items-center">
                    <span className="text-2xl font-black">{unlockedCount}</span>
                    <span className="text-sm font-bold text-gray-500 ml-1">/ {totalCount}</span>
                </div>
            </div>

            {/* Progress bar */}
            <div className="mb-6">
                <div className="w-full h-3 bg-gray-200 border-2 border-black">
                    <div
                        className="h-full bg-gradient-to-r from-green-400 to-emerald-500 transition-all duration-500"
                        style={{ width: `${progressPercent}%` }}
                    />
                </div>
                <p className="text-xs font-bold text-gray-500 mt-2 uppercase text-center">
                    {progressPercent.toFixed(0)}% Complete • {totalCount - unlockedCount} badges remaining
                </p>
            </div>

            {/* Badge grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                {badges.map(badge => (
                    <Badge
                        key={badge.id}
                        badge={badge}
                        unlocked={badge.unlocked}
                    />
                ))}
            </div>
        </div>
    );
};

export default Achievements;
