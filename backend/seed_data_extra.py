import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict_api.settings')
django.setup()

from patients.models import Patient
from accounts.models import User
from appointments.models import Appointment
from consultations.models import Consultation
from prescriptions.models import Prescription

first_names = ["Hassan", "Khadija", "Youssef", "Fatima", "Omar", "Aicha", "Mohamed", "Zineb", "Karim", "Meryem", "Amine", "Naima", "Ali", "Salma", "Driss", "Kawtar", "Hamza", "Imane", "Bilal", "Ghita"]
last_names = ["Bennani", "Alaoui", "Tazi", "El Fassi", "Chraibi", "Tahiri", "Lahlou", "Berrada", "El Idrissi", "Benjelloun", "Naciri", "Benali"]
cities = ["Casablanca", "Rabat", "Marrakech", "Fes", "Tangier", "Agadir", "Meknes"]
diseases = ["Hypertension artérielle", "Diabète Type 2", "Angine", "Bronchite aiguë", "Gastrite", "Migraine ophtalmique", "Anémie", "Douleurs lombaires", "Sciatique", "Grippe saisonnière"]

doctors = list(User.objects.filter(role='DOCTOR'))
if len(doctors) == 0:
    print("No doctors found! Cant create appointments.")
else:
    for i in range(25):
        # Patient
        p = Patient.objects.create(
            first_name=random.choice(first_names),
            last_name=random.choice(last_names),
            date_of_birth=f"19{random.randint(50,99)}-0{random.randint(1,9)}-{random.randint(10,28)}",
            gender=random.choice(['M', 'F']),
            phone=f"+2126{random.randint(10000000, 99999999)}",
            city=random.choice(cities),
            cin=f"{random.choice(['A','B','C','D'])}{random.randint(10000, 99999)}"
        )
        
        # Determine status and create appointment
        statuses = ['COMPLETED', 'PLANNED', 'CANCELLED']
        astatus = random.choices(statuses, weights=[60, 30, 10])[0]
        adate = (timezone.now() + timedelta(days=random.randint(-30, 30))).date()
        
        # Avoid exact duplicate time block exceptions by randomizing hour between 8 and 18, and skipping unique constraint errors gracefully
        try:
            a = Appointment.objects.create(
                patient=p,
                doctor=random.choice(doctors),
                date=adate,
                time=f"{random.randint(8,18)}:00:00",
                duration=30,
                reason="Consultation de routine",
                status=astatus
            )
            
            if astatus == 'COMPLETED':
                c = Consultation.objects.create(
                    appointment=a,
                    symptoms="Fievere, maux de tete" if random.random() > 0.5 else "Fatigue, toux",
                    diagnosis=random.choice(diseases),
                    doctor_notes="Patient stable, repos recommande.",
                    ai_suggestions={}
                )
                if random.random() > 0.4:
                    Prescription.objects.create(
                        consultation=c,
                        medications="Doliprane 1000mg\nVitamine C",
                        dosage="1 comp matin / 1 soir\n1 comp par jour",
                        posology="Prendre avec un verre d'eau",
                        duration="5 jours"
                    )
        except Exception as e:
            print(f"Skipped one appointment due to logic collision: {e}")
            pass
            
    print("Successfully created 25 full patient profiles and related tracking!")
