
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)
from flask import current_app


class OpenAIService:

    def __init__(self):
        api_key = current_app.config.get("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured"
            )

        # OpenRouter-compatible OpenAI client
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

        self.default_model = current_app.config.get(
            "OPENAI_MODEL",
            "openai/gpt-5",
        )

        self.temperature = current_app.config.get(
            "OPENAI_TEMPERATURE",
            0.7,
        )

        self.max_tokens = current_app.config.get(
            "OPENAI_MAX_TOKENS",
            4000,
        )

    def build_messages(
        self,
        system_prompt: str,
        context: list,
    ):
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]
        messages.extend(context)
        return messages

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(
            multiplier=1,
            min=2,
            max=10,
        ),
    )
    def send_message(
        self,
        messages: list,
        model: str | None = None,
        temperature: float | None = None,
    ):
        return self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=(
                temperature
                if temperature is not None
                else self.temperature
            ),
            max_tokens=self.max_tokens,
        )

    def generate_response(
        self,
        messages: list,
        model: str | None = None,
    ):
        response = self.send_message(
            messages=messages,
            model=model,
        )

        content = response.choices[0].message.content
        return content or ""

    def stream_response(
        self,
        messages: list,
        model: str | None = None,
    ):
        stream = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            stream=True,
            max_tokens=self.max_tokens,
        )

        for chunk in stream:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                yield content

    def generate_title(
        self,
        first_message: str,
    ):
        prompt = f"""
Generate a short conversation title.

User message:
{first_message}

Rules:
- Maximum 6 words
- No punctuation
- No quotes
- Title case
"""

        title = self.generate_response(
            [
                {
                    "role": "system",
                    "content": (
                        "You generate short conversation titles."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )

        return title.strip()

    def count_tokens(self, text: str):
        # Approximation; replace with a tokenizer later.
        return max(1, len(text.split()))

    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
    ):
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": (
                prompt_tokens + completion_tokens
            ),
        }
