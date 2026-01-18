from training_session.models import TrainingSession
from rest_framework.response import Response
from rest_framework import status


class ReqContextMixin:
    @property
    def _req_context(self):
        return self.context["request"]


class TrainingSessionMixin:
    def get_training_session_with_id(self, id=id):
        try:
            # We can move this to selector
            return TrainingSession.objects.select_related("coach", "client", "gym").get(id=id)
        except TrainingSession.DoesNotExist:
            return Response({"detail": "Training session not found."}, status=status.HTTP_404_NOT_FOUND)
