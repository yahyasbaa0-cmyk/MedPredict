from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Consultation
from .serializers import ConsultationSerializer
import requests
from django.conf import settings

from rest_framework.exceptions import PermissionDenied

class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['appointment__patient__first_name', 'appointment__patient__last_name', 'diagnosis']
    filterset_fields = ['appointment__doctor', 'appointment__patient']

    def get_queryset(self):
        qs = Consultation.objects.all().order_by('-date')
        user = self.request.user
        if user.is_authenticated and user.role == 'DOCTOR':
            return qs.filter(appointment__doctor=user)
        return qs

    def check_permissions(self, request):
        super().check_permissions(request)
        if request.user.is_authenticated and request.user.role == 'SECRETARY' and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            raise PermissionDenied("Les secrétaires ne sont pas autorisées à modifier les consultations.")

    @action(detail=False, methods=['post'], url_path='analyze-symptoms')
    def analyze_symptoms(self, request):
        symptoms = request.data.get('symptoms', [])
        if not symptoms:
            return Response({"error": "No symptoms provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Appel au microservice Flask
            response = requests.post(
                settings.AI_SERVICE_URL,
                json={'symptoms': symptoms},
                timeout=2.0
            )
            response.raise_for_status()
            data = response.json()
            return Response(data, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            # Fail-safe mechanism
            return Response(
                {"predictions": [], "error": "AI Service unavailable", "details": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
