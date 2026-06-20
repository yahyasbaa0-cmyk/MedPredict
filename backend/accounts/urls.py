from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, NotificationViewSet, chatbot_message
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('chatbot/', chatbot_message, name='chatbot-message'),
]
