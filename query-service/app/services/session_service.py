from datetime import datetime

from app.schemas.chat import HistoryTurn


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, list[HistoryTurn]] = {}

    def get_history(self, session_id: str) -> list[HistoryTurn]:
        return list(self._sessions.get(session_id, []))

    def append_turns(self, session_id: str, user_message: str, assistant_answer: str) -> None:
        turns = self._sessions.setdefault(session_id, [])
        turns.append(HistoryTurn(role="user", content=user_message, timestamp=datetime.utcnow()))
        turns.append(
            HistoryTurn(role="assistant", content=assistant_answer, timestamp=datetime.utcnow())
        )

    def delete_history(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
