import os
import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from .models import WhatsAppSession, Appointment
from patients.models import Patient
from accounts.models import User

def send_outbound_whatsapp(to_phone, message_body):
    """
    Sends an outbound WhatsApp message using Twilio REST API.
    """
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    sender = os.environ.get('TWILIO_PHONE_NUMBER', 'whatsapp:+14155238886')

    if not account_sid or not auth_token:
        print("Twilio credentials are not configured in environment.")
        return None

    # Format destination phone number to ensure it has whatsapp: prefix
    if not to_phone.startswith('whatsapp:'):
        clean_num = to_phone.strip()
        if clean_num.startswith('0'):
            clean_num = '+212' + clean_num[1:]
        to_phone = f"whatsapp:{clean_num}"

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_body,
            from_=sender,
            to=to_phone
        )
        return message.sid
    except Exception as e:
        print(f"Failed to send outbound WhatsApp message: {e}")
        return None

@csrf_exempt
def whatsapp_webhook(request):
    """
    Webhook for handling Twilio WhatsApp messages.
    Provides a deterministic menu chatbot representing the 5 quick actions.
    """
    if request.method == 'POST':
        incoming_msg = request.POST.get('Body', '').strip().lower()
        sender_id = request.POST.get('From', '')

        resp = MessagingResponse()
        msg = resp.message()

        if not sender_id:
            return HttpResponse(str(resp))

        # Get or create session
        session, created = WhatsAppSession.objects.get_or_create(phone_number=sender_id)

        # 1. Identify Patient by Phone Number
        clean_phone = sender_id.replace('whatsapp:', '').strip()
        patient = None
        if len(clean_phone) >= 9:
            patient = Patient.objects.filter(phone__icontains=clean_phone[-9:]).first()

        # Define welcome menu text
        menu_text = (
            "Bienvenue chez *MedPredict*! 🏥\n"
            "Comment puis-je vous aider aujourd'hui ? Veuillez répondre avec le numéro de l'action souhaitée (1 à 5) :\n\n"
            "1️⃣ *Prendre un rendez-vous* (Book Appointment)\n"
            "2️⃣ *Suivre mes rendez-vous* (Track Appointment)\n"
            "3️⃣ *Créneaux disponibles* (Available Times)\n"
            "4️⃣ *Médecins disponibles* (Available Doctors)\n"
            "5️⃣ *Gérer mes rendez-vous* (Manage Appointment)\n\n"
            "Tapez *Menu* à tout moment pour afficher cette liste."
        )

        # Menu Route logic
        if incoming_msg in ['menu', 'bonjour', 'hello', 'salut', 'hi', 'start', 'recommencer']:
            msg.body(menu_text)
            return HttpResponse(str(resp), content_type='text/xml')

        if incoming_msg == '1':
            # Action 1: Book Appointment
            reply = (
                "📅 *Prendre un rendez-vous*\n\n"
                "Pour réserver une consultation en quelques clics, veuillez utiliser notre portail de réservation en ligne :\n"
                "🔗 http://localhost:5173/book"
            )
            msg.body(reply)

        elif incoming_msg == '2':
            # Action 2: Track Appointment
            if not patient:
                reply = (
                    "📋 *Suivre mes rendez-vous*\n\n"
                    "Votre numéro de téléphone n'est pas associé à un dossier patient enregistré.\n\n"
                    "Si vous êtes déjà patient, veuillez vous connecter à votre Espace Patient en ligne pour suivre vos rendez-vous :\n"
                    "🔗 http://localhost:5173/my-appointments"
                )
                msg.body(reply)
            else:
                appts = Appointment.objects.filter(patient=patient).order_by('-date', '-time')
                if not appts.exists():
                    reply = (
                        f"Bonjour {patient.first_name}! 📋\n\n"
                        "Vous n'avez aucun rendez-vous enregistré pour le moment.\n"
                        "Pour en réserver un, tapez *1*."
                    )
                    msg.body(reply)
                else:
                    upcoming = appts.exclude(status__in=['CANCELLED', 'COMPLETED'])
                    past = appts.filter(status__in=['CANCELLED', 'COMPLETED'])

                    reply = f"Bonjour {patient.first_name}! 📋\n*Vos Rendez-vous* ({appts.count()} au total) :\n\n"

                    if upcoming.exists():
                        reply += "🟢 *À venir :*\n"
                        for i, a in enumerate(upcoming):
                            doctor_name = f"Dr. {a.doctor.first_name} {a.doctor.last_name}"
                            reply += f"{i+1}. {a.date.strftime('%d/%m/%Y')} à {a.time.strftime('%H:%M')} — {doctor_name} ({a.get_status_display()})\n"
                        reply += "\n"

                    if past.exists():
                        reply += "📁 *Historique (3 derniers) :*\n"
                        for i, a in enumerate(past[:3]):
                            reply += f"- {a.date.strftime('%d/%m/%Y')} — {a.get_status_display()}\n"
                    
                    msg.body(reply)

        elif incoming_msg == '3':
            # Action 3: Available Times
            doctors = User.objects.filter(role='DOCTOR')
            if not doctors.exists():
                msg.body("⚠️ Aucun médecin n'est disponible actuellement.")
            else:
                tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                reply = f"🕐 *Créneaux disponibles pour demain ({tomorrow.strftime('%d/%m/%Y')}) :*\n\n"
                
                # Fetch slots for first 3 doctors
                for doc in doctors[:3]:
                    # Standard slots
                    all_slots = ['09:00', '09:30', '10:00', '11:00', '14:00', '15:30', '16:00', '17:00']
                    booked_appointments = Appointment.objects.filter(
                        doctor=doc, 
                        date=tomorrow
                    ).exclude(status='CANCELLED')
                    
                    booked_times = [appt.time.strftime('%H:%M') for appt in booked_appointments]
                    available_slots = [slot for slot in all_slots if slot not in booked_times]
                    
                    reply += f"👨‍⚕️ *Dr. {doc.first_name} {doc.last_name}* :\n"
                    if available_slots:
                        reply += f"   {', '.join(available_slots)}\n\n"
                    else:
                        reply += "   ❌ Complet\n\n"
                
                reply += "Pour réserver un créneau, tapez *1*."
                msg.body(reply)

        elif incoming_msg == '4':
            # Action 4: Available Doctors
            doctors = User.objects.filter(role='DOCTOR')
            if not doctors.exists():
                msg.body("⚠️ Aucun médecin n'est enregistré pour le moment.")
            else:
                reply = f"👨‍⚕️ *Notre Équipe Médicale* ({doctors.count()} médecins) :\n\n"
                for i, doc in enumerate(doctors):
                    reply += f"{i+1}. *Dr. {doc.first_name} {doc.last_name}*\n"
                    reply += "   🏥 Médecine Générale\n\n"
                
                reply += "Pour prendre un rendez-vous avec un médecin, tapez *1*."
                msg.body(reply)

        elif incoming_msg == '5':
            # Action 5: Manage Appointment
            reply = (
                "⚙️ *Gérer vos Rendez-vous*\n\n"
                "Pour annuler ou modifier l'heure de votre rendez-vous, veuillez :\n"
                "• 🖥️ Accéder à votre Espace Patient : http://localhost:5173/my-appointments\n"
                "• 📞 Contacter directement le secrétariat de la clinique"
            )
            msg.body(reply)

        else:
            # Fallback when message doesn't match options
            fallback_text = (
                "Désolé, je n'ai pas compris. 🤖\n"
                "Veuillez répondre avec le numéro de l'action souhaitée (1 à 5) :\n\n"
                "1️⃣ Prendre un rendez-vous\n"
                "2️⃣ Suivre mes rendez-vous\n"
                "3️⃣ Créneaux disponibles\n"
                "4️⃣ Médecins disponibles\n"
                "5️⃣ Gérer mes rendez-vous\n\n"
                "Tapez *Menu* à tout moment pour afficher cette liste."
            )
            msg.body(fallback_text)

        return HttpResponse(str(resp), content_type='text/xml')

    return HttpResponse("Méthode non autorisée.", status=405)
