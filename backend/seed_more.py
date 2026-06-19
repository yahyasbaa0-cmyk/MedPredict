import os
import django
import random
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict_api.settings')
django.setup()

from patients.models import Patient
from appointments.models import Appointment
from consultations.models import Consultation
from accounts.models import User

print('Starting bulk seed...')

doctors = list(User.objects.filter(role='DOCTOR'))
if not doctors:
    # Fallback to creating a doctor if none exists
    doc = User.objects.create_user(username='dr_seed', email='doc@test.com', password='password123', first_name='Amine', last_name='Lahlou', role='DOCTOR')
    doctors = [doc]

first_names = ['Yassine', 'Sara', 'Omar', 'Karim', 'Aya', 'Khadija', 'Hassan', 'Meriem', 'Tariq', 'Mouna', 'Zineb', 'Nabil', 'Rania', 'Amine', 'Salma', 'Ilyas', 'Fatima', 'Zakaria', 'Mehdi', 'Nizar', 'Ines', 'Youssef', 'Nadia', 'Reda', 'Sana', 'Hamza', 'Imane']
last_names = ['Benjelloun', 'El Fassi', 'Bennis', 'Tazi', 'Guessous', 'Alami', 'Berrada', 'Iraqi', 'Sqalli', 'Chraibi', 'Kettani', 'Benkirane', 'Lahlou', 'El Amrani', 'Zeroual', 'Jazouli', 'Mernissi']
cities = ['Casablanca', 'Rabat', 'Marrakech', 'Fes', 'Tangier']
blood_groups = ['A+', 'O+', 'B+', 'AB+', 'O-']

import datetime
base_date = datetime.date(2026, 4, 1)

count = 0
for i in range(30):
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    p = Patient.objects.create(
        first_name=fn,
        last_name=ln,
        date_of_birth=f'19{random.randint(50, 99)}-0{random.randint(1,9)}-1{random.randint(0,9)}',
        gender=random.choice(['M', 'F']),
        phone=f'+2126{random.randint(10000000, 99999999)}',
        email=f'{fn.lower()}.{ln.lower()}{random.randint(1,100)}@example.ma',
        blood_group=random.choice(blood_groups),
        cin=f'{random.choice([