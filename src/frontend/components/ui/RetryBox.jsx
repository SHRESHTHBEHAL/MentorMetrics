import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import Button from '../Button';

const RetryBox = ({ message = "Something went wrong.", onRetry, retryLabel = "Try Again" }) => {
    return (
        <div className="rounded-lg bg-white border border-red-200 p-6 shadow-sm text-center">
            <div className="flex justify-center mb-3">
                <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
            <p className="text-gray-700 mb-4 font-medium">{message}</p>
            <Button onClick={onRetry} variant="outline" className="inline-flex items-center">
                <RefreshCw className="mr-2 h-4 w-4" />
                {retryLabel}
            </Button>
        </div>
    );
};

export default RetryBox;
