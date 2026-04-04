import { useState, useEffect, useRef } from "react";

// ─── DATA MODEL ───────────────────────────────────────────────────────────────

const STAGES = [
  { id: 1, name: "Pre-Purchase / Discovery", weight: 0.10, color: "#00CFFF" },
  { id: 2, name: "Vendor Evaluation & Selection", weight: 0.20, color: "#1B5EBE" },
  { id: 3, name: "Onboarding & Implementation", weight: 0.12, color: "#4D8FFF" },
  { id: 4, name: "Identity & Access Configuration", weight: 0.18, color: "#00CFFF" },
  { id: 5, name: "Operations & Governance", weight: 0.20, color: "#1B5EBE" },
  { id: 6, name: "Commercial Lifecycle", weight: 0.10, color: "#4D8FFF" },
  { id: 7, name: "Risk, Exit & Replacement", weight: 0.10, color: "#00CFFF" },
];

const PERSONAS = [
  { id: "ciso", label: "CISO / Security", icon: "🛡️", color: "#EF4444" },
  { id: "it-admin", label: "IT Admin / IAM", icon: "⚙️", color: "#F59E0B" },
  { id: "procurement", label: "Procurement", icon: "💰", color: "#10B981" },
  { id: "cto", label: "CTO / Engineering", icon: "🏗️", color: "#6366F1" },
  { id: "legal", label: "Legal & Compliance", icon: "⚖️", color: "#8B5CF6" },
  { id: "dept-head", label: "Dept Head / End User", icon: "👥", color: "#EC4899" },
];

const METRICS = [
  { id: "1.1", stage: 1, name: "Feature Parity with Competitors", owner: "procurement" },
  { id: "1.2", stage: 1, name: "Roadmap Publishing", owner: "procurement" },
  { id: "1.3", stage: 1, name: "Roadmap Clarity", owner: "cto" },
  { id: "1.4", stage: 1, name: "Thought Leadership", owner: "dept-head" },
  { id: "1.5", stage: 1, name: "Design System Maturity", owner: "dept-head" },
  { id: "1.6", stage: 1, name: "Pricing Transparency", owner: "procurement" },
  { id: "2.1", stage: 2, name: "API Coverage", owner: "cto" },
  { id: "2.2", stage: 2, name: "Automation Coverage", owner: "cto" },
  { id: "2.3", stage: 2, name: "Login Methods + SSO", owner: "ciso" },
  { id: "2.4", stage: 2, name: "RBAC Granularity", owner: "ciso" },
  { id: "2.5", stage: 2, name: "Compliance Coverage", owner: "ciso" },
  { id: "2.6", stage: 2, name: "Activity Logging", owner: "ciso" },
  { id: "2.7", stage: 2, name: "Support SLAs", owner: "it-admin" },
  { id: "2.8", stage: 2, name: "Financial Runway / Vendor Stability", owner: "procurement" },
  { id: "3.1", stage: 3, name: "Blueprints, Templates & Walkthroughs", owner: "it-admin" },
  { id: "3.2", stage: 3, name: "Data Ingestion Mechanisms", owner: "it-admin" },
  { id: "3.3", stage: 3, name: "Data Correction Tools", owner: "it-admin" },
  { id: "3.4", stage: 3, name: "Multi-Device Support", owner: "dept-head" },
  { id: "3.5", stage: 3, name: "Time to Value", owner: "cto" },
  { id: "3.6", stage: 3, name: "Support During Onboarding", owner: "dept-head" },
  { id: "4.1", stage: 4, name: "SSO + MFA Enforcement", owner: "ciso" },
  { id: "4.2", stage: 4, name: "User Provisioning Automation (SCIM)", owner: "ciso" },
  { id: "4.3", stage: 4, name: "IGA Coverage", owner: "ciso" },
  { id: "4.4", stage: 4, name: "Privileged Access Controls", owner: "ciso" },
  { id: "4.5", stage: 4, name: "Multi-Org / Multi-Tenant Support", owner: "ciso" },
  { id: "5.1", stage: 5, name: "Compliance Automation", owner: "legal" },
  { id: "5.2", stage: 5, name: "Audit Log Completeness & Retention", owner: "ciso" },
  { id: "5.3", stage: 5, name: "Automated Remediation", owner: "it-admin" },
  { id: "5.4", stage: 5, name: "Collaboration Governance", owner: "dept-head" },
  { id: "5.5", stage: 5, name: "Partner Ecosystem", owner: "it-admin" },
  { id: "6.1", stage: 6, name: "Pricing Model & Scaling", owner: "procurement" },
  { id: "6.2", stage: 6, name: "Roadmap Delivery History", owner: "procurement" },
  { id: "6.3", stage: 6, name: "Customer Advocacy", owner: "procurement" },
  { id: "6.4", stage: 6, name: "Dedicated Support Escalation", owner: "procurement" },
  { id: "7.1", stage: 7, name: "Data Portability & Export Tooling", owner: "legal" },
  { id: "7.2", stage: 7, name: "Vendor Lock-in Avoidance", owner: "legal" },
  { id: "7.3", stage: 7, name: "Immutable Logs for Offboarding", owner: "legal" },
  { id: "7.4", stage: 7, name: "Zero-Touch Deprovisioning", owner: "legal" },
];

const VERDICT_THRESHOLDS = [
  { min: 4.0, max: 5.0, label: "Strong", sub: "Recommended", color: "#10B981" },
  { min: 3.0, max: 3.99, label: "Enterprise Baseline", sub: "Approvable with monitoring", color: "#4D8FFF" },
  { min: 2.0, max: 2.99, label: "Emerging", sub: "Conditional — vendor commitments required", color: "#F59E0B" },
  { min: 0, max: 1.99, label: "Not Enterprise-Ready", sub: "Do Not Procure", color: "#EF4444" },
];

function getVerdict(score) {
  return VERDICT_THRESHOLDS.find(v => score >= v.min && score <= v.max) || VERDICT_THRESHOLDS[3];
}

function calcUIndex(scores) {
  let total = 0;
  STAGES.forEach(stage => {
    const stageMetrics = METRICS.filter(m => m.stage === stage.id);
    const scored = stageMetrics.filter(m => scores[m.id] != null);
    if (scored.length === 0) return;
    const stageSum = scored.reduce((s, m) => s + (scores[m.id] || 0), 0);
    const stageScore = (stageSum / (stageMetrics.length * 5)) * 5;
    total += stageScore * stage.weight;
  });
  return Math.round(total * 100) / 100;
}

// ─── API HELPER ────────────────────────────────────────────────────────────────

async function callClaude(messages, system) {
  const resp = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system,
      messages,
    }),
  });
  const data = await resp.json();
  return data.content?.find(b => b.type === "text")?.text || "";
}

// ─── STORAGE HELPERS ───────────────────────────────────────────────────────────

async function loadState(productSlug) {
  try {
    const r = await window.storage.get(`eval:${productSlug}:state`);
    return r ? JSON.parse(r.value) : null;
  } catch { return null; }
}

async function saveState(productSlug, state) {
  try {
    await window.storage.set(`eval:${productSlug}:state`, JSON.stringify(state));
  } catch {}
}

