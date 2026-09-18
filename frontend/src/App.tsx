/*
  THESIS: a research instrument, not a SaaS dashboard — refuses the soft-shadow
  card-grid "AI product" look in favor of the analyst-terminal lineage
  (Bloomberg terminal / EDGAR filings / lab notebook).
  OWN-WORLD: near-black ground, restrained neutral + one signal-amber accent
  for actions/focus; semantic green/red reserved strictly for BUY/SELL (an
  earned finance convention, not decoration). IBM Plex Mono for tickers,
  model tags, and citations; system sans for prose/labels. Hairline borders,
  status-LED + text pill on every agent card (never color alone).
  STORY: enter a ticker + risk profile + as-of date, run once; the six-agent
  roster lights up with its real state — a working result, a genuine
  "not implemented yet" from the backend's own NotImplementedError, or
  "debate-only" for roles that don't run standalone.
  FIRST VIEWPORT: terminal title bar with a live backend-connection LED,
  the query bar directly below, then the agent roster grid.
  FORM: quant-terminal / EDGAR-filing lineage, code-led (no image-gen tool
  available in this environment).
  FINISH: unreviewed and undocumented is unfinished; this build ends with
  the finish review, the verdict, DESIGN.md, and every shipping raster
  carrying its provenance.
*/
import { useEffect, useState } from "react";
import type { AgentAnalysis, RiskProfileName, RosterEntry } from "./api";
import { analyze, AnalyzeError, checkHealth, fetchRoster } from "./api";
import { AgentCard, type CardState } from "./components/AgentCard";
import "./App.css";

const RISK_PROFILES: { value: RiskProfileName; label: string }[] = [
  { value: "risk_averse", label: "Risk-averse" },
  { value: "risk_neutral", label: "Risk-neutral" },
  { value: "risk_seeking", label: "Risk-seeking" },
];

function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function App() {
  const [backendUp, setBackendUp] = useState<boolean | null>(null);
  const [roster, setRoster] = useState<RosterEntry[]>([]);
  const [ticker, setTicker] = useState("AAPL");
  const [riskProfile, setRiskProfile] = useState<RiskProfileName>("risk_neutral");
  const [asOf, setAsOf] = useState(todayISO());
  const [results, setResults] = useState<Record<string, CardState>>({});
  const [running, setRunning] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let timer: number;

    async function poll() {
      const up = await checkHealth();
      if (cancelled) return;
      setBackendUp(up);
      if (up) {
        try {
          const r = await fetchRoster();
          if (!cancelled) setRoster(r);
        } catch {
          /* backend flapped between health check and roster fetch; next poll retries */
        }
      } else {
        timer = window.setTimeout(poll, 1500);
      }
    }
    poll();
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, []);

  async function runAll() {
    if (!ticker.trim()) return;
    setRunning(true);
    const nextResults: Record<string, CardState> = {};
    for (const entry of roster) {
      nextResults[entry.role] = entry.status === "debate_only" ? { kind: "idle" } : { kind: "loading" };
    }
    setResults(nextResults);

    await Promise.all(
      roster
        .filter((entry) => entry.status !== "debate_only")
        .map(async (entry) => {
          try {
            const data: AgentAnalysis = await analyze({
              ticker: ticker.trim().toUpperCase(),
              role: entry.role,
              risk_profile: riskProfile,
              as_of: asOf,
            });
            setResults((prev) => ({ ...prev, [entry.role]: { kind: "done", data } }));
          } catch (err) {
            const message = err instanceof AnalyzeError ? err.message : "Request failed";
            const status = err instanceof AnalyzeError ? err.status : 0;
            setResults((prev) => ({ ...prev, [entry.role]: { kind: "error", status, message } }));
          }
        })
    );
    setRunning(false);
  }

  return (
    <div className="app">
      <header className="titlebar">
        <div className="titlebar-brand">
          <span className="titlebar-glyph">{"//"}</span>
          <span>ALPHAAGENTS</span>
          <span className="titlebar-version">V2</span>
        </div>
        <div className="titlebar-status">
          <span className={`led ${backendUp ? "tone-ready" : backendUp === false ? "tone-error" : "tone-loading"}`} />
          <span>{backendUp ? "backend connected" : backendUp === false ? "backend unreachable" : "connecting…"}</span>
        </div>
      </header>

      <section className="query-bar">
        <label className="field">
          <span>Ticker</span>
          <input
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="AAPL"
            maxLength={10}
          />
        </label>

        <label className="field">
          <span>Risk profile</span>
          <select value={riskProfile} onChange={(e) => setRiskProfile(e.target.value as RiskProfileName)}>
            {RISK_PROFILES.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>As of</span>
          <input type="date" value={asOf} onChange={(e) => setAsOf(e.target.value)} />
        </label>

        <button className="run-button" onClick={runAll} disabled={!backendUp || running || !ticker.trim()}>
          {running ? "Running…" : "Run"}
        </button>
      </section>

      <main className="roster-grid">
        {roster.length === 0 && backendUp && <p className="empty-note">Loading agent roster…</p>}
        {roster.map((entry) => (
          <AgentCard key={entry.role} entry={entry} state={results[entry.role] ?? { kind: "idle" }} />
        ))}
      </main>
    </div>
  );
}
