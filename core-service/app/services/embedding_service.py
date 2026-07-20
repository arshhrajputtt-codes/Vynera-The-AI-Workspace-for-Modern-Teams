import httpx

from app.core.config import settings
from app.core.exceptions import ProviderError

OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"

_local_model = None


def _get_local_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer

        _local_model = SentenceTransformer(settings.LOCAL_EMBEDDING_MODEL)
    return _local_model


class EmbeddingService:
    def __init__(self, api_key: str | None = None, model: str | None = None, provider: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_EMBEDDING_MODEL
        self.provider = provider or settings.EMBEDDING_PROVIDER

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self.provider == "ollama":
            return self._embed_ollama(texts)
        if self.provider == "local":
            return self._embed_local(texts)
        return self._embed_openai(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def _embed_ollama(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        try:
            with httpx.Client(timeout=30.0) as client:
                for text in texts:
                    response = client.post(
                        f"{settings.OLLAMA_BASE_URL}/api/embeddings",
                        json={"model": settings.OLLAMA_EMBEDDING_MODEL, "prompt": text},
                    )
                    response.raise_for_status()
                    vectors.append(response.json()["embedding"])
        except httpx.HTTPStatusError as exc:
            raise ProviderError(
                "ollama-embeddings",
                f"{exc.response.text} (have you run: ollama pull {settings.OLLAMA_EMBEDDING_MODEL})",
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderError("ollama-embeddings", f"{exc} (is Ollama running?)") from exc

        return vectors

    def _embed_local(self, texts: list[str]) -> list[list[float]]:
        try:
            model = _get_local_model()
            vectors = model.encode(texts, convert_to_numpy=True)
        except Exception as exc:
            raise ProviderError("local-embeddings", str(exc)) from exc

        return [vector.tolist() for vector in vectors]

    def _embed_openai(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            raise ProviderError("openai", "OPENAI_API_KEY is not configured")

        try:
            response = httpx.post(
                OPENAI_EMBEDDINGS_URL,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "input": texts},
                timeout=30.0,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ProviderError("openai", exc.response.text) from exc
        except httpx.RequestError as exc:
            raise ProviderError("openai", str(exc)) from exc

        data = response.json()["data"]
        data.sort(key=lambda item: item["index"])
        return [item["embedding"] for item in data]