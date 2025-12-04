import React from 'react';
import NavBar from './NavBar';

const Layout = ({ children }) => {
    return (
        <div className="min-h-screen bg-white font-mono text-black">
            <NavBar />
            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                {children}
            </main>
        </div>
    );
};

export default Layout;
