import json
from collections.abc import AsyncIterator

import httpx


class ChatbotClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def chat_stream(self, message: str, model: str | None, session_id: str | None) -> AsyncIterator[dict]:
        payload = {"message": message, "model": model, "session_id": session_id}
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", f"{self.base_url}/chat/stream", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        yield json.loads(line[6:])

    async def get(self, path: str):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{self.base_url}{path}")
            response.raise_for_status()
            return response.json()
