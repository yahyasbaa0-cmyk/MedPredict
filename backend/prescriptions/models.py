from django.db import models
from consultations.models import Consultation

class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    
    medications = models.TextField(help_text="Liste des médicaments")
    dosage = models.TextField(help_text="Dosage pour chaque médicament")
    posology = models.TextField(help_text="Posologie détaillée")
    duration = models.CharField(max_length=100, help_text="Durée du traitement")
    recommendations = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ordonnance pour {self.consultation.appointment.patient} ({self.created_at.strftime('%Y-%m-%d')})"
