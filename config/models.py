"""Per-agent model assignment.

The original AlphaAgents paper runs every agent role on GPT-4o — so its
"debate" is one model agreeing/disagreeing with itself in different voices.
Assigning different roles to different model families gives debate a real
chance to surface disagreement that isn't just prompt-induced role-play.
"""

from dataclasses import dataclass
from enum import Enum


class Provider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"


@dataclass(frozen=True)
class ModelConfig:
    provider: Provider
    model_id: str
    temperature: float = 0.2

    def as_run_tag(self) -> str:
        """Stable identifier logged with every run for reproducibility."""
        return f"{self.provider.value}:{self.model_id}:t{self.temperature}"


# Default assignment: heterogeneous across the three original roles, plus the
# new roles. Override per-experiment via `AGENT_MODELS` in a run config, not
# by editing this file, so a run's model assignment is always explicit and
# logged rather than implicit.
DEFAULT_AGENT_MODELS: dict[str, ModelConfig] = {
    "fundamental": ModelConfig(Provider.ANTHROPIC, "claude-sonnet-5"),
    "sentiment": ModelConfig(Provider.OPENAI, "gpt-5"),
    "valuation": ModelConfig(Provider.ANTHROPIC, "claude-sonnet-5"),
    "macro": ModelConfig(Provider.GOOGLE, "gemini-2.5-pro"),
    "verifier": ModelConfig(Provider.ANTHROPIC, "claude-opus-5"),
    "red_team": ModelConfig(Provider.OPENAI, "gpt-5"),
}
