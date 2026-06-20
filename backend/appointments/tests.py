import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from patients.models import Patient
from appointments.models import Appointment

class PublicBookingTestCase(APITestCase):
    def setUp(self):
        # Create a doctor
        self.doctor = User.objects.create_user(
            username='doctor1',
            password='password123',
            role='DOCTOR',
            first_name='John',
            last_name='Doe'
        )
        self.book_url = reverse('public-book-appointment')

    def test_public_booking_creates_account(self):
        data = {
            'doctor_id': self.doctor.id,
            'date': '2026-07-01',
            'time': '09:00',
            'reason': 'Checkup',
            'cin': 'AB123456',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'phone': '0600000001',
            'gender': 'F',
            'date_of_birth': '1995-05-15'
        }
        
        # Verify no user with username 'AB123456' exists
        self.assertFalse(User.objects.filter(username='AB123456').exists())
        
        response = self.client.post(self.book_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['account_created'])
        self.assertEqual(response.data['account_username'], 'AB123456')
        self.assertEqual(response.data['account_password'], 'AB1234562025')
        self.assertFalse(response.data['has_existing_account'])

        # Verify User and Patient models are created and linked
        user = User.objects.get(username='AB123456')
        self.assertEqual(user.role, 'PATIENT')
        self.assertEqual(user.first_name, 'Alice')
        self.assertEqual(user.last_name, 'Smith')

        patient = Patient.objects.get(cin='AB123456')
        self.assertEqual(patient.user, user)

    def test_public_booking_uses_existing_account(self):
        # First, pre-create the patient and user account
        user = User.objects.create_user(
            username='CD789012',
            password='CD7890122025',
            role='PATIENT',
            first_name='Bob',
            last_name='Brown'
        )
        patient = Patient.objects.create(
            cin='CD789012',
            first_name='Bob',
            last_name='Brown',
            phone='0600000002',
            date_of_birth=datetime.date(1990, 1, 1),
            user=user
        )

        data = {
            'doctor_id': self.doctor.id,
            'date': '2026-07-01',
            'time': '10:00',
            'reason': 'Follow-up',
            'cin': 'CD789012',
            'first_name': 'Bob',
            'last_name': 'Brown',
            'phone': '0600000002',
            'gender': 'M',
            'date_of_birth': '1990-01-01'
        }

        response = self.client.post(self.book_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['account_created'])
        self.assertTrue(response.data['has_existing_account'])

        # Verify no new user was created
        self.assertEqual(User.objects.filter(username='CD789012').count(), 1)


class PatientAppointmentsTestCase(APITestCase):
    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor2',
            password='password123',
            role='DOCTOR',
            first_name='Sarah',
            last_name='Connor'
        )
        self.patient_user = User.objects.create_user(
            username='EF345678',
            password='password123',
            role='PATIENT',
            first_name='David',
            last_name='Webb'
        )
        self.patient = Patient.objects.create(
            cin='EF345678',
            first_name='David',
            last_name='Webb',
            phone='0600000003',
            date_of_birth=datetime.date(1990, 1, 1),
            user=self.patient_user
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date='2026-07-02',
            time='11:00',
            reason='Consultation',
            status='PLANNED'
        )
        self.my_appointments_url = reverse('my-appointments')

    def test_my_appointments_authenticated(self):
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get(self.my_appointments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.appointment.id)
        self.assertEqual(response.data[0]['reason'], 'Consultation')

    def test_my_appointments_anonymous_denied(self):
        response = self.client.get(self.my_appointments_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_appointments_staff_denied(self):
        self.client.force_authenticate(user=self.doctor)
        response = self.client.get(self.my_appointments_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
