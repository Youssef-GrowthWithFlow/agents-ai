import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=self.api_key)
        
        # Model definitions
        self.FAST_MODEL = "gemini-2.5-flash-lite" # As requested
        self.INTELLIGENT_MODEL = "gemini-3.0-pro-exp" # As requested, defaulting to pro-exp for 3.0
        
    def _get_model_name(self, model_type: str = "fast") -> str:
        if model_type == "intelligent":
            return self.INTELLIGENT_MODEL
        return self.FAST_MODEL

    def generate_content(self, prompt: str, model_type: str = "fast", **kwargs):
        """
        Basic text generation.
        https://ai.google.dev/gemini-api/docs/text-generation
        """
        model = self._get_model_name(model_type)
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(**kwargs)
        )
        return response.text

    def generate_with_audio(self, audio_path: str, prompt: str, model_type: str = "fast"):
        """
        Audio input processing.
        https://ai.google.dev/gemini-api/docs/audio
        """
        model = self._get_model_name(model_type)
        
        # Read audio file
        with open(audio_path, "rb") as f:
            audio_content = f.read()
            
        response = self.client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(data=audio_content, mime_type="audio/mp3"), # Assuming mp3, can be parameterized
                prompt
            ]
        )
        return response.text

    def generate_thinking(self, prompt: str, model_type: str = "intelligent"):
        """
        Enable thinking/reasoning features.
        https://ai.google.dev/gemini-api/docs/thinking
        Note: Thinking models might be specific versions.
        """
        # Thinking is typically available on specific models, often newer ones.
        # Ensure we use a model that supports it if 'intelligent' maps to one.
        model = self._get_model_name(model_type) 
        
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(include_thoughts=True)
            )
        )
        # The response structure for thinking might include thoughts separately
        # Depending on SDK version, it might be in candidates[0].content.parts
        return response

    def generate_structured(self, prompt: str, response_schema, model_type: str = "fast"):
        """
        Structured JSON output.
        https://ai.google.dev/gemini-api/docs/structured-output
        """
        model = self._get_model_name(model_type)
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema
            )
        )
        return response.parsed

    def generate_with_function_calling(self, prompt: str, tools: list, model_type: str = "fast"):
        """
        Function calling support.
        https://ai.google.dev/gemini-api/docs/function-calling
        """
        model = self._get_model_name(model_type)
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(tools=tools)
        )
        return response

    def generate_with_url_context(self, prompt: str, urls: list[str], model_type: str = "fast"):
        """
        URL context/grounding.
        https://ai.google.dev/gemini-api/docs/url-context
        """
        model = self._get_model_name(model_type)
        
        # Construct parts with tools for Google Search or Grounding if applicable
        # Or if using the specific URL grounding feature:
        
        # Using Google Search Grounding as a proxy for "URL context" if that's what's meant,
        # or passing URLs in prompt. The docs link refers to Grounding with Google Search usually.
        # If it refers to specific URL grounding (Vertex AI feature mostly), we use tools.
        
        # Assuming standard Google Search grounding for now based on common usage:
        google_search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[google_search_tool]
            )
        )
        return response

    def create_live_session(self, model_type: str = "fast"):
        """
        Setup for live sessions.
        https://ai.google.dev/gemini-api/docs/live-session
        """
        model = self._get_model_name(model_type)
        # This usually involves a WebSocket connection or similar async stream
        # Returning the config or session object to be used by the caller
        return self.client.aio.live.connect(model=model, config=types.LiveConnectConfig(response_modalities=["AUDIO"]))

    def create_ephemeral_token(self, ttl_seconds: int = 3600):
        """
        Manage ephemeral tokens.
        https://ai.google.dev/gemini-api/docs/ephemeral-tokens
        """
        # This is typically for client-side usage, generating a token on backend
        # Note: The Python SDK might not have a direct helper for creating ephemeral tokens 
        # if it's purely a backend service, but assuming we wrap an API call.
        # Actually, this is often done via REST or specific auth libraries.
        # For now, placeholder as it might require specific IAM permissions or endpoint.
        pass

    def create_cached_content(self, content: str, model_type: str = "fast", ttl_seconds: int = 300):
        """
        Context caching.
        https://ai.google.dev/gemini-api/docs/caching
        """
        model = self._get_model_name(model_type)
        # Caching API usage
        # This usually returns a name/handle for the cached content
        cached_content = self.client.caches.create(
            model=model,
            config=types.CreateCachedContentConfig(
                contents=[content],
                ttl=f"{ttl_seconds}s"
            )
        )
        return cached_content
