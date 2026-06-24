from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Consultation
from .serializers import ConsultationSerializer
import os
import json
import requests
from django.conf import settings
from accounts.permissions import IsDoctorOrAdmin

class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsDoctorOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['appointment__patient__first_name', 'appointment__patient__last_name', 'diagnosis']
    filterset_fields = ['appointment__doctor', 'appointment__patient']

    def get_queryset(self):
        qs = Consultation.objects.all().order_by('-date')
        user = self.request.user
        if user.is_authenticated and user.role == 'DOCTOR':
            return qs.filter(appointment__doctor=user)
        return qs

    @action(detail=False, methods=['post'], url_path='analyze-symptoms')
    def analyze_symptoms(self, request):
        symptoms = request.data.get('symptoms', [])
        if not symptoms:
            return Response({"error": "No symptoms provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            groq_token = os.environ.get('GROQ_API_TOKEN')
            if not groq_token:
                return Response(
                    {"predictions": [], "error": "Configuration error: GROQ_API_TOKEN is not configured."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            headers = {
                "Authorization": f"Bearer {groq_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a medical AI assistant. Predict the top 3 most likely diseases "
                            "based on the symptoms provided. Output your response as a JSON object matching this schema:\n"
                            "{\n"
                            "  \"predictions\": [\n"
                            "    {\"disease\": \"string\", \"confidence\": float}\n"
                            "  ]\n"
                            "}\n"
                            "Confidence should be a percentage between 0 and 100 representing probability. "
                            "Output ONLY the JSON object, with no other explanations or text."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Symptoms list: {', '.join(symptoms)}"
                    }
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=5.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Parse the assistant message content
            content_str = result['choices'][0]['message']['content']
            data = json.loads(content_str)
            data["disclaimer"] = "Outil d'aide - ne remplace pas le diagnostic médical"
            return Response(data, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            # Fail-safe mechanism
            return Response(
                {"predictions": [], "error": "AI Service unavailable", "details": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except (KeyError, json.JSONDecodeError) as e:
            return Response(
                {"predictions": [], "error": "AI Service returned invalid response format", "details": str(e)},
                status=status.HTTP_502_BAD_GATEWAY
            )
