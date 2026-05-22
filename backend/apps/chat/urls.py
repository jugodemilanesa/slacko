from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("sessions/", views.SessionListCreateView.as_view(), name="session_list"),
    path("sessions/search/", views.SessionSearchView.as_view(), name="session_search"),
    path("sessions/<uuid:pk>/", views.SessionDetailView.as_view(), name="session_detail"),
    path(
        "sessions/<uuid:pk>/messages/",
        views.SessionMessagesView.as_view(),
        name="session_messages",
    ),
]
