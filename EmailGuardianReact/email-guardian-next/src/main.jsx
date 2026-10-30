import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ShieldCheck,
  ShieldAlert,
  ScanSearch,
  Activity,
  FileText,
  UploadCloud,
  ArrowUpRight,
  ChevronRight,
  Clock3,
  Search,
  Settings2,
  CircleHelp,
  LayoutDashboard,
  Radar,
  LockKeyhole,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Link2,
  Mail,
  File,
  X,
  Sparkles,
  Menu,
  Eye,
  Cpu,
} from "lucide-react";
import "./styles.css";

function App() {
  const [selectedReport, setSelectedReport] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [file, setFile] = useState(null);
  const [tab, setTab] = useState("Overview");
  const [mobileNav, setMobileNav] = useState(false);
  const [history, setHistory] = useState(() => {
  try {
    return JSON.parse(
      localStorage.getItem("emailGuardianHistory") || "[]"
    );
  } catch {
    return [];
  }
});
  const [error, setError] = useState("");
  const [historySearch, setHistorySearch] = useState("");
  const [historyFilter, setHistoryFilter] = useState("All");
 const [settings, setSettings] = useState(() => {
  try {
    const saved = localStorage.getItem("emailGuardianSettings");
    return saved
      ? { compact: false, confirmBeforeScan: true, ...JSON.parse(saved) }
      : { compact: false, confirmBeforeScan: true };
  } catch {
    return { compact: false, confirmBeforeScan: true };
  }
});

const [apiStatus, setApiStatus] = useState("Checking...");

useEffect(() => {
  localStorage.setItem("emailGuardianSettings", JSON.stringify(settings));
}, [settings]);
useEffect(() => {
  document.body.classList.toggle("compact-layout", settings.compact);

  return () => {
    document.body.classList.remove("compact-layout");
  };
}, [settings.compact]);

const checkApiConnection = async () => {
  setApiStatus("Checking...");
  try {
    const response = await fetch(
      "https://email-guardian-api.deven7722.workers.dev/api/health"
    );
    if (!response.ok) throw new Error("API unavailable");
    const data = await response.json();
    if (data.status !== "healthy") throw new Error("API unhealthy");
    setApiStatus("Connected");
  } catch {
    setApiStatus("Offline");
  }
};

  const mapHistoryItem = (item) => ({
    id: item.id,
    name: item.filename || item.name || "Unknown file",
    type: (item.filename || item.name || "FILE").split(".").pop().toUpperCase(),
    verdict: item.prediction || item.verdict || "Unknown",
    score: item.confidence == null ? "N/A" : `${item.confidence}%`,
    time: item.scanned_at ? new Date(item.scanned_at).toLocaleTimeString() : (item.time || "—"),
    date: item.scanned_at ? new Date(item.scanned_at).toLocaleDateString() : (item.date || "—"),
    subject: item.subject || "Not available",
    sender: item.sender || "Not available",
    urls: Array.isArray(item.urls_found) ? item.urls_found : (Array.isArray(item.urls) ? item.urls : []),
    color: (item.prediction || item.verdict) === "Phishing" ? "red" : (item.prediction || item.verdict) === "Legitimate" ? "green" : "amber",
  });

  const loadHistory = () => {
  try {
    const savedHistory = JSON.parse(
      localStorage.getItem("emailGuardianHistory") || "[]"
    );

    setHistory(savedHistory);
  } catch (err) {
    console.error("Could not load saved scan history:", err);
    setHistory([]);
  }
};

  useEffect(() => {
    loadHistory();
    fetch("http://127.0.0.1:8000/api/health")
      .then((response) => { if (!response.ok) throw new Error(); return response.json(); })
      .then(() => setApiStatus("Connected"))
      .catch(() => setApiStatus("Offline"));
  }, []);

  const fileKind = useMemo(
    () => (file ? file.name.split(".").pop().toUpperCase() : ""),
    [file]
  );

  const pickFile = (selectedFile) => {
    setError("");
    setResult(null);

    if (!selectedFile) return;

    const extension = selectedFile.name.split(".").pop().toLowerCase();

    if (!["eml", "txt", "pdf"].includes(extension)) {
      setFile(null);
      setError("Choose an .eml, .txt, or .pdf file.");
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setFile(null);
      setError("File is larger than 10 MB. Choose a smaller file.");
      return;
    }

    setFile(selectedFile);
  };

  const scan = async () => {
  if (!file) {
    setError("Upload an email file first.");
    return;
  }

  if (settings.confirmBeforeScan) {
    const confirmed = window.confirm(
      "Are you sure you want to analyse this email?"
    );
    if (!confirmed) return;
  }

  setScanning(true);
  setError("");
  setResult(null);

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
      "https://email-guardian-api.deven7722.workers.dev/api/analyze",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(
        data.detail || data.error || "Analysis failed."
      );
    }

    const scannedAt = data.scanned_at
      ? new Date(data.scanned_at)
      : new Date();

    setResult({
      name: data.filename,
      size: `${(file.size / 1024).toFixed(1)} KB`,
      note: data.message,
      prediction: data.prediction,
      confidence: data.confidence,
      subject: data.subject,
      sender: data.sender,
      urls: data.urls_found || [],
      urlCount: data.url_count || 0,
    });

    const historyItem = {
      id: data.scan_id || Date.now(),
      name: data.filename || file.name,
      type: "TXT",
      verdict: data.prediction,
      score: `${data.confidence}%`,
      time: scannedAt.toLocaleTimeString(),
      date: scannedAt.toLocaleDateString(),
      subject: data.subject || "Not available",
      sender: data.sender || "Not available",
      urls: data.urls_found || [],
      color:
        data.prediction === "Phishing"
          ? "red"
          : data.prediction === "Legitimate"
          ? "green"
          : "amber",
    };

    setHistory((previous) => {
      const updated = [historyItem, ...previous];
      localStorage.setItem(
        "emailGuardianHistory",
        JSON.stringify(updated)
      );
      return updated;
    });

  } catch (err) {
    setError(
      err.message ||
        "Could not connect to the Email Guardian API on Cloudflare."
    );
  } finally {
    setScanning(false);
  }
};
  const navItems = [
    ["Overview", LayoutDashboard],
    ["Email scanner", ScanSearch],
    ["Threat intelligence", Radar],
    ["Scan history", Clock3],
    ["Reports", FileText],
    ["Model evaluation", Activity],
  ];

  const openTab = (label) => {
    setTab(label);
    setMobileNav(false);
    if (label === "Email scanner") {
      setTab("Overview");
      window.setTimeout(() => document.querySelector(".scanner-panel")?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
    }
  };

  const filteredHistory = history.filter((item) => {
    const matchesSearch = `${item.name} ${item.subject} ${item.sender}`.toLowerCase().includes(historySearch.toLowerCase());
    const matchesFilter = historyFilter === "All" || item.verdict === historyFilter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileNav ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark">
            <ShieldCheck size={23} />
          </div>
          <div>
            <div className="brand-name">
              email<span>guardian</span>
            </div>
            <div className="brand-sub">THREAT INTELLIGENCE</div>
          </div>
          <button
            className="mobile-close"
            onClick={() => setMobileNav(false)}
          >
            <X size={18} />
          </button>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <div className="workspace-switch">
          <div className="workspace-avatar">EG</div>
          <div>
            <b>Personal workspace</b>
            <small>Local analysis environment</small>
          </div>
          <ChevronRight size={15} />
        </div>

        <nav>
          {navItems.map(([label, Icon]) => (
            <button
              key={label}
              className={`nav-item ${tab === label ? "active" : ""}`}
              onClick={() => openTab(label)}
            >
              <Icon size={17} />
              <span>{label}</span>
              {label === "Threat intelligence" && (
                <span className="nav-badge">NEW</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="security-card">
            <div className="security-icon">
              <LockKeyhole size={17} />
            </div>
            <div>
              <b>Private by design</b>
              <p>Keep sensitive messages in your local workflow.</p>
            </div>
          </div>

          <button className={`nav-item muted ${tab === "Settings" ? "active" : ""}`} onClick={() => openTab("Settings")}>
            <Settings2 size={17} /> Settings
          </button>

          <button
            className="nav-item muted"
            onClick={() => openTab("Help & safety")}
          >
            <CircleHelp size={17} /> Help &amp; safety
          </button>

          <div className="profile">
            <div className="profile-avatar">EG</div>
            <div>
              <b>Email Guardian</b>
              <small>Community edition</small>
            </div>
            <span className="online-dot" />
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setMobileNav(true)}
          >
            <Menu size={20} />
          </button>

          <div className="breadcrumb">
            Workspace <ChevronRight size={14} /> <b>{tab}</b>
          </div>

          <div className="topbar-right">
            <span className="system-status">
              <span className="pulse-dot" /> LOCAL ENVIRONMENT
            </span>
            <button className="icon-button" aria-label="Search scan history" title="Search scan history" onClick={() => { setTab("Scan history"); setHistorySearch(""); }}>
              <Search size={17} />
            </button>
            <div className="top-avatar">EG</div>
          </div>
        </header>

        <div className="page-content">
          {tab === "Scan history" ? (
            <section className="panel history-panel">
              <div className="history-heading"><div><div className="section-label">SAVED ACTIVITY</div><h2>Scan history</h2><p>History loaded from the local database. {history.length} saved scan(s).</p></div><button className="view-all" onClick={loadHistory}>Refresh history <Activity size={15} /></button></div>
              <div style={{display:"flex", gap:12, flexWrap:"wrap", margin:"18px 0"}}>
                <input aria-label="Search scan history" placeholder="Search filename, subject, sender..." value={historySearch} onChange={(e)=>setHistorySearch(e.target.value)} style={{flex:"1 1 240px", minWidth:0, padding:12, borderRadius:10, border:"1px solid #344054", background:"#111827", color:"inherit"}} />
                <select aria-label="Filter by verdict" value={historyFilter} onChange={(e)=>setHistoryFilter(e.target.value)} style={{padding:12, borderRadius:10, border:"1px solid #344054", background:"#111827", color:"inherit"}}><option>All</option><option>Phishing</option><option>Legitimate</option></select>
              </div>
              <div className="table-wrap"><table><thead><tr><th>FILE</th><th>TYPE</th><th>ASSESSMENT</th><th>MODEL SCORE</th><th>DATE</th><th>TIME</th></tr></thead><tbody>
                {filteredHistory.length === 0 ? <tr><td colSpan="6">No matching saved scans. Analyze an email first, or change the filters.</td></tr> : filteredHistory.map((item,index)=><tr key={item.id || `${item.name}-${index}`}><td><div className="file-cell"><div className="file-type-icon"><FileText size={16}/></div><b>{item.name}</b></div></td><td><span className="type-badge">{item.type}</span></td><td><span className={`verdict ${item.color}`}><span/>{item.verdict}</span></td><td className="score-cell">{item.score}</td><td>{item.date}</td><td className="time-cell">{item.time}</td></tr>)}
              </tbody></table></div>
            </section>
          ) : tab === "Threat intelligence" ? (
            <section className="panel insight-panel"><div className="panel-heading"><div><div className="section-label">THREAT INTELLIGENCE</div><h2>Threat signals and guidance</h2><p>Indicators to review during email triage. These are guidance, not proof of malicious intent.</p></div><Radar size={22}/></div>
              {[['Urgency & pressure','Threats, countdowns, or demands to act immediately.'],['Suspicious links','Look-alike domains, IP-based URLs, shortened links, or unusual paths.'],['Credential requests','Requests for passwords, one-time codes, payment details, or account recovery.'],['Sender mismatch','Compare From, Reply-To, and available authentication results in EML headers.']].map(([title,desc])=><div className="signal-item" key={title}><div className="signal-icon amber"><AlertTriangle size={16}/></div><div><b>{title}</b><p>{desc}</p></div></div>)}
              <div className="signal-disclaimer"><ShieldAlert size={15}/> Email Guardian does not currently perform live reputation lookups for every URL.</div>
            </section>
          ) : tab === "Reports" ? (
  <section className="panel history-panel">
    <div className="section-label">REPORT CENTER</div>
    <h2>Scan reports</h2>
    <p>View detailed reports generated from previously scanned emails.</p>

    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>FILE</th>
            <th>ASSESSMENT</th>
            <th>CONFIDENCE</th>
            <th>DATE</th>
            <th>ACTION</th>
          </tr>
        </thead>

        <tbody>
          {history.length === 0 ? (
            <tr>
              <td colSpan="5">No reports available. Scan an email first.</td>
            </tr>
          ) : (
            history.map((item, index) => (
              <tr key={item.id || index}>
                <td>{item.name}</td>
                <td>
                  <span className={`verdict ${item.color}`}>
                    <span />{item.verdict}
                  </span>
                </td>
                <td>{item.score}</td>
                <td>{item.date}</td>
                <td>
                  <button
                    className="view-all"
                    onClick={() => setSelectedReport(item)}
                  >
                    View report
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>

    {selectedReport && (
      <div className="panel" style={{ marginTop: 24 }}>
        <div className="section-label">DETAILED SCAN REPORT</div>
        <h2>{selectedReport.name}</h2>

        <p>
          <strong>Assessment:</strong> {selectedReport.verdict}
        </p>
        <p>
          <strong>Model confidence:</strong> {selectedReport.score}
        </p>
        <p>
          <strong>File type:</strong> {selectedReport.type}
        </p>
        <p>
          <strong>Date:</strong> {selectedReport.date}
        </p>
        <p>
          <strong>Time:</strong> {selectedReport.time}
        </p>
        <p>
          <strong>Subject:</strong> {selectedReport.subject}
        </p>
        <p>
          <strong>Sender:</strong> {selectedReport.sender}
        </p>

        <h3>Detected URLs</h3>

        {selectedReport.urls?.length > 0 ? (
          <ul>
            {selectedReport.urls.map((url, index) => (
              <li key={index} style={{ overflowWrap: "anywhere" }}>
                {url}
              </li>
            ))}
          </ul>
        ) : (
          <p>No URLs detected or URL information unavailable.</p>
        )}

        <div style={{ display: "flex", gap: 12, marginTop: 20 }}>
          <button
            className="view-all"
            onClick={() => {
              const report = [
                "EMAIL GUARDIAN - SCAN REPORT",
                "-----------------------------",
                `File: ${selectedReport.name}`,
                `Assessment: ${selectedReport.verdict}`,
                `Confidence: ${selectedReport.score}`,
                `File type: ${selectedReport.type}`,
                `Date: ${selectedReport.date}`,
                `Time: ${selectedReport.time}`,
                `Subject: ${selectedReport.subject}`,
                `Sender: ${selectedReport.sender}`,
                "Detected URLs:",
                ...(selectedReport.urls || []).map(url => `- ${url}`),
                "",
                "This result is a model assessment, not a guarantee."
              ].join("\n");

              const blob = new Blob([report], {
                type: "text/plain"
              });

              const link = document.createElement("a");
              link.href = URL.createObjectURL(blob);
              link.download = `EmailGuardian_${selectedReport.name}.txt`;
              link.click();
              URL.revokeObjectURL(link.href);
            }}
          >
            Download report
          </button>

          <button
            className="view-all"
            onClick={() => setSelectedReport(null)}
          >
            Close report
          </button>
        </div>
      </div>
    )}
  </section>
  ) : tab === "Model evaluation" ? (
            <section className="panel history-panel">
              <div className="section-label">MODEL QUALITY &amp; ARCHITECTURE</div>
              <h2>Model evaluation</h2>
              <p>
                Email Guardian uses a trained Logistic Regression classifier
                with TF-IDF feature extraction to classify emails as phishing
                or legitimate.
              </p>

              <div className="metrics-grid">
                {[
                  ["Algorithm", "Logistic Regression", "Supervised machine learning"],
                  ["Feature extraction", "TF-IDF", "Text feature representation"],
                  ["Vocabulary size", "44 Features", "Exported model vocabulary"],
                  ["Classification", "Binary", "Phishing / Legitimate"],
                ].map(([title, value, desc]) => (
                  <div className="metric-card" key={title}>
                    <div className="metric-top">
                      <span>{title.toUpperCase()}</span>
                      <div className="metric-icon purple">
                        <Activity size={17} />
                      </div>
                    </div>
                    <div className="metric-value">{value}</div>
                    <div className="metric-foot">{desc}</div>
                  </div>
                ))}
              </div>

              <div style={{ marginTop: 25 }}>
                <div className="section-label">MODEL WORKFLOW</div>
                <h3>Email classification pipeline</h3>
                {[
                  ["1", "Email input", "Upload an email text file for analysis."],
                  ["2", "Text preprocessing", "Clean the email content and prepare text for analysis."],
                  ["3", "TF-IDF vectorization", "Convert text into numerical features using the trained vocabulary."],
                  ["4", "Logistic Regression", "Calculate the classification score and prediction probabilities."],
                  ["5", "Final prediction", "Display Phishing or Legitimate with a confidence score."],
                ].map(([number, title, desc]) => (
                  <div className="signal-item" key={number}>
                    <div className="signal-icon amber">{number}</div>
                    <div>
                      <b>{title}</b>
                      <p>{desc}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ marginTop: 25 }}>
                <div className="section-label">EVALUATION METRICS</div>
                <h3>Performance evaluation status</h3>
                <div className="metrics-grid">
                  {[
                    ["Accuracy", "Overall classification correctness"],
                    ["Precision", "Correctness of phishing predictions"],
                    ["Recall", "Coverage of actual phishing emails"],
                    ["F1-score", "Balance between precision and recall"],
                  ].map(([title, desc]) => (
                    <div className="metric-card" key={title}>
                      <div className="metric-top">
                        <span>{title.toUpperCase()}</span>
                        <div className="metric-icon purple">
                          <Activity size={17} />
                        </div>
                      </div>
                      <div className="metric-value">Pending</div>
                      <div className="metric-foot">{desc}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="signal-disclaimer" style={{ marginTop: 20 }}>
                <ShieldAlert size={15} />
                Formal evaluation requires a separate labelled test dataset.
                Individual scan confidence scores are not overall model accuracy.
              </div>
            </section>

          ) : tab === "Settings" ? (
            <section className="panel history-panel">
              <div className="section-label">PREFERENCES</div>
              <h2>Settings</h2>
              <p>Local application preferences.</p>
              <div style={{ display: "grid", gap: 18, marginTop: 20 }}>
                <label style={{ display: "flex", gap: 12, alignItems: "center" }}>
                  <input
                    type="checkbox"
                    checked={settings.confirmBeforeScan}
                    onChange={(e) =>
                      setSettings((v) => ({
                        ...v,
                        confirmBeforeScan: e.target.checked,
                      }))
                    }
                  />
                  Confirm before starting a scan (preference stored for this session)
                </label>
                <label style={{ display: "flex", gap: 12, alignItems: "center" }}>
                  <input
                    type="checkbox"
                    checked={settings.compact}
                    onChange={(e) =>
                      setSettings((v) => ({
                        ...v,
                        compact: e.target.checked,
                      }))
                    }
                  />
                  Compact layout preference (visual effect can be added later)
                </label>
                <div>Backend status: <strong>{apiStatus}</strong></div>
                <button className="view-all" onClick={checkApiConnection}>
  Test connection <Activity size={15}/>
</button>
              </div>
            </section>
          ) : tab === "Help & safety" ? (
            <section className="panel history-panel"><div className="section-label">HELP & SAFETY</div><h2>Using Email Guardian safely</h2><ul><li>Supported formats: .eml, .txt, and .pdf, up to 10 MB.</li><li>Predictions are machine-learning assessments, not guarantees.</li><li>Do not click suspicious links just to test them.</li><li>Verify requests through a separate trusted channel.</li><li>Scan history is stored in the local SQLite database for the configured local user ID; this is not a multi-account login system.</li></ul><p>Backend status: <strong>{apiStatus}</strong></p></section>
          ) : (
          <>
          <section className="welcome-row">
            <div>
              <div className="eyebrow">
                <Sparkles size={13} /> EMAIL SECURITY, REIMAGINED
              </div>
              <h1>
                Good security starts
                <br />
                <span>with a closer look.</span>
              </h1>
              <p className="welcome-copy">
                Inspect suspicious messages, surface risk signals, and make a
                more informed decision before you click.
              </p>
            </div>

            <div className="hero-orbit">
              <div className="orbit orbit-one" />
              <div className="orbit orbit-two" />
              <div className="orbit-core">
                <ShieldCheck size={43} />
              </div>
              <div className="orbit-tag tag-top">
                <span className="tiny-green" /> Protected workspace
              </div>
              <div className="orbit-tag tag-bottom">
                <Radar size={14} /> AI threat screening
              </div>
            </div>
          </section>

          <section className="metrics-grid">
            <div className="metric-card">
              <div className="metric-top">
                <span>SUPPORTED FORMATS</span>
                <div className="metric-icon blue">
                  <FileText size={17} />
                </div>
              </div>
              <div className="metric-value">
                03 <small>formats</small>
              </div>
              <div className="metric-foot">
                <span className="mini-pill">EML</span>
                <span className="mini-pill">TXT</span>
                <span className="mini-pill">PDF</span>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-top">
                <span>ANALYSIS ENGINE</span>
                <div className="metric-icon purple">
                  <Cpu size={17} />
                </div>
              </div>
              <div className="metric-value">
                ML <small>classifier</small>
              </div>
              <div className="metric-foot">
                <span className="status-line">
                  <span className="tiny-green" /> Model API connected
                </span>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-top">
                <span>WORKSPACE STATUS</span>
                <div className="metric-icon green">
                  <Activity size={17} />
                </div>
              </div>
              <div className="metric-value">
                Ready <small>for upload</small>
              </div>
              <div className="metric-foot">
                <span className="status-line">
                  <span className="tiny-green" /> Local analysis
                </span>
              </div>
            </div>
          </section>

          <section className="content-grid">
            <div className="panel scanner-panel">
              <div className="panel-heading">
                <div>
                  <div className="section-label">01 / SCAN MESSAGE</div>
                  <h2>Inspect an email</h2>
                  <p>Upload a message file to analyze it with your trained model.</p>
                </div>
                <div className="panel-heading-icon">
                  <ScanSearch size={21} />
                </div>
              </div>

              <div
                className={`dropzone ${dragging ? "dragging" : ""} ${
                  file ? "has-file" : ""
                }`}
                onDragOver={(event) => {
                  event.preventDefault();
                  setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={(event) => {
                  event.preventDefault();
                  setDragging(false);
                  pickFile(event.dataTransfer.files?.[0]);
                }}
              >
                <input
                  id="file-input"
                  type="file"
                  accept=".eml,.txt,.pdf"
                  onChange={(event) => pickFile(event.target.files?.[0])}
                />

                <div className="upload-symbol">
                  <UploadCloud size={25} />
                </div>

                {file ? (
                  <>
                    <h3>{file.name}</h3>
                    <p>
                      {(file.size / 1024).toFixed(1)} KB · {fileKind} file
                      selected
                    </p>
                    <button
                      className="text-button"
                      onClick={() => {
                        setFile(null);
                        setResult(null);
                        setError("");
                      }}
                    >
                      Remove file <X size={13} />
                    </button>
                  </>
                ) : (
                  <>
                    <h3>Drop your email file here</h3>
                    <p>
                      or{" "}
                      <label htmlFor="file-input" className="browse-link">
                        browse files
                      </label>{" "}
                      from your computer
                    </p>
                    <div className="format-row">
                      <span>
                        <File size={13} /> .EML
                      </span>
                      <span>
                        <FileText size={13} /> .TXT
                      </span>
                      <span>
                        <FileText size={13} /> .PDF
                      </span>
                    </div>
                  </>
                )}
              </div>

              {error && (
                <div className="error-message">
                  <AlertTriangle size={15} /> {error}
                </div>
              )}

              <div className="scan-actions">
                <div className="privacy-note">
                  <LockKeyhole size={14} /> Max 10 MB · Review sensitive files
                  before uploading.
                </div>
                <button
                  className="scan-button"
                  onClick={scan}
                  disabled={scanning}
                >
                  {scanning ? (
                    <>
                      <span className="spinner" /> Analyzing...
                    </>
                  ) : (
                    <>
                      Analyze email <ArrowUpRight size={17} />
                    </>
                  )}
                </button>
              </div>

              {result && (
                <div
  className={`preview-result ${
    result.prediction === "Phishing" ? "phishing-result" : "legitimate-result"
  }`}
>
                  <div className="preview-result-title">
                    {result.prediction === "Phishing" ? (
                      <ShieldAlert size={18} />
                    ) : (
                      <CheckCircle2 size={18} />
                    )}
                    Analysis result
                  </div>

                  <h3>{result.prediction}</h3>
                  <b>{result.name}</b>
                  <p>{result.note}</p>

                  {result.confidence != null && (
                    <p>
                      Model confidence: <strong>{result.confidence}%</strong>
                    </p>
                  )}

                  <p>
                    <strong>Subject:</strong> {result.subject || "Not available"}
                  </p>
                  <p>
                    <strong>Sender:</strong> {result.sender || "Not available"}
                  </p>
                  <p>
                    <strong>URLs found:</strong> {result.urlCount}
                  </p>

                  {result.urls.length > 0 && (
                    <ul>
                      {result.urls.map((url, index) => (
                        <li key={`${url}-${index}`}>{url}</li>
                      ))}
                    </ul>
                  )}

                  <p>
                    <Eye size={14} /> This result is a model assessment, not a
                    guarantee that a message is safe.
                  </p>
                </div>
              )}

              <div className="scanner-footer">
                <span>
                  <ShieldCheck size={14} /> File type checked
                </span>
                <span>
                  <Zap size={14} /> Model analysis
                </span>
                <span>
                  <Eye size={14} /> Review before acting
                </span>
              </div>
            </div>

            <div className="right-column">
              <div className="panel insight-panel">
                <div className="panel-heading compact">
                  <div>
                    <div className="section-label">02 / WHAT TO LOOK FOR</div>
                    <h2>Threat signals</h2>
                  </div>
                  <Radar size={20} className="muted-icon" />
                </div>

                <div className="signal-item">
                  <div className="signal-icon red">
                    <AlertTriangle size={16} />
                  </div>
                  <div>
                    <b>Urgency &amp; pressure</b>
                    <p>Threats, countdowns, or “act now” language.</p>
                  </div>
                  <span className="signal-arrow">
                    <ChevronRight size={15} />
                  </span>
                </div>

                <div className="signal-item">
                  <div className="signal-icon amber">
                    <Link2 size={16} />
                  </div>
                  <div>
                    <b>Suspicious links</b>
                    <p>Unexpected destinations or look-alike domains.</p>
                  </div>
                  <span className="signal-arrow">
                    <ChevronRight size={15} />
                  </span>
                </div>

                <div className="signal-item">
                  <div className="signal-icon purple">
                    <Mail size={16} />
                  </div>
                  <div>
                    <b>Credential requests</b>
                    <p>Requests for passwords, OTPs, or payment details.</p>
                  </div>
                  <span className="signal-arrow">
                    <ChevronRight size={15} />
                  </span>
                </div>

                <div className="signal-disclaimer">
                  <ShieldAlert size={15} /> Signals are guidance—not proof of
                  malicious intent.
                </div>
              </div>

              <div className="panel tips-panel">
                <div className="tips-title">
                  <div className="tips-icon">
                    <ShieldCheck size={17} />
                  </div>
                  <div>
                    <b>Before you click</b>
                    <p>A 10-second safety check</p>
                  </div>
                </div>
                <div className="tip-row">
                  <CheckCircle2 size={15} /> Verify the sender using a separate
                  channel.
                </div>
                <div className="tip-row">
                  <CheckCircle2 size={15} /> Preview links without opening them.
                </div>
                <div className="tip-row">
                  <CheckCircle2 size={15} /> Never share passwords or one-time
                  codes.
                </div>
              </div>
            </div>
          </section>

          <section className="panel history-panel">
            <div className="history-heading">
              <div>
                <div className="section-label">03 / ACTIVITY</div>
                <h2>Recent scan activity</h2>
                <p>Results loaded from your local scan-history database.</p>
              </div>
              <button className="view-all" onClick={() => openTab("Scan history")}>
                View activity <ArrowUpRight size={15} />
              </button>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>FILE</th>
                    <th>TYPE</th>
                    <th>ASSESSMENT</th>
                    <th>MODEL SCORE</th>
                    <th>WHEN</th>
                  </tr>
                </thead>
                <tbody>
                  {history.length === 0 ? (
                    <tr>
                      <td colSpan="5">No scans yet. Analyze a file to begin.</td>
                    </tr>
                  ) : (
                    history.map((item, index) => (
                      <tr key={`${item.name}-${index}`}>
                        <td>
                          <div className="file-cell">
                            <div className="file-type-icon">
                              <FileText size={16} />
                            </div>
                            <b>{item.name}</b>
                          </div>
                        </td>
                        <td>
                          <span className="type-badge">{item.type}</span>
                        </td>
                        <td>
                          <span className={`verdict ${item.color}`}>
                            <span /> {item.verdict}
                          </span>
                        </td>
                        <td className="score-cell">{item.score}</td>
                        <td className="time-cell">{item.time}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <div className="history-foot">
              <span>
                <span className="tiny-green" /> Session history
              </span>
              <span>Saved scans remain available after refreshing the page.</span>
            </div>
          </section>

          </>
          )}
          <footer className="page-footer">
            <div className="footer-brand">
              <ShieldCheck size={17} /> Email Guardian <span>·</span>{" "}
              <small>Security is a habit, not a single scan.</small>
            </div>
            <div>
              <span className="footer-dot" /> Local model API
            </div>
          </footer>
        </div>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);