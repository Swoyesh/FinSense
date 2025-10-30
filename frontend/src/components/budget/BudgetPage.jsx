import React, { useState } from "react";
import {
  Upload,
  Download,
  TrendingUp,
  BarChart3,
  PieChart,
  Sparkles,
} from "lucide-react";
import { budgetAPI } from "../../services/api";

const BudgetPage = ({ token, user, onAuthRequired }) => {
  const [files, setFiles] = useState([]);
  const [income, setIncome] = useState("");
  const [savings, setSavings] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleSubmit = async () => {
    if (!user) {
      onAuthRequired();
      return;
    }

    if (files.length === 0 || !income || !savings) {
      alert("Please fill all fields and upload at least one file");
      return;
    }

    setLoading(true);

    try {
      const data = await budgetAPI.predictBudget(files, income, savings);
      setResults(data);
    } catch (error) {
      alert(
        "Failed to process budget forecast: " +
          (error.response?.data?.detail || error.message)
      );
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = async (type) => {
    try {
      let blob;
      let filename;

      if (type === "classification") {
        blob = await budgetAPI.downloadClassification();
        filename = "transaction_classification.xlsx";
      } else {
        blob = await budgetAPI.downloadBudget();
        filename = "budget_forecast.xlsx";
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert(
        "Download failed: " + (error.response?.data?.detail || error.message)
      );
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto overflow-y-auto h-full">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-linear-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-4">
          Classification & Budget Forecast
        </h1>
        <div>
        <p className="text-gray-400">
          Upload your transaction history to generate intelligent budget
          forecasts
        </p>
        </div>
      </div>

      <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 mb-8">
        <h2 className="text-2xl font-semibold text-white mb-6 flex items-center space-x-2">
          <Upload size={24} className="text-blue-400" />
          <span>Upload Transaction Data</span>
        </h2>

        <div className="space-y-6">
          <div>
            <label className="block text-gray-300 mb-3 font-medium">
              Transaction Files (Excel)
            </label>
            <input
              type="file"
              accept=".xlsx,.xls"
              multiple
              onChange={handleFileChange}
              className="w-full px-5 py-4 bg-gray-900 bg-opacity-50 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition"
            />
            {files.length > 0 && (
              <p className="text-blue-400 mt-3 flex items-center space-x-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span>{files.length} file(s) selected</span>
              </p>
            )}
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-gray-300 mb-3 font-medium">
                Monthly Income (NPR)
              </label>
              <input
                type="number"
                value={income}
                onChange={(e) => setIncome(e.target.value)}
                placeholder="100000"
                className="w-full px-5 py-4 bg-gray-900 bg-opacity-50 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition"
              />
            </div>

            <div>
              <label className="block text-gray-300 mb-3 font-medium">
                Savings Target (NPR)
              </label>
              <input
                type="number"
                value={savings}
                onChange={(e) => setSavings(e.target.value)}
                placeholder="20000"
                className="w-full px-5 py-4 bg-gray-900 bg-opacity-50 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition"
              />
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-700 disabled:to-gray-700 text-white font-semibold py-4 rounded-xl transition shadow-lg shadow-blue-500/20"
          >
            {loading ? (
              <span className="flex items-center justify-center space-x-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Analyzing...</span>
              </span>
            ) : (
              "Generate Forecast"
            )}
          </button>
        </div>
      </div>

      {results && (
        <div className="space-y-6">
          {/* Download Buttons */}
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => downloadFile("classification")}
              className="flex items-center space-x-2 bg-green-600 bg-opacity-20 hover:bg-opacity-30 border border-green-500 border-opacity-30 px-6 py-3 rounded-xl transition"
            >
              <Download size={20} />
              <span className="font-medium">Download Classification</span>
            </button>
            <button
              onClick={() => downloadFile("budget")}
              className="flex items-center space-x-2 bg-purple-600 bg-opacity-20 hover:bg-opacity-30 border border-purple-500 border-opacity-30 px-6 py-3 rounded-xl transition"
            >
              <Download size={20} />
              <span className="font-medium">Download Budget</span>
            </button>
          </div>

          {/* Forecast Visualization */}
          {results.image_data && (
            <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
              <h3 className="text-2xl font-semibold text-white mb-6 flex items-center space-x-2">
                <BarChart3 size={24} className="text-purple-400" />
                <span>Forecast Visualization</span>
              </h3>
              <div className="bg-white rounded-xl p-4">
                <img
                  src={`data:image/png;base64,${results.image_data}`}
                  alt="Budget Forecast"
                  className="w-full rounded-lg"
                />
              </div>
              <p className="text-gray-400 text-sm mt-4 flex items-center space-x-2">
                <Sparkles size={16} className="text-blue-400" />
                <span>Chart generated from 3+ months of transaction data</span>
              </p>
            </div>
          )}

          {/* Budget Allocation */}
          {results.budget && (
            <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
              <h3 className="text-2xl font-semibold text-white mb-6 flex items-center space-x-2">
                <PieChart size={24} className="text-blue-400" />
                <span>Budget Allocation</span>
              </h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(results.budget).map(([category, amount]) => (
                  <div
                    key={category}
                    className="bg-gray-900 bg-opacity-50 p-6 rounded-xl border border-gray-700 hover:border-gray-600 transition"
                  >
                    <p className="text-gray-400 text-sm font-medium mb-2">
                      {category}
                    </p>
                    <p className="text-3xl font-bold bg-linear-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                      NPR {amount.toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Forecast Details */}
          {results.forecast && (
            <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
              <h3 className="text-2xl font-semibold text-white mb-6 flex items-center space-x-2">
                <TrendingUp size={24} className="text-yellow-400" />
                <span>Forecast Details</span>
              </h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(results.forecast).map(([key, value]) => (
                  <div
                    key={key}
                    className="bg-gray-900 bg-opacity-50 p-6 rounded-xl border border-gray-700 hover:border-gray-600 transition"
                  >
                    <p className="text-gray-400 text-sm font-medium mb-2 capitalize">
                      {key.replaceAll("_", " ")}
                    </p>
                    <p className="text-3xl font-bold bg-linear-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                      {typeof value === "number"
                        ? value.toFixed(2)
                        : Array.isArray(value) || typeof value === "object"
                        ? JSON.stringify(value)
                        : value}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BudgetPage;
