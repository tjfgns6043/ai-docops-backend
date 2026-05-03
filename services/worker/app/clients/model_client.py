"""Worker model client."""

import httpx

from ..core.config import Settings


class WorkerModelClient:
    """HTTP client used by worker tasks."""

    def __init__(self, settings: Settings) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.model_server_url,
            timeout=httpx.Timeout(connect=1.0, read=30.0, write=5.0, pool=1.0),
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for texts."""
        response = await self._client.post("/embed", json={"texts": texts, "normalize": True})
        response.raise_for_status()
        return [list(map(float, item)) for item in response.json()["embeddings"]]

    async def summarize(self, text: str, max_sentences: int) -> dict[str, object]:
        """Return extractive summary."""
        response = await self._client.post(
            "/summarize-extractive",
            json={"text": text, "max_sentences": max_sentences, "language": "mixed"},
        )
        response.raise_for_status()
        return dict(response.json())
