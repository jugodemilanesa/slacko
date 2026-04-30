from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class TheoryQueryView(APIView):
    """Query the bibliography for theoretical concepts."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request) -> Response:
        # TODO: implement RAG search + LLM response
        question = request.data.get("question", "")
        return Response(
            {
                "answer": f"[RAG pendiente] Pregunta recibida: {question}",
                "sources": [],
            },
            status=status.HTTP_200_OK,
        )
