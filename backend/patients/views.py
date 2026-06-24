from django.db import models
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Patient
from .serializers import PatientSerializer
from accounts.permissions import IsAdminOrDoctorOrSecretary

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAdminOrDoctorOrSecretary]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    filterset_fields = ['is_archived']

    def get_queryset(self):
        qs = Patient.objects.all().order_by('-created_at')
        user = self.request.user
        if user.is_authenticated and user.role == 'DOCTOR':
            return qs.filter(
                models.Q(appointments__doctor=user, appointments__status__in=['CONFIRMED', 'COMPLETED', 'IN_PROGRESS']) |
                models.Q(created_by=user)
            ).distinct()
        return qs

    def perform_create(self, serializer):
        patient = serializer.save(created_by=self.request.user)
        if not patient.user:
            from accounts.models import User
            username = patient.cin or f"pat_{patient.id}"
            if not User.objects.filter(username=username).exists():
                password = f"{username}2025"
                user_account = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=patient.first_name,
                    last_name=patient.last_name,
                    email=patient.email or '',
                    phone=patient.phone or '',
                    role='PATIENT'
                )
                patient.user = user_account
                patient.save()