async function loadScores(productSlug) {
  try {
    const r = await window.storage.get(`eval:${productSlug}:scores`);
    return r ? JSON.parse(r.value) : {};
  } catch { return {}; }
}

async function saveScores(productSlug, scores) {
  try {
    await window.storage.set(`eval:${productSlug}:scores`, JSON.stringify(scores));
  } catch {}
}

async function listEvals() {
  try {
    const r = await window.storage.list("eval:");
    const slugs = new Set();
    (r?.keys || []).forEach(k => {
      const parts = k.split(":");
      if (parts[2] === "state") slugs.add(parts[1]);
    });
    return [...slugs];
  } catch { return []; }
}

// ─── SCORE BADGE ──────────────────────────────────────────────────────────────

function ScoreBadge({ score, size = "sm" }) {
  const colors = ["#EF4444","#F97316","#F59E0B","#84CC16","#10B981","#10B981"];
  const bg = score == null ? "#334155" : colors[score] || "#334155";
  const sz = size === "lg" ? { width: 40, height: 40, fontSize: 18, fontWeight: 800 }
    : { width: 28, height: 28, fontSize: 13, fontWeight: 700 };
  return (
    <div style={{
      ...sz, background: bg, borderRadius: 6, display: "flex",
      alignItems: "center", justifyContent: "center", color: "#fff",
      flexShrink: 0, letterSpacing: "-0.5px", transition: "background 0.3s",
      boxShadow: score != null ? `0 0 10px ${bg}55` : "none",
    }}>
      {score == null ? "—" : score}
    </div>
  );
}

// ─── RADAR CHART ──────────────────────────────────────────────────────────────

