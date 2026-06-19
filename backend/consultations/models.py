from django.db import models
from appointments.models import Appointment

class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation')
    date = models.DateTimeField(auto_now_add=True)
    
    symptoms = models.TextField(help_text="Liste des symptômes séparés par des virgules")
    clinical_examination = models.TextField(blank=True, null=True)
    diagnosis = models.CharField(max_length=255, blank=True, null=True)
    doctor_notes = models.TextField(blank=True, null=True)
    
    ai_suggestions = models.JSONField(blank=True, null=True, help_text="{ 'predictions': [...] }")

    def __str__(self):
        return f"Consultation pour {self.appointment.patient} le {self.date.strftime('%Y-%m-%d')}"
