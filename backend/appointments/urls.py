from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, public_book_appointment, get_public_doctors, get_available_slots
from .whatsapp_views import whatsapp_webhook

router = DefaultRouter()
router.register(r'', AppointmentViewSet)

urlpatterns = [
    path('public/book/', public_book_appointment, name='public-book-appointment'),
    path('public/doctors/', get_public_doctors, name='public-doctors'),
    path('public/available-slots/', get_available_slots, name='public-available-slots'),
    path('whatsapp/webhook/', whatsapp_webhook, name='whatsapp-webhook'),
    path('', include(router.urls)),
]
