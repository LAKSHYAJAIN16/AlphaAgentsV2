import type { AgentAnalysis, RosterEntry } from "../api";

export type CardState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "done"; data: AgentAnalysis }
  | { kind: "error"; status: number; message: string };

function statusPill(entry: RosterEntry, state: CardState): { text: string; tone: string } {
  if (state.kind === "loading") return { text: "RUNNING", tone: "tone-loading" };
  if (state.kind === "done") return { text: state.data.recommendation, tone: `tone-${state.data.recommendation.toLowerCase()}` };
  if (state.kind === "error") {
    if (state.status === 501) return { text: "NOT IMPLEMENTED", tone: "tone-stub" };
    return { text: "ERROR", tone: "tone-error" };
  }
  if (entry.status === "debate_only") return { text: "DEBATE-ONLY", tone: "tone-muted" };
  if (entry.status === "not_implemented") return { text: "NOT IMPLEMENTED", tone: "tone-stub" };
  return { text: "READY", tone: "tone-ready" };
}

export function AgentCard({ entry, state }: { entry: RosterEntry; state: CardState }) {
  const pill = statusPill(entry, state);

  return (
    <div className={`agent-card state-${state.kind}`}>
      <div className="agent-card-header">
        <div className="agent-card-title">
          <span className={`led ${pill.tone}`} aria-hidden="true" />
          <span className="agent-card-label">{entry.label}</span>
        </div>
        <span className={`pill ${pill.tone}`}>{pill.text}</span>
      </div>
      <div className="agent-card-model">{entry.model_tag}</div>

      {entry.status === "debate_only" && state.kind === "idle" && (
        <p className="agent-card-note">Runs only inside the multi-agent debate loop — not queryable standalone.</p>
      )}

      {state.kind === "error" && (
        <p className="agent-card-note agent-card-note--error">{state.message}</p>
      )}

      {state.kind === "done" && (
        <div className="agent-card-result">
          <div className="conviction-row">
            <span className="conviction-label">Conviction</span>
            <div className="conviction-bar">
              <div className="conviction-fill" style={{ width: `${(state.data.conviction / 10) * 100}%` }} />
            </div>
            <span className="conviction-value">{state.data.conviction.toFixed(1)}/10</span>
          </div>
          <p className="agent-card-reasoning">{state.data.reasoning}</p>
          {state.data.citations.length > 0 && (
            <ul className="citation-list">
              {state.data.citations.map((c, i) => (
                <li key={i}>
                  <span className="citation-source">{c.source}</span>
                  <span className="citation-excerpt">{c.excerpt}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
