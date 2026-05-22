"""REST endpoints for sessions and messages.

Most of the work happens over WebSocket (see ``apps.chat.consumers``); these
HTTP endpoints back the history sidebar and any "load a previous chat"
action. All endpoints are scoped to ``request.user``.
"""

from __future__ import annotations

from django.db.models import Q
from rest_framework import filters, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Message, Session
from .serializers import (
    MessageSerializer,
    SessionCreateSerializer,
    SessionSerializer,
    SessionSummarySerializer,
    SessionUpdateSerializer,
)


class SessionListCreateView(generics.ListCreateAPIView):
    """``GET`` for the history sidebar, ``POST`` to start a new session."""

    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ("updated_at", "created_at", "pinned")
    ordering = ("-pinned", "-updated_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SessionCreateSerializer
        return SessionSummarySerializer

    def get_queryset(self):
        qs = Session.objects.filter(user=self.request.user)
        archived = self.request.query_params.get("archived")
        if archived in ("true", "1"):
            qs = qs.filter(archived=True)
        elif archived in ("false", "0", None):
            qs = qs.filter(archived=False)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """``GET`` full session + messages; ``PATCH`` to rename/archive/pin; ``DELETE``."""

    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return SessionUpdateSerializer
        return SessionSerializer

    def get_queryset(self):
        return Session.objects.filter(user=self.request.user)


class SessionMessagesView(generics.ListAPIView):
    """Paginated message list for a single session."""

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MessageSerializer

    def get_queryset(self):
        session_id = self.kwargs["pk"]
        return Message.objects.filter(
            session_id=session_id,
            session__user=self.request.user,
        )


class SessionSearchView(APIView):
    """Full-text-ish search across the user's sessions.

    Uses PostgreSQL ``ILIKE`` over titles + message bodies. Not as strong as
    ``tsvector`` but works on any backend; upgrade once we standardize on PG.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request) -> Response:
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Response({"sessions": [], "messages": []})

        sessions_qs = Session.objects.filter(user=request.user).filter(
            Q(title__icontains=q)
            | Q(messages__content__icontains=q)
        ).distinct()[:20]

        messages_qs = (
            Message.objects.filter(
                session__user=request.user,
                content__icontains=q,
            )
            .select_related("session")
            .order_by("-created_at")[:20]
        )

        return Response(
            {
                "sessions": SessionSummarySerializer(sessions_qs, many=True).data,
                "messages": [
                    {
                        "id": str(m.id),
                        "session_id": str(m.session_id),
                        "role": m.role,
                        "content": m.content,
                        "created_at": m.created_at,
                    }
                    for m in messages_qs
                ],
            },
            status=status.HTTP_200_OK,
        )
