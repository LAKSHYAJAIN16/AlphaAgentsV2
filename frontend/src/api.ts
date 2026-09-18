const API_BASE = "http://127.0.0.1:8765";

export type Recommendation = "BUY" | "SELL" | "HOLD";
export type RiskProfileName = "risk_averse" | "risk_neutral" | "risk_seeking";
export type RosterStatus = "ready" | "not_implemented" | "debate_only";

export interface Citation {
  source: string;
  excerpt: string;
}

export interface AgentAnalysis {
  agent_role: string;
  ticker: string;
  as_of: string;
  recommendation: Recommendation;
  conviction: number;
  reasoning: string;
  citations: Citation[];
  model_tag: string;
}

export interface RosterEntry {
  role: string;
  label: string;
  status: RosterStatus;
  model_tag: string;
}

export interface AnalyzeRequestBody {
  ticker: string;
  role: string;
  risk_profile: RiskProfileName;
  as_of?: string;
}

export class AnalyzeError extends Error {
  status: number;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2000) });
    return res.ok;
  } catch {
    return false;
  }
}

export async function fetchRoster(): Promise<RosterEntry[]> {
  const res = await fetch(`${API_BASE}/roster`);
  if (!res.ok) throw new Error(`roster fetch failed: ${res.status}`);
  return res.json();
}

export async function analyze(body: AnalyzeRequestBody): Promise<AgentAnalysis> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await res.json().catch(() => ({ detail: res.statusText }));
  if (!res.ok) {
    throw new AnalyzeError(res.status, payload.detail ?? res.statusText);
  }
  return payload as AgentAnalysis;
}
