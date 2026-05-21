import json
import aiohttp
import requests

from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.base_client import AIClient


class CustomAnthropicAIClient(AIClient):
    """
    Custom HTTP client for Anthropic's Claude API.

    This implementation uses raw HTTP requests (requests/aiohttp) instead of
    the official SDK, demonstrating how to interact with Claude's API directly
    and handle its Server-Sent Events (SSE) streaming format.
    """

    def response(self, messages: list[Message], **kwargs) -> Message:
        """
        Get a synchronous response using raw HTTP POST request.

        Args:
            messages (list[Message]): The conversation history.
            **kwargs: Additional parameters like max_tokens (default: 1024).

        Returns:
            Message: The AI's response message.

        Raises:
            ValueError: If the API response contains no content blocks.
            Exception: If the HTTP request fails (non-200 status code).

        Note:
            Requires 'x-api-key' header and 'anthropic-version' header.
            Claude's API returns content as an array of content blocks.
            The response is printed to stdout before being returned.
        """
        #TODO:
        # https://docs.anthropic.com/en/api/messages-examples
        # - Prepare headers with api key, anthropic version and content type
        # - Add System prompt
        # - Execute post request to AI API (use `requests`)
        # - Parse response
        # - Print response to console
        # - Return ASSISTANT message
        try:
            response = requests.post(
                url=f"{self._endpoint}/v1/messages",
                headers={
                    "x-api-key": self._api_key,
                    "anthropic-version": "2024-06-01",
                    "Content-Type": "application/json",
                },  
                json={
                    "model": self._model_name,
                    "max_tokens": kwargs.get("max_tokens", 1024),
                    "system": self._system_prompt,
                    "messages": [m.to_dict() for m in messages if m.role != Role.SYSTEM],
                }, 
            )
            response.raise_for_status()
            response_data = response.json()
            content_blocks = response_data.get("content", [])
            if not content_blocks:
                raise ValueError("API response contains no content blocks.")
            text = "".join(block.get("text", "") for block in content_blocks)
            print(f"AI: {text}")
            return Message(role=Role.ASSISTANT, content=text)
        except requests.exceptions.RequestException as e:
            print(f"HTTP request failed: {e}")
            raise

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        """
        Get a streaming response using raw HTTP with Server-Sent Events (SSE).

        The response is streamed using Anthropic's SSE format, with text deltas
        printed immediately as they arrive.

        Args:
            messages (list[Message]): The conversation history.
            **kwargs: Additional parameters like max_tokens (default: 1024).

        Returns:
            Message: The complete AI response message after all deltas are received.

        Note:
            Uses Server-Sent Events (SSE) format where each line starts with "data: ".
            Listens for 'content_block_delta' events with 'text_delta' type.
            Stops processing when 'message_stop' event is received.
            Each delta is printed to stdout as it arrives.
        """
        #TODO:
        # https://docs.anthropic.com/en/docs/build-with-claude/streaming
        # - Prepare headers with api key, anthropic version and content type
        # - Add System prompt
        # - Execute post request to AI API (use `aihttp`)
        # - Handle stream with chunks
        # - Parse response
        # - Print chunks to console
        # - Return ASSISTANT message
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=f"{self._endpoint}/v1/messages",
                    headers={
                        "x-api-key": self._api_key,
                        "anthropic-version": "2024-06-01",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self._model_name,
                        "max_tokens": kwargs.get("max_tokens", 1024),
                        "system": self._system_prompt,
                        "messages": [m.to_dict() for m in messages if m.role != Role.SYSTEM],
                    },
                ) as response:
                    async for line in response.content:
                        line = line.decode("utf-8")
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            if data.get("type") == "content_block_delta":
                                print(data.get("delta", {}).get("text", ""), end="", flush=True)
        except Exception as e:
            print(f"Error occurred: {e}")
            raise

