from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from apis.api_coach_cms.serializers.serializers_users import CoachInfoSerializer, CustomTokenObtainPairSerializer
from core.utils import get_logger, AppLog
from user.log_templates import LOG_COACH_LOGGED_IN

logger = get_logger(__name__)


class CurrentCoachInfoView(generics.RetrieveUpdateAPIView):
    """
    View for getting current logged coach information.
    """
    serializer_class = CoachInfoSerializer
    # We need to create custom permissions
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            # test log
            AppLog(logger, LOG_COACH_LOGGED_IN, coach=self.request.user.coach)
            return self.request.user.coach
        except ObjectDoesNotExist:
            raise Http404


class LoginCoachView(TokenObtainPairView):
    """
        View to handle login, we inherit View from simple_jwt library.
        """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)
