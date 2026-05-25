from contextlib import contextmanager

from app.config import Settings
from app.storage import PostgresStore


class FakeCursor:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str, str]]]] = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def executemany(self, operation: str, parameters: list[tuple[str, str, str]]) -> None:
        self.calls.append((operation, parameters))


class FakeConnection:
    def __init__(self) -> None:
        self.executions: list[tuple[str, tuple[str, str]]] = []
        self.messages_cursor = FakeCursor()
        self.committed = False

    def execute(self, operation: str, parameters: tuple[str, str]) -> None:
        self.executions.append((operation, parameters))

    def cursor(self) -> FakeCursor:
        return self.messages_cursor

    def commit(self) -> None:
        self.committed = True


def test_postgres_append_turns_uses_cursor_executemany(monkeypatch):
    store = PostgresStore(Settings(database_url="postgresql://test"))
    connection = FakeConnection()

    @contextmanager
    def fake_connection():
        yield connection

    monkeypatch.setattr(store, "_connection", fake_connection)

    store.append_turns("proj-demo", "sess-1", "pergunta", "resposta")

    assert connection.executions[0][1] == ("sess-1", "proj-demo")
    assert connection.messages_cursor.calls[0][1] == [
        ("sess-1", "user", "pergunta"),
        ("sess-1", "assistant", "resposta"),
    ]
    assert connection.committed is True
