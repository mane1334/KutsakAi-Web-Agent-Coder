#!/usr/bin/env python3
"""
Demonstration script for the refactored ollama_client with streaming support.

This script shows:
1. How to use the new generate_code_stream function for real-time streaming
2. How the backward-compatible generate_code function still works
3. How standardized error handling works
"""

from ollama_client import (
    generate_code_stream, 
    generate_code, 
    OllamaError, 
    OllamaConnectionError
)
import time

def demo_streaming():
    """Demonstrate the new streaming functionality."""
    print("=== Streaming Demo ===")
    print("Using generate_code_stream() for real-time output:")
    print()
    
    try:
        prompt = "Create a simple Python function that calculates factorial"
        print(f"Prompt: {prompt}")
        print("\nStreaming response:")
        print("-" * 50)
        
        # Collect chunks for timing demo
        chunks = []
        start_time = time.time()
        
        for i, chunk in enumerate(generate_code_stream(prompt)):
            print(chunk, end='', flush=True)
            chunks.append(chunk)
            
            # Add a small delay to simulate real-time viewing
            time.sleep(0.01)
        
        end_time = time.time()
        print("\n" + "-" * 50)
        print(f"Received {len(chunks)} chunks in {end_time - start_time:.2f} seconds")
        
    except OllamaConnectionError as e:
        print(f"Connection error: {e}")
        print("Make sure Ollama is running on localhost:11434")
    except OllamaError as e:
        print(f"Ollama error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def demo_backward_compatibility():
    """Demonstrate backward compatibility with existing code."""
    print("\n\n=== Backward Compatibility Demo ===")
    print("Using generate_code() (non-streaming, backward compatible):")
    print()
    
    try:
        prompt = "Create a Python function that reverses a string"
        print(f"Prompt: {prompt}")
        print("\nComplete response:")
        print("-" * 50)
        
        start_time = time.time()
        result = generate_code(prompt)
        end_time = time.time()
        
        print(result)
        print("-" * 50)
        print(f"Response received in {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {e}")

def demo_error_handling():
    """Demonstrate standardized error handling."""
    print("\n\n=== Error Handling Demo ===")
    print("Testing with an invalid model:")
    print()
    
    try:
        # This should raise an OllamaModelError
        result = list(generate_code_stream("test", "nonexistent-model"))
        print("Unexpected success!")
    except OllamaConnectionError as e:
        print(f"Connection Error: {e}")
        print(f"Error Code: {e.error_code}")
    except OllamaError as e:
        print(f"Ollama Error: {e}")
        print(f"Error Code: {e.error_code}")
        print(f"Error Type: {type(e).__name__}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def demo_with_callbacks():
    """Demonstrate backward compatibility with callbacks."""
    print("\n\n=== Callback Demo (Backward Compatibility) ===")
    print("Using generate_code() with on_chunk and on_progress callbacks:")
    print()
    
    chunks_received = []
    progress_updates = []
    
    def on_chunk(chunk):
        chunks_received.append(chunk)
        print(f"[CHUNK] {repr(chunk)}")
    
    def on_progress(progress):
        progress_updates.append(progress)
        print(f"[PROGRESS] {progress}%")
    
    try:
        prompt = "Create a simple hello world function"
        print(f"Prompt: {prompt}")
        print("\nCallbacks will show chunks and progress:")
        print("-" * 50)
        
        result = generate_code(
            prompt, 
            on_chunk=on_chunk, 
            on_progress=on_progress
        )
        
        print("-" * 50)
        print(f"Final result: {result}")
        print(f"Total chunks: {len(chunks_received)}")
        print(f"Progress updates: {progress_updates}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Ollama Client Streaming Demo")
    print("============================")
    print()
    print("This demo requires Ollama to be running with the 'codellama' model.")
    print("If Ollama is not available, you'll see connection errors.")
    print()
    
    # Run the demos
    demo_streaming()
    demo_backward_compatibility() 
    demo_error_handling()
    demo_with_callbacks()
    
    print("\n\nDemo completed!")
    print("\nKey features demonstrated:")
    print("✓ Real-time streaming with generate_code_stream()")
    print("✓ Backward compatible generate_code()")
    print("✓ Standardized error handling with specific error types")
    print("✓ Legacy callback support (on_chunk, on_progress)")
    print("✓ Proper error propagation and handling")
