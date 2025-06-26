"""Unit tests for the refactored ollama_client with streaming support."""

import json
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Import the client and error classes
from ollama_client import (
    generate_code_stream,
    generate_code, 
    generate_code_with_retry,
    OllamaError,
    OllamaConnectionError,
    OllamaTimeoutError,
    OllamaModelError,
    OllamaResponseError,
    OllamaStreamError
)


class TestOllamaErrors:
    """Test standardized error classes."""
    
    def test_ollama_error_base(self):
        """Test base OllamaError class."""
        error = OllamaError("Test message", "TEST_CODE", Exception("Original"))
        assert str(error) == "[TEST_CODE] Test message"
        assert error.message == "Test message"
        assert error.error_code == "TEST_CODE"
        assert isinstance(error.original_error, Exception)
    
    def test_ollama_error_no_code(self):
        """Test OllamaError without error code."""
        error = OllamaError("Test message")
        assert str(error) == "Test message"
        assert error.error_code is None
    
    def test_ollama_connection_error(self):
        """Test OllamaConnectionError."""
        error = OllamaConnectionError()
        assert "Unable to connect to Ollama service" in str(error)
        assert error.error_code == "CONNECTION_ERROR"
    
    def test_ollama_timeout_error(self):
        """Test OllamaTimeoutError."""
        error = OllamaTimeoutError()
        assert "Ollama request timed out" in str(error)
        assert error.error_code == "TIMEOUT_ERROR"
    
    def test_ollama_model_error(self):
        """Test OllamaModelError."""
        error = OllamaModelError("not found", "test-model")
        assert "Model 'test-model': not found" in str(error)
        assert error.error_code == "MODEL_ERROR"
        assert error.model == "test-model"
    
    def test_ollama_response_error(self):
        """Test OllamaResponseError."""
        error = OllamaResponseError("Bad response")
        assert "Bad response" in str(error)
        assert error.error_code == "RESPONSE_ERROR"
    
    def test_ollama_stream_error(self):
        """Test OllamaStreamError."""
        error = OllamaStreamError()
        assert "Error during streaming" in str(error)
        assert error.error_code == "STREAM_ERROR"


