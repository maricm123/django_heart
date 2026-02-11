from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.utils import generate_presigned_url
from django_heart import settings


class UploadProfilePictureView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_name = request.data.get("file_name")
        file_type = request.data.get("file_type")

        if not file_name or not file_type:
            return Response({"error": "file_name and file_type required"}, status=status.HTTP_400_BAD_REQUEST)

        presigned_url = generate_presigned_url(file_name, file_type)

        s3_url = \
            (f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}"
             f".amazonaws.com/{file_name}")

        return Response({
            "presigned_url": presigned_url,
            "s3_url": s3_url
        }, status=status.HTTP_200_OK)
