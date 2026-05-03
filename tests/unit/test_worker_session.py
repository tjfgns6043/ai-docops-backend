from sqlalchemy.pool import NullPool

from services.worker.app.db import session as worker_session


def test_worker_session_factory_uses_null_pool(monkeypatch) -> None:
    captured: dict[str, object] = {}
    engine = object()

    def fake_create_async_engine(url: str, **kwargs: object) -> object:
        captured["url"] = url
        captured.update(kwargs)
        return engine

    monkeypatch.setattr(worker_session, "create_async_engine", fake_create_async_engine)

    factory = worker_session.make_session_factory("postgresql+asyncpg://app:app@localhost:5432/app")

    assert captured["poolclass"] is NullPool
    assert factory.kw["bind"] is engine
