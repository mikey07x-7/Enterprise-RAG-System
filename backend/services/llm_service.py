"""
LLM Service

Handles communication with the Groq API
for Retrieval-Augmented Generation.
"""

from functools import lru_cache

from groq import Groq

from core.config import settings
from core.logger import logger


class LLMService:
    """
    Handles interaction with the Groq LLM.
    """

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        # Keep the model configurable.
        self.model = "openai/gpt-oss-20b"

        logger.success(
            f"Groq LLM initialized: {self.model}"
        )

    # ======================================================
    # Generate Answer
    # ======================================================

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> str:
        """
        Generate a response using Groq.
        """

        messages = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        try:

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            answer = response.choices[0].message.content

            if not answer:
                raise RuntimeError(
                    "Groq returned an empty response."
                )

            return answer.strip()

        except Exception as exc:

            logger.exception(
                f"Groq generation failed: {exc}"
            )

            raise


@lru_cache
def get_llm_service() -> LLMService:
    """
    Return cached LLM service instance.
    """

    return LLMService()


llm_service = get_llm_service()