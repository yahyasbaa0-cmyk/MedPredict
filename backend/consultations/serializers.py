from rest_framework import serializers
from .models import Consultation
from appointments.serializers import AppointmentSerializer

class ConsultationSerializer(serializers.ModelSerializer):
    appointment_details = AppointmentSerializer(source='appointment', read_only=True)
    
    class Meta:
        model = Consultation
        fields = '__all__'
