import { useState } from "react";

export default function App() {
  const [question, setQuestion] = useState("");
  const [sql, setSql] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState([]);
  const [columns, setColumns] = useState([]);
  const [retrievedTables, setRetrievedTables] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError(null);

    try {
           const response = await fetch(`${import.meta.env.VITE_API_URL}/query`, 
  {        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
          execute: true,
        }),
      });

      if (!response.ok) {
        throw new Error("API request failed");
      }

      const data = await response.json();

      setSql(data.sql || "");
      setResult(data.results || []);
      setColumns(data.columns || []);
      setRetrievedTables(data.retrieved_tables || []);
    } catch (err) {
      console.error("Error:", err);
      setError("Something went wrong while generating SQL.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>Text-to-SQL Demo</h1>

      {/* INPUT SECTION */}
      <div style={{ marginBottom: "20px" }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter your question about the database..."
          style={{ width: "400px", padding: "8px" }}
        />

        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{ marginLeft: "10px", padding: "8px 12px" }}
        >
          {loading ? "Generating SQL..." : "Generate SQL"}
        </button>
      </div>

      {/* ERROR */}
      {error && (
        <div style={{ color: "red", marginBottom: "10px" }}>
          {error}
        </div>
      )}

      {/* SQL OUTPUT */}
      {sql && (
        <div style={{ marginBottom: "20px" }}>
          <h3>Generated SQL</h3>
          <pre style={{ background: "#f4f4f4", padding: "10px" }}>
            {sql}
          </pre>
        </div>
      )}

      {/* RETRIEVED TABLES */}
      {retrievedTables.length > 0 && (
        <div style={{ marginBottom: "20px" }}>
          <h3>Retrieved Tables</h3>
          {retrievedTables.map((table) => (
            <span
              key={table}
              style={{
                marginRight: "10px",
                padding: "4px 8px",
                background: "#e0e0e0",
                borderRadius: "4px",
              }}
            >
              {table}
            </span>
          ))}
        </div>
      )}

      {/* RESULTS TABLE */}
      {result.length > 0 && (
        <div>
          <h3>Results</h3>

          <table
            border="1"
            cellPadding="8"
            style={{ borderCollapse: "collapse" }}
          >
            {/* HEADER */}
            {columns.length > 0 && (
              <thead>
                <tr>
                  {columns.map((col) => (
                    <th key={col} style={{ background: "#f0f0f0" }}>
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
            )}

            {/* BODY */}
            <tbody>
              {result.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}