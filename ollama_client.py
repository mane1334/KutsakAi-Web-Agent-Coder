"""Cliente para interação com o Ollama."""

import os
import requests
import logging
import json
import time
from typing import List, Optional, Dict, Any, Callable, Generator
from functools import wraps
from enum import Enum

# Importa os novos sistemas
from config_manager import get_config
from logger import get_logger, monitor_performance, LogContext
from cache_system import get_cache, cache_get_or_compute
from llm_providers import ProviderFactory

# ============================================================================
# STANDARDIZED ERROR CLASSES
# ============================================================================

class OllamaError(Exception):
    """Base exception class for all Ollama-related errors."""
    def __init__(self, message: str, error_code: Optional[str] = None, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.original_error = original_error
    
    def __str__(self):
        base_msg = self.message
        if self.error_code:
            base_msg = f"[{self.error_code}] {base_msg}"
        return base_msg

class OllamaConnectionError(OllamaError):
    """Raised when cannot connect to Ollama service."""
    def __init__(self, message: str = "Unable to connect to Ollama service", original_error: Optional[Exception] = None):
        super().__init__(message, "CONNECTION_ERROR", original_error)

class OllamaTimeoutError(OllamaError):
    """Raised when Ollama request times out."""
    def __init__(self, message: str = "Ollama request timed out", original_error: Optional[Exception] = None):
        super().__init__(message, "TIMEOUT_ERROR", original_error)

class OllamaModelError(OllamaError):
    """Raised when there's an issue with the specified model."""
    def __init__(self, message: str, model: str, original_error: Optional[Exception] = None):
        super().__init__(f"Model '{model}': {message}", "MODEL_ERROR", original_error)
        self.model = model

class OllamaResponseError(OllamaError):
    """Raised when Ollama returns an error response."""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, "RESPONSE_ERROR", original_error)

class OllamaStreamError(OllamaError):
    """Raised when there's an error during streaming."""
    def __init__(self, message: str = "Error during streaming", original_error: Optional[Exception] = None):
        super().__init__(message, "STREAM_ERROR", original_error)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações (immutable)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_MODELS_URL = f"{OLLAMA_BASE_URL}/api/tags"
OLLAMA_PULL_URL = f"{OLLAMA_BASE_URL}/api/pull"
OLLAMA_MODEL = "codellama"

# System prompt padrão
DEFAULT_SYSTEM_PROMPT = """You are an expert Web Agent specialized in creating modern, high-performance, and visually stunning websites.

CORE RULES:
1. ONLY USE HTML, CSS AND JAVASCRIPT.
2. ALWAYS PROVIDE THE RESPONSE AS A SINGLE, COMPLETE HTML FILE.
3. MAKE IT FULLY RESPONSIVE (Mobile-First).
4. USE MODERN DESIGN SYSTEMS (Glassmorphism, Neumorphism, Minimalist, or Bold Modern).

FRAMEWORKS & LIBRARIES:
- Always include TailwindCSS: <script src="https://cdn.tailwindcss.com"></script>
- Use Lucide Icons or FontAwesome for iconography.
- Use Google Fonts (Inter, Poppins, or Roboto).
- For animations, use Framer Motion (via script) or AOS (Animate On Scroll).

DESIGN GUIDELINES:
- Clean typography and generous whitespace.
- Vibrant gradients and subtle shadows.
- Interactive elements with smooth transitions.
- Dark mode support by default or as a toggle.
- High accessibility standards (WCAG).

OUTPUT FORMAT:
Return only the HTML code within a single file. No explanations unless requested."""

def prepare_file_context(files: Dict[str, str]) -> str:
    """Prepara o contexto dos arquivos para o Ollama.
    
    Args:
        files: Dicionário com {caminho_arquivo: conteúdo}
    """
    context = []
    for filepath, content in files.items():
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1]
        file_type = {
            '.html': 'HTML',
            '.css': 'CSS',
            '.js': 'JavaScript'
        }.get(ext.lower(), 'Código')
        
        context.append(f"\n=== Arquivo {filename} ({file_type}) ===\n{content}\n")
    
    return "\n".join(context)

