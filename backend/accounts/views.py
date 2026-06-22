from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from .models import User, Notification
from .serializers import UserSerializer, NotificationSerializer
import os
import json
import requests

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'ADMIN'

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsAdmin]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['patch'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def chatbot_message(request):
    message = request.data.get('message', '')
    history = request.data.get('history', [])
    if not message:
        return Response({'error': 'No message provided'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        groq_token = os.environ.get('GROQ_API_TOKEN')
        if not groq_token:
            return Response(
                {'error': 'Configuration error: GROQ_API_TOKEN is not configured.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        headers = {
            "Authorization": f"Bearer {groq_token}",
            "Content-Type": "application/json"
        }
        
        # Build prompt with role context
        user_role = getattr(request.user, 'role', 'SECRETARY')
        user_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        
        # Format conversation history
        messages_payload = [
            {
                "role": "system",
                "content": (
                    "You are MedPredict Assistant, a friendly and professional medical AI assistant at the MedPredict clinic. "
                    f"You are talking to {user_name} who has the role of {user_role} at the clinic. "
                    "Help them with clinic operations, scheduling, administrative questions, or patient support. "
                    "Keep your responses concise, professional, and directly helpful. Do not mention system details, "
                    "tokens, or internal APIs."
                )
            }
        ]
        
        # Add history (last 5 messages for context)
        for h in history[-5:]:
            role = "user" if h.get('type') == 'user' else "assistant"
            messages_payload.append({
                "role": role,
                "content": h.get('text', '')
            })
            
        # Add current message
        messages_payload.append({
            "role": "user",
            "content": message
        })
        
        payload = {
            "model": "llama3-70b-8192",
            "messages": messages_payload,
            "temperature": 0.7,
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10.0
        )
        response.raise_for_status()
        result = response.json()
        
        reply = result['choices'][0]['message']['content']
        return Response({'reply': reply}, status=status.HTTP_200_OK)
        
    except requests.exceptions.RequestException as e:
        return Response(
            {'reply': "Désolé, je rencontre des difficultés temporaires pour contacter mon service d'intelligence. Veuillez réessayer."},
            status=status.HTTP_200_OK
        )
