"""Per-agent model assignment.

The original AlphaAgents paper runs every agent role on GPT-4o — so its
"debate" is one model agreeing/disagreeing with itself in different voices.
This project uses open-weight models served locally via Ollama
(https://ollama.com) instead of a closed API:

- Genuine model heterogeneity: different agent roles run on different model
  *families* (Llama, Mistral, Qwen, Gemma, DeepSeek), not just different
  prompts on top of one vendor's model.
- Free and fully reproducible: no API cost, no silent model-version drift
  out of your control.

Requires Ollama running locally (`ollama serve`) with each assigned model
pulled (`ollama pull <model_id>`).
"""

from dataclasses import dataclass
from enum import Enum


class Provider(str, Enum):
    OLLAMA = "ollama"


@dataclass(frozen=True)
class ModelConfig:
    provider: Provider
    model_id: str
    temperature: float = 0.2

    def as_run_tag(self) -> str:
        """Stable identifier logged with every run for reproducibility."""
        return f"{self.provider.value}:{self.model_id}:t{self.temperature}"


# Default assignment: heterogeneous across model families. Override
# per-experiment via a run config rather than editing this file, so a run's
# model assignment is always explicit and logged rather than implicit.
DEFAULT_AGENT_MODELS: dict[str, ModelConfig] = {
    "fundamental": ModelConfig(Provider.OLLAMA, "qwen2.5:14b"),
    "sentiment": ModelConfig(Provider.OLLAMA, "mistral:7b"),
    "valuation": ModelConfig(Provider.OLLAMA, "llama3.1:8b"),
    "macro": ModelConfig(Provider.OLLAMA, "gemma2:9b"),
    "verifier": ModelConfig(Provider.OLLAMA, "deepseek-r1:14b"),
    "red_team": ModelConfig(Provider.OLLAMA, "mixtral:8x7b"),
}
