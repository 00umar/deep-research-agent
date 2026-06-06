"""
Multi-provider LLM client with automatic fallback.

Priority order: Gemini → Cerebras → Groq fast → Groq quality
- gemini (gemini-2.0-flash): 1M TPM free tier, primary workhorse
- cerebras (gpt-oss-120b): fast inference, first fallback
- groq-fast (llama-3.1-8b-instant): 30K TPM, second fallback
- groq-quality (llama-3.3-70b-versatile): 12K TPM, last resort
- 5s minimum gap between calls prevents burst rate limiting
- If all rate-limited, waits 65s then retries from the top
"""

import os
import time
from openai import OpenAI, RateLimitError, BadRequestError, NotFoundError
from loguru import logger

PROVIDERS = [
    {
        "name": "gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "key_env": "GEMINI_API_KEY",
        "model": "gemini-2.0-flash",        # 1M TPM free tier — primary workhorse
    },
    {
        "name": "cerebras",
        "base_url": "https://api.cerebras.ai/v1",
        "key_env": "CEREBRAS_API_KEY",
        "model": "gpt-oss-120b",
    },
    {
        "name": "groq-fast",
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "model": "llama-3.1-8b-instant",   # 30K TPM
    },
    {
        "name": "groq-quality",
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "model": "llama-3.3-70b-versatile",  # 12K TPM — last resort
    },
]

# Minimum seconds between LLM API calls to avoid burst rate limiting.
# At ~2500 tokens/call, groq-fast's 30K TPM allows ~12 calls/min → need ≥5s gap.
MIN_CALL_INTERVAL = 6.0  # 10 RPM — keeps Gemini (15 RPM limit) from rate limiting under load


class LLMClient:
    """Tries providers in order. Switches automatically on rate limits."""

    def __init__(self):
        self._clients: dict[str, OpenAI] = {}
        for p in PROVIDERS:
            key = os.getenv(p["key_env"])
            if key:
                self._clients[p["name"]] = OpenAI(api_key=key, base_url=p["base_url"])
                logger.debug(f"LLMClient: {p['name']} ready")
            else:
                logger.warning(f"LLMClient: {p['name']} skipped — {p['key_env']} not found in .env")

        if not self._clients:
            raise RuntimeError("No LLM providers configured. Add GEMINI_API_KEY, GROQ_API_KEY, or CEREBRAS_API_KEY to .env")

        self.active_provider: str = next(iter(self._clients))
        self._last_call_time: float = 0.0

    @property
    def _available(self) -> list[dict]:
        return [p for p in PROVIDERS if p["name"] in self._clients]

    def complete(self, messages: list, tools: list = None, tool_choice: str = "auto") -> tuple:
        """
        Send a completion. Returns (response, provider_name).
        Automatically falls back to next provider on rate limit.
        Retries with backoff on tool_use_failed before switching providers.
        """
        # Enforce minimum gap between calls to avoid burst rate limiting
        elapsed = time.time() - self._last_call_time
        if elapsed < MIN_CALL_INTERVAL:
            time.sleep(MIN_CALL_INTERVAL - elapsed)
        self._last_call_time = time.time()

        for wait_round in range(20):
            for provider in self._available:
                result = self._try_provider(provider, messages, tools, tool_choice)
                if result is not None:
                    self.active_provider = provider["name"]
                    self._last_call_time = time.time()
                    return result, provider["name"]

            logger.warning(f"All providers rate limited. Waiting 65s (round {wait_round + 1}/20)...")
            time.sleep(65)

        raise RuntimeError("All LLM providers exhausted after retries. Check API keys and quota.")

    def _try_provider(self, provider: dict, messages: list, tools: list, tool_choice: str):
        """
        Try one provider. Returns response on success, None if rate-limited.
        Retries internally on tool_use_failed.
        """
        if provider["name"] not in self._clients:
            return None
        client = self._clients[provider["name"]]
        tool_fail_count = 0

        while True:
            try:
                kwargs = {
                    "model": provider["model"],
                    "messages": messages,
                    "parallel_tool_calls": False,
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = tool_choice

                return client.chat.completions.create(**kwargs)

            except RateLimitError:
                logger.warning(f"{provider['name']} rate limited — switching to next provider")
                return None

            except BadRequestError as e:
                if "tool_use_failed" in str(e):
                    tool_fail_count += 1
                    if tool_fail_count >= 4:
                        logger.warning(f"{provider['name']}: persistent tool_use_failed — switching provider")
                        return None
                    wait = 10 * tool_fail_count  # 10s → 20s → 30s
                    logger.warning(f"Tool format glitch on {provider['name']}, retrying in {wait}s ({tool_fail_count}/3)...")
                    time.sleep(wait)
                else:
                    raise

            except NotFoundError as e:
                logger.error(f"{provider['name']}: model not found — {e}. Permanently disabling.")
                self._clients.pop(provider["name"], None)
                return None

            except Exception as e:
                if hasattr(e, "status_code") and e.status_code == 413:
                    logger.warning(f"{provider['name']}: request too large (413) — switching provider")
                    return None
                raise
