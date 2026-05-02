from libs.common.hashing import hash_api_key, sha256_hex


def test_api_key_hash_is_deterministic_and_not_plaintext() -> None:
    api_key = "ak_dev_tenant_a_123456"

    digest = hash_api_key(api_key)

    assert digest == sha256_hex(api_key)
    assert digest != api_key
    assert len(digest) == 64
