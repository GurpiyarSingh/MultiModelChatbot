import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.schemas import Message, SessionDetail, SessionSummary


class SessionStore:
    """Single-process session storage, persisted to one JSON file after each change."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.sessions: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self.file_path.exists():
            return
        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                self.sessions = raw
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"Could not read sessions file {self.file_path}: {exc}") from exc

    def _save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(json.dumps(self.sessions, indent=2), encoding="utf-8")

    def create_or_get(self, session_id: str | None, model: str) -> str:
        if session_id and session_id in self.sessions:
            return session_id
        if session_id:
            raise KeyError(session_id)
        session_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        self.sessions[session_id] = {"model": model, "created_at": now, "updated_at": now, "messages": []}
        self._save()
        return session_id

    def messages(self, session_id: str) -> list[Message]:
        return [Message.model_validate(item) for item in self.sessions[session_id]["messages"]]

    def add_message(self, session_id: str, message: Message) -> None:
        self.sessions[session_id]["messages"].append(message.model_dump())
        self.sessions[session_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()

    def detail(self, session_id: str) -> SessionDetail:
        session = self.sessions[session_id]
        return SessionDetail(
            id=session_id, model=session["model"], message_count=len(session["messages"]),
            updated_at=session["updated_at"], messages=self.messages(session_id),
        )

    def list(self) -> list[SessionSummary]:
        return sorted(
            [
                SessionSummary(id=sid, model=data["model"], message_count=len(data["messages"]), updated_at=data["updated_at"])
                for sid, data in self.sessions.items()
            ],
            key=lambda item: item.updated_at,
            reverse=True,
        )
