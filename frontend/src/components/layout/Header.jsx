import React from 'react';
import { LogOut, User } from 'lucide-react';
import { Link } from 'react-router-dom';
import f_logo from '../../assets/final_logo.png'

const Header = ({ user, onAuthClick, onLogout, onLogoClick }) => {
  return (
    <header className="bg-gray-900 bg-opacity-50 backdrop-blur-xl border-b border-gray-800 px-6 py-4 sticky top-0 z-50 cursor-pointer">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3" onClick={onLogoClick}>
          <div >
            <img src={f_logo} alt="Logo" className="w-12 h-12" />
          </div>
          <div>
            <span className="text-2xl font-bold bg-linear-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              FinSense
            </span>
            <p className="text-xs text-gray-500">AI-Powered Finance</p>
          </div>
        </div>

        {user ? (
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3 bg-gray-800 bg-opacity-50 backdrop-blur-sm px-4 py-2.5 rounded-xl border border-gray-700">
              <div className="w-8 h-8 bg-linear-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <User size={18} className="text-white" />
              </div>
              <div className="hidden md:block">
                <p className="text-sm font-medium text-white">{user.full_name}</p>
                <p className="text-xs text-gray-400">@{user.username}</p>
              </div>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center space-x-2 bg-red-600 bg-opacity-20 hover:bg-opacity-30 border border-red-500 border-opacity-30 px-4 py-2.5 rounded-xl transition"
            >
              <LogOut size={18} />
              <span className="hidden md:inline">Logout</span>
            </button>
          </div>
        ) : (
          <button
            onClick={onAuthClick}
            className="bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-2.5 rounded-xl font-semibold transition shadow-lg shadow-blue-500/20"
          >
            Sign In
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;