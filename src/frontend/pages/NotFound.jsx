import React from 'react';
import { Link } from 'react-router-dom';
import { Home, AlertCircle } from 'lucide-react';
import Button from '../components/Button';

const NotFound = () => {
    return (
        <div className="min-h-[80vh] flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
            <div className="text-center">
                <div className="flex justify-center mb-6">
                    <div className="bg-indigo-50 p-4 rounded-full">
                        <AlertCircle className="h-12 w-12 text-indigo-600" />
                    </div>
                </div>
                <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl mb-2">
                    404
                </h1>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Page Not Found</h2>
                <p className="text-base text-gray-500 max-w-md mx-auto mb-8">
                    Sorry, we couldn't find the page you're looking for. It might have been moved or doesn't exist.
                </p>
                <div className="flex justify-center">
                    <Link to="/">
                        <Button variant="primary" className="flex items-center">
                            <Home className="mr-2 h-4 w-4" />
                            Go Back Home
                        </Button>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default NotFound;
