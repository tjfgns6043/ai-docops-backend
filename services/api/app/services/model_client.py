"""HTTP client for the model server."""

from http import HTTPStatus

import httpx

from ..core.config import Settings
from ..core.errors import ApiError


class ModelClient:
    """Async model server client."""

    def __init__(self, settings: Settings) -> None:
        timeout = httpx.Timeout(
            connect=settings.model_connect_timeout_seconds,
            read=settings.model_read_timeout_seconds,
            write=settings.model_write_timeout_seconds,
            pool=settings.model_pool_timeout_seconds,
        )
        self.settings = settings
        self._client = httpx.AsyncClient(base_url=settings.model_server_url, timeout=timeout)

    async def embed(self, texts: list[str], normalize: bool = True) -> dict[str, object]:
        """Call model-server /embed."""
        return await self._post(
            "/embed",
            {"texts": texts, "normalize": normalize},
            "MODEL_UNAVAILABLE",
        )

    async def summarize(
        self,
        text: str,
        max_sentences: int,
        language: str,
    ) -> dict[str, object]:
        """Call model-server /summarize-extractive."""
        payload = {"text": text, "max_sentences": max_sentences, "language": language}
        return await self._post("/summarize-extractive", payload, "MODEL_UNAVAILABLE")

    async def classify(
        self,
        text: str,
        labels: list[dict[str, str]],
        top_k: int,
    ) -> dict[str, object]:
        """Call model-server /classify-prototype."""
        payload = {"text": text, "labels": labels, "top_k": top_k}
        return await self._post("/classify-prototype", payload, "MODEL_UNAVAILABLE")

    async def _post(
        self,
        path: str,
        payload: dict[str, object],
        error_code: str,
    ) -> dict[str, object]:
        try:
            response = await self._client.post(path, json=payload)
            response.raise_for_status()
            return dict(response.json())
        except httpx.TimeoutException as exc:
            raise ApiError(
                "MODEL_TIMEOUT",
                "model server request timed out",
                HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc
        except httpx.HTTPError as exc:
            raise ApiError(
                error_code,
                "model server is temporarily unavailable",
                HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc


def get_model_client(settings: Settings) -> ModelClient:
    """Create a model client."""
    return ModelClient(settings)
