import requests
import json
import logging
from typing import Generator, Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class LLMProvider:
    """Classe base para provedores de LLM."""
    def generate_stream(self, prompt: str, model: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        raise NotImplementedError

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def generate_stream(self, prompt: str, model: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "system": system_prompt
        }
        try:
            response = requests.post(url, json=payload, stream=True, timeout=(10, 300))
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    if "response" in chunk:
                        yield chunk["response"]
                    if chunk.get("done"):
                        break
        except Exception as e:
            logger.error(f"Erro no Ollama: {e}")
            yield f"[Erro Ollama: {str(e)}]"

class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def generate_stream(self, prompt: str, model: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/mane1334/KutsakAi-Web-Agent-Coder",
            "X-Title": "KutsakAI Web Agent",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, stream=True)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        chunk = json.loads(data_str)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
        except Exception as e:
            logger.error(f"Erro no OpenRouter: {e}")
            yield f"[Erro OpenRouter: {str(e)}]"

class NVIDIAProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://integrate.api.nvidia.com/v1/chat/completions"

    def generate_stream(self, prompt: str, model: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": 0.5,
            "top_p": 1,
            "max_tokens": 1024
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, stream=True)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        chunk = json.loads(data_str)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
        except Exception as e:
            logger.error(f"Erro na NVIDIA: {e}")
            yield f"[Erro NVIDIA: {str(e)}]"

class ProviderFactory:
    @staticmethod
    def get_provider(provider_name: str, config: Dict[str, Any]) -> LLMProvider:
        if provider_name.lower() == "ollama":
            return OllamaProvider(config.get("base_url", "http://localhost:11434"))
        elif provider_name.lower() == "openrouter":
            return OpenRouterProvider(config.get("api_key", ""))
        elif provider_name.lower() == "nvidia":
            return NVIDIAProvider(config.get("api_key", ""))
        else:
            raise ValueError(f"Provedor desconhecido: {provider_name}")
