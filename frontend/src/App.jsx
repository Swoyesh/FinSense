import React, { useState, useRef } from 'react';
import { useAuth } from './hooks/useAuth';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import ChatPage from './components/chat/ChatPage';
import BudgetPage from './components/budget/BudgetPage';
import AuthModal from './components/auth/AuthModal';
import './index.css';

function App() {
  const { user, token, login, register, logout, loading } = useAuth();
  const [currentPage, setCurrentPage] = useState('chat');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleAuthRequired = () => {
    setShowAuthModal(true);
  };

  const handleAuthSuccess = () => {
    setShowAuthModal(false);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    if (window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  };

  const chatPageRef = useRef()

  const handleLogoClick = () => {
    chatPageRef.current.resetChat()
  }

  if (loading) {
    return (
      <div className="h-screen bg-linear-to-br from-gray-950 via-gray-900 to-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-linear-to-br from-gray-950 via-gray-900 to-gray-950 text-white flex flex-col overflow-hidden">
      <Header
      onLogoClick = {handleLogoClick}
        user={user}
        onAuthClick={() => setShowAuthModal(true)}
        onLogout={logout}
      />

      <div className="flex flex-1 overflow-hidden">
        {user && (
          <Sidebar
            currentPage={currentPage}
            onPageChange={handlePageChange}
            isOpen={sidebarOpen}
            toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          />
        )}

        <main className={`flex-1 ${user ? 'lg:ml-72' : ''} overflow-hidden`}>
          {currentPage === 'chat' ? (
            <ChatPage ref={chatPageRef} token={token} onAuthRequired={handleAuthRequired} />
          ) : user ? (
            <BudgetPage
              token={token}
              user={user}
              onAuthRequired={handleAuthRequired}
            />
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <p className="text-gray-400 mb-4">
                  Please login to access Budget Forecast
                </p>
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="bg-linear-to-r from-blue-600 to-purple-600 px-6 py-3 rounded-xl"
                >
                  Sign In
                </button>
              </div>
            </div>
          )}
        </main>
      </div>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
        onLogin={login}
        onRegister={register}
      />
    </div>
  );
}

export default App
