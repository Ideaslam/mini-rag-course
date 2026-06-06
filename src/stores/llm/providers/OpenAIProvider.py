from ..LLMInterface import LLMInterface
from openai import OpenAI


class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str,api_url: str=None,default_input_max_characters: int=1000,default_output_max_characters: int=1000,default_temperature: float=1.0):
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_characters = default_output_max_characters
        self.default_temperature = default_temperature

    def set_generation_model(self, model_id: str):
        self.generation_model = model_id

    def set_embedding_model(self, model_id: str):
        self.embedding_model = model_id

    def generate_text(self, prompt: str, max_output_tokens: int, temperature: float = None) -> str:
        client = OpenAI()
        response = client.chat.completions.create(
            model=self.generation_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_output_tokens,
            temperature=temperature if temperature is not None else 1.0,
        )
        return response.choices[0].message.content.strip()

    def embed_text(self, text: str):
        client = OpenAI()
        response = client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str):
        return [{"role": role, "content": prompt}]
   