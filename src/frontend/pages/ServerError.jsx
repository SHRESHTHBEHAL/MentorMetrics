import React from 'react';
import { Link } from 'react-router-dom';
import { RefreshCw, Home, AlertTriangle } from 'lucide-react';
import Button from '../components/Button';

const ServerError = () => {
    return (
        <div className="min-h-[80vh] flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
            <div className="text-center">
                <div className="flex justify-center mb-6">
                    <div className="bg-red-50 p-4 rounded-full">
                        <AlertTriangle className="h-12 w-12 text-red-600" />
                    </div>
                </div>
                <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl mb-2">
                    500
                </h1>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Something went wrong</h2>
                <p className="text-base text-gray-500 max-w-md mx-auto mb-8">
                    We encountered an unexpected error. Please try again later or contact support if the problem persists.
                </p>
                <div className="flex flex-col sm:flex-row justify-center gap-4">
                    <Button
                        variant="primary"
                        className="flex items-center justify-center"
                        onClick={() => window.location.reload()}
                    >
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Retry
                    </Button>
                    <Link to="/">
                        <Button variant="outline" className="flex items-center justify-center w-full">
                            <Home className="mr-2 h-4 w-4" />
                            Go Back Home
                        </Button>
                    </Link>
                </div>
                <div className="mt-8">
                    <a href="#" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                        Contact Support
                    </a>
                </div>
            </div>
        </div>
    );
};

export default ServerError;
