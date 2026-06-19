from rest_framework import serializers
from .models import Prescription
from consultations.serializers import ConsultationSerializer

class PrescriptionSerializer(serializers.ModelSerializer):
    consultation_details = ConsultationSerializer(source='consultation', read_only=True)
    
    class Meta:
        model = Prescription
        fields = '__all__'
