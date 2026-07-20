import json
from collections.abc import Generator

import httpx

from app.core.config import settings
from app.core.exceptions import ProviderError

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


class LLMService:
    def __init__(self, api_key: str | None = None, provider: str | None = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.provider = provider or settings.LLM_PROVIDER

    def stream_completion(
        self,
        system_prompt: str,
        messages: list[dict],
        model: str,
        temperature: float,
        max_tokens: int = 1024,
    ) -> Generator[dict, None, None]:
        """
        Yields events as the response streams in:
          {"type": "delta", "text": "..."}                              — for each token chunk
          {"type": "usage", "input_tokens": N, "output_tokens": N}      — once, at the end

        Callers accumulate "delta" events for the visible response and use
        the final "usage" event for cost/analytics tracking (Module 7).
        """
        if self.provider == "ollama":
            yield from self._stream_ollama(system_prompt, messages, model, temperature)
        else:
            yield from self._stream_anthropic(system_prompt, messages, model, temperature, max_tokens)

    def complete(
        self, system_prompt: str, messages: list[dict], model: str, temperature: float
    ) -> dict:
        """Non-streaming convenience wrapper — collects the full stream, used for draft generation."""
        full_text = ""
        input_tokens = 0
        output_tokens = 0
        actual_model = model

        for event in self.stream_completion(system_prompt, messages, model, temperature):
            if event["type"] == "delta":
                full_text += event["text"]
            elif event["type"] == "usage":
                input_tokens = event["input_tokens"]
                output_tokens = event["output_tokens"]
                actual_model = event.get("model", model)

        return {
            "content": full_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": actual_model,
        }

    # --- Ollama (free, local) ---

    def _stream_ollama(
        self, system_prompt: str, messages: list[dict], model: str, temperature: float
    ) -> Generator[dict, None, None]:
        # employee.model may still hold an Anthropic-style name (e.g. from
        # before this swap) — fall back to the configured Ollama model
        # rather than sending a model name Ollama won't recognize.
        ollama_model = model if model and not model.startswith("claude") else settings.OLLAMA_MODEL

        payload = {
            "model": ollama_model,
            "messages": [{"role": "system", "content": system_prompt}, *messages],
            "options": {"temperature": temperature},
            "stream": True,
        }

        input_tokens = 0
        output_tokens = 0

        try:
            with httpx.stream(
                "POST", f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload, timeout=120.0
            ) as response:
                if response.status_code != 200:
                    raise ProviderError("ollama", response.read().decode(errors="replace"))

                for line in response.iter_lines():
                    if not line:
                        continue

                    event = json.loads(line)
                    text = event.get("message", {}).get("content", "")
                    if text:
                        yield {"type": "delta", "text": text}

                    if event.get("done"):
                        input_tokens = event.get("prompt_eval_count", 0)
                        output_tokens = event.get("eval_count", 0)

        except httpx.RequestError as exc:
            # Most common cause: Ollama isn't running (`ollama serve`) or
            # the model hasn't been pulled (`ollama pull <model>`).
            raise ProviderError(
                "ollama", f"{exc} (is Ollama running? try: ollama serve)"
            ) from exc

        yield {
            "type": "usage",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": ollama_model,
        }

    # --- Anthropic (paid) ---

    def _stream_anthropic(
        self, system_prompt: str, messages: list[dict], model: str, temperature: float, max_tokens: int
    ) -> Generator[dict, None, None]:
        if not self.api_key:
            raise ProviderError("anthropic", "ANTHROPIC_API_KEY is not configured")

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": messages,
            "stream": True,
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }

        input_tokens = 0
        output_tokens = 0

        try:
            with httpx.stream(
                "POST", ANTHROPIC_MESSAGES_URL, json=payload, headers=headers, timeout=60.0
            ) as response:
                if response.status_code != 200:
                    raise ProviderError("anthropic", response.read().decode(errors="replace"))

                for line in response.iter_lines():
                    if not line or not line.startswith("data:"):
                        continue

                    event = json.loads(line[len("data:") :].strip())
                    event_type = event.get("type")

                    if event_type == "content_block_delta":
                        text = event.get("delta", {}).get("text", "")
                        if text:
                            yield {"type": "delta", "text": text}

                    elif event_type == "message_start":
                        input_tokens = event.get("message", {}).get("usage", {}).get(
                            "input_tokens", 0
                        )

                    elif event_type == "message_delta":
                        output_tokens = event.get("usage", {}).get("output_tokens", 0)

        except httpx.RequestError as exc:
            raise ProviderError("anthropic", str(exc)) from exc

        yield {
            "type": "usage",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": model,
        }
