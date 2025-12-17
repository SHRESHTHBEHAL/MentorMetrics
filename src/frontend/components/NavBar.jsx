import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { BarChart2, Upload, Home, LogOut, User, Menu, X, Zap } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Button from './Button';

const NavBar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { user, signOut } = useAuth();
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    useEffect(() => {
        setIsMenuOpen(false);
    }, [location]);

    const handleLogout = async () => {
        await signOut();
        navigate('/');
    };

    const handleLogin = () => {
        navigate('/login');
    };

    const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

    const NavLink = ({ to, children }) => {
        const isActive = location.pathname === to;
        return (
            <Link
                to={to}
                className={`inline-flex items-center px-2 lg:px-4 pt-1 text-sm lg:text-base font-bold border-b-4 transition-all whitespace-nowrap ${isActive
                    ? 'border-black text-black'
                    : 'border-transparent text-gray-500 hover:text-black hover:border-gray-300'
                    }`}
            >
                {children}
            </Link>
        );
    };

    const MobileNavLink = ({ to, children }) => {
        const isActive = location.pathname === to;
        return (
            <Link
                to={to}
                className={`block pl-3 pr-4 py-3 border-l-4 text-lg font-bold transition-colors ${isActive
                    ? 'bg-black text-white border-black'
                    : 'border-transparent text-gray-600 hover:bg-gray-100 hover:border-black hover:text-black'
                    }`}
            >
                {children}
            </Link>
        );
    };

    return (
        <nav className="bg-white border-b-4 border-black">
            <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
                <div className="flex justify-between h-16 lg:h-20">
                    {/* Logo */}
                    <div className="flex items-center">
                        <Link to="/" className="flex-shrink-0 flex items-center gap-1 lg:gap-2 group">
                            <div className="bg-black text-white p-1.5 lg:p-2 group-hover:bg-white group-hover:text-black border-2 border-black transition-colors">
                                <BarChart2 className="h-5 w-5 lg:h-8 lg:w-8" />
                            </div>
                            <span className="text-sm sm:text-lg lg:text-2xl font-black tracking-tighter uppercase">MentorMetrics</span>
                        </Link>
                    </div>

                    {/* Desktop Navigation - Hidden on mobile */}
                    <div className="hidden lg:flex lg:items-center lg:space-x-4">
                        <NavLink to="/">HOME</NavLink>
                        {user && (
                            <>
                                <NavLink to="/upload">UPLOAD</NavLink>
                                <NavLink to="/sessions">SESSIONS</NavLink>
                                <NavLink to="/dashboard">DASHBOARD</NavLink>
                                <NavLink to="/live-practice">
                                    <Zap className="w-4 h-4 mr-1 text-yellow-500" />
                                    LIVE
                                </NavLink>
                            </>
                        )}
                    </div>

                    {/* Desktop Right Side - Hidden on mobile */}
                    <div className="hidden lg:flex lg:items-center lg:space-x-4">
                        {user ? (
                            <>
                                <div className="flex items-center text-xs font-bold border-2 border-black px-2 py-1 bg-gray-100 max-w-[180px]">
                                    <User className="h-4 w-4 mr-1 flex-shrink-0" />
                                    <span className="truncate">{user.email}</span>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="flex items-center px-3 py-1.5 bg-white border-2 border-black text-sm font-bold hover:bg-black hover:text-white transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[1px] hover:translate-y-[1px]"
                                >
                                    <LogOut className="h-4 w-4 mr-1" />
                                    LOGOUT
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={handleLogin}
                                className="px-4 py-2 bg-black text-white border-2 border-black font-bold hover:bg-white hover:text-black transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[1px] hover:translate-y-[1px]"
                            >
                                LOGIN
                            </button>
                        )}
                    </div>

                    {/* Mobile Menu Button - Visible on mobile only */}
                    <div className="flex items-center lg:hidden">
                        <button
                            onClick={toggleMenu}
                            className="inline-flex items-center justify-center p-2 text-black hover:bg-black hover:text-white focus:outline-none border-2 border-black transition-colors"
                        >
                            <span className="sr-only">Open main menu</span>
                            {isMenuOpen ? (
                                <X className="block h-6 w-6" aria-hidden="true" />
                            ) : (
                                <Menu className="block h-6 w-6" aria-hidden="true" />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {isMenuOpen && (
                <div className="lg:hidden border-t-4 border-black bg-white">
                    <div className="pt-2 pb-3 space-y-1 px-2">
                        <MobileNavLink to="/">HOME</MobileNavLink>
                        {user && (
                            <>
                                <MobileNavLink to="/upload">UPLOAD</MobileNavLink>
                                <MobileNavLink to="/sessions">SESSIONS</MobileNavLink>
                                <MobileNavLink to="/dashboard">DASHBOARD</MobileNavLink>
                                <MobileNavLink to="/live-practice">⚡ LIVE PRACTICE</MobileNavLink>
                            </>
                        )}
                    </div>
                    <div className="pt-4 pb-4 border-t-4 border-black">
                        {user ? (
                            <div className="flex flex-col space-y-4 px-4">
                                <div className="flex items-center p-2 border-2 border-black bg-gray-50">
                                    <User className="h-5 w-5 mr-2 flex-shrink-0" />
                                    <div className="text-sm font-bold truncate">{user.email}</div>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="w-full flex justify-center items-center px-4 py-3 bg-white border-2 border-black font-bold hover:bg-black hover:text-white transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]"
                                >
                                    <LogOut className="h-5 w-5 mr-2" />
                                    LOGOUT
                                </button>
                            </div>
                        ) : (
                            <div className="px-4">
                                <button
                                    onClick={handleLogin}
                                    className="w-full flex justify-center px-6 py-3 bg-black text-white border-2 border-black font-bold hover:bg-white hover:text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]"
                                >
                                    LOGIN
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default NavBar;