class TestGenerateCodeStream:
    """Test the generate_code_stream function."""
    
    @patch('ollama_client.requests.post')
    def test_successful_streaming(self, mock_post):
        """Test successful streaming response."""
        # Mock successful streaming response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = [
            b'{"response": "def ", "done": false}',
            b'{"response": "hello():", "done": false}',
            b'{"response": "\\n    return \\"Hello\\"", "done": true}'
        ]
        mock_post.return_value = mock_response
        
        # Test streaming
        chunks = list(generate_code_stream("Create a hello function"))
        
        # Verify results
        assert len(chunks) == 3
        assert chunks[0] == "def "
        assert chunks[1] == "hello():"
        assert chunks[2] == "\n    return \"Hello\""
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['stream'] is True
        assert 'prompt' in call_args[1]['json']
        assert 'model' in call_args[1]['json']
    
    @patch('ollama_client.requests.post')
    def test_empty_chunks_filtered(self, mock_post):
        """Test that empty response chunks are filtered out."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = [
            b'{"response": "", "done": false}',  # Empty response
            b'{"response": "code", "done": false}',
            b'{"response": "", "done": true}'  # Empty final response
        ]
        mock_post.return_value = mock_response
        
        chunks = list(generate_code_stream("test"))
        
        # Only non-empty chunks should be yielded
        assert len(chunks) == 1
        assert chunks[0] == "code"
    
    @patch('ollama_client.requests.post')
    def test_connection_error(self, mock_post):
        """Test connection error handling."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(OllamaConnectionError) as exc_info:
            list(generate_code_stream("test"))
        
        assert exc_info.value.error_code == "CONNECTION_ERROR"
        assert isinstance(exc_info.value.original_error, requests.exceptions.ConnectionError)
    
    @patch('ollama_client.requests.post')
    def test_timeout_error(self, mock_post):
        """Test timeout error handling."""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(OllamaTimeoutError) as exc_info:
            list(generate_code_stream("test"))
        
        assert exc_info.value.error_code == "TIMEOUT_ERROR"
        assert isinstance(exc_info.value.original_error, requests.exceptions.Timeout)
    
    @patch('ollama_client.requests.post')
    def test_model_not_found_error(self, mock_post):
        """Test model not found error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "model not found"
        
        http_error = requests.exceptions.HTTPError("404 Client Error")
        http_error.response = mock_response
        mock_post.side_effect = http_error
        
        with pytest.raises(OllamaModelError) as exc_info:
            list(generate_code_stream("test", "nonexistent-model"))
        
        assert exc_info.value.error_code == "MODEL_ERROR"
        assert exc_info.value.model == "nonexistent-model"
    
    @patch('ollama_client.requests.post')
    def test_http_error_other(self, mock_post):
        """Test other HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        
        http_error = requests.exceptions.HTTPError("500 Server Error")
        http_error.response = mock_response
        mock_post.side_effect = http_error
        
        with pytest.raises(OllamaResponseError) as exc_info:
            list(generate_code_stream("test"))
        
        assert exc_info.value.error_code == "RESPONSE_ERROR"
        assert "HTTP 500" in str(exc_info.value)
    
    @patch('ollama_client.requests.post')
    def test_response_error_in_stream(self, mock_post):
        """Test error reported in streaming response."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = [
            b'{"error": "Model failed to generate response"}'
        ]
        mock_post.return_value = mock_response
        
        with pytest.raises(OllamaResponseError) as exc_info:
            list(generate_code_stream("test"))
        
        assert "Model failed to generate response" in str(exc_info.value)
    
    @patch('ollama_client.requests.post')
    def test_invalid_json_in_stream(self, mock_post):
        """Test invalid JSON in streaming response."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = [
            b'invalid json content'
        ]
        mock_post.return_value = mock_response
        
        with pytest.raises(OllamaStreamError) as exc_info:
            list(generate_code_stream("test"))
        
        assert "Invalid JSON in response" in str(exc_info.value)
    
    @patch('ollama_client.requests.post')
    def test_network_error_during_streaming(self, mock_post):
        """Test network error during streaming."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.side_effect = requests.exceptions.RequestException("Network error")
        mock_post.return_value = mock_response
        
        with pytest.raises(OllamaStreamError) as exc_info:
            list(generate_code_stream("test"))
        
        assert "Network error during streaming" in str(exc_info.value)
    
    @patch('ollama_client.requests.post')
    def test_unexpected_error(self, mock_post):
        """Test unexpected error handling."""
        mock_post.side_effect = RuntimeError("Unexpected error")
        
        with pytest.raises(OllamaStreamError) as exc_info:
            list(generate_code_stream("test"))
        
        assert "Unexpected error during streaming" in str(exc_info.value)


class TestGenerateCode:
    """Test the generate_code wrapper function."""
    
    @patch('ollama_client.generate_code_stream')
    def test_successful_code_generation(self, mock_stream):
        """Test successful code generation (concatenation of stream)."""
        mock_stream.return_value = ["def ", "hello():", "\n    return 'Hello'"]
        
        result = generate_code("Create a hello function")
        
        assert result == "def hello():\n    return 'Hello'"
        mock_stream.assert_called_once_with("Create a hello function", "codellama")
    
    @patch('ollama_client.generate_code_stream')
    def test_custom_model(self, mock_stream):
        """Test code generation with custom model."""
        mock_stream.return_value = ["result"]
        
        result = generate_code("test", "custom-model")
        
        assert result == "result"
        mock_stream.assert_called_once_with("test", "custom-model")
    
    @patch('ollama_client.generate_code_stream')
    def test_error_propagation(self, mock_stream):
        """Test that errors from streaming are handled for backward compatibility."""
        mock_stream.side_effect = OllamaConnectionError("Connection failed")
        
        result = generate_code("test")
        
        # For backward compatibility, errors are returned as strings
        assert isinstance(result, str)
        assert "[Erro:" in result


class TestGenerateCodeWithRetry:
    """Test the generate_code_with_retry function."""
    
    @patch('ollama_client.generate_code_stream')
    def test_successful_first_attempt(self, mock_stream):
        """Test successful generation on first attempt."""
        mock_stream.return_value = ["generated code"]
        
        result = generate_code_with_retry("test")
        
        assert result == "generated code"
        mock_stream.assert_called_once_with("test", "codellama")
    
    @patch('ollama_client.generate_code_stream')
    @patch('ollama_client.time.sleep')
    def test_retry_on_connection_error(self, mock_sleep, mock_stream):
        """Test retry behavior on connection errors."""
        # First two attempts fail, third succeeds
        mock_stream.side_effect = [
            OllamaConnectionError("Connection failed"),
            OllamaConnectionError("Connection failed"),
            iter(["success"])
        ]
        
        result = generate_code_with_retry("test", max_retries=2)
        
        assert result == "success"
        assert mock_stream.call_count == 3
        assert mock_sleep.call_count == 2  # Should sleep before retry attempts
    
    @patch('ollama_client.generate_code_stream')
    @patch('ollama_client.time.sleep')
    def test_retry_on_timeout_error(self, mock_sleep, mock_stream):
        """Test retry behavior on timeout errors."""
        mock_stream.side_effect = [
            OllamaTimeoutError("Timeout"),
            iter(["success"])
        ]
        
        result = generate_code_with_retry("test", max_retries=1)
        
        assert result == "success"
        assert mock_stream.call_count == 2
        mock_sleep.assert_called_once()
    
    @patch('ollama_client.generate_code_stream')
    def test_no_retry_on_other_errors(self, mock_stream):
        """Test that non-retryable errors are not retried."""
        mock_stream.side_effect = OllamaResponseError("Bad response")
        
        with pytest.raises(OllamaResponseError):
            generate_code_with_retry("test")
        
        # Should only be called once (no retry)
        mock_stream.assert_called_once()
    
    @patch('ollama_client.generate_code_stream')
    @patch('ollama_client.time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_stream):
        """Test behavior when max retries are exceeded."""
        mock_stream.side_effect = OllamaConnectionError("Always fails")
        
        with pytest.raises(OllamaConnectionError) as exc_info:
            generate_code_with_retry("test", max_retries=2)
        
        assert "Maximum retries exceeded" in str(exc_info.value)
        assert mock_stream.call_count == 3  # Initial + 2 retries
        assert mock_sleep.call_count == 2  # Sleep before each retry
    
    @patch('ollama_client.generate_code_stream')
    def test_exponential_backoff(self, mock_stream):
        """Test exponential backoff timing."""
        with patch('ollama_client.time.sleep') as mock_sleep:
            mock_stream.side_effect = [
                OllamaConnectionError("Fail 1"),
                OllamaConnectionError("Fail 2"),
                OllamaConnectionError("Fail 3"),
                iter(["success"])
            ]
            
            result = generate_code_with_retry("test", max_retries=3, base_delay=1.0)
            
            assert result == "success"
            
            # Check exponential backoff: 1.0, 2.0, 4.0
            expected_delays = [1.0, 2.0, 4.0]
            actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
            assert actual_delays == expected_delays


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""
    
    @patch('ollama_client.requests.post')
    def test_generate_code_maintains_interface(self, mock_post):
        """Test that generate_code maintains its interface."""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = [
            b'{"response": "test code", "done": true}'
        ]
        mock_post.return_value = mock_response
        
        # Test that the function can be called as before
        result = generate_code("test prompt")
        
        assert isinstance(result, str)
        assert result == "test code"
    
    @patch('ollama_client.requests.post')
    def test_generate_code_with_model_parameter(self, mock_post):
        """Test that model parameter still works."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = [
            b'{"response": "code", "done": true}'
        ]
        mock_post.return_value = mock_response
        
        result = generate_code("test", "custom-model")
        
        # Verify the model was passed correctly
        call_args = mock_post.call_args
        assert call_args[1]['json']['model'] == "custom-model"
        assert result == "code"
    
    @patch('ollama_client.generate_code_stream')
    def test_generate_code_with_callbacks(self, mock_stream):
        """Test backward compatibility with on_chunk and on_progress callbacks."""
        mock_stream.return_value = ["chunk1", "chunk2", "chunk3"]
        
        chunks_received = []
        progress_received = []
        
        def on_chunk(chunk):
            chunks_received.append(chunk)
        
        def on_progress(progress):
            progress_received.append(progress)
        
        result = generate_code("test", on_chunk=on_chunk, on_progress=on_progress)
        
        assert result == "chunk1chunk2chunk3"
        assert chunks_received == ["chunk1", "chunk2", "chunk3"]
        assert 100 in progress_received  # Final progress should be 100
    
    @patch('ollama_client.generate_code_stream')
    def test_generate_code_with_context_files(self, mock_stream):
        """Test backward compatibility with context_files parameter."""
        mock_stream.return_value = ["enhanced code"]
        
        context_files = {
            "test.html": "<html><body>test</body></html>",
            "test.css": "body { color: red; }"
        }
        
        result = generate_code("Improve this", context_files=context_files)
        
        assert result == "enhanced code"
        # Verify that the prompt was enhanced with context
        mock_stream.assert_called_once()
        call_args = mock_stream.call_args[0]
        assert "Contexto dos arquivos existentes:" in call_args[0]
        assert "test.html" in call_args[0]
        assert "test.css" in call_args[0]
    
    @patch('ollama_client.generate_code_stream')
    def test_generate_code_error_returns_string(self, mock_stream):
        """Test that errors are returned as strings for backward compatibility."""
        mock_stream.side_effect = OllamaConnectionError("Connection failed")
        
        result = generate_code("test")
        
        assert isinstance(result, str)
        assert "[Erro:" in result
        assert "Connection failed" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
