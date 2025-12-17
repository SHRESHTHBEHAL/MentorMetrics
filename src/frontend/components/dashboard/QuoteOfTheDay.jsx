import React from 'react';
import { Quote } from 'lucide-react';

const QUOTES = [
    { text: "The art of communication is the language of leadership.", author: "James Humes" },
    { text: "Teach less, learn more.", author: "Anonymous" },
    { text: "Effective communication is 20% what you know and 80% how you feel about what you know.", author: "Jim Rohn" },
    { text: "The two words 'information' and 'communication' are often used interchangeably, but they signify quite different things. Information is giving out; communication is getting through.", author: "Sydney J. Harris" },
    { text: "Speak clearly, if you speak at all; carve every word before you let it fall.", author: "Oliver Wendell Holmes" }
];

const QuoteOfTheDay = () => {
    // Pick quote based on date so it persists for the day
    const dateNum = new Date().getDate();
    const quote = QUOTES[dateNum % QUOTES.length];

    return (
        <div className="bg-white border-4 border-black p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] flex flex-col justify-center h-full relative group hover:bg-black hover:text-white transition-all duration-300">
            <div className="absolute top-4 right-4 opacity-10 group-hover:opacity-30">
                <Quote className="w-16 h-16" />
            </div>

            <blockquote className="relative z-10">
                <p className="text-xl font-black uppercase italic leading-tight mb-4">
                    "{quote.text}"
                </p>
                <footer className="text-sm font-bold uppercase tracking-wider opacity-60">
                    — {quote.author}
                </footer>
            </blockquote>
        </div>
    );
};

export default QuoteOfTheDay;
