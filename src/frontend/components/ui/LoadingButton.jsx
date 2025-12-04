import React from 'react';
import { Loader2 } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const LoadingButton = ({
    children,
    isLoading = false,
    disabled = false,
    variant = 'primary',
    className,
    ...props
}) => {
    const baseStyles = "inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-200";

    const variants = {
        primary: "text-white bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500 disabled:bg-indigo-400",
        secondary: "text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:ring-indigo-500 disabled:bg-indigo-50 disabled:text-indigo-400",
        outline: "text-gray-700 bg-white border-gray-300 hover:bg-gray-50 focus:ring-indigo-500 disabled:bg-gray-50 disabled:text-gray-400",
        destructive: "text-white bg-red-600 hover:bg-red-700 focus:ring-red-500 disabled:bg-red-400"
    };

    return (
        <button
            className={twMerge(baseStyles, variants[variant], className)}
            disabled={disabled || isLoading}
            aria-busy={isLoading}
            {...props}
        >
            {isLoading && (
                <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
            )}
            {children}
        </button>
    );
};

export default LoadingButton;
