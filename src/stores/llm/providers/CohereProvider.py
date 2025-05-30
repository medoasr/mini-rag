from ...llm_interface import LLMInterface
from typing import Optional
import logging
from ...llm_enums import CohereEnums, DocumentType
import cohere


class CohereProvider(LLMInterface):
    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):
        super().__init__()
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)
        self.enums = CohereEnums
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
            self.logger.error('Cohere Client was not not set')
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for Chohere was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(self.construct_prompt(
            prompt, CohereEnums.USER.value))

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message=self.process_text(prompt),
            temperature=temperature,
            max_tokens=max_output_tokens
        )

        if not response or not response.text:
            self.logger.error("Error While Generating")
            return None
        return response.text

    def embed_text(self, text: str, document_type: Optional[str] = None):
        if not self.client:
            self.logger.error('Cohere Client was not not set')
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Cohere was not set")
            return None

        input_type = CohereEnums.DOCUMENT
        if document_type == DocumentType.QUERY:
            input_type = CohereEnums.QUERY
        response = self.client.embed(
            model=self.embedding_model_id,
            input_type=input_type,
            texts=[self.process_text(text)],
            embedding_types=['float']
        )
        # just Validation
        if not response or not response.embeddings or not isinstance(response.embeddings, list):
            self.logger.error("Error While Embedding with Cohere")
            return None
        return response.embeddings[0]

    def construct_prompt(self, prompt: str, role: str):

        return {
            "role": role,
            "content": self.process_text(prompt)
        }
