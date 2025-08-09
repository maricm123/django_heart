from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from api_coach_cms.serializers.serializers_users import CoachInfoSerializer


class CurrentCoachInfoView(generics.RetrieveUpdateAPIView):
    """
    View for getting current logged coach information.
    """
    serializer_class = CoachInfoSerializer
    # We need to create custom permissions
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.coach
        except ObjectDoesNotExist:
            raise Http404
