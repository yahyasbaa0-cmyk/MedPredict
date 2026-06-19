from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from patients.models import Patient
from appointments.models import Appointment
from consultations.models import Consultation
from accounts.models import User
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # Activité générale
        total_patients = Patient.objects.count()
        total_doctors = User.objects.filter(role='DOCTOR').count()
        
        # Consultations du mois dernier
        consultations_last_30d = Consultation.objects.filter(date__gte=thirty_days_ago).count()
        
        # Répartition Pathologies (Top 5)
        pathologies = Consultation.objects.exclude(diagnosis__isnull=True).exclude(diagnosis__exact='')\
                        .values('diagnosis').annotate(count=Count('id')).order_by('-count')[:5]

        # Taux de RDV
        appointments_total = Appointment.objects.count()
        appointments_completed = Appointment.objects.filter(status='COMPLETED').count()
        appointments_cancelled = Appointment.objects.filter(status='CANCELLED').count()
        
        rdv_stats = {
            "total": appointments_total,
            "completed": appointments_completed,
            "cancelled": appointments_cancelled,
        }

        # Utilisation IA
        ai_used_count = Consultation.objects.exclude(ai_suggestions__isnull=True).exclude(ai_suggestions={}).count()
        total_consultations = Consultation.objects.count()
        ai_usage_rate = (ai_used_count / total_consultations * 100) if total_consultations > 0 else 0

        return Response({
            "general_activity": {
                "total_patients": total_patients,
                "total_doctors": total_doctors,
                "consultations_last_30d": consultations_last_30d
            },
            "pathologies_distribution": list(pathologies),
            "appointments_stats": rdv_stats,
            "ai_usage": {
                "used_count": ai_used_count,
                "usage_rate": round(ai_usage_rate, 2)
            }
        })
