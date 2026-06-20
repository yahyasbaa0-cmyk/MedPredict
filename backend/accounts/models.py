from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrateur'),
        ('DOCTOR', 'Médecin'),
        ('SECRETARY', 'Secrétaire'),
        ('PATIENT', 'Patient'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='SECRETARY')
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient}: {self.message[:20]}"
