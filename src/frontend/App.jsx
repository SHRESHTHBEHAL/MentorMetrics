import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Upload from './pages/Upload';
import Status from './pages/Status';
import Results from './pages/Results';
import Dashboard from './pages/Dashboard';
import Sessions from './pages/Sessions';
import Logs from './pages/admin/Logs';
import SessionDebug from './pages/debug/SessionDebug';
import Login from './pages/Login';
import Register from './pages/Register';
import LivePractice from './pages/LivePractice';
import { ToastProvider } from './components/ui/ToastProvider';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

import NotFound from './pages/NotFound';
import ServerError from './pages/ServerError';
import ErrorBoundary from './components/errors/ErrorBoundary';

function App() {
    return (
        <Router>
            <AuthProvider>
                <ToastProvider>
                    <ErrorBoundary>
                        <Layout>
                            <Routes>
                                <Route path="/" element={<Home />} />
                                <Route path="/login" element={<Login />} />
                                <Route path="/register" element={<Register />} />
                                <Route path="/upload" element={
                                    <ProtectedRoute>
                                        <Upload />
                                    </ProtectedRoute>
                                } />
                                <Route path="/status" element={
                                    <ProtectedRoute>
                                        <Status />
                                    </ProtectedRoute>
                                } />
                                <Route path="/results" element={
                                    <ProtectedRoute>
                                        <Results />
                                    </ProtectedRoute>
                                } />
                                <Route path="/dashboard" element={
                                    <ProtectedRoute>
                                        <Dashboard />
                                    </ProtectedRoute>
                                } />
                                <Route path="/sessions" element={
                                    <ProtectedRoute>
                                        <Sessions />
                                    </ProtectedRoute>
                                } />
                                <Route path="/admin/logs" element={
                                    <ProtectedRoute>
                                        <Logs />
                                    </ProtectedRoute>
                                } />
                                <Route path="/debug/session" element={
                                    <ProtectedRoute>
                                        <SessionDebug />
                                    </ProtectedRoute>
                                } />
                                <Route path="/live-practice" element={
                                    <ProtectedRoute>
                                        <LivePractice />
                                    </ProtectedRoute>
                                } />
                                <Route path="/500" element={<ServerError />} />
                                <Route path="*" element={<NotFound />} />
                            </Routes>
                        </Layout>
                    </ErrorBoundary>
                </ToastProvider>
            </AuthProvider>
        </Router>
    );
}

export default App;