def generate_code(prompt: str, model: str = OLLAMA_MODEL, system_prompt: Optional[str] = None, 
                 context_files: Optional[Dict[str, str]] = None, session: Optional[requests.Session] = None,
                 on_chunk: Optional[Callable[[str], None]] = None, 
                 on_progress: Optional[Callable[[int], None]] = None,
                 stream: bool = False, **kwargs) -> str:
    """Generate code using the Ollama model without streaming (backward compatible).
    
    Args:
        prompt: The prompt to generate code from
        model: The model to use for generation
        system_prompt: System prompt (legacy parameter, ignored in new implementation)
        context_files: Context files (legacy parameter, ignored in new implementation) 
        session: Request session (legacy parameter, ignored in new implementation)
        on_chunk: Callback for chunks (legacy parameter, used if provided)
        on_progress: Callback for progress (legacy parameter, used if provided)
        stream: Stream mode (legacy parameter, ignored - always uses streaming internally)
        **kwargs: Additional legacy parameters (ignored)
    
    Returns:
        str: The concatenated generated code from the model response
    
    Raises:
        OllamaError: Any error related to Ollama response handling
    """
    # Handle legacy context files by incorporating them into the prompt
    if context_files:
        file_context = prepare_file_context(context_files)
        prompt = f"""
Contexto dos arquivos existentes:
{file_context}

Com base no contexto acima, {prompt}
"""
    
    # Collect chunks and call callbacks if provided
    chunks = []
    chunk_count = 0
    
    try:
        for chunk in generate_code_stream(prompt, model):
            chunks.append(chunk)
            chunk_count += 1
            
            # Call legacy callbacks if provided
            if on_chunk:
                on_chunk(chunk)
            
            if on_progress:
                # Rough progress estimation based on chunk count
                progress = min(95, chunk_count * 2)
                on_progress(progress)
        
        # Final progress callback
        if on_progress:
            on_progress(100)
            
        return ''.join(chunks)
        
    except Exception as e:
        # For backward compatibility, return error message instead of raising
        error_msg = f"[Erro: {str(e)}]"
        if on_chunk:
            on_chunk(error_msg)
        return error_msg


def generate_code_with_retry(prompt: str, model: str = OLLAMA_MODEL, max_retries: int = 3, base_delay: float = 1.0) -> str:
    """Generate code with automatic retry and exponential backoff.
    
    Args:
        prompt: The prompt to generate code from
        model: The model to use for generation
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds for exponential backoff
        
    Returns:
        str: Generated code or error message
        
    Raises:
        OllamaError: When all retries are exhausted or non-retryable error occurs
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                delay = base_delay * (2 ** (attempt - 1))
                logger.info(f"Attempt {attempt + 1}/{max_retries + 1} after {delay}s delay")
                time.sleep(delay)
                
            # Use the streaming function directly to get proper exception handling
            result_chunks = list(generate_code_stream(prompt, model))
            return ''.join(result_chunks)
            
        except (OllamaConnectionError, OllamaTimeoutError) as e:
            last_exception = e
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries:
                break
                
        except OllamaError as e:
            # For other Ollama errors, don't retry
            logger.error(f"Non-retryable Ollama error: {e}")
            raise e
    
    logger.error(f"All {max_retries + 1} attempts failed")
    raise OllamaConnectionError(f"Maximum retries exceeded. Last error: {str(last_exception)}", last_exception)

def generate_code_stream(prompt: str, model: str = OLLAMA_MODEL) -> Generator[str, None, None]:
    """Generate code using the active provider with streaming support."""
    try:
        config_data = get_config("providers", {})
        active_provider = config_data.get("active", "ollama")
        provider_config = config_data.get(active_provider, {})
        
        provider = ProviderFactory.get_provider(active_provider, provider_config)
        
        logger.info(f"Starting streaming request using provider {active_provider} and model {model}")
        
        for chunk in provider.generate_stream(prompt, model, system_prompt=DEFAULT_SYSTEM_PROMPT):
            yield chunk
            
    except Exception as e:
        logger.error(f"Erro na geração de código: {e}")
        yield f"[Erro: {str(e)}]"

def list_models(session: Optional[requests.Session] = None) -> List[str]:
    """Lista os modelos disponíveis no Ollama.
    
    Args:
        session: Optional session to use for the request
    """
    try:
        session = session or requests.Session()
        response = session.get(OLLAMA_MODELS_URL)
        response.raise_for_status()
        models = [m["name"] for m in response.json().get("models", [])]
        return models or [OLLAMA_MODEL]
    except:
        logger.error("Erro ao listar modelos, usando modelo padrão")
        return [OLLAMA_MODEL]
