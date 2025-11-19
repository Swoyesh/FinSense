import React, { useState } from 'react';
import { TrendingUp, PieChart } from 'lucide-react';
import { budgetAPI } from '../../services/api';

const BudgetPage = ({ token, user, onAuthRequired }) => {
  const [income, setIncome] = useState('');
  const [savings, setSavings] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async () => {
    if (!user) {
      onAuthRequired();
      return;
    }

    if (income === '' || savings === '') {
      setErrorMessage('Please enter both income and savings.');
      return;
    }

    if (income < 0 || savings < 0) {
      setErrorMessage('Income and savings cannot be negative.');
      return;
    }

    if (Number(savings) >= Number(income)) {
      setErrorMessage('Savings cannot be equal to or greater than income.');
      return;
    }

    setErrorMessage('');
    setLoading(true);

    try {
      const data = await budgetAPI.generateBudget([], income, savings);
      setResults(data);
    } catch (error) {
      alert('Failed to process budget: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const downloadBudget = async () => {
    try {
      const blob = await budgetAPI.downloadBudget();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'budget_forecast.xlsx';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('Download failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  const isButtonDisabled =
    loading ||
    income === '' ||
    savings === '' ||
    income < 0 ||
    savings < 0 ||
    Number(savings) >= Number(income);

  return (
    <div className="p-8 max-w-5xl mx-auto overflow-y-auto h-full">
      <h1 className="text-4xl font-bold bg-linear-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-4">
        Budget Forecast
      </h1>

      <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 mb-8">
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-gray-300 mb-3 font-medium">Monthly Income (NPR)</label>
            <input
              type="number"
              min="0"
              value={income}
              onChange={(e) => setIncome(e.target.value)}
              placeholder="100000"
              className="w-full px-5 py-4 bg-gray-900 bg-opacity-50 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition"
            />
          </div>
          <div>
            <label className="block text-gray-300 mb-3 font-medium">Savings Target (NPR)</label>
            <input
              type="number"
              min="0"
              value={savings}
              onChange={(e) => setSavings(e.target.value)}
              placeholder="20000"
              className="w-full px-5 py-4 bg-gray-900 bg-opacity-50 text-white rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700 focus:border-blue-500 transition"
            />
          </div>
        </div>

        {errorMessage && (
          <p className="text-red-400 font-semibold mb-4">{errorMessage}</p>
        )}

        <button
          onClick={handleSubmit}
          disabled={isButtonDisabled}
          className="w-full bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-700 disabled:to-gray-700 text-white font-semibold py-4 rounded-xl transition shadow-lg shadow-blue-500/20"
        >
          {loading ? 'Processing...' : 'Generate Forecast'}
        </button>
      </div>

      {results && (
        <div className="space-y-6">
          {/* Forecast Image */}
          {results.image_data && (
            <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8">
              <h3 className="text-2xl font-semibold text-white mb-6 flex items-center space-x-2">
                <TrendingUp size={24} className="text-blue-400" />
                <span>Forecast Visualization</span>
              </h3>
              <img
                src={`data:image/png;base64,${results.image_data}`}
                alt="Budget Forecast"
                className="w-full h-auto rounded-xl border border-gray-700"
              />
            </div>
          )}

          {/* Budget Table or Message */}
          {results.budget && Object.keys(results.budget).length > 0 ? (
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
                    <p className="text-gray-400 text-sm font-medium mb-2">{category}</p>
                    <p className="text-3xl font-bold bg-linear-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                      NPR {amount.toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
              {/* Only show download button if budget exists */}
              <button
                onClick={downloadBudget}
                className="mt-6 bg-green-600 px-6 py-3 rounded-xl font-semibold text-white"
              >
                Download Budget
              </button>
            </div>
          ) : (
            <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 text-center text-red-400 font-semibold">
              {results.message || 'No budget data available.'}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BudgetPage;
