from django.db import models
from django.core.validators import RegexValidator

class Patient(models.Model):
    BLOOD_GROUPS = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    )
    
    GENDER_CHOICES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre'),
    )

    MOROCCAN_CITIES = (
        ('Casablanca', 'Casablanca'),
        ('Rabat', 'Rabat'),
        ('Fes', 'Fès'),
        ('Marrakech', 'Marrakech'),
        ('Tangier', 'Tanger'),
        ('Agadir', 'Agadir'),
        ('Meknes', 'Meknès'),
        ('Oujda', 'Oujda'),
        ('Other', 'Autre'),
    )

    phone_regex = RegexValidator(
        regex=r'^(?:\+212|0)[5-7]\d{8}$',
        message="Le numéro de téléphone doit être au format: '+212600000000' ou '0600000000'."
    )

    id = models.AutoField(primary_key=True)
    cin = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Carte d'Identité Nationale")
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    city = models.CharField(max_length=100, choices=MOROCCAN_CITIES, default='Casablanca')
    address = models.TextField(blank=True, null=True)
    
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=150, blank=True, null=True, help_text="Nom et téléphone du contact d'urgence")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_patients')
    user = models.OneToOneField('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='patient_profile')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
