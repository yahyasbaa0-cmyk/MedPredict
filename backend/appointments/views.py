from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Appointment
from .serializers import AppointmentSerializer
from patients.models import Patient
from accounts.models import User, Notification
from accounts.permissions import IsAdminOrDoctorOrSecretary
import datetime

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAdminOrDoctorOrSecretary]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__last_name', 'reason']
    filterset_fields = ['status', 'date', 'doctor']

    def get_queryset(self):
        qs = Appointment.objects.all().order_by('-date', '-time')
        user = self.request.user
        if user.is_authenticated and user.role == 'DOCTOR':
            return qs.filter(doctor=user)
        return qs

    def perform_create(self, serializer):
        appointment = serializer.save()
        if appointment.doctor != self.request.user:
            Notification.objects.create(
                recipient=appointment.doctor,
                message=f"Nouveau rendez-vous planifié avec {appointment.patient.first_name} {appointment.patient.last_name} le {appointment.date} à {appointment.time}."
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def public_book_appointment(request):
    try:
        data = request.data
        
        # 1. Get or Create Patient
        cin = data.get('cin')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone')
        
        if not all([cin, first_name, last_name, phone]):
            return Response({'error': 'Veuillez remplir toutes les informations personnelles.'}, status=status.HTTP_400_BAD_REQUEST)

        patient, created = Patient.objects.get_or_create(
            cin=cin,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'gender': data.get('gender', 'O'),
                'date_of_birth': data.get('date_of_birth', '2000-01-01') # Default if not provided
            }
        )

        # 2. Create Appointment
        doctor_id = data.get('doctor_id')
        date = data.get('date')
        time = data.get('time')
        reason = data.get('reason', 'Consultation médicale')

        if not all([doctor_id, date, time]):
            return Response({'error': 'Veuillez sélectionner un médecin, une date et une heure.'}, status=status.HTTP_400_BAD_REQUEST)

        doctor = User.objects.get(id=doctor_id, role='DOCTOR')
        
        appointment = Appointment(
            patient=patient,
            doctor=doctor,
            date=date,
            time=time,
            reason=reason,
            status='PLANNED'
        )
        appointment.clean() # Runs validation (like double booking check)
        appointment.save()

        Notification.objects.create(
            recipient=doctor,
            message=f"Nouveau rendez-vous (patient externe) planifié avec {patient.first_name} {patient.last_name} le {date} à {time}."
        )

        # 3. Auto-create patient account if they don't have one
        account_created = False
        account_username = None
        account_password = None

        if not patient.user:
            # Check if a user with this CIN as username already exists
            if not User.objects.filter(username=cin).exists():
                password = f"{cin}2025"
                user_account = User.objects.create_user(
                    username=cin,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    email=data.get('email', ''),
                    phone=phone,
                    role='PATIENT'
                )
                patient.user = user_account
                patient.save()
                account_created = True
                account_username = cin
                account_password = password

        return Response({
            'message': 'Rendez-vous confirmé avec succès.',
            'appointment_id': appointment.id,
            'account_created': account_created,
            'account_username': account_username,
            'account_password': account_password,
            'has_existing_account': patient.user is not None and not account_created,
        }, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        return Response({'error': 'Médecin introuvable.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_doctors(request):
    doctors = User.objects.filter(role='DOCTOR')
    data = [{'id': d.id, 'first_name': d.first_name, 'last_name': d.last_name, 'specialty': 'Médecine Générale'} for d in doctors]
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_slots(request):
    doctor_id = request.query_params.get('doctor_id')
    date_str = request.query_params.get('date')
    
    if not doctor_id or not date_str:
        return Response({'error': 'Veuillez fournir doctor_id et date.'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        doctor = User.objects.get(id=doctor_id, role='DOCTOR')
    except User.DoesNotExist:
        return Response({'error': 'Médecin introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        
    # Standard slots
    all_slots = ['09:00', '09:30', '10:00', '11:00', '14:00', '15:30', '16:00', '17:00']
    
    # Get booked appointments for this doctor on this date
    booked_appointments = Appointment.objects.filter(
        doctor=doctor, 
        date=date_str
    ).exclude(status='CANCELLED')
    
    if booked_appointments.count() >= len(all_slots):
        return Response([]) # Day is full
        
    booked_times = [appt.time.strftime('%H:%M') for appt in booked_appointments]
    
    available_slots = [slot for slot in all_slots if slot not in booked_times]
    
    return Response(available_slots)

@api_view(['GET'])
def my_appointments(request):
    """Return all appointments for the authenticated patient."""
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'Non authentifié.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if user.role != 'PATIENT':
        return Response({'error': 'Accès réservé aux patients.'}, status=status.HTTP_403_FORBIDDEN)
    
    # Find the patient profile linked to this user
    if not hasattr(user, 'patient_profile') or user.patient_profile is None:
        return Response({'error': 'Aucun dossier patient lié à ce compte.'}, status=status.HTTP_404_NOT_FOUND)
    
    patient = user.patient_profile
    appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-time')
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)