function RadarChart({ scores }) {
  const cx = 120, cy = 120, r = 90;
  const n = STAGES.length;
  const stageScores = STAGES.map(stage => {
    const ms = METRICS.filter(m => m.stage === stage.id);
    const scored = ms.filter(m => scores[m.id] != null);
    if (!scored.length) return 0;
    return scored.reduce((s, m) => s + scores[m.id], 0) / (ms.length * 5);
  });

  const pts = (vals) => vals.map((v, i) => {
    const angle = (i / n) * 2 * Math.PI - Math.PI / 2;
    return [cx + v * r * Math.cos(angle), cy + v * r * Math.sin(angle)];
  });

  const gridLevels = [0.2, 0.4, 0.6, 0.8, 1.0];
  const labelPts = pts(Array(n).fill(1.22));
  const dataPts = pts(stageScores);
  const polyData = dataPts.map(p => p.join(",")).join(" ");

  return (
    <svg viewBox="0 0 240 240" style={{ width: "100%", maxWidth: 240 }}>
      {gridLevels.map(lv => {
        const gp = pts(Array(n).fill(lv));
        return <polygon key={lv} points={gp.map(p => p.join(",")).join(" ")}
          fill="none" stroke="#1e3a5f" strokeWidth={1} />;
      })}
      {Array(n).fill(0).map((_, i) => {
        const ep = pts([1])[0];
        const angle = (i / n) * 2 * Math.PI - Math.PI / 2;
        return <line key={i} x1={cx} y1={cy}
          x2={cx + r * Math.cos(angle)} y2={cy + r * Math.sin(angle)}
          stroke="#1e3a5f" strokeWidth={1} />;
      })}
      <polygon points={polyData} fill="#00CFFF22" stroke="#00CFFF" strokeWidth={2} />
      {dataPts.map((p, i) => (
        <circle key={i} cx={p[0]} cy={p[1]} r={4} fill="#00CFFF" />
      ))}
      {labelPts.map((p, i) => (
        <text key={i} x={p[0]} y={p[1]} textAnchor="middle" dominantBaseline="middle"
          fill="#94a3b8" fontSize={7.5} fontFamily="'IBM Plex Mono', monospace">
          {`S${i + 1}`}
        </text>
      ))}
    </svg>
  );
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────

export default function SaaSEvaluator() {
  const [screen, setScreen] = useState("home"); // home | setup | evaluate | results | history | alternatives
  const [productName, setProductName] = useState("");
  const [productSlug, setProductSlug] = useState("");
  const [useCase, setUseCase] = useState("");
  const [activePersona, setActivePersona] = useState(null);
  const [scores, setScores] = useState({});
  const [evidence, setEvidence] = useState({});
  const [completedPersonas, setCompletedPersonas] = useState(new Set());
  const [aiLoading, setAiLoading] = useState(false);
  const [aiInsight, setAiInsight] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [historySlugs, setHistorySlugs] = useState([]);
  const [setupStep, setSetupStep] = useState(1);
  const [autoResearching, setAutoResearching] = useState(false);
  const [researchProgress, setResearchProgress] = useState(0);
  // Alternatives
  const [alternatives, setAlternatives] = useState([]); // [{name, slug, scores, status}]
  const [altInput, setAltInput] = useState("");
  const [altResearching, setAltResearching] = useState(null); // slug currently being researched
  const [altResearchProgress, setAltResearchProgress] = useState(0);
  const [compareMetricFilter, setCompareMetricFilter] = useState("all"); // all | blockers | gaps
  const chatEndRef = useRef(null);

  useEffect(() => {
    listEvals().then(setHistorySlugs);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const slugify = (name) => name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

  // Auto-research all metrics via Claude
  const autoResearch = async (product, usecase) => {
    setAutoResearching(true);
    setResearchProgress(0);
    const newScores = {};
    const newEvidence = {};
    const batchSize = 5;
    const metricBatches = [];
    for (let i = 0; i < METRICS.length; i += batchSize) {
      metricBatches.push(METRICS.slice(i, i + batchSize));
    }

    for (let bi = 0; bi < metricBatches.length; bi++) {
      const batch = metricBatches[bi];
      const system = `You are a SaaS enterprise evaluator. Score the following metrics for "${product}" (use case: ${usecase || "general enterprise"}).
Return ONLY valid JSON: {"scores":{"metric_id": score_0_to_5, ...}, "evidence":{"metric_id": "brief evidence string", ...}}
Use your training knowledge. Score 0-5 integers. Be realistic and conservative. No extra text.`;
      const prompt = batch.map(m => `${m.id}: ${m.name}`).join("\n");
      try {
        const raw = await callClaude([{ role: "user", content: prompt }], system);
        const clean = raw.replace(/```json|```/g, "").trim();
        const parsed = JSON.parse(clean);
        Object.assign(newScores, parsed.scores || {});
        Object.assign(newEvidence, parsed.evidence || {});
      } catch {}
      setResearchProgress(Math.round(((bi + 1) / metricBatches.length) * 100));
    }

    setScores(newScores);
    setEvidence(newEvidence);
    await saveScores(slugify(product), newScores);
    setAutoResearching(false);
    setScreen("evaluate");
  };

  const startEvaluation = async () => {
    const slug = slugify(productName);
    setProductSlug(slug);
    const existing = await loadState(slug);
    let s = {}, e = {};
    if (existing) {
      s = await loadScores(slug) || {};
      e = existing.evidence || {};
      setCompletedPersonas(new Set(existing.completedPersonas || []));
    }
    setScores(s);
    setEvidence(e);
    await saveState(slug, { product: productName, useCase, completedPersonas: [], evidence: {} });
    await autoResearch(productName, useCase);
  };

  const loadEvaluation = async (slug) => {
    const state = await loadState(slug);
    if (!state) return;
    const s = await loadScores(slug) || {};
    setProductName(state.product);
    setProductSlug(slug);
    setUseCase(state.useCase || "");
    setScores(s);
    setCompletedPersonas(new Set(state.completedPersonas || []));
    const alts = state.alternatives || [];
    const hydratedAlts = await Promise.all(alts.map(async (alt) => {
      const altScores = await loadScores(alt.slug) || {};
      return { ...alt, scores: altScores };
    }));
    setAlternatives(hydratedAlts);
    setScreen("evaluate");
  };

  const researchAlternative = async (altName) => {
    const altSlug = slugify(altName);
    if (alternatives.find(a => a.slug === altSlug)) return;
    setAlternatives(prev => [...prev, { name: altName, slug: altSlug, scores: {}, status: "researching" }]);
    setAltResearching(altSlug);
    setAltResearchProgress(0);
    const newScores = {};
    const batchSize = 5;
    const batches = [];
    for (let i = 0; i < METRICS.length; i += batchSize) batches.push(METRICS.slice(i, i + batchSize));
    for (let bi = 0; bi < batches.length; bi++) {
      const batch = batches[bi];
      const system = `You are a SaaS enterprise evaluator. Score the following metrics for "${altName}" (use case: ${useCase || "general enterprise"}).
Return ONLY valid JSON: {"scores":{"metric_id": score_0_to_5}}
Use your training knowledge. Score 0-5 integers. Be realistic and conservative. No extra text.`;
      try {
        const raw = await callClaude([{ role: "user", content: batch.map(m => `${m.id}: ${m.name}`).join("\n") }], system);
        const parsed = JSON.parse(raw.replace(/\`\`\`json|\`\`\`/g, "").trim());
        Object.assign(newScores, parsed.scores || {});
      } catch {}
      setAltResearchProgress(Math.round(((bi + 1) / batches.length) * 100));
      setAlternatives(prev => prev.map(a => a.slug === altSlug ? { ...a, scores: { ...newScores } } : a));
    }
    await saveScores(altSlug, newScores);
    const state = await loadState(productSlug) || {};
    state.alternatives = [...(state.alternatives || []).filter(a => a.slug !== altSlug), { name: altName, slug: altSlug, status: "complete" }];
    await saveState(productSlug, state);
    setAlternatives(prev => prev.map(a => a.slug === altSlug ? { ...a, scores: newScores, status: "complete" } : a));
    setAltResearching(null);
  };

  const removeAlternative = async (altSlug) => {
    setAlternatives(prev => prev.filter(a => a.slug !== altSlug));
    const state = await loadState(productSlug) || {};
    state.alternatives = (state.alternatives || []).filter(a => a.slug !== altSlug);
    await saveState(productSlug, state);
  };

  const handleScoreChange = async (metricId, val) => {
    const updated = { ...scores, [metricId]: val };
    setScores(updated);
    await saveScores(productSlug, updated);
  };

  const markPersonaDone = async (personaId) => {
    const updated = new Set([...completedPersonas, personaId]);
    setCompletedPersonas(updated);
    const state = await loadState(productSlug) || {};
    state.completedPersonas = [...updated];
    await saveState(productSlug, state);
    setActivePersona(null);
    // AI insight
    setAiLoading(true);
    setAiInsight("");
    const personaMetrics = METRICS.filter(m => m.owner === personaId);
    const personaScores = personaMetrics.map(m => `${m.name}: ${scores[m.id] ?? "unscored"}`).join(", ");
    const system = `You are a ${PERSONAS.find(p => p.id === personaId)?.label} evaluating "${productName}" as an enterprise SaaS. Be concise, opinionated, and speak in your persona's voice.`;
    const txt = await callClaude([{
      role: "user",
      content: `Based on these scores — ${personaScores} — give a 2-sentence verdict as this persona on whether ${productName} should be approved, and the single biggest risk.`
    }], system);
    setAiInsight(txt);
    setAiLoading(false);
  };

  const sendChat = async () => {
    if (!chatInput.trim() || chatLoading) return;
    const msg = chatInput.trim();
    setChatInput("");
    const newMessages = [...chatMessages, { role: "user", content: msg }];
    setChatMessages(newMessages);
    setChatLoading(true);
    const system = `You are a SaaS enterprise evaluator assistant. The product being evaluated is "${productName}" (use case: ${useCase}). 
Current U-index score: ${calcUIndex(scores)}/5. You have access to scoring data. Be direct, expert, persona-aware.`;
    const reply = await callClaude(newMessages, system);
    setChatMessages([...newMessages, { role: "assistant", content: reply }]);
    setChatLoading(false);
  };

  const uIndex = calcUIndex(scores);
  const verdict = getVerdict(uIndex);
  const scoredCount = Object.keys(scores).filter(k => scores[k] != null).length;
  const readyForReport = completedPersonas.size === 6;

  // ── SCREENS ──────────────────────────────────────────────────────────────────

  if (screen === "home") return (
    <div style={S.root}>
      <div style={S.nav}>
        <span style={S.logo}>SaaS<span style={{ color: "#00CFFF" }}>Eval</span></span>
        <span style={{ ...S.navTag, cursor: "pointer" }} onClick={() => setScreen("history")}>
          📂 History ({historySlugs.length})
        </span>
      </div>
      <div style={S.hero}>
        <div style={S.heroBadge}>POWERED BY AUTONOMYX · SaaS USABILITY INDEX</div>
        <h1 style={S.heroTitle}>Enterprise SaaS<br /><span style={{ color: "#00CFFF" }}>Evaluation Engine</span></h1>
        <p style={S.heroSub}>
          Multi-persona scoring across 35 metrics and 7 stages.<br />
          AI-researched. Team-validated. Report-ready.
        </p>
        <button style={S.ctaBtn} onClick={() => setScreen("setup")}>
          Start New Evaluation →
        </button>
        <div style={S.stageGrid}>
          {STAGES.map(s => (
            <div key={s.id} style={{ ...S.stageCard, borderColor: s.color + "44" }}>
              <div style={{ color: s.color, fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, marginBottom: 4 }}>
                S{s.id} · {Math.round(s.weight * 100)}%
              </div>
              <div style={{ color: "#e2e8f0", fontSize: 12, fontWeight: 600 }}>{s.name}</div>
            </div>
          ))}
        </div>
        <div style={S.personaRow}>
          {PERSONAS.map(p => (
            <div key={p.id} style={{ ...S.personaChip, borderColor: p.color + "66" }}>
              {p.icon} {p.label}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  if (screen === "setup") return (
    <div style={S.root}>
      <div style={S.nav}>
        <span style={{ ...S.logo, cursor: "pointer" }} onClick={() => setScreen("home")}>← SaaS<span style={{ color: "#00CFFF" }}>Eval</span></span>
      </div>
      <div style={S.centered}>
        <div style={S.card}>
          <h2 style={S.cardTitle}>New Evaluation</h2>
          <p style={S.cardSub}>Claude will auto-research all 35 metrics to pre-populate scores. Your team then confirms, challenges, and completes.</p>
          <label style={S.label}>Product / Vendor Name</label>
          <input style={S.input} placeholder="e.g. Notion, Rippling, Workday…"
            value={productName} onChange={e => setProductName(e.target.value)}
            onKeyDown={e => e.key === "Enter" && productName.trim() && setSetupStep(2)} />
          {setupStep >= 2 && <>
            <label style={S.label}>Primary Use Case (optional)</label>
            <input style={S.input} placeholder="e.g. Team wiki and knowledge management"
              value={useCase} onChange={e => setUseCase(e.target.value)} />
          </>}
          <button style={{
            ...S.ctaBtn, marginTop: 24, width: "100%", opacity: productName.trim() ? 1 : 0.4,
            pointerEvents: productName.trim() ? "auto" : "none"
          }} onClick={() => {
            if (setupStep === 1) setSetupStep(2);
            else startEvaluation();
          }}>
            {setupStep === 1 ? "Continue →" : "🔍 Auto-Research & Start →"}
          </button>
        </div>
      </div>
    </div>
  );

  if (autoResearching) return (
    <div style={S.root}>
      <div style={{ ...S.centered, textAlign: "center" }}>
        <div style={{ fontSize: 48, marginBottom: 16, animation: "spin 2s linear infinite" }}>🔍</div>
        <h2 style={{ color: "#e2e8f0", fontFamily: "'IBM Plex Mono', monospace", marginBottom: 8 }}>
          AI Researching {productName}
        </h2>
        <p style={{ color: "#64748b", marginBottom: 24 }}>Pre-populating all 35 metrics from Claude's knowledge…</p>
        <div style={{ width: 300, height: 8, background: "#1e293b", borderRadius: 4, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${researchProgress}%`, background: "linear-gradient(90deg, #1B5EBE, #00CFFF)", transition: "width 0.4s", borderRadius: 4 }} />
        </div>
        <div style={{ color: "#00CFFF", fontFamily: "'IBM Plex Mono', monospace", marginTop: 8, fontSize: 13 }}>
          {researchProgress}% complete
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );

  if (screen === "evaluate") {
    const personaMetrics = activePersona ? METRICS.filter(m => m.owner === activePersona) : [];
    const blockers = METRICS.filter(m => [2, 4, 5].includes(m.stage) && scores[m.id] != null && scores[m.id] <= 1);

    return (
      <div style={S.root}>
        <div style={S.nav}>
          <span style={{ ...S.logo, cursor: "pointer" }} onClick={() => { setActivePersona(null); setScreen("home"); }}>
            ← SaaS<span style={{ color: "#00CFFF" }}>Eval</span>
          </span>
          <span style={S.navTag}>{productName}</span>
          <div style={{ display: "flex", gap: 8 }}>
            <button style={S.smBtn} onClick={() => setScreen("alternatives")}>
              ⚖️ Alternatives ({alternatives.length})
            </button>
            <button style={S.smBtn} onClick={() => setScreen("results")}>View Report →</button>
          </div>
        </div>

        {!activePersona ? (
          <div style={{ padding: "24px 20px", maxWidth: 1000, margin: "0 auto" }}>
            {/* Score summary bar */}
            <div style={S.scoreBar}>
              <div>
                <div style={{ color: "#64748b", fontSize: 12, fontFamily: "'IBM Plex Mono', monospace", marginBottom: 4 }}>U-INDEX</div>
                <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
                  <span style={{ fontSize: 40, fontWeight: 800, color: verdict.color, fontFamily: "'IBM Plex Mono', monospace" }}>{uIndex.toFixed(2)}</span>
                  <span style={{ color: "#64748b", fontSize: 14 }}>/5</span>
                </div>
                <div style={{ color: verdict.color, fontWeight: 700, fontSize: 14 }}>{verdict.label}</div>
                <div style={{ color: "#64748b", fontSize: 12 }}>{verdict.sub}</div>
              </div>
              <RadarChart scores={scores} />
              <div>
                <div style={{ color: "#64748b", fontSize: 12, marginBottom: 8 }}>{scoredCount}/35 metrics scored</div>
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  {STAGES.map(s => {
                    const ms = METRICS.filter(m => m.stage === s.id);
                    const scored = ms.filter(m => scores[m.id] != null);
                    const avg = scored.length ? scored.reduce((a, m) => a + scores[m.id], 0) / (ms.length * 5) * 5 : 0;
                    return (
                      <div key={s.id} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ width: 20, color: "#64748b", fontSize: 11, fontFamily: "monospace" }}>S{s.id}</span>
                        <div style={{ flex: 1, height: 5, background: "#1e293b", borderRadius: 3, overflow: "hidden" }}>
                          <div style={{ height: "100%", width: `${(avg / 5) * 100}%`, background: s.color, borderRadius: 3, transition: "width 0.5s" }} />
                        </div>
                        <span style={{ color: "#94a3b8", fontSize: 11, width: 28, textAlign: "right", fontFamily: "monospace" }}>
                          {avg.toFixed(1)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Blockers */}
            {blockers.length > 0 && (
              <div style={S.blockerBox}>
                <div style={{ fontWeight: 700, color: "#EF4444", marginBottom: 6 }}>
                  🚨 {blockers.length} Procurement Blocker{blockers.length > 1 ? "s" : ""}
                </div>
                {blockers.map(m => (
                  <div key={m.id} style={{ fontSize: 12, color: "#fca5a5", marginBottom: 2 }}>
                    {m.id} {m.name} — Score: {scores[m.id]}
                  </div>
                ))}
              </div>
            )}

            {/* Alternatives quick strip */}
            {alternatives.length > 0 && (
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 16, alignItems: "center" }}>
                <span style={{ color: "#64748b", fontSize: 12, fontFamily: "monospace" }}>ALTERNATIVES:</span>
                {alternatives.map(alt => {
                  const altU = calcUIndex(alt.scores);
                  const altV = getVerdict(altU);
                  return (
                    <div key={alt.slug} style={{
                      background: "#0f172a", border: `1px solid ${altV.color}44`,
                      borderRadius: 8, padding: "4px 10px", display: "flex", alignItems: "center", gap: 6,
                    }}>
                      <span style={{ color: "#e2e8f0", fontSize: 12, fontWeight: 600 }}>{alt.name}</span>
                      {alt.status === "researching"
                        ? <span style={{ color: "#64748b", fontSize: 11, fontFamily: "monospace" }}>…</span>
                        : <span style={{ color: altV.color, fontSize: 12, fontFamily: "monospace", fontWeight: 700 }}>{altU.toFixed(2)}</span>
                      }
                    </div>
                  );
                })}
                <button style={{ ...S.smBtn, fontSize: 11, padding: "4px 10px" }} onClick={() => setScreen("alternatives")}>
                  + Manage
                </button>
              </div>
            )}

            {/* Persona cards */}
            <h3 style={{ color: "#94a3b8", fontSize: 13, fontFamily: "'IBM Plex Mono', monospace", marginBottom: 12, marginTop: 24 }}>
              EVALUATION TEAM — SELECT YOUR PERSONA
            </h3>
            <div style={S.personaGrid}>
              {PERSONAS.map(p => {
                const pMetrics = METRICS.filter(m => m.owner === p.id);
                const pScored = pMetrics.filter(m => scores[m.id] != null).length;
                const done = completedPersonas.has(p.id);
                return (
                  <div key={p.id} style={{
                    ...S.personaCard,
                    borderColor: done ? p.color : p.color + "44",
                    background: done ? p.color + "11" : "#0f172a",
                    cursor: "pointer",
                  }} onClick={() => setActivePersona(p.id)}>
                    <div style={{ fontSize: 28, marginBottom: 8 }}>{p.icon}</div>
                    <div style={{ fontWeight: 700, color: "#e2e8f0", fontSize: 14 }}>{p.label}</div>
                    <div style={{ color: "#64748b", fontSize: 12, marginTop: 4 }}>
                      {pScored}/{pMetrics.length} metrics
                    </div>
                    <div style={{
                      marginTop: 8, fontSize: 11, fontWeight: 600,
                      color: done ? p.color : "#475569",
                      fontFamily: "'IBM Plex Mono', monospace"
                    }}>
                      {done ? "✓ COMPLETE" : "→ ENTER"}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* AI Chat */}
            <div style={S.chatBox}>
              <div style={{ color: "#94a3b8", fontSize: 13, fontFamily: "'IBM Plex Mono', monospace", marginBottom: 12 }}>
                💬 ASK THE AI EVALUATOR
              </div>
              <div style={{ minHeight: 80, maxHeight: 200, overflowY: "auto", marginBottom: 10 }}>
                {chatMessages.map((m, i) => (
                  <div key={i} style={{
                    marginBottom: 8, padding: "8px 12px", borderRadius: 8,
                    background: m.role === "user" ? "#1e3a5f" : "#0f172a",
                    border: m.role === "assistant" ? "1px solid #1e293b" : "none",
                    fontSize: 13, color: "#e2e8f0", lineHeight: 1.5,
                  }}>
                    <span style={{ color: m.role === "user" ? "#00CFFF" : "#4D8FFF", fontSize: 11, fontFamily: "monospace" }}>
                      {m.role === "user" ? "YOU" : "AI"} ·{" "}
                    </span>
                    {m.content}
                  </div>
                ))}
                {chatLoading && <div style={{ color: "#4D8FFF", fontSize: 13, fontFamily: "monospace" }}>Thinking…</div>}
                <div ref={chatEndRef} />
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <input style={{ ...S.input, flex: 1, margin: 0 }}
                  placeholder="Ask about this evaluation, risks, comparisons…"
                  value={chatInput} onChange={e => setChatInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && sendChat()} />
                <button style={S.smBtn} onClick={sendChat}>Send</button>
              </div>
            </div>

            {readyForReport && (
              <button style={{ ...S.ctaBtn, width: "100%", marginTop: 16 }} onClick={() => setScreen("results")}>
                🎉 All Personas Complete — Generate Report →
              </button>
            )}
          </div>
        ) : (
          /* ── Persona scoring view ── */
          <div style={{ padding: "24px 20px", maxWidth: 760, margin: "0 auto" }}>
            {(() => {
              const persona = PERSONAS.find(p => p.id === activePersona);
              return <>
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
                  <button style={S.smBtn} onClick={() => { setActivePersona(null); setAiInsight(""); }}>← Back</button>
                  <span style={{ fontSize: 24 }}>{persona.icon}</span>
                  <div>
                    <div style={{ fontWeight: 700, color: "#e2e8f0", fontSize: 18 }}>{persona.label}</div>
                    <div style={{ color: "#64748b", fontSize: 13 }}>Reviewing {productName} · {personaMetrics.length} metrics</div>
                  </div>
                </div>

                {personaMetrics.map(metric => (
                  <div key={metric.id} style={S.metricRow}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                        <span style={{ color: "#64748b", fontFamily: "monospace", fontSize: 12 }}>{metric.id}</span>
                        <span style={{ color: "#e2e8f0", fontWeight: 600, fontSize: 14 }}>{metric.name}</span>
                        {[2, 4, 5].includes(metric.stage) && scores[metric.id] != null && scores[metric.id] <= 1 &&
                          <span style={{ color: "#EF4444", fontSize: 12 }}>🚨</span>}
                      </div>
                      {evidence[metric.id] && (
                        <div style={{ color: "#475569", fontSize: 12, fontStyle: "italic", marginBottom: 6 }}>
                          AI research: {evidence[metric.id]}
                        </div>
                      )}
                      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                        {[0, 1, 2, 3, 4, 5].map(n => (
                          <button key={n} style={{
                            ...S.scoreBtn,
                            background: scores[metric.id] === n ? persona.color : "#1e293b",
                            color: scores[metric.id] === n ? "#fff" : "#64748b",
                            borderColor: scores[metric.id] === n ? persona.color : "#334155",
                          }} onClick={() => handleScoreChange(metric.id, n)}>
                            {n}
                          </button>
                        ))}
                      </div>
                    </div>
                    <ScoreBadge score={scores[metric.id]} />
                  </div>
                ))}

                {aiInsight && (
                  <div style={S.insightBox}>
                    <div style={{ color: "#00CFFF", fontSize: 12, fontFamily: "monospace", marginBottom: 6 }}>AI VERDICT · {persona.label.toUpperCase()}</div>
                    <div style={{ color: "#e2e8f0", fontSize: 14, lineHeight: 1.6 }}>{aiInsight}</div>
                  </div>
                )}
                {aiLoading && <div style={{ color: "#4D8FFF", fontSize: 13, fontFamily: "monospace", margin: "12px 0" }}>Generating AI verdict…</div>}

                <button style={{ ...S.ctaBtn, width: "100%", marginTop: 16, background: persona.color }}
                  onClick={() => markPersonaDone(activePersona)}>
                  ✓ Mark {persona.label} Section Complete
                </button>
              </>;
            })()}
          </div>
        )}
      </div>
    );
  }

  if (screen === "results") {
    const blockers = METRICS.filter(m => [2, 4, 5].includes(m.stage) && scores[m.id] != null && scores[m.id] <= 1);
    return (
      <div style={S.root}>
        <div style={S.nav}>
          <span style={{ ...S.logo, cursor: "pointer" }} onClick={() => setScreen("evaluate")}>← Back</span>
          <span style={S.navTag}>{productName} · Evaluation Report</span>
        </div>
        <div style={{ padding: "24px 20px", maxWidth: 900, margin: "0 auto" }}>
          <div style={{ ...S.scoreBar, marginBottom: 32, flexWrap: "wrap" }}>
            <div>
              <div style={{ color: "#64748b", fontFamily: "monospace", fontSize: 12, marginBottom: 4 }}>SAAS USABILITY INDEX</div>
              <div style={{ fontSize: 64, fontWeight: 900, color: verdict.color, fontFamily: "'IBM Plex Mono', monospace", lineHeight: 1 }}>
                {uIndex.toFixed(2)}
              </div>
              <div style={{ color: verdict.color, fontWeight: 800, fontSize: 20, marginTop: 4 }}>{verdict.label}</div>
              <div style={{ color: "#94a3b8", fontSize: 14, marginTop: 4 }}>{verdict.sub}</div>
              <div style={{ color: "#475569", fontSize: 13, marginTop: 8 }}>
                {scoredCount}/35 metrics · {completedPersonas.size}/6 personas complete
              </div>
            </div>
            <RadarChart scores={scores} />
          </div>

          {blockers.length > 0 && (
            <div style={{ ...S.blockerBox, marginBottom: 24 }}>
              <div style={{ fontWeight: 700, color: "#EF4444", marginBottom: 8, fontSize: 15 }}>
                🚨 {blockers.length} Procurement Blocker{blockers.length > 1 ? "s" : ""} — Must Resolve Before Approval
              </div>
              {blockers.map(m => (
                <div key={m.id} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <ScoreBadge score={scores[m.id]} size="sm" />
                  <span style={{ color: "#fca5a5", fontSize: 13 }}>{m.id} {m.name}</span>
                  <span style={{ color: "#64748b", fontSize: 12 }}>Stage {m.stage}</span>
                </div>
              ))}
            </div>
          )}

          {STAGES.map(stage => {
            const ms = METRICS.filter(m => m.stage === stage.id);
            const scored = ms.filter(m => scores[m.id] != null);
            const stageAvg = scored.length ? scored.reduce((a, m) => a + scores[m.id], 0) / (ms.length * 5) * 5 : 0;
            return (
              <div key={stage.id} style={{ marginBottom: 20, border: `1px solid ${stage.color}33`, borderRadius: 10, overflow: "hidden" }}>
                <div style={{
                  padding: "12px 16px", background: stage.color + "11",
                  display: "flex", alignItems: "center", justifyContent: "space-between"
                }}>
                  <div>
                    <span style={{ color: stage.color, fontFamily: "monospace", fontSize: 12, marginRight: 8 }}>S{stage.id}</span>
                    <span style={{ color: "#e2e8f0", fontWeight: 700 }}>{stage.name}</span>
                    <span style={{ color: "#64748b", fontSize: 12, marginLeft: 8 }}>
                      Weight: {Math.round(stage.weight * 100)}%
                    </span>
                  </div>
                  <div style={{ color: stage.color, fontFamily: "monospace", fontWeight: 700, fontSize: 18 }}>
                    {stageAvg.toFixed(1)}/5
                  </div>
                </div>
                <div style={{ padding: "8px 0" }}>
                  {ms.map(m => {
                    const p = PERSONAS.find(p => p.id === m.owner);
                    return (
                      <div key={m.id} style={{
                        display: "flex", alignItems: "center", gap: 12,
                        padding: "8px 16px",
                        borderBottom: "1px solid #1e293b",
                      }}>
                        <ScoreBadge score={scores[m.id]} />
                        <div style={{ flex: 1 }}>
                          <span style={{ color: "#94a3b8", fontSize: 12, fontFamily: "monospace" }}>{m.id} </span>
                          <span style={{ color: "#e2e8f0", fontSize: 13 }}>{m.name}</span>
                        </div>
                        <span style={{ color: p?.color || "#64748b", fontSize: 11, fontFamily: "monospace" }}>
                          {p?.icon} {p?.label}
                        </span>
                        {[2, 4, 5].includes(stage.id) && scores[m.id] != null && scores[m.id] <= 1 &&
                          <span style={{ color: "#EF4444" }}>🚨</span>}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (screen === "alternatives") {
    const allProducts = [
      { name: productName, slug: productSlug, scores, isPrimary: true },
      ...alternatives.map(a => ({ ...a, isPrimary: false })),
    ];
    const primaryU = calcUIndex(scores);

    const filteredMetrics = compareMetricFilter === "blockers"
      ? METRICS.filter(m => [2, 4, 5].includes(m.stage) && scores[m.id] != null && scores[m.id] <= 1)
      : compareMetricFilter === "gaps"
      ? METRICS.filter(m => {
          const primary = scores[m.id] ?? 0;
          return alternatives.some(a => (a.scores[m.id] ?? 0) > primary);
        })
      : METRICS;

    return (
      <div style={S.root}>
        <div style={S.nav}>
          <span style={{ ...S.logo, cursor: "pointer" }} onClick={() => setScreen("evaluate")}>← Back</span>
          <span style={S.navTag}>{productName} · Alternatives Considered</span>
          <button style={S.smBtn} onClick={() => setScreen("results")}>View Report →</button>
        </div>

        <div style={{ padding: "24px 20px", maxWidth: 1100, margin: "0 auto" }}>
          {/* Add alternative */}
          <div style={{ ...S.chatBox, marginBottom: 24 }}>
            <div style={{ color: "#94a3b8", fontSize: 13, fontFamily: "monospace", marginBottom: 12 }}>
              ⚖️ ADD ALTERNATIVE PRODUCT TO COMPARE
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <input
                style={{ ...S.input, flex: 1, margin: 0 }}
                placeholder="e.g. Confluence, Coda, Notion AI…"
                value={altInput}
                onChange={e => setAltInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter" && altInput.trim() && !altResearching) {
                    researchAlternative(altInput.trim());
                    setAltInput("");
                  }
                }}
              />
              <button
                style={{
                  ...S.ctaBtn, padding: "10px 20px", fontSize: 14,
                  opacity: altInput.trim() && !altResearching ? 1 : 0.4,
                  pointerEvents: altInput.trim() && !altResearching ? "auto" : "none",
                }}
                onClick={() => { researchAlternative(altInput.trim()); setAltInput(""); }}
              >
                {altResearching ? "Researching…" : "Research & Add →"}
              </button>
            </div>
            {altResearching && (
              <div style={{ marginTop: 10 }}>
                <div style={{ width: "100%", height: 5, background: "#1e293b", borderRadius: 3, overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${altResearchProgress}%`, background: "linear-gradient(90deg, #8B5CF6, #EC4899)", transition: "width 0.4s", borderRadius: 3 }} />
                </div>
                <div style={{ color: "#8B5CF6", fontFamily: "monospace", fontSize: 12, marginTop: 4 }}>
                  Researching {alternatives.find(a => a.slug === altResearching)?.name}… {altResearchProgress}%
                </div>
              </div>
            )}
          </div>

          {/* Summary cards */}
          {allProducts.length > 1 && (
            <>
              <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 24 }}>
                {allProducts.map(prod => {
                  const u = prod.isPrimary ? primaryU : calcUIndex(prod.scores);
                  const v = getVerdict(u);
                  const isWinner = allProducts.every(p => {
                    const pu = p.isPrimary ? primaryU : calcUIndex(p.scores);
                    return u >= pu;
                  });
                  return (
                    <div key={prod.slug} style={{
                      flex: "1 1 160px", background: "#0f172a",
                      border: `2px solid ${prod.isPrimary ? "#00CFFF" : v.color + "55"}`,
                      borderRadius: 12, padding: "16px 18px", position: "relative",
                    }}>
                      {prod.isPrimary && (
                        <div style={{
                          position: "absolute", top: -10, left: 12,
                          background: "#00CFFF", color: "#020817", fontSize: 10,
                          fontWeight: 700, borderRadius: 4, padding: "2px 7px",
                          fontFamily: "monospace",
                        }}>PRIMARY</div>
                      )}
                      {isWinner && (
                        <div style={{
                          position: "absolute", top: -10, right: 12,
                          background: "#10B981", color: "#fff", fontSize: 10,
                          fontWeight: 700, borderRadius: 4, padding: "2px 7px",
                          fontFamily: "monospace",
                        }}>WINNER</div>
                      )}
                      <div style={{ fontWeight: 700, color: "#e2e8f0", marginBottom: 4 }}>{prod.name}</div>
                      {prod.status === "researching"
                        ? <div style={{ color: "#64748b", fontSize: 12 }}>Researching…</div>
                        : <>
                          <div style={{ fontSize: 32, fontWeight: 900, color: v.color, fontFamily: "monospace", lineHeight: 1 }}>{u.toFixed(2)}</div>
                          <div style={{ color: v.color, fontSize: 12, fontWeight: 600, marginTop: 4 }}>{v.label}</div>
                          <div style={{ color: "#475569", fontSize: 11, marginTop: 2 }}>{v.sub}</div>
                        </>
                      }
                      {!prod.isPrimary && (
                        <button style={{
                          marginTop: 10, background: "none", border: "1px solid #334155",
                          borderRadius: 4, color: "#EF4444", fontSize: 11, padding: "3px 8px",
                          cursor: "pointer",
                        }} onClick={() => removeAlternative(prod.slug)}>Remove</button>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Metric filter */}
              <div style={{ display: "flex", gap: 8, marginBottom: 16, alignItems: "center" }}>
                <span style={{ color: "#64748b", fontSize: 12, fontFamily: "monospace" }}>SHOW:</span>
                {[["all", "All Metrics"], ["blockers", "🚨 Blockers Only"], ["gaps", "⚠️ Where Alternatives Win"]].map(([val, label]) => (
                  <button key={val} style={{
                    ...S.smBtn,
                    background: compareMetricFilter === val ? "#1B5EBE" : "#1e293b",
                    color: compareMetricFilter === val ? "#fff" : "#94a3b8",
                    fontSize: 12,
                  }} onClick={() => setCompareMetricFilter(val)}>{label}</button>
                ))}
              </div>

              {/* Comparison table */}
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid #1e293b" }}>
                      <th style={{ textAlign: "left", padding: "10px 12px", color: "#64748b", fontFamily: "monospace", fontSize: 11, fontWeight: 600, width: 240 }}>METRIC</th>
                      {allProducts.map(p => (
                        <th key={p.slug} style={{
                          textAlign: "center", padding: "10px 12px",
                          color: p.isPrimary ? "#00CFFF" : "#94a3b8",
                          fontFamily: "monospace", fontSize: 11, fontWeight: 700,
                          borderLeft: "1px solid #1e293b",
                        }}>{p.name}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {STAGES.map(stage => {
                      const stageMetrics = filteredMetrics.filter(m => m.stage === stage.id);
                      if (!stageMetrics.length) return null;
                      return [
                        <tr key={"stage-" + stage.id} style={{ background: stage.color + "11" }}>
                          <td colSpan={allProducts.length + 1} style={{
                            padding: "8px 12px", color: stage.color,
                            fontFamily: "monospace", fontSize: 11, fontWeight: 700, letterSpacing: "0.05em"
                          }}>
                            S{stage.id} · {stage.name.toUpperCase()} · {Math.round(stage.weight * 100)}%
                          </td>
                        </tr>,
                        ...stageMetrics.map(metric => {
                          const primaryScore = scores[metric.id];
                          const maxAltScore = alternatives.length
                            ? Math.max(...alternatives.map(a => a.scores[metric.id] ?? 0))
                            : 0;
                          const isGap = primaryScore != null && maxAltScore > primaryScore;
                          const isBlocker = [2, 4, 5].includes(metric.stage) && primaryScore != null && primaryScore <= 1;
                          return (
                            <tr key={metric.id} style={{
                              borderBottom: "1px solid #1e293b",
                              background: isBlocker ? "#EF444408" : isGap ? "#F59E0B08" : "transparent",
                            }}>
                              <td style={{ padding: "9px 12px" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                                  {isBlocker && <span style={{ fontSize: 11 }}>🚨</span>}
                                  {isGap && !isBlocker && <span style={{ fontSize: 11 }}>⚠️</span>}
                                  <span style={{ color: "#64748b", fontFamily: "monospace", fontSize: 11 }}>{metric.id}</span>
                                  <span style={{ color: "#e2e8f0" }}>{metric.name}</span>
                                </div>
                              </td>
                              {allProducts.map(prod => {
                                const s = prod.isPrimary ? scores[metric.id] : prod.scores[metric.id];
                                const allScores = allProducts.map(p => p.isPrimary ? scores[metric.id] ?? 0 : p.scores[metric.id] ?? 0);
                                const isTop = s != null && s === Math.max(...allScores);
                                const colors = ["#EF4444","#F97316","#F59E0B","#84CC16","#10B981","#10B981"];
                                const bg = s == null ? "#334155" : colors[s] || "#334155";
                                return (
                                  <td key={prod.slug} style={{
                                    textAlign: "center", padding: "9px 12px",
                                    borderLeft: "1px solid #1e293b",
                                  }}>
                                    <div style={{
                                      display: "inline-flex", alignItems: "center", justifyContent: "center",
                                      width: 28, height: 28, borderRadius: 6, background: bg,
                                      color: "#fff", fontWeight: 700, fontSize: 13,
                                      boxShadow: isTop && s != null ? `0 0 8px ${bg}88` : "none",
                                      outline: isTop && s != null ? `2px solid ${bg}` : "none",
                                      outlineOffset: 2,
                                    }}>
                                      {s == null ? "—" : s}
                                    </div>
                                  </td>
                                );
                              })}
                            </tr>
                          );
                        })
                      ];
                    })}
                  </tbody>
                </table>
              </div>

              {/* Stage-level comparison bars */}
              <div style={{ marginTop: 32 }}>
                <div style={{ color: "#94a3b8", fontSize: 12, fontFamily: "monospace", marginBottom: 12 }}>STAGE-LEVEL COMPARISON</div>
                {STAGES.map(stage => {
                  const ms = METRICS.filter(m => m.stage === stage.id);
                  return (
                    <div key={stage.id} style={{ marginBottom: 14 }}>
                      <div style={{ color: "#64748b", fontSize: 11, fontFamily: "monospace", marginBottom: 6 }}>
                        S{stage.id} · {stage.name}
                      </div>
                      {allProducts.map(prod => {
                        const pScores = prod.isPrimary ? scores : prod.scores;
                        const scored = ms.filter(m => pScores[m.id] != null);
                        const avg = scored.length ? scored.reduce((a, m) => a + pScores[m.id], 0) / (ms.length * 5) * 5 : 0;
                        const pv = getVerdict(avg);
                        return (
                          <div key={prod.slug} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                            <span style={{
                              width: 100, fontSize: 11, color: prod.isPrimary ? "#00CFFF" : "#94a3b8",
                              fontWeight: prod.isPrimary ? 700 : 400, textAlign: "right", flexShrink: 0,
                            }}>{prod.name}</span>
                            <div style={{ flex: 1, height: 8, background: "#1e293b", borderRadius: 4, overflow: "hidden" }}>
                              <div style={{
                                height: "100%", width: `${(avg / 5) * 100}%`,
                                background: prod.isPrimary ? stage.color : pv.color + "aa",
                                borderRadius: 4, transition: "width 0.5s"
                              }} />
                            </div>
                            <span style={{ color: "#94a3b8", fontSize: 11, fontFamily: "monospace", width: 30 }}>
                              {avg.toFixed(1)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {alternatives.length === 0 && (
            <div style={{ textAlign: "center", color: "#475569", marginTop: 60, fontSize: 15 }}>
              No alternatives added yet.<br />
              <span style={{ color: "#64748b", fontSize: 13 }}>Add a competitor above and Claude will auto-research all 35 metrics for a side-by-side comparison.</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (screen === "history") return (
    <div style={S.root}>
      <div style={S.nav}>
        <span style={{ ...S.logo, cursor: "pointer" }} onClick={() => setScreen("home")}>← SaaS<span style={{ color: "#00CFFF" }}>Eval</span></span>
        <span style={S.navTag}>Evaluation History</span>
      </div>
      <div style={{ padding: "24px 20px", maxWidth: 700, margin: "0 auto" }}>
        {historySlugs.length === 0 ? (
          <div style={{ color: "#64748b", textAlign: "center", marginTop: 60 }}>
            No evaluations yet. <span style={{ color: "#00CFFF", cursor: "pointer" }} onClick={() => setScreen("setup")}>Start one →</span>
          </div>
        ) : historySlugs.map(slug => (
          <div key={slug} style={{
            ...S.card, cursor: "pointer", marginBottom: 12, display: "flex",
            alignItems: "center", justifyContent: "space-between", padding: "14px 18px"
          }} onClick={() => loadEvaluation(slug)}>
            <div>
              <div style={{ color: "#e2e8f0", fontWeight: 700, textTransform: "capitalize" }}>
                {slug.replace(/-/g, " ")}
              </div>
              <div style={{ color: "#64748b", fontSize: 12, marginTop: 2 }}>Click to continue evaluation</div>
            </div>
            <span style={{ color: "#00CFFF", fontSize: 13 }}>Resume →</span>
          </div>
        ))}
      </div>
    </div>
  );

  return null;
}

// ─── STYLES ───────────────────────────────────────────────────────────────────

const S = {
  root: {
    minHeight: "100vh",
    background: "#020817",
    color: "#e2e8f0",
    fontFamily: "'IBM Plex Sans', -apple-system, sans-serif",
  },
  nav: {
    display: "flex", alignItems: "center", justifyContent: "space-between",
    padding: "14px 20px", borderBottom: "1px solid #1e293b",
    background: "#020817ee", position: "sticky", top: 0, zIndex: 100,
    backdropFilter: "blur(12px)",
  },
  logo: {
    fontSize: 20, fontWeight: 900, letterSpacing: "-1px",
    fontFamily: "'IBM Plex Mono', monospace", color: "#e2e8f0",
    textDecoration: "none",
  },
  navTag: {
    background: "#1e293b", border: "1px solid #334155", borderRadius: 20,
    padding: "4px 12px", fontSize: 12, color: "#94a3b8", fontFamily: "monospace",
  },
  hero: {
    textAlign: "center", padding: "64px 20px 80px",
    background: "radial-gradient(ellipse at 50% 0%, #001141 0%, #020817 70%)",
  },
  heroBadge: {
    display: "inline-block", background: "#00CFFF11", border: "1px solid #00CFFF44",
    color: "#00CFFF", borderRadius: 20, padding: "4px 14px",
    fontSize: 11, fontFamily: "'IBM Plex Mono', monospace",
    letterSpacing: "0.08em", marginBottom: 24,
  },
  heroTitle: {
    fontSize: "clamp(32px, 6vw, 56px)", fontWeight: 900, lineHeight: 1.1,
    margin: "0 0 16px", letterSpacing: "-2px", color: "#f1f5f9",
  },
  heroSub: {
    color: "#64748b", fontSize: 16, lineHeight: 1.7, margin: "0 auto 32px", maxWidth: 520,
  },
  ctaBtn: {
    background: "linear-gradient(135deg, #1B5EBE, #00CFFF)",
    color: "#fff", border: "none", borderRadius: 10,
    padding: "14px 32px", fontSize: 16, fontWeight: 700,
    cursor: "pointer", letterSpacing: "-0.3px",
    boxShadow: "0 0 30px #00CFFF44",
    transition: "all 0.2s",
  },
  stageGrid: {
    display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: 10, marginTop: 48, maxWidth: 800, margin: "48px auto 0",
  },
  stageCard: {
    background: "#0f172a", border: "1px solid",
    borderRadius: 10, padding: "12px 14px", textAlign: "left",
  },
  personaRow: {
    display: "flex", flexWrap: "wrap", justifyContent: "center",
    gap: 8, marginTop: 24,
  },
  personaChip: {
    background: "#0f172a", border: "1px solid",
    borderRadius: 20, padding: "6px 14px", fontSize: 13, color: "#94a3b8",
  },
  centered: {
    display: "flex", alignItems: "center", justifyContent: "center",
    minHeight: "calc(100vh - 57px)", padding: 20,
  },
  card: {
    background: "#0f172a", border: "1px solid #1e293b",
    borderRadius: 14, padding: "28px 28px", width: "100%", maxWidth: 520,
  },
  cardTitle: {
    fontSize: 22, fontWeight: 800, color: "#f1f5f9", margin: "0 0 8px",
    letterSpacing: "-0.5px",
  },
  cardSub: { color: "#64748b", fontSize: 14, lineHeight: 1.6, margin: "0 0 24px" },
  label: { display: "block", color: "#94a3b8", fontSize: 13, fontFamily: "monospace", marginBottom: 6, marginTop: 16 },
  input: {
    width: "100%", background: "#1e293b", border: "1px solid #334155",
    borderRadius: 8, padding: "10px 14px", color: "#f1f5f9", fontSize: 14,
    outline: "none", boxSizing: "border-box",
    fontFamily: "'IBM Plex Sans', sans-serif",
  },
  smBtn: {
    background: "#1e293b", border: "1px solid #334155", borderRadius: 8,
    padding: "8px 14px", color: "#94a3b8", fontSize: 13, cursor: "pointer",
    fontFamily: "'IBM Plex Sans', sans-serif",
  },
  scoreBar: {
    display: "flex", gap: 32, alignItems: "center",
    background: "#0f172a", border: "1px solid #1e293b",
    borderRadius: 14, padding: 24, marginBottom: 20,
  },
  blockerBox: {
    background: "#EF444411", border: "1px solid #EF444444",
    borderRadius: 10, padding: "14px 18px",
  },
  personaGrid: {
    display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
    gap: 12,
  },
  personaCard: {
    border: "1px solid", borderRadius: 12, padding: "18px 14px",
    textAlign: "center", transition: "all 0.2s",
  },
  chatBox: {
    marginTop: 24, background: "#0f172a", border: "1px solid #1e293b",
    borderRadius: 12, padding: 16,
  },
  metricRow: {
    display: "flex", alignItems: "flex-start", gap: 12,
    padding: "14px 0", borderBottom: "1px solid #1e293b",
  },
  scoreBtn: {
    width: 34, height: 34, border: "1px solid", borderRadius: 6,
    cursor: "pointer", fontWeight: 700, fontSize: 14, transition: "all 0.15s",
    fontFamily: "'IBM Plex Mono', monospace",
  },
  insightBox: {
    marginTop: 20, background: "#001141", border: "1px solid #1B5EBE44",
    borderRadius: 10, padding: "14px 18px",
  },
};
