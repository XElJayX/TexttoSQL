import { useState } from "react";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  .app {
    min-height: 100vh;
    background: #0a0a0f;
    color: #e8e4dc;
    font-family: 'DM Sans', sans-serif;
    position: relative;
    overflow-x: hidden;
  }

  .noise {
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E");
    opacity: 0.03;
    pointer-events: none;
    z-index: 0;
  }

  .glow-orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(120px);
    pointer-events: none;
    z-index: 0;
  }
  .glow-orb-1 {
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(212,175,55,0.08) 0%, transparent 70%);
    top: -100px; right: -100px;
  }
  .glow-orb-2 {
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(100,80,200,0.06) 0%, transparent 70%);
    bottom: -50px; left: -80px;
  }

  .container {
    position: relative;
    z-index: 1;
    max-width: 900px;
    margin: 0 auto;
    padding: 60px 32px 80px;
  }

  /* HEADER */
  .header {
    margin-bottom: 56px;
  }
  .header-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 400;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #d4af37;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .header-eyebrow::before {
    content: '';
    display: inline-block;
    width: 24px;
    height: 1px;
    background: #d4af37;
  }
  .header-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(36px, 5vw, 52px);
    font-weight: 500;
    line-height: 1.1;
    letter-spacing: -0.02em;
    color: #f0ece4;
  }
  .header-title em {
    font-style: italic;
    color: #d4af37;
  }
  .header-subtitle {
    margin-top: 14px;
    font-size: 15px;
    font-weight: 300;
    color: #7a7570;
    letter-spacing: 0.01em;
    max-width: 460px;
    line-height: 1.6;
  }

  /* DIVIDER */
  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(212,175,55,0.3) 30%, rgba(212,175,55,0.3) 70%, transparent);
    margin-bottom: 40px;
  }

  /* INPUT SECTION */
  .input-section {
    margin-bottom: 40px;
  }
  .input-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #5a5550;
    margin-bottom: 10px;
    display: block;
  }
  .input-wrapper {
    display: flex;
    gap: 0;
    border: 1px solid rgba(212,175,55,0.2);
    border-radius: 4px;
    background: rgba(255,255,255,0.02);
    transition: border-color 0.25s, box-shadow 0.25s;
    overflow: hidden;
  }
  .input-wrapper:focus-within {
    border-color: rgba(212,175,55,0.5);
    box-shadow: 0 0 0 3px rgba(212,175,55,0.06), 0 4px 24px rgba(0,0,0,0.3);
  }
  .query-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    padding: 16px 20px;
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    font-weight: 300;
    color: #e8e4dc;
    letter-spacing: 0.01em;
  }
  .query-input::placeholder { color: #3a3632; }
  .submit-btn {
    background: #d4af37;
    color: #0a0a0f;
    border: none;
    padding: 16px 28px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    cursor: pointer;
    transition: background 0.2s, opacity 0.2s;
    white-space: nowrap;
    flex-shrink: 0;
  }
  .submit-btn:hover:not(:disabled) { background: #e8c84a; }
  .submit-btn:disabled { opacity: 0.45; cursor: not-allowed; }

  /* LOADING */
  .loading-bar {
    height: 2px;
    background: rgba(212,175,55,0.15);
    border-radius: 1px;
    overflow: hidden;
    margin-top: 12px;
  }
  .loading-bar-inner {
    height: 100%;
    background: linear-gradient(90deg, transparent, #d4af37, transparent);
    animation: shimmer 1.4s infinite;
    width: 60%;
  }
  @keyframes shimmer {
    0% { transform: translateX(-200%); }
    100% { transform: translateX(350%); }
  }

  /* ERROR */
  .error-box {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(220, 60, 60, 0.06);
    border: 1px solid rgba(220, 60, 60, 0.2);
    border-radius: 4px;
    padding: 14px 18px;
    margin-bottom: 28px;
    font-size: 13px;
    color: #e07070;
    letter-spacing: 0.01em;
  }
  .error-dot {
    width: 6px; height: 6px;
    background: #e07070;
    border-radius: 50%;
    flex-shrink: 0;
  }

  /* RESULTS SECTIONS */
  .results-grid {
    display: flex;
    flex-direction: column;
    gap: 28px;
    animation: fadeUp 0.4s ease both;
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .card {
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 6px;
    overflow: hidden;
    background: rgba(255,255,255,0.015);
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    background: rgba(255,255,255,0.02);
  }
  .card-title {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #5a5550;
  }
  .card-badge {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #d4af37;
    background: rgba(212,175,55,0.08);
    border: 1px solid rgba(212,175,55,0.15);
    padding: 3px 8px;
    border-radius: 2px;
    letter-spacing: 0.05em;
  }

  /* SQL BLOCK */
  .sql-code {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    line-height: 1.7;
    color: #c8c0b0;
    padding: 20px 24px;
    overflow-x: auto;
    white-space: pre;
    letter-spacing: 0.02em;
  }
  .sql-keyword { color: #d4af37; }
  .sql-fn { color: #a89fd4; }
  .sql-str { color: #7aad8a; }

  /* TABLES TAGS */
  .tables-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 18px 20px;
  }
  .table-tag {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #9090a8;
    background: rgba(100,80,200,0.07);
    border: 1px solid rgba(100,80,200,0.15);
    padding: 5px 12px;
    border-radius: 2px;
    letter-spacing: 0.06em;
    transition: border-color 0.2s, color 0.2s;
  }
  .table-tag:hover {
    border-color: rgba(100,80,200,0.4);
    color: #b0b0d0;
  }

  /* RESULTS TABLE */
  .table-scroll {
    overflow-x: auto;
  }
  .results-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
  }
  .results-table thead tr {
    background: rgba(255,255,255,0.025);
    border-bottom: 1px solid rgba(212,175,55,0.15);
  }
  .results-table th {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #d4af37;
    padding: 13px 20px;
    text-align: left;
    font-weight: 400;
    white-space: nowrap;
  }
  .results-table td {
    padding: 12px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.035);
    color: #b8b0a4;
    font-weight: 300;
    white-space: nowrap;
  }
  .results-table tbody tr {
    transition: background 0.15s;
  }
  .results-table tbody tr:last-child td { border-bottom: none; }
  .results-table tbody tr:hover { background: rgba(255,255,255,0.025); }

  .row-count {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: #3a3632;
    letter-spacing: 0.1em;
  }

  /* EMPTY */
  .empty-state {
    text-align: center;
    padding: 64px 20px;
    color: #2e2c28;
  }
  .empty-icon {
    font-size: 32px;
    margin-bottom: 12px;
    opacity: 0.4;
  }
  .empty-text {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }
`;

function highlightSQL(sql) {
  const keywords = /\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|GROUP BY|ORDER BY|HAVING|LIMIT|OFFSET|AND|OR|NOT|IN|LIKE|AS|DISTINCT|COUNT|SUM|AVG|MAX|MIN|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TABLE|INDEX|NULL|IS|BY|ASC|DESC|UNION|WITH|CASE|WHEN|THEN|ELSE|END)\b/gi;
  const fns = /\b(COALESCE|IFNULL|ISNULL|CAST|CONVERT|SUBSTRING|TRIM|UPPER|LOWER|LENGTH|ROUND|FLOOR|CEIL|NOW|DATE|YEAR|MONTH|DAY)\b/gi;
  const strings = /('([^'\\]|\\.)*')/g;

  return sql
    .replace(strings, '<span class="sql-str">$1</span>')
    .replace(keywords, '<span class="sql-keyword">$&</span>')
    .replace(fns, '<span class="sql-fn">$&</span>');
}

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
      const response = await fetch(`${import.meta.env.VITE_API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, execute: true }),
      });
      if (!response.ok) throw new Error("API request failed");
      const data = await response.json();
      setSql(data.sql || "");
      setResult(data.results || []);
      setColumns(data.columns || []);
      setRetrievedTables(data.retrieved_tables || []);
    } catch (err) {
      setError("The query could not be processed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const hasResults = sql || retrievedTables.length > 0 || result.length > 0;

  return (
    <>
      <style>{styles}</style>
      <div className="app">
        <div className="noise" />
        <div className="glow-orb glow-orb-1" />
        <div className="glow-orb glow-orb-2" />

        <div className="container">
          {/* HEADER */}
          <header className="header">
            <div className="header-eyebrow">Text-to-SQL Interface</div>
            <h1 className="header-title">
              Query your data<br />
              Text to <em>SQL</em>
            </h1>
            <p className="header-subtitle">
              Translate natural language questions into precise SQL — no syntax required.
            </p>
          </header>

          <div className="divider" />

          {/* INPUT */}
          <div className="input-section">
            <label className="input-label">Your question</label>
            <div className="input-wrapper">
              <input
                className="query-input"
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                placeholder="e.g. Show me total revenue by region last quarter"
              />
              <button className="submit-btn" onClick={handleSubmit} disabled={loading}>
                {loading ? "Processing" : "Run Query"}
              </button>
            </div>
            {loading && (
              <div className="loading-bar">
                <div className="loading-bar-inner" />
              </div>
            )}
          </div>

          {/* ERROR */}
          {error && (
            <div className="error-box">
              <div className="error-dot" />
              {error}
            </div>
          )}

          {/* RESULTS */}
          {!loading && hasResults && (
            <div className="results-grid">

              {/* SQL */}
              {sql && (
                <div className="card">
                  <div className="card-header">
                    <span className="card-title">Generated SQL</span>
                    <span className="card-badge">SQL</span>
                  </div>
                  <div
                    className="sql-code"
                    dangerouslySetInnerHTML={{ __html: highlightSQL(sql) }}
                  />
                </div>
              )}

              {/* TABLES */}
              {retrievedTables.length > 0 && (
                <div className="card">
                  <div className="card-header">
                    <span className="card-title">Referenced Tables</span>
                    <span className="card-badge">{retrievedTables.length} table{retrievedTables.length !== 1 ? "s" : ""}</span>
                  </div>
                  <div className="tables-list">
                    {retrievedTables.map((t) => (
                      <span key={t} className="table-tag">{t}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* RESULTS TABLE */}
              {result.length > 0 && (
                <div className="card">
                  <div className="card-header">
                    <span className="card-title">Query Results</span>
                    <span className="row-count">{result.length} row{result.length !== 1 ? "s" : ""}</span>
                  </div>
                  <div className="table-scroll">
                    <table className="results-table">
                      {columns.length > 0 && (
                        <thead>
                          <tr>
                            {columns.map((col) => (
                              <th key={col}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                      )}
                      <tbody>
                        {result.map((row, i) => (
                          <tr key={i}>
                            {row.map((cell, j) => (
                              <td key={j}>{cell ?? <span style={{ color: "#2e2c28" }}>null</span>}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

            </div>
          )}

          {/* EMPTY */}
          {!loading && !hasResults && !error && (
            <div className="empty-state">
              <div className="empty-icon">⌘</div>
              <div className="empty-text">Ask a question to begin</div>
            </div>
          )}

        </div>
      </div>
    </>
  );
}