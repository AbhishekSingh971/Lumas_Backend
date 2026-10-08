from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from flask import current_app


class OpenAIService:

    def __init__(self):

        api_key = current_app.config.get(
            "OPENAI_API_KEY"
        )

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured"
            )

        self.client = OpenAI(
            api_key=api_key
        )

        self.default_model = current_app.config.get(
            "OPENAI_MODEL",
            "gpt-5"
        )

        self.temperature = current_app.config.get(
            "OPENAI_TEMPERATURE",
            0.7
        )

        self.max_tokens = current_app.config.get(
            "OPENAI_MAX_TOKENS",
            4000
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

        response = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=temperature
            if temperature is not None
            else self.temperature,
            max_completion_tokens=self.max_tokens,
        )

        return response

    def generate_response(
        self,
        messages: list,
        model: str | None = None,
    ):

        response = self.send_message(
            messages=messages,
            model=model,
        )

        return (
            response
            .choices[0]
            .message
            .content
        )

    def stream_response(
        self,
        messages: list,
        model: str | None = None,
    ):

        stream = self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            stream=True,
        )

        for chunk in stream:

            if (
                chunk.choices
                and chunk.choices[0].delta
                and chunk.choices[0].delta.content
            ):
                yield (
                    chunk.choices[0]
                    .delta
                    .content
                )

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
                        "You generate short "
                        "conversation titles."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )

        return title.strip()

    def count_tokens(
        self,
        text: str,
    ):
        """
        Temporary approximation.

        Later replace with tiktoken.
        """

        return max(
            1,
            len(text.split())
        )

    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
    ):
        """
        Placeholder.

        Will be connected to
        UsageRepository later.
        """

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": (
                prompt_tokens
                + completion_tokens
            ),
        }