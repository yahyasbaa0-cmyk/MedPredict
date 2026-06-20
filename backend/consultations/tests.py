from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from accounts.models import User
import requests

class ConsultationAIIntegrationTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user(
            username='doctor_test', 
            password='testpassword123',
            role='DOCTOR'
        )
        self.client.force_authenticate(user=self.user)
        self.url = '/api/consultations/analyze-symptoms/'
        
        import os
        os.environ['GROQ_API_TOKEN'] = 'mock-groq-token'

    @patch('consultations.views.requests.post')
    def test_analyze_symptoms_success(self, mock_post):
        # Setup mock to return a successful response matching Groq format
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"predictions": [{"disease": "Common Cold", "confidence": 85.0}, {"disease": "Flu", "confidence": 10.0}]}'
                    }
                }
            ]
        }
        
        data = {'symptoms': ['Cough', 'Fever']}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('predictions', response.data)
        self.assertEqual(response.data['predictions'][0]['disease'], 'Common Cold')

    @patch('consultations.views.requests.post')
    def test_analyze_symptoms_ai_service_down(self, mock_post):
        # Simulate a connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Failed to connect")
        
        data = {'symptoms': ['Cough', 'Fever']}
        response = self.client.post(self.url, data, format='json')
        
        # Verify fail-safe handles the exception and returns 503 Service Unavailable
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'AI Service unavailable')
        self.assertEqual(response.data['predictions'], [])
