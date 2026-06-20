import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from accounts.models import User
import requests

class ChatbotAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff_user',
            password='testpassword123',
            role='SECRETARY',
            first_name='Amina',
            last_name='Berrada'
        )
        self.url = reverse('chatbot-message')
        os.environ['GROQ_API_TOKEN'] = 'mock-chatbot-token'

    def test_chatbot_unauthenticated_blocked(self):
        response = self.client.post(self.url, {'message': 'Hello'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_chatbot_empty_message_rejected(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'message': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('accounts.views.requests.post')
    def test_chatbot_success(self, mock_post):
        self.client.force_authenticate(user=self.user)
        
        # Mock successful Groq response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Bonjour Amina! Comment puis-je vous aider aujourd'hui à la clinique ?"
                    }
                }
            ]
        }

        payload = {
            'message': 'Hello',
            'history': [
                {'type': 'bot', 'text': 'Welcome to MedPredict. How can I assist you today?'}
            ]
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reply', response.data)
        self.assertEqual(response.data['reply'], "Bonjour Amina! Comment puis-je vous aider aujourd'hui à la clinique ?")
