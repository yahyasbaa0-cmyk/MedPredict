import datetime
import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
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

    def test_cancel_my_appointment_success(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('cancel-my-appointment', kwargs={'pk': self.appointment.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'CANCELLED')
        
        # Verify notification was created for doctor
        from accounts.models import Notification
        notification = Notification.objects.filter(recipient=self.doctor).first()
        self.assertIsNotNone(notification)
        self.assertIn("a annulé son rendez-vous", notification.message)

    def test_cancel_my_appointment_not_owner(self):
        other_patient_user = User.objects.create_user(
            username='YZ999999',
            password='password123',
            role='PATIENT'
        )
        Patient.objects.create(
            cin='YZ999999',
            first_name='Other',
            last_name='Patient',
            phone='0600000009',
            date_of_birth=datetime.date(1990, 1, 1),
            user=other_patient_user
        )
        self.client.force_authenticate(user=other_patient_user)
        url = reverse('cancel-my-appointment', kwargs={'pk': self.appointment.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_my_appointment_already_completed(self):
        self.appointment.status = 'COMPLETED'
        self.appointment.save()
        
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('cancel-my-appointment', kwargs={'pk': self.appointment.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unconfirmed_appointment_prevents_scheduling(self):
        from django.core.exceptions import ValidationError
        new_appointment = Appointment(
            patient=self.patient,
            doctor=self.doctor,
            date='2026-07-03',
            time='14:00',
            reason='Another consultation',
            status='PLANNED'
        )
        with self.assertRaises(ValidationError):
            new_appointment.clean()

    def test_doctor_patients_list_excludes_unconfirmed(self):
        self.client.force_authenticate(user=self.doctor)
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # Confirm the appointment
        self.appointment.status = 'CONFIRMED'
        self.appointment.save()

        # Doctor should see the patient now
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.patient.id)


class PasswordResetTestCase(APITestCase):
    def setUp(self):
        self.secretary = User.objects.create_user(
            username='secretary1',
            password='password123',
            role='SECRETARY'
        )
        self.patient_user = User.objects.create_user(
            username='patient1',
            password='password123',
            role='PATIENT'
        )
        self.reset_url = reverse('user-reset-password', kwargs={'pk': self.patient_user.pk})

    def test_secretary_can_reset_password(self):
        self.client.force_authenticate(user=self.secretary)
        response = self.client.post(self.reset_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['new_password'], 'patient12025')
        
        self.patient_user.refresh_from_db()
        self.assertTrue(self.patient_user.check_password('patient12025'))


class WhatsAppWebhookTestCase(APITestCase):
    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor3',
            password='password123',
            role='DOCTOR',
            first_name='Ali',
            last_name='Baddou'
        )
        self.patient_user = User.objects.create_user(
            username='GH123456',
            password='password123',
            role='PATIENT'
        )
        self.patient = Patient.objects.create(
            cin='GH123456',
            first_name='Karim',
            last_name='Alami',
            phone='212600000000',
            date_of_birth=datetime.date(1990, 1, 1),
            user=self.patient_user
        )
        self.webhook_url = reverse('whatsapp-webhook')

    def test_whatsapp_webhook_menu_greeting(self):
        data = {
            'Body': 'Bonjour',
            'From': 'whatsapp:+212600000000'
        }
        response = self.client.post(self.webhook_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Bienvenue chez *MedPredict*", response.content.decode('utf-8'))
        self.assertIn("Prendre un rendez-vous", response.content.decode('utf-8'))

    def test_whatsapp_webhook_option_one(self):
        data = {
            'Body': '1',
            'From': 'whatsapp:+212600000000'
        }
        response = self.client.post(self.webhook_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("http://localhost:5173/book", response.content.decode('utf-8'))

    def test_whatsapp_webhook_option_four(self):
        data = {
            'Body': '4',
            'From': 'whatsapp:+212600000000'
        }
        response = self.client.post(self.webhook_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Dr. Ali Baddou", response.content.decode('utf-8'))

