import React from 'react';
import { BookOpen, Code, Calculator, Beaker, Briefcase, GraduationCap } from 'lucide-react';

// Subject configurations matching backend
const SUBJECTS = [
    {
        id: 'general',
        label: 'General',
        icon: GraduationCap,
        description: 'Balanced evaluation',
        color: 'bg-gray-100 border-gray-300 hover:bg-gray-200'
    },
    {
        id: 'math',
        label: 'Math',
        icon: Calculator,
        description: 'Step-by-step focus',
        color: 'bg-blue-50 border-blue-300 hover:bg-blue-100'
    },
    {
        id: 'programming',
        label: 'Code',
        icon: Code,
        description: 'Code accuracy',
        color: 'bg-green-50 border-green-300 hover:bg-green-100'
    },
    {
        id: 'english',
        label: 'English',
        icon: BookOpen,
        description: 'Pronunciation',
        color: 'bg-yellow-50 border-yellow-300 hover:bg-yellow-100'
    },
    {
        id: 'science',
        label: 'Science',
        icon: Beaker,
        description: 'Accuracy + demos',
        color: 'bg-purple-50 border-purple-300 hover:bg-purple-100'
    },
    {
        id: 'business',
        label: 'Business',
        icon: Briefcase,
        description: 'Presentation',
        color: 'bg-orange-50 border-orange-300 hover:bg-orange-100'
    }
];

const SubjectSelector = ({ selectedSubject, onSubjectChange }) => {
    return (
        <div className="bg-white border-4 border-black p-4 sm:p-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] mb-6 overflow-hidden">
            <h3 className="font-black uppercase text-base sm:text-lg mb-3 flex items-center">
                <GraduationCap className="w-5 h-5 mr-2 flex-shrink-0" />
                Subject Area
            </h3>
            <p className="text-xs sm:text-sm text-gray-600 mb-4">
                Select subject for tailored evaluation.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-3">
                {SUBJECTS.map((subject) => {
                    const Icon = subject.icon;
                    const isSelected = selectedSubject === subject.id;

                    return (
                        <button
                            key={subject.id}
                            type="button"
                            onClick={() => onSubjectChange(subject.id)}
                            className={`p-2 sm:p-3 border-2 text-left transition-all overflow-hidden ${isSelected
                                    ? 'border-black bg-black text-white shadow-none'
                                    : `border-black ${subject.color}`
                                }`}
                        >
                            <div className="flex items-center mb-1">
                                <Icon className={`w-4 h-4 mr-1.5 flex-shrink-0 ${isSelected ? 'text-yellow-400' : 'text-gray-700'}`} />
                                <span className="font-bold text-xs sm:text-sm truncate">{subject.label}</span>
                            </div>
                            <p className={`text-[10px] sm:text-xs truncate ${isSelected ? 'text-gray-300' : 'text-gray-500'}`}>
                                {subject.description}
                            </p>
                            {isSelected && (
                                <div className="mt-1 text-[10px] text-yellow-400 font-bold">
                                    ✓ Selected
                                </div>
                            )}
                        </button>
                    );
                })}
            </div>
        </div>
    );
};

export { SUBJECTS };
export default SubjectSelector;

