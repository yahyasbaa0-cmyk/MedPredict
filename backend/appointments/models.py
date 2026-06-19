from django.db import models
from django.core.exceptions import ValidationError
from patients.models import Patient
from accounts.models import User

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PLANNED', 'Planifié'),
        ('CONFIRMED', 'Confirmé'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminé'),
        ('CANCELLED', 'Annulé'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', limit_choices_to={'role': 'DOCTOR'})
    
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(default=30, help_text="Duration in minutes")
    
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.status != 'CANCELLED':
            # Verifier double booking pour le datetime exact (simplifié)
            overlapping_appointments = Appointment.objects.filter(
                doctor=self.doctor,
                date=self.date,
                time=self.time,
            ).exclude(status='CANCELLED')
            
            if self.pk:
                overlapping_appointments = overlapping_appointments.exclude(pk=self.pk)
                
            if overlapping_appointments.exists():
                raise ValidationError("Ce médecin a déjà un rendez-vous à cette date et heure.")
                
            # Verify maximum appointments per day
            daily_appointments = Appointment.objects.filter(
                doctor=self.doctor,
                date=self.date,
            ).exclude(status='CANCELLED')
            
            if self.pk:
                daily_appointments = daily_appointments.exclude(pk=self.pk)
                
            # Allow max 8 appointments per day (based on available slots)
            if daily_appointments.count() >= 8:
                raise ValidationError("La journée est déjà complète pour ce médecin.")
                
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient} avec le Dr. {self.doctor} - {self.date} à {self.time}"

class WhatsAppSession(models.Model):
    phone_number = models.CharField(max_length=50, primary_key=True)
    state = models.CharField(max_length=50, default='START')
    data = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} - {self.state}"
