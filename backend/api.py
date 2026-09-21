"""Local HTTP API for the Electron frontend.

Binds to 127.0.0.1 only and is spawned automatically by the Electron main
process (frontend/electron/main.cjs) — the user never runs `uvicorn` by
hand. No auth: this is a single-user local research tool, not a hosted
service, so there's no boundary here worth protecting with one.
"""

from datetime import date

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.fundamental import FundamentalAgent
from agents.llm_client import ModelCallError
from agents.macro import MacroAgent
from agents.sentiment import SentimentAgent
from agents.single_agent_control import SingleAgentControl
from agents.valuation import ValuationAgent
from config.models import DEFAULT_AGENT_MODELS
from config.risk_profiles import ALL_PROFILES

load_dotenv()  # env vars are only read lazily inside agent calls, not at import time

app = FastAPI(title="AlphaAgentsV2 backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static roster metadata — status reflects the real implementation state
# documented in DESIGN.md, not something derived at runtime, so the
# frontend never has to guess.
ROSTER = [
    {"role": "fundamental", "label": "Fundamental", "status": "ready"},
    {"role": "sentiment", "label": "Sentiment", "status": "ready"},
    {"role": "valuation", "label": "Valuation", "status": "ready"},
    {"role": "macro", "label": "Macro", "status": "not_implemented"},
    {"role": "verifier", "label": "Verifier", "status": "debate_only"},
    {"role": "red_team", "label": "Red Team", "status": "debate_only"},
]

ANALYZABLE_AGENTS = {
    "fundamental": FundamentalAgent,
    "sentiment": SentimentAgent,
    "valuation": ValuationAgent,
    "macro": MacroAgent,
    "single_agent_control": SingleAgentControl,
}


class AnalyzeRequest(BaseModel):
    ticker: str
    role: str
    risk_profile: str = "risk_neutral"
    as_of: str | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/roster")
def roster() -> list[dict]:
    return [{**entry, "model_tag": DEFAULT_AGENT_MODELS[entry["role"]].as_run_tag()} for entry in ROSTER]


@app.post("/analyze")
def analyze(req: AnalyzeRequest) -> dict:
    if req.role not in ANALYZABLE_AGENTS:
        raise HTTPException(status_code=400, detail=f"Unknown or non-queryable role: {req.role}")
    if req.risk_profile not in ALL_PROFILES:
        raise HTTPException(status_code=400, detail=f"Unknown risk profile: {req.risk_profile}")
    if not req.ticker.strip():
        raise HTTPException(status_code=400, detail="ticker is required")

    as_of = date.fromisoformat(req.as_of) if req.as_of else date.today()
    agent_cls = ANALYZABLE_AGENTS[req.role]
    model_config = DEFAULT_AGENT_MODELS.get(req.role, DEFAULT_AGENT_MODELS["valuation"])
    agent = agent_cls(model_config=model_config, risk_profile=ALL_PROFILES[req.risk_profile])

    try:
        result = agent.analyze(req.ticker.strip().upper(), as_of)
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc) or "Not implemented yet") from exc
    except ModelCallError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result.to_dict()
