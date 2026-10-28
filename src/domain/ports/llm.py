from abc import ABC, abstractmethod


class LLMPort(ABC):
    """Port for language model generation."""

    @abstractmethod
    def generate_answer(self, prompt: str) -> str:
        """Sends the assembled prompt to the LLM and returns the generated text."""
        pass
