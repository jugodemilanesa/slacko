from rest_framework import generics, permissions

from .models import Session
from .serializers import SessionCreateSerializer, SessionSerializer


class SessionListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SessionCreateSerializer
        return SessionSerializer

    def get_queryset(self):
        return Session.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SessionDetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SessionSerializer

    def get_queryset(self):
        return Session.objects.filter(user=self.request.user)
