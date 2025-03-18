from enum import Enum

class LLMEnums(Enum):
    OPENAI="OPENAI"
    COHERE="COHERE"

class OpenAiEnums(Enum):
    SYSTEM="system"
    USER="user"
    ASSISTANT="assistant"