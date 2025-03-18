from urllib import response
from ..llm_interface import LLMInterface
from typing import Optional
from openai import OpenAI
import logging
from ..llm_enums import OpenAiEnums


class OpenaiProvider(LLMInterface):

    def __init__(self, api_key: str, api_url: Optional[str] = None,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):
        super().__init__()
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url

        )
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, max_output_tokens: Optional[int] = None, temperature: Optional[float] = None, chat_history: list = []):
        if not self.client:
            self.logger.error('OpenAi Client was not not set')
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for openai was not set")
            return None
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        chat_history.append(self.construct_prompt(
            prompt, OpenAiEnums.USER.value))
        response = self.client.chat.completions.create(
            model=self.generation_model_id, messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error While Generating")
            return None
        return response.choices[0].message.content

    def embed_text(self, text: str, document_type: Optional[str] = None):
        if not self.client:
            self.logger.error('OpenAi Client was not not set')
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model for openai was not set")
            return None
        response = self.client.embeddings.create(
            model=self.embedding_model_id, input=text
        )
        # just Validation
        if not response or response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error While Embed with openai")
            return None
        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str):

        return {
            "role": role,
            "content": self.process_text(prompt)
        }
