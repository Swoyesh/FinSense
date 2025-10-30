import React, {
  useState,
  useEffect,
  useRef,
  useImperativeHandle,
  forwardRef,
} from "react";
import { Send } from "lucide-react";
import { chatAPI } from "../../services/api";
import f_logo from "../../assets/final_logo.png";

const ChatPage = forwardRef(({ token, onAuthRequired }, ref) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useImperativeHandle(ref, () => ({
    resetChat: () => {
      setMessages([]);
    },
  }));

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      console.log("Sending message to backend...");
      const data = await chatAPI.sendMessage(userMessage, token);

      console.log("Backend response:", data);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            data.response ||
            "I apologize, but I couldn't process that request.",
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      if (error.response?.status === 401) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "This question requires authentication. Please sign in to continue.",
            requiresAuth: true,
          },
        ]);
        onAuthRequired();
      } else {
        // Show the actual error message
        const errorMessage =
          error.response?.data?.detail ||
          error.response?.data?.response ||
          error.message ||
          "I encountered an error. Please try again.";

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: errorMessage,
          },
        ]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const exampleQuestions = [
    {
      icon: "💡",
      title: "Financial Basics",
      question: "What is compound interest and is it useful?",
    },
    {
      icon: "💰",
      title: "Differences",
      question: "Explain the difference between sip and mutual funds?",
    },
    {
      icon: "📈",
      title: "Investment Guide",
      question: "Explain investment basics for beginners",
    },
  ];

  if (messages.length === 0) {
    return (
      <div className="flex flex-col h-full items-center justify-center p-6">
        <div className="max-w-4xl w-full space-y-12">
          <div className="text-center space-y-6">
            <div className="flex justify-center mb-8">
              <div className="relative">
                <div className="absolute inset-0 bg-linear-to-r from-blue-500 to-purple-600 rounded-3xl blur-2xl opacity-25"></div>
                <div>
                  <img src={f_logo} alt="Logo" className="w-40 h-40" />
                </div>
              </div>
            </div>
            <h1 className="text-6xl font-bold bg-linear-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent leading-tight">
              FinSense AI
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
              Your intelligent financial companion. Get instant answers about
              budgeting, investments, and personal finance.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            {exampleQuestions.map((item, idx) => (
              <button
                key={idx}
                onClick={() => setInput(item.question)}
                className="bg-gray-800 bg-opacity-50 backdrop-blur-sm p-6 rounded-2xl hover:bg-opacity-70 transition border border-gray-700 hover:border-gray-600 text-left group"
              >
                <div className="text-3xl mb-3">{item.icon}</div>
                <p className="text-white font-semibold mb-2 group-hover:text-blue-400 transition">
                  {item.title}
                </p>
                <p className="text-gray-400 text-sm leading-relaxed">
                  {item.question}
                </p>
              </button>
            ))}
          </div>

          <div className="flex space-x-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask anything about finance..."
              className="flex-1 px-6 py-4 bg-gray-800 bg-opacity-50 backdrop-blur-sm text-white rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg border border-gray-700 focus:border-blue-500 transition"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed p-4 rounded-2xl transition shadow-lg shadow-blue-500/20"
            >
              <Send size={24} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-3xl px-6 py-4 rounded-2xl ${
                msg.role === "user"
                  ? "bg-linear-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20"
                  : msg.requiresAuth
                  ? "bg-yellow-600 bg-opacity-10 border border-yellow-600 border-opacity-30 text-yellow-300"
                  : "bg-gray-800 bg-opacity-50 backdrop-blur-sm text-gray-100 border border-gray-700"
              }`}
            >
              <p className="whitespace-pre-wrap leading-relaxed">
                {msg.content}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm px-6 py-4 rounded-2xl border border-gray-700">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
                  style={{ animationDelay: "150ms" }}
                ></div>
                <div
                  className="w-2 h-2 bg-pink-500 rounded-full animate-bounce"
                  style={{ animationDelay: "300ms" }}
                ></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-gray-800 p-6 bg-gray-900 bg-opacity-50 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto flex space-x-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a follow-up question..."
            className="flex-1 px-6 py-4 bg-gray-800 bg-opacity-50 backdrop-blur-sm text-white rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed p-4 rounded-2xl transition shadow-lg shadow-blue-500/20"
          >
            <Send size={24} />
          </button>
        </div>
      </div>
    </div>
  );
});

export default ChatPage;
