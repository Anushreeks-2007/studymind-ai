import { useState } from "react";
import {
  Brain,
  LayoutDashboard,
  Database,
  Search,
  FileText,
  Activity,
  Settings,
  Plus,
  Send,
  Sparkles,
  Network,
  Clock3,
  Menu,
  PanelLeftClose
} from "lucide-react";

import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [documents, setDocuments] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const navigation = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Context Analysis", icon: Brain },
    { name: "Operational Memory", icon: Database },
    { name: "Knowledge Search", icon: Search },
    { name: "Evidence Tracking", icon: FileText },
    { name: "Decision Support", icon: Activity }
  ];

  async function processDocuments() {
    const documentList = documents
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);

    if (documentList.length < 4) {
      setMessage("Please enter at least 4 documents.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/process`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          documents: documentList
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Document processing failed.");
      }

      setAnalysis(data);
      setMessage("Documents processed successfully!");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function searchMemory() {
    if (!query.trim()) {
      setMessage("Please enter a question.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query,
          top_k: 3
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Search failed.");
      }

      setResults(data.results || []);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  const totalDocuments = analysis?.total_documents ?? "—";

  return (
    <div className="app-container">

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Brain size={25} />
          </div>
          <div>
            <h2>StudyMind <span>AI</span></h2>
            <p>Intelligent Knowledge System</p>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav>
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.name}
                className={`nav-item ${
                  activePage === item.name ? "active" : ""
                }`}
                onClick={() => setActivePage(item.name)}
              >
                <Icon size={19} />
                <span>{item.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <button className="nav-item">
            <Settings size={19} />
            <span>Settings</span>
          </button>

          <div className="profile">
            <div className="avatar">SM</div>
            <div>
              <strong>StudyMind User</strong>
              <small>Personal Workspace</small>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">

        <header className="topbar">
          <div className="breadcrumb">
            <span>Workspace</span>
            <span>/</span>
            <strong>{activePage}</strong>
          </div>

          <div className="topbar-right">
            <div className="system-status">
              <span className="status-dot"></span>
              AI Workspace
            </div>
            <div className="avatar small-avatar">SM</div>
          </div>
        </header>

        <section className="page-content">

          <div className="welcome-section">
            <div>
              <div className="eyebrow">
                <Sparkles size={15} />
                INTELLIGENCE THAT REMEMBERS
              </div>

              <h1>
                Think smarter.
                <span> Understand deeper.</span>
              </h1>

              <p>
                Your intelligent workspace for contextual knowledge,
                information retrieval and decision support.
              </p>
            </div>

            <div className="date-card">
              <Clock3 size={17} />
              <span>Knowledge Workspace</span>
            </div>
          </div>

          <div className="stats-grid">

            <div className="stat-card">
              <div className="stat-icon purple">
                <FileText size={21} />
              </div>
              <p>Documents Processed</p>
              <h2>{totalDocuments}</h2>
              <small>Current analysis</small>
            </div>

            <div className="stat-card">
              <div className="stat-icon blue">
                <Network size={21} />
              </div>
              <p>Knowledge Groups</p>
              <h2>
                {analysis
                  ? Object.keys(analysis.groups || {}).length
                  : "—"}
              </h2>
              <small>Discovered clusters</small>
            </div>

            <div className="stat-card">
              <div className="stat-icon green">
                <Activity size={21} />
              </div>
              <p>Silhouette Score</p>
              <h2>
                {analysis
                  ? analysis.evaluation?.silhouette_score
                  : "—"}
              </h2>
              <small>Clustering evaluation</small>
            </div>

            <div className="stat-card">
              <div className="stat-icon orange">
                <Brain size={21} />
              </div>
              <p>Memory Engine</p>
              <h2>Active</h2>
              <small>SQLite + ML pipeline</small>
            </div>

          </div>

          <div className="workspace-grid">

            <section className="panel document-panel">
              <div className="panel-heading">
                <div>
                  <div className="panel-icon">
                    <Plus size={19} />
                  </div>
                  <h3>Knowledge Ingestion</h3>
                  <p>Add information to your intelligent memory.</p>
                </div>
                <span className="tag">ML PIPELINE</span>
              </div>

              <label>Enter your documents</label>

              <textarea
                value={documents}
                onChange={(e) => setDocuments(e.target.value)}
                placeholder={
                  "Enter one document per line...\n\nExample:\nMachine learning helps analyze data.\nStudents learn through practice."
                }
              />

              <div className="input-hint">
                <span>One document per line</span>
                <span>
                  {documents.split("\n").filter(
                    (item) => item.trim()
                  ).length} documents
                </span>
              </div>

              <button
                className="primary-button"
                onClick={processDocuments}
                disabled={loading}
              >
                <Sparkles size={17} />
                {loading ? "Processing..." : "Analyze Documents"}
              </button>
            </section>

            <section className="panel search-panel">
              <div className="panel-heading">
                <div>
                  <div className="panel-icon blue-panel">
                    <Search size={19} />
                  </div>
                  <h3>Ask StudyMind</h3>
                  <p>Search your stored knowledge using natural language.</p>
                </div>
                <span className="tag blue-tag">RETRIEVAL</span>
              </div>

              <label>Your question</label>

              <textarea
                className="search-input"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="What would you like to know?"
              />

              <div className="search-tip">
                <Sparkles size={15} />
                Search across your stored documents.
              </div>

              <button
                className="primary-button search-button"
                onClick={searchMemory}
                disabled={loading}
              >
                <Send size={16} />
                {loading ? "Searching..." : "Search Memory"}
              </button>
            </section>

          </div>

          {message && (
            <div className="message-box">
              {message}
            </div>
          )}

          {results.length > 0 && (
            <section className="panel results-panel">
              <div className="results-heading">
                <div>
                  <h3>Retrieved Knowledge</h3>
                  <p>Most relevant stored documents for your query.</p>
                </div>
                <span className="tag">{results.length} RESULTS</span>
              </div>

              {results.map((item, index) => (
                <div className="result-item" key={index}>
                  <div className="result-number">
                    0{index + 1}
                  </div>

                  <div className="result-content">
                    <strong>{item.document}</strong>
                    <small>
                      Similarity score: {item.similarity}
                    </small>
                  </div>

                  <span className="score">
                    {item.similarity}
                  </span>
                </div>
              ))}
            </section>
          )}

          {analysis && (
            <section className="panel results-panel">
              <div className="results-heading">
                <div>
                  <h3>Knowledge Clusters</h3>
                  <p>Documents grouped by the ML clustering model.</p>
                </div>
                <span className="tag">
                  {Object.keys(analysis.groups || {}).length} GROUPS
                </span>
              </div>

              <div className="cluster-grid">
                {Object.entries(analysis.groups || {}).map(
                  ([group, items]) => (
                    <div className="cluster-card" key={group}>
                      <span>CLUSTER {Number(group) + 1}</span>
                      <h4>{items.length} Documents</h4>

                      {items.map((item, index) => (
                        <p key={index}>{item}</p>
                      ))}
                    </div>
                  )
                )}
              </div>
            </section>
          )}

          {!analysis && results.length === 0 && (
            <section className="empty-state">
              <div className="empty-icon">
                <Brain size={32} />
              </div>
              <h3>Your knowledge workspace is ready</h3>
              <p>
                Start by adding documents or asking a question
                about your stored information.
              </p>
            </section>
          )}

          <footer className="app-footer">
            <span>StudyMind AI © 2026</span>
            <span>Built for intelligent information management</span>
          </footer>

        </section>
      </main>
    </div>
  );
}

export default App;