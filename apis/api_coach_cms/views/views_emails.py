from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from core.models import EmailTrainingSessionReport
from core.selectors import (
    get_coach_email_reports,
    get_coach_email_reports_filtered,
    get_coach_email_reports_stats
)


class EmailTrainingSessionReportSerializer(serializers.ModelSerializer):
    """Serializer za training session email report"""
    session_title = serializers.CharField(source='training_session.title', read_only=True)
    client_name = serializers.CharField(source='training_session.client.user.name', read_only=True)
    coach_name = serializers.CharField(source='coach.user.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = EmailTrainingSessionReport
        fields = [
            'id',
            'session_title',
            'client_name',
            'coach_name',
            'recipient_email',
            'status',
            'status_display',
            'sent_at',
            'attempt_count',
            'error_message',
            'created_at',
        ]
        read_only_fields = fields


class GetCoachEmailReportsView(generics.ListAPIView):
    """
    Pregled svih email reporta koje je coach poslao.
    GET /api/coach/email-reports/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailTrainingSessionReportSerializer
    
    def get_queryset(self):
        """Filtriraj emaile po ulogovanom coachu koristeći selector"""
        user = self.request.user
        coach = getattr(user, 'coach', None)
        
        if not coach:
            return EmailTrainingSessionReport.objects.none()
        
        return get_coach_email_reports(coach)
    

class GetEmailDetailsView(generics.RetrieveAPIView):
    class OutputSerializer(serializers.ModelSerializer):
        coach = serializers.CharField(source='coach.user.name', read_only=True)
        client = serializers.CharField(source='training_session.client.user.name', read_only=True)
        training_session = serializers.CharField(source='training_session.title', read_only=True)
        class Meta:
            model = EmailTrainingSessionReport
            fields = "__all__"
    permission_classes = [IsAuthenticated]
    serializer_class = OutputSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        user = self.request.user
        coach = getattr(user, 'coach', None)

        if not coach:
            return EmailTrainingSessionReport.objects.none()
        
        return get_coach_email_reports(coach)


class GetCoachEmailReportsFilteredView(APIView):
    """
    Pregled email reporta sa filterima.
    GET /api/coach/email-reports-filtered/?status=sent&limit=10
    
    Query params:
    - status: pending, sent, failed
    - limit: broj rezultata (default 20)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        coach = getattr(user, 'coach', None)
        
        if not coach:
            return Response(
                {'error': 'Only coaches can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filter params
        status_filter = request.query_params.get('status', None)
        limit = int(request.query_params.get('limit', 20))
        
        try:
            queryset = get_coach_email_reports_filtered(coach, status=status_filter, limit=limit)
            
            # Serialize
            serializer = EmailTrainingSessionReportSerializer(queryset, many=True)
            
            return Response({
                'count': len(serializer.data),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetCoachEmailReportStatsView(APIView):
    """
    Statistika email reporta za coacha.
    GET /api/coach/email-reports-stats/
    
    Vraća:
    - total_sent: Ukupno poslanih emaila
    - total_pending: Čekajući emaili
    - total_failed: Neuspešno poslani emaili
    - success_rate: Procenat uspešnih slanja
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        coach = getattr(user, 'coach', None)
        
        if not coach:
            return Response(
                {'error': 'Only coaches can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            stats = get_coach_email_reports_stats(coach)
            return Response(stats, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
