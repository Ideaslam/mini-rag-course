from enum import Enum


class LLMModelEnum(Enum):
    OPENAI="openai"
    ANTHROPIC="anthropic"
    GOOGLE="google"
    COHERE="cohere"
    HUGGINGFACE="huggingface"
    MOONBEAM="moonbeam"