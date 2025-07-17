import os
import time
import logging
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Third-party SDKs
try:
    import openai  # type: ignore
except ImportError:  # pragma: no cover
    openai = None  # type: ignore

try:
    import anthropic  # type: ignore
except ImportError:  # pragma: no cover
    anthropic = None  # type: ignore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LLMClient(BaseModel):
    """Unified client for OpenAI & Anthropic chat LLMs."""

    provider: str = "openai"
    model: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 150
    max_retries: int = 3

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
        # underscore_attrs_are_private = True  # Removed in Pydantic V2

    def __init__(self, **data):
        super().__init__(**data)
        self.provider = self.provider.lower()

        # Resolve API keys & models
        if self.provider == "openai":
            self.api_key = self.api_key or os.getenv("OPENAI_API_KEY")
            if openai is None:
                raise ImportError("openai package is required for OpenAI provider")
            # Create OpenAI client with new v1.0+ syntax
            self._openai_client = openai.OpenAI(api_key=self.api_key)
            self.model = self.model or os.getenv("DEFAULT_MODEL", "gpt-4-turbo")
        elif self.provider == "anthropic":
            self.api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
            if anthropic is None:
                raise ImportError("anthropic package is required for Anthropic provider")
            self._anthropic_client = anthropic.Anthropic(api_key=self.api_key)
            # Allow overriding the default Anthropic model via environment variables, mirroring
            # the behaviour we already provide for OpenAI models.  This lets users supply a
            # model they have access to (e.g. "claude-3-haiku-20240307" or "claude-3-opus-20240229")
            # without needing to touch the code.  If no override is provided we fall back to the
            # widely-available & inexpensive Haiku tier instead of Sonnet to maximise compatibility.
            self.model = (
                self.model
                or os.getenv("ANTHROPIC_MODEL")
                or os.getenv("DEFAULT_MODEL")
                or "claude-3-haiku-20240307"
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def generate_action(self, prompt: str) -> str:
        """Generate a single action string from *prompt*.

        For simple strategies (base / few_shot) we expect the model to reply
        with a single-line action. For reflection we allow multi-line answers
        (reasoning + action). Therefore we return the *entire* response and
        let the caller perform any necessary post-processing.
        """
        if self.provider == "openai":
            raw = self._call_openai(prompt)
        elif self.provider == "anthropic":
            raw = self._call_anthropic(prompt)
        else:  # pragma: no cover — should never reach here due to __init__ validation
            raise ValueError(f"Unsupported provider {self.provider}")

        return raw.strip()  # Caller (e.g., AndroidAgent) will parse

    # ------------------------------------------------------------------
    # Internal provider calls with retry / exponential backoff
    # ------------------------------------------------------------------
    def _call_openai(self, prompt: str) -> str:  # pragma: no cover (difficult to unit test)
        for attempt in range(1, self.max_retries + 1):
            try:
                # Updated for OpenAI v1.0+ API
                response = self._openai_client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return response.choices[0].message.content
            except Exception as exc:  # noqa: BLE001  # Broad catch acceptable for retries
                self._log_retry("OpenAI", exc, attempt)
        raise RuntimeError("OpenAI API failed after maximum retries")

    def _call_anthropic(self, prompt: str) -> str:  # pragma: no cover
        for attempt in range(1, self.max_retries + 1):
            try:
                completion = self._anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}],
                )
                return completion.content[0].text
            except Exception as exc:  # noqa: BLE001
                self._log_retry("Anthropic", exc, attempt)
        raise RuntimeError("Anthropic API failed after maximum retries")

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def _log_retry(self, provider: str, exc: Exception, attempt: int) -> None:
        wait = 2 ** (attempt - 1)
        logger.warning(
            "%s API error on attempt %d/%d: %s – retrying in %ds",
            provider,
            attempt,
            self.max_retries,
            exc,
            wait,
        )
        time.sleep(wait)