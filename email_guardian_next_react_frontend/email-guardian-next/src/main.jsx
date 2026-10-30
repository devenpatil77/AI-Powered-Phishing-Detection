import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ShieldCheck, ShieldAlert, ScanSearch, Activity, FileText, UploadCloud,
  ArrowUpRight, ChevronRight, Clock3, Search, Settings2, CircleHelp,
  LayoutDashboard, Radar, LockKeyhole, Zap, CheckCircle2, AlertTriangle,
  Link2, Mail, File, X, Sparkles, Menu, Download, Eye, Cpu
} from "lucide-react";
import "./styles.css";

const recent = [
  { name: "invoice_update.eml", type: "EML", verdict: "Phishing", score: "96.2%", time: "2 min ago", color: "red" },
  { name: "team_meeting.txt", type: "TXT", verdict: "Legitimate", score: "91.8%", time: "18 min ago", color: "green" },
  { name: "account_notice.pdf", type: "PDF", verdict: "Phishing", score: "88.4%", time: "Yesterday", color: "red" },
];

function App() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [tab, setTab] = useState("Overview");
  const [mobileNav, setMobileNav] = useState(false);
  const [history, setHistory] = useState(recent);
  const [error, setError] = useState("");

  const fileKind = useMemo(() => {
    if (!file) return "";
    return file.name.split(".").pop().toUpperCase();
  }, [file]);

  const pickFile = (f) => {
    setError("");
    setResult(null);
    if (!f) return;
    const ext = f.name.split(".").pop().toLowerCase();
    if (!["eml", "txt", "pdf"].includes(ext)) {
      setError("Choose an .eml, .txt, or .pdf file.");
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setError("File is larger than 10 MB. Choose a smaller file.");
      return;
    }
    setFile(f);
  };

 const scan = async () => {
  if (!file) {
    setError("Upload an email file first.");
    return;
  }

  if (!file.name.toLowerCase().endsWith(".txt")) {
    setError("Cloudflare API currently supports .txt files only. Please select a TXT email file.");
    return;
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
      throw new Error(data.detail || "Email analysis failed.");
    }

    const scanResult = {
      name: data.filename || file.name,
      size: (file.size / 1024).toFixed(1) + " KB",
      note: `Prediction: ${data.prediction} | Confidence: ${data.confidence}%`,
      prediction: data.prediction,
      confidence: data.confidence,
      probabilities: data.probabilities,
      urls: data.urls_found || [],
    };

    setResult(scanResult);

    setHistory((previous) => [
      {
        name: scanResult.name,
        type: "TXT",
        verdict: scanResult.prediction,
        score: `${scanResult.confidence}%`,
        time: "Just now",
        color: scanResult.prediction === "Phishing" ? "red" : "green",
      },
      ...previous,
    ]);
  } catch (error) {
    setError(
      error.message ||
      "Could not connect to the Email Guardian API. Please try again."
    );
  } finally {
    setScanning(false);
  }
};

  const navItems = [
    ["Overview", LayoutDashboard], ["Email scanner", ScanSearch], ["Threat intelligence", Radar], ["Scan history", Clock3]
  ];

  return <div className="app-shell">
    <aside className={`sidebar ${mobileNav ? "sidebar-open" : ""}`}>
      <div className="brand">
        <div className="brand-mark"><ShieldCheck size={23}/></div>
        <div><div className="brand-name">email<span>guardian</span></div><div className="brand-sub">THREAT INTELLIGENCE</div></div>
        <button className="mobile-close" onClick={() => setMobileNav(false)}><X size={18}/></button>
      </div>
      <div className="workspace-label">WORKSPACE</div>
      <div className="workspace-switch"><div className="workspace-avatar">EG</div><div><b>Personal workspace</b><small>Local analysis environment</small></div><ChevronRight size={15}/></div>
      <nav>
        {navItems.map(([label, Icon]) => <button key={label} className={`nav-item ${tab === label ? "active" : ""}`} onClick={() => {setTab(label); setMobileNav(false);}}>
          <Icon size={17}/><span>{label}</span>{label === "Threat intelligence" && <span className="nav-badge">NEW</span>}
        </button>)}
      </nav>
      <div className="sidebar-bottom">
        <div className="security-card"><div className="security-icon"><LockKeyhole size={17}/></div><div><b>Private by design</b><p>Keep sensitive messages in your local workflow.</p></div></div>
        <button className="nav-item muted" onClick={() => setTab("Settings")}><Settings2 size={17}/>Settings</button>
        <button className="nav-item muted" onClick={() => setTab("Help & safety")}><CircleHelp size={17}/>Help & safety</button>
        <div className="profile"><div className="profile-avatar">EG</div><div><b>Email Guardian</b><small>Community edition</small></div><span className="online-dot"/></div>
      </div>
    </aside>

    <main className="main">
      <header className="topbar">
        <button className="mobile-menu" onClick={() => setMobileNav(true)}><Menu size={20}/></button>
        <div className="breadcrumb">Workspace <ChevronRight size={14}/> <b>{tab}</b></div>
        <div className="topbar-right"><span className="system-status"><span className="pulse-dot"/> LOCAL ENVIRONMENT</span><button className="icon-button"><Search size={17}/></button><div className="top-avatar">EG</div></div>
      </header>

      <div className="page-content">
        <section className="welcome-row">
          <div><div className="eyebrow"><Sparkles size={13}/> EMAIL SECURITY, REIMAGINED</div><h1>Good security starts<br/><span>with a closer look.</span></h1><p className="welcome-copy">Inspect suspicious messages, surface risk signals, and make a more informed decision before you click.</p></div>
          <div className="hero-orbit"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="orbit-core"><ShieldCheck size={43}/></div><div className="orbit-tag tag-top"><span className="tiny-green"/> Protected workspace</div><div className="orbit-tag tag-bottom"><Radar size={14}/> AI threat screening</div></div>
        </section>

        <section className="metrics-grid">
          <div className="metric-card"><div className="metric-top"><span>SUPPORTED FORMATS</span><div className="metric-icon blue"><FileText size={17}/></div></div><div className="metric-value">03 <small>formats</small></div><div className="metric-foot"><span className="mini-pill">EML</span><span className="mini-pill">TXT</span><span className="mini-pill">PDF</span></div></div>
          <div className="metric-card"><div className="metric-top"><span>ANALYSIS ENGINE</span><div className="metric-icon purple"><Cpu size={17}/></div></div><div className="metric-value">ML <small>classifier</small></div><div className="metric-foot"><span className="status-line"><span className="tiny-green"/> Model integration required</span></div></div>
          <div className="metric-card"><div className="metric-top"><span>WORKSPACE STATUS</span><div className="metric-icon green"><Activity size={17}/></div></div><div className="metric-value">Ready <small>for upload</small></div><div className="metric-foot"><span className="status-line"><span className="tiny-green"/> Frontend preview active</span></div></div>
        </section>

        <section className="content-grid">
          <div className="panel scanner-panel">
            <div className="panel-heading"><div><div className="section-label">01 / SCAN MESSAGE</div><h2>Inspect an email</h2><p>Upload a message file to prepare it for analysis.</p></div><div className="panel-heading-icon"><ScanSearch size={21}/></div></div>
            <div className={`dropzone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`} onDragOver={e => {e.preventDefault();setDragging(true);}} onDragLeave={() => setDragging(false)} onDrop={e => {e.preventDefault();setDragging(false);pickFile(e.dataTransfer.files?.[0]);}}>
              <input id="file-input" type="file" accept=".eml,.txt,.pdf" onChange={e => pickFile(e.target.files?.[0])}/>
              <div className="upload-symbol"><UploadCloud size={25}/></div>
              {file ? <><h3>{file.name}</h3><p>{(file.size/1024).toFixed(1)} KB · {fileKind} file selected</p><button className="text-button" onClick={() => {setFile(null);setResult(null);}}>Remove file <X size={13}/></button></> :
                <><h3>Drop your email file here</h3><p>or <label htmlFor="file-input" className="browse-link">browse files</label> from your computer</p><div className="format-row"><span><File size={13}/> .EML</span><span><FileText size={13}/> .TXT</span><span><FileText size={13}/> .PDF</span></div></>}
            </div>
            {error && <div className="error-message"><AlertTriangle size={15}/>{error}</div>}
            <div className="scan-actions"><div className="privacy-note"><LockKeyhole size={14}/> Max 10 MB · Do not upload confidential emails to untrusted systems.</div><button className="scan-button" onClick={scan} disabled={scanning}>{scanning ? <><span className="spinner"/> Preparing scan…</> : <>Prepare analysis <ArrowUpRight size={17}/></>}</button></div>
            {result && (
  <div className="preview-result">
    <div className="preview-result-title">
      {result.prediction === "Phishing"
        ? <ShieldAlert size={18} />
        : <CheckCircle2 size={18} />}
      Analysis complete
    </div>

    <b>{result.name}</b>

    <p>{result.size}</p>

    <h3>
      {result.prediction === "Phishing"
        ? "⚠️ Potential phishing email"
        : "✓ Classified as legitimate"}
    </h3>

    <p>Model confidence: {result.confidence}%</p>

    {result.urls?.length > 0 && (
      <div>
        <b>Links detected: {result.urls.length}</b>
        <ul>
          {result.urls.map((url, index) => (
            <li key={index} style={{ overflowWrap: "anywhere" }}>
              {url}
            </li>
          ))}
        </ul>
      </div>
    )}

    <p>{result.note}</p>
  </div>
)}
            <div className="scanner-footer"><span><ShieldCheck size={14}/> File type checked</span><span><Zap size={14}/> Lightweight workflow</span><span><Eye size={14}/> Review before acting</span></div>
          </div>

          <div className="right-column">
            <div className="panel insight-panel"><div className="panel-heading compact"><div><div className="section-label">02 / WHAT TO LOOK FOR</div><h2>Threat signals</h2></div><Radar size={20} className="muted-icon"/></div>
              <div className="signal-item"><div className="signal-icon red"><AlertTriangle size={16}/></div><div><b>Urgency & pressure</b><p>Threats, countdowns, or “act now” language.</p></div><span className="signal-arrow"><ChevronRight size={15}/></span></div>
              <div className="signal-item"><div className="signal-icon amber"><Link2 size={16}/></div><div><b>Suspicious links</b><p>Unexpected destinations or look-alike domains.</p></div><span className="signal-arrow"><ChevronRight size={15}/></span></div>
              <div className="signal-item"><div className="signal-icon purple"><Mail size={16}/></div><div><b>Credential requests</b><p>Requests for passwords, OTPs, or payment details.</p></div><span className="signal-arrow"><ChevronRight size={15}/></span></div>
              <div className="signal-disclaimer"><ShieldAlert size={15}/> Signals are guidance—not proof of malicious intent.</div>
            </div>
            <div className="panel tips-panel"><div className="tips-title"><div className="tips-icon"><ShieldCheck size={17}/></div><div><b>Before you click</b><p>A 10-second safety check</p></div></div><div className="tip-row"><CheckCircle2 size={15}/> Verify the sender using a separate channel.</div><div className="tip-row"><CheckCircle2 size={15}/> Preview links without opening them.</div><div className="tip-row"><CheckCircle2 size={15}/> Never share passwords or one-time codes.</div></div>
          </div>
        </section>

        <section className="panel history-panel">
          <div className="history-heading"><div><div className="section-label">03 / ACTIVITY</div><h2>Recent scan activity</h2><p>Example rows for the interface preview. Real history requires backend storage.</p></div><button className="view-all" onClick={() => setTab("Scan history")}>View activity <ArrowUpRight size={15}/></button></div>
          <div className="table-wrap"><table><thead><tr><th>FILE</th><th>TYPE</th><th>ASSESSMENT</th><th>MODEL SCORE</th><th>WHEN</th><th></th></tr></thead><tbody>{history.map((item,i)=><tr key={item.name+i}><td><div className="file-cell"><div className="file-type-icon"><FileText size={16}/></div><b>{item.name}</b></div></td><td><span className="type-badge">{item.type}</span></td><td><span className={`verdict ${item.color}`}><span/> {item.verdict}</span></td><td className="score-cell">{item.score}</td><td className="time-cell">{item.time}</td><td><button className="row-action" title="Details"><ArrowUpRight size={15}/></button></td></tr>)}</tbody></table></div>
          <div className="history-foot"><span><span className="tiny-green"/> Interface demo data</span><span>Connect scan history to backend to show actual results.</span></div>
        </section>
        <footer className="page-footer"><div className="footer-brand"><ShieldCheck size={17}/> Email Guardian <span>·</span> <small>Security is a habit, not a single scan.</small></div><div><span className="footer-dot"/> Preview build · Backend not connected</div></footer>
      </div>
    </main>
  </div>;
}

createRoot(document.getElementById("root")).render(<App />);
