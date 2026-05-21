"""WebSocket consumer for real-time chat with Slacko.

Routes each user message through the orchestrator (LLM + tools) and streams
the assistant response back. Persists both messages to the DB so the session
can be reloaded later.
"""

from __future__ import annotations

import logging
import uuid

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer that runs every message through the orchestrator."""

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        user = self.scope.get("user")
        if user is None or not getattr(user, "is_authenticated", False):
            await self.close(code=4401)
            return

        self.session = await self._load_session(self.session_id, user.id)
        if self.session is None:
            await self.close(code=4404)
            return

        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive_json(self, content: dict):
        user_text = (content.get("message") or "").strip()
        if not user_text:
            return

        await self._save_message(self.session.id, "user", user_text, {})

        try:
            turn = await self._run_turn(self.session.id, user_text)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Orchestrator crashed on session %s", self.session.id)
            await self.send_json(
                {
                    "type": "error",
                    "message": "Algo falló mientras procesaba tu mensaje.",
                    "details": str(exc),
                }
            )
            return

        metadata = {"provider": turn.provider}
        if turn.error:
            metadata["error"] = turn.error

        await self._save_assistant_message(
            self.session.id,
            content=turn.content,
            metadata=metadata,
            tool_calls=turn.tool_calls,
            citations=turn.citations,
        )

        await self.send_json(
            {
                "type": "message",
                "role": "assistant",
                "content": turn.content,
                "metadata": metadata,
                "tool_calls": turn.tool_calls,
                "citations": turn.citations,
            }
        )

    # ─── DB helpers (sync → async wrappers) ───────────────────────────────

    @database_sync_to_async
    def _load_session(self, session_id: str, user_id: int):
        from .models import Session

        try:
            return Session.objects.get(id=uuid.UUID(str(session_id)), user_id=user_id)
        except (Session.DoesNotExist, ValueError):
            return None

    @database_sync_to_async
    def _save_message(self, session_id, role: str, content: str, metadata: dict):
        from .models import Message

        return Message.objects.create(
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata,
        )

    @database_sync_to_async
    def _save_assistant_message(
        self,
        session_id,
        *,
        content: str,
        metadata: dict,
        tool_calls: list,
        citations: list,
    ):
        from .models import Message

        return Message.objects.create(
            session_id=session_id,
            role="assistant",
            content=content,
            metadata=metadata,
            tool_calls=tool_calls,
            citations=citations,
        )

    @database_sync_to_async
    def _run_turn(self, session_id, user_text: str):
        from apps.chat.models import Session
        from apps.orchestrator.orchestrator import run_turn

        session = Session.objects.get(id=session_id)
        return run_turn(session, user_text)
