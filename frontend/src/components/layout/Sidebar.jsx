import React from 'react';
import { MessageCircle, TrendingUp, Menu, Sparkles } from 'lucide-react';

const Sidebar = ({ currentPage, onPageChange, isOpen, toggleSidebar }) => {
  return (
    <>
      <button
        onClick={toggleSidebar}
        className="fixed top-24 left-4 z-40 lg:hidden bg-gray-800 bg-opacity-50 backdrop-blur-sm p-3 rounded-xl border border-gray-700"
      >
        <Menu size={20} />
      </button>

      <aside
        className={`fixed left-0 top-[73px] h-[calc(100%-73px)] bg-gray-900 bg-opacity-50 backdrop-blur-xl border-r border-gray-800 transition-transform ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 w-72 z-30`}
      >
        <nav className="p-6 space-y-3">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Navigation
          </div>
          <button
            onClick={() => {
              onPageChange('chat');
              toggleSidebar();
            }}
            className={`w-full flex items-center space-x-3 px-5 py-3.5 rounded-xl transition group ${
              currentPage === 'chat'
                ? 'bg-linear-to-r from-blue-600 to-purple-600 shadow-lg shadow-blue-500/20'
                : 'hover:bg-gray-800 hover:bg-opacity-50'
            }`}
          >
            <MessageCircle
              size={20}
              className={
                currentPage === 'chat'
                  ? 'text-white'
                  : 'text-gray-400 group-hover:text-white'
              }
            />
            <span
              className={`font-medium ${
                currentPage === 'chat'
                  ? 'text-white'
                  : 'text-gray-400 group-hover:text-white'
              }`}
            >
              AI Assistant
            </span>
          </button>
          <button
            onClick={() => {
              onPageChange('budget');
              toggleSidebar();
            }}
            className={`w-full flex items-center space-x-3 px-5 py-3.5 rounded-xl transition group ${
              currentPage === 'budget'
                ? 'bg-linear-to-r from-blue-600 to-purple-600 shadow-lg shadow-blue-500/20'
                : 'hover:bg-gray-800 hover:bg-opacity-50'
            }`}
          >
            <TrendingUp
              size={20}
              className={
                currentPage === 'budget'
                  ? 'text-white'
                  : 'text-gray-400 group-hover:text-white'
              }
            />
            <span
              className={`font-medium ${
                currentPage === 'budget'
                  ? 'text-white'
                  : 'text-gray-400 group-hover:text-white'
              }`}
            >
              Budget Forecast
            </span>
          </button>

          <div className="pt-6 mt-6 border-t border-gray-800">
            <div className="bg-linear-to-br from-blue-600 to-purple-600 p-4 rounded-xl">
              <div className="flex items-center space-x-2 mb-2">
                <Sparkles size={18} className="text-white" />
                <span className="text-sm font-semibold text-white">Pro Tip</span>
              </div>
              <p className="text-xs text-blue-100 leading-relaxed">
                Upload 3+ months of transaction data for accurate forecasts and
                visualizations!
              </p>
            </div>
          </div>
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;