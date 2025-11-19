import React, { useState } from "react";
import { X } from "lucide-react";
import f_logo from "../../assets/final_logo.png";

const AuthModal = ({ isOpen, onClose, onSuccess, onLogin, onRegister }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    fullName: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async () => {
    setError("");
    setLoading(true);

    try {
      if (isLogin) {
        await onLogin(formData.username, formData.password);
      } else {
        await onRegister(
          formData.email,
          formData.username,
          formData.fullName,
          formData.password
        );
      }
      onSuccess();
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || "Authentication failed"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") handleSubmit();
  };

  const handleChange = (field) => (e) => {
    setFormData({ ...formData, [field]: e.target.value });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl max-w-md w-full p-8 relative shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-6 right-6 text-gray-400 hover:text-white transition"
        >
          <X size={24} />
        </button>

        <div className="mb-8">  
          <div>
            <img src={f_logo} alt="Logo" className="w-12 h-12" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">
            {isLogin ? "Welcome Back" : "Get Started"}
          </h2>
          <p className="text-gray-400">
            {isLogin ? "Sign in to your account" : "Create your account"}
          </p>
        </div>

        {error && (
          <div className="bg-red-500 bg-opacity-10 border border-red-500 text-red-400 px-4 py-3 rounded-xl mb-6 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4">
          {!isLogin && (
            <>
              <input
                type="email"
                placeholder="Email address"
                className="w-full px-4 py-3.5 bg-gray-800 bg-opacity-50 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition"
                value={formData.email}
                onChange={handleChange("email")}
                onKeyPress={handleKeyPress}
              />
              <input
                type="text"
                placeholder="Full name"
                className="w-full px-4 py-3.5 bg-gray-800 bg-opacity-50 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition"
                value={formData.fullName}
                onChange={handleChange("fullName")}
                onKeyPress={handleKeyPress}
              />
            </>
          )}

          <input
            type="text"
            placeholder="Username"
            className="w-full px-4 py-3.5 bg-gray-800 bg-opacity-50 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition"
            value={formData.username}
            onChange={handleChange("username")}
            onKeyPress={handleKeyPress}
          />

          <input
            type="password"
            placeholder="Password"
            className="w-full px-4 py-3.5 bg-gray-800 bg-opacity-50 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition"
            value={formData.password}
            onChange={handleChange("password")}
            onKeyPress={handleKeyPress}
          />

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3.5 rounded-xl transition disabled:opacity-50 shadow-lg shadow-blue-500/20"
          >
            {loading ? "Processing..." : isLogin ? "Sign In" : "Create Account"}
          </button>
        </div>

        <div className="mt-6 text-center">
          <span className="text-gray-400 text-sm">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
          </span>
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError("");
            }}
            className="text-blue-400 hover:text-blue-300 font-medium text-sm transition"
          >
            {isLogin ? "Sign Up" : "Sign In"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
