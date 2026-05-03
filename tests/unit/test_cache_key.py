from services.api.app.services.cache_service import build_cache_key, hash_payload


def test_cache_key_includes_tenant_model_preprocess_and_hash() -> None:
    input_hash = hash_payload({"text": "hello"})

    key = build_cache_key(
        "local",
        "tenant-a",
        "summary",
        "model-v1",
        "preprocess-v1",
        input_hash,
    )

    assert key.startswith("ai-docops:local:tenant-a:summary:model-v1:preprocess-v1:")
    assert key.endswith(input_hash)
