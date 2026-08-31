"""
Groq LLM Client

Provides a simple interface to the Groq API
for generating responses from retrieved context.
"""

from functools import lru_cache

from groq import Groq

from core.config import settings
from core.logger import logger


class GroqClient:
    """
    Client wrapper for Groq Chat Completions API.
    """

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.model = settings.GROQ_MODEL

        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        logger.success(
            f"Groq client initialized with model: {self.model}"
        )

    # ======================================================
    # Generate Response
    # ======================================================

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate a response using the Groq LLM.
        """

        if not user_prompt.strip():
            raise ValueError(
                "User prompt cannot be empty."
            )

        try:

            response = self.client.chat.completions.create(
                    model=self.model,

                    messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                    ],

                    temperature=temperature,

                    max_completion_tokens=max_tokens,

                    reasoning_effort="low",
        )

            answer = response.choices[0].message.content

            if not answer:
                raise RuntimeError(
                    "Groq returned an empty response."
                )

            logger.success(
                "Groq response generated successfully."
            )

            return answer.strip()

        except Exception as exc:

            logger.exception(
                f"Groq generation failed: {exc}"
            )

            raise


# ==========================================================
# Singleton
# ==========================================================

@lru_cache
def get_groq_client() -> GroqClient:
    """
    Return cached Groq client.
    """

    return GroqClient()


groq_client = get_groq_client()