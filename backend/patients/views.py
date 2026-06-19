from django.db import models
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Patient
from .serializers import PatientSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    filterset_fields = ['is_archived']

    def get_queryset(self):
        qs = Patient.objects.all().order_by('-created_at')
        user = self.request.user
        if user.is_authenticated and user.role == 'DOCTOR':
            return qs.filter(models.Q(appointments__doctor=user) | models.Q(created_by=user)).distinct()
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
