import React, { useState, useEffect } from "react";
import { Download } from "lucide-react";
import { API_BASE_URL } from "../../utils/constants";

const ClassificationPage = ({ token, user, onAuthRequired }) => {
  const [files, setFiles] = useState([]);
  const [loadingSpeed, setLoadingSpeed] = useState(false);
  const [loadingAccuracy, setLoadingAccuracy] = useState(false);
  const [classificationType, setClassificationType] = useState(null);
  const [completed, setCompleted] = useState(false);
  const [tableData, setTableData] = useState([]);

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 20;

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
    setCompleted(false);
    setClassificationType(null);
    setTableData([]);
  };

  const handleClassification = async (type) => {
    if (!user) {
      onAuthRequired();
      return;
    }

    if (files.length === 0) {
      alert("Please upload at least one file.");
      return;
    }

    try {
      type === "speed" ? setLoadingSpeed(true) : setLoadingAccuracy(true);

      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));

      const endpoint =
        type === "speed" ? "/predict_speed" : "/predict_accuracy";

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Classification failed");
      }

      const data = await response.json();

      // ✅ FIX: handle both `data.df` and raw JSON array
      let dfArray = [];
      if (Array.isArray(data)) {
        dfArray = data;
      } else if (Array.isArray(data.df)) {
        dfArray = data.df;
      } else if (Array.isArray(data.df_json)) {
        dfArray = data.df_json;
      }

      if (dfArray.length === 0) {
        alert("No table data found in response.");
        return;
      }

      setTableData(dfArray);
      setClassificationType(type);
      setCompleted(true);
      setCurrentPage(1);
    } catch (error) {
      alert(`Failed ${type} classification: ${error.message}`);
    } finally {
      type === "speed" ? setLoadingSpeed(false) : setLoadingAccuracy(false);
    }
  };

  const handleDownload = async () => {
    if (!classificationType) return;

    const endpoint =
      classificationType === "speed"
        ? "/download/speed_classification"
        : "/download/accurate_classification";

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) throw new Error("Download failed");

      const blob = await response.blob();
      const filename =
        classificationType === "speed"
          ? "speed_classification.xlsx"
          : "accuracy_classification.xlsx";

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      alert("Download failed");
    }
  };

  // Pagination logic
  const totalPages = Math.ceil(tableData.length / rowsPerPage);
  const currentRows = tableData.slice(
    (currentPage - 1) * rowsPerPage,
    currentPage * rowsPerPage
  );

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) setCurrentPage(page);
  };

  useEffect(() => {
    setCurrentPage(1);
  }, [tableData]);

  return (
    <div className="p-8 max-w-6xl mx-auto overflow-y-auto min-h-screen">
      <h1 className="text-4xl font-bold text-white mb-6">
        Transaction Classification
      </h1>

      {/* Upload Section */}
      <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 mb-8">
        <label className="block text-gray-300 mb-3 font-medium">
          Upload Transaction Files
        </label>
        <input
          type="file"
          accept=".xlsx,.xls"
          multiple
          onChange={handleFileChange}
          className="w-full px-5 py-4 bg-gray-900 bg-opacity-50 text-white rounded-xl mb-4"
        />

        <div className="flex gap-4 flex-wrap">
          <button
            onClick={() => handleClassification("speed")}
            disabled={loadingSpeed}
            className="flex-1 bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-700 disabled:to-gray-700 text-white font-semibold py-4 rounded-xl transition shadow-lg"
          >
            {loadingSpeed ? "Processing Speed..." : "Classify (Speed)"}
          </button>

          <button
            onClick={() => handleClassification("accuracy")}
            disabled={loadingAccuracy}
            className="flex-1 bg-linear-to-r from-purple-600 to-blue-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-700 disabled:to-gray-700 text-white font-semibold py-4 rounded-xl transition shadow-lg"
          >
            {loadingAccuracy ? "Processing Accuracy..." : "Classify (Accuracy)"}
          </button>
        </div>
      </div>

      {/* Results */}
      {completed && tableData.length > 0 && (
        <div className="bg-gray-800 bg-opacity-50 p-8 rounded-2xl border border-gray-700 mb-1000">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-2xl font-semibold text-white">
              Classification Results
            </h3>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 bg-green-600 px-4 py-2 rounded-xl hover:bg-green-700 text-white"
            >
              <Download size={16} />
              Download{" "}
              {classificationType === "speed" ? "Speed" : "Accuracy"} CSV
            </button>
          </div>

          <div className="max-h-[70vh] overflow-auto rounded-xl">
            <div className="overflow-x-auto">
              <table className="min-w-full border-collapse text-sm text-gray-300">
                <thead>
                  <tr className="bg-gray-900 text-gray-200 sticky top-0">
                    {Object.keys(currentRows[0] || {}).map((key) => (
                      <th
                        key={key}
                        className="py-3 px-4 border-b border-gray-700 text-left"
                      >
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {currentRows.map((row, i) => (
                    <tr
                      key={i}
                      className={`hover:bg-gray-700/50 transition ${
                        i % 2 === 0 ? "bg-gray-900/40" : "bg-gray-800/40"
                      }`}
                    >
                      {Object.values(row).map((value, j) => (
                        <td
                          key={j}
                          className="py-2 px-4 border-b border-gray-700 text-gray-200"
                        >
                          {String(value)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {tableData.length > rowsPerPage && (
            <div className="flex justify-center items-center mt-4 gap-3">
              <button
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1}
                className={`px-3 py-1 rounded-lg border ${
                  currentPage === 1
                    ? "border-gray-700 text-gray-500 cursor-not-allowed"
                    : "border-gray-500 hover:bg-gray-700"
                }`}
              >
                Prev
              </button>

              <span className="text-gray-300">
                Page {currentPage} of {totalPages}
              </span>

              <button
                onClick={() => goToPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={`px-3 py-1 rounded-lg border ${
                  currentPage === totalPages
                    ? "border-gray-700 text-gray-500 cursor-not-allowed"
                    : "border-gray-500 hover:bg-gray-700"
                }`}
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ClassificationPage;
