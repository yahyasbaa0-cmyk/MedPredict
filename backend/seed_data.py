import os
import django
from datetime import date, time, timedelta

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from patients.models import Patient
from appointments.models import Appointment
from consultations.models import Consultation
from prescriptions.models import Prescription

User = get_user_model()

def run():
    print("Flushing database...")
    Prescription.objects.all().delete()
    Consultation.objects.all().delete()
    Appointment.objects.all().delete()
    Patient.objects.all().delete()
    User.objects.exclude(is_superuser=True).delete()

    print("Seeding database with Moroccan demo data...")
    
    # Create doctors
    dr_bennani, _ = User.objects.get_or_create(username='dr_bennani', defaults={'role': 'DOCTOR', 'first_name': 'Youssef', 'last_name': 'Bennani', 'email': 'y.bennani@medpredict.ma'})
    dr_bennani.set_password('password123')
    dr_bennani.save()
        
    dr_chaoui, _ = User.objects.get_or_create(username='dr_chaoui', defaults={'role': 'DOCTOR', 'first_name': 'Khadija', 'last_name': 'Chaoui', 'email': 'k.chaoui@medpredict.ma'})
    dr_chaoui.set_password('password123')
    dr_chaoui.save()

    # Create Patients
    patients_data = [
        {'cin': 'BJ123456', 'first_name': 'Lamine', 'last_name': 'Yamal', 'date_of_birth': '2007-07-13', 'gender': 'M', 'blood_group': 'O+', 'email': 'lamine@test.ma', 'phone': '+212600123456', 'city': 'Rabat'},
        {'cin': 'AB987654', 'first_name': 'Fatima', 'last_name': 'El Fassi', 'date_of_birth': '1985-05-12', 'gender': 'F', 'blood_group': 'A+', 'email': 'fatima.elfassi@test.ma', 'phone': '+212611223344', 'city': 'Casablanca'},
        {'cin': 'CD112233', 'first_name': 'Karim', 'last_name': 'Zouhair', 'date_of_birth': '1990-11-23', 'gender': 'M', 'blood_group': 'B-', 'email': 'karim.z@test.ma', 'phone': '+212698765432', 'city': 'Marrakech'},
        {'cin': 'EF445566', 'first_name': 'Amina', 'last_name': 'Berrada', 'date_of_birth': '1977-05-25', 'gender': 'F', 'blood_group': 'AB+', 'email': 'amina.berrada@test.ma', 'phone': '+212777777777', 'city': 'Fes'},
    ]
    
    patients = []
    for pd in patients_data:
        p, created = Patient.objects.get_or_create(cin=pd.get('cin'), defaults=pd)
        patients.append(p)
        print(f"Patient {p.first_name} {p.last_name} created.")

    today = date.today()

    # Create Appointments
    appointments_data = [
        {'patient': patients[0], 'doctor': dr_bennani, 'date': today, 'time': time(9, 0), 'reason': 'Consultation pédiatrique', 'status': 'COMPLETED'},
        {'patient': patients[1], 'doctor': dr_bennani, 'date': today, 'time': time(10, 30), 'reason': 'Douleurs articulaires', 'status': 'PLANNED'},
        {'patient': patients[2], 'doctor': dr_chaoui, 'date': today + timedelta(days=1), 'time': time(14, 0), 'reason': 'Suivi diabète', 'status': 'CONFIRMED'},
        {'patient': patients[3], 'doctor': dr_chaoui, 'date': today, 'time': time(11, 0), 'reason': 'Fatigue générale', 'status': 'COMPLETED'},
    ]
    
    apps = []
    for ad in appointments_data:
        a, created = Appointment.objects.get_or_create(
            patient=ad['patient'], doctor=ad['doctor'], date=ad['date'], time=ad['time'],
            defaults={'reason': ad['reason'], 'status': ad['status']}
        )
        apps.append(a)
    
    print("Appointments generated.")

    # Create Consultations and Prescriptions for COMPLETED appointment
    app_completed_1 = apps[0]
    c1, created = Consultation.objects.get_or_create(
        appointment=app_completed_1,
        defaults={
            'symptoms': 'fièvre, toux, fatigue',
            'clinical_examination': 'Température 39°C. Gorge très rouge.',
            'diagnosis': 'Angine bactérienne',
            'doctor_notes': 'Prélèvement effectué. Repos de 3 jours.',
            'ai_suggestions': {'predictions': [{'disease': 'Angine', 'confidence': 92}, {'disease': 'Covid-19', 'confidence': 45}]}
        }
    )
    
    if created:
        print("Consultation 1 generated.")
        Prescription.objects.get_or_create(
            consultation=c1,
            defaults={
                'medications': 'Amoxicilline 1g\nParacétamol 1000mg',
                'dosage': '1 comprimé\n1 comprimé en cas de fièvre',
                'posology': 'Amoxicilline: 1 comprimé matin et soir.\nParacétamol: maximum 3/jour.',
                'duration': '7 jours',
                'recommendations': 'Boire beaucoup d\'eau. Reste au chaud.'
            }
        )
        print("Prescription 1 generated.")

    print("Data seeding completed successfully!")

if __name__ == '__main__':
    run()
