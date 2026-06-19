import json
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from .models import WhatsAppSession, Appointment
from patients.models import Patient
from accounts.models import User

def format_date(date_str):
    try:
        # Tries to parse DD/MM/YYYY
        date_obj = datetime.strptime(date_str.strip(), "%d/%m/%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return None

def format_time(time_str):
    try:
        # Tries to parse HH:MM
        time_obj = datetime.strptime(time_str.strip(), "%H:%M")
        return time_obj.strftime("%H:%M:%S")
    except ValueError:
        return None

@csrf_exempt
def whatsapp_webhook(request):
    """
    Webhook for handling Twilio WhatsApp messages.
    Maintains conversation state in WhatsAppSession model.
    """
    if request.method == 'POST':
        incoming_msg = request.POST.get('Body', '').strip().lower()
        sender_id = request.POST.get('From', '')

        # Create Twilio response
        resp = MessagingResponse()
        msg = resp.message()

        if not sender_id:
            return HttpResponse(str(resp))

        # Get or create session
        session, created = WhatsAppSession.objects.get_or_create(phone_number=sender_id)
        state = session.state

        # Restart conversation if user says "bonjour", "hello", "menu", "annuler"
        if incoming_msg in ['bonjour', 'hello', 'salut', 'menu', 'annuler', 'quitter']:
            session.state = 'START'
            session.data = {}
            session.save()
            msg.body("Bienvenue chez *MedPredict*! 🏥\nJe suis l'assistant virtuel.\nVoulez-vous prendre un rendez-vous médical ?\nRépondez par *OUI* ou *NON*.")
            return HttpResponse(str(resp))

        # STATE MACHINE
        if state == 'START':
            if incoming_msg == 'oui':
                session.state = 'ASK_CIN'
                session.save()
                msg.body("Parfait! Veuillez entrer votre *Numéro de CIN* (ex: AB123456) :")
            elif incoming_msg == 'non':
                msg.body("D'accord. Si vous avez besoin de quoi que ce soit, n'hésitez pas à me dire *Bonjour* ! 👋")
            else:
                msg.body("Je n'ai pas compris. Veuillez répondre par *OUI* ou *NON*.")

        elif state == 'ASK_CIN':
            cin = incoming_msg.upper()
            session.data['cin'] = cin
            
            # Check if patient exists
            try:
                patient = Patient.objects.get(cin=cin)
                session.data['patient_id'] = patient.id
                session.state = 'ASK_DOCTOR'
                session.save()
                msg.body(f"Content de vous revoir, {patient.first_name}! 👋\nQuel médecin souhaitez-vous consulter ?\n*1.* Dr. Bennani\n*2.* Dr. Chaoui\nRépondez par 1 ou 2.")
            except Patient.DoesNotExist:
                session.state = 'ASK_FIRST_NAME'
                session.save()
                msg.body("Je vois que vous êtes nouveau! Bienvenue. 😊\nQuel est votre *prénom* ?")

        elif state == 'ASK_FIRST_NAME':
            session.data['first_name'] = incoming_msg.capitalize()
            session.state = 'ASK_LAST_NAME'
            session.save()
            msg.body("Merci. Quel est votre *nom de famille* ?")

        elif state == 'ASK_LAST_NAME':
            session.data['last_name'] = incoming_msg.upper()
            
            # Create the patient in DB with defaults for required fields
            new_patient = Patient.objects.create(
                first_name=session.data['first_name'],
                last_name=session.data['last_name'],
                cin=session.data['cin'],
                phone=sender_id.replace('whatsapp:', ''),
                date_of_birth='1990-01-01', # Default
                gender='O' # Autre par défaut
            )
            session.data['patient_id'] = new_patient.id
            
            session.state = 'ASK_DOCTOR'
            session.save()
            msg.body("Dossier créé avec succès! ✅\nQuel médecin souhaitez-vous consulter ?\n*1.* Dr. Bennani\n*2.* Dr. Chaoui\nRépondez par 1 ou 2.")

        elif state == 'ASK_DOCTOR':
            if incoming_msg == '1':
                session.data['doctor_username'] = 'dr_bennani'
                session.state = 'ASK_DATE'
                session.save()
                msg.body("Vous avez choisi le *Dr. Bennani*. 👨‍⚕️\nPour quelle date souhaitez-vous le rendez-vous ?\nFormat requis : *JJ/MM/AAAA* (ex: 25/12/2026)")
            elif incoming_msg == '2':
                session.data['doctor_username'] = 'dr_chaoui'
                session.state = 'ASK_DATE'
                session.save()
                msg.body("Vous avez choisi le *Dr. Chaoui*. 👩‍⚕️\nPour quelle date souhaitez-vous le rendez-vous ?\nFormat requis : *JJ/MM/AAAA* (ex: 25/12/2026)")
            else:
                msg.body("Veuillez répondre par *1* pour Dr. Bennani ou *2* pour Dr. Chaoui.")

        elif state == 'ASK_DATE':
            formatted_date = format_date(incoming_msg)
            if formatted_date:
                session.data['date'] = formatted_date
                session.state = 'ASK_TIME'
                session.save()
                msg.body("Date enregistrée! 📅\nÀ quelle heure souhaitez-vous venir ?\nFormat requis : *HH:MM* (ex: 10:30 ou 15:00)")
            else:
                msg.body("Format de date invalide. ❌\nVeuillez utiliser le format *JJ/MM/AAAA* (ex: 25/12/2026).")

        elif state == 'ASK_TIME':
            formatted_time = format_time(incoming_msg)
            if formatted_time:
                session.data['time'] = formatted_time
                
                try:
                    # Retrieve the selected doctor and patient
                    doctor = User.objects.get(username=session.data['doctor_username'])
                    patient = Patient.objects.get(id=session.data['patient_id'])
                    
                    # Create the appointment
                    appointment = Appointment(
                        patient=patient,
                        doctor=doctor,
                        date=session.data['date'],
                        time=session.data['time'],
                        reason="Rendez-vous pris via WhatsApp",
                        status="PLANNED"
                    )
                    appointment.save() # Will run the .clean() validation
                    
                    # Reset state
                    session.state = 'START'
                    session.data = {}
                    session.save()
                    
                    # Send confirmation
                    date_display = datetime.strptime(appointment.date, "%Y-%m-%d").strftime("%d/%m/%Y")
                    time_display = datetime.strptime(appointment.time, "%H:%M:%S").strftime("%H:%M")
                    msg.body(f"🎉 *Rendez-vous Confirmé !*\n\nPatient: {patient.first_name} {patient.last_name}\nMédecin: Dr. {doctor.last_name}\nDate: {date_display}\nHeure: {time_display}\n\nMerci d'avoir utilisé MedPredict. À bientôt! 👋")
                    
                except Exception as e:
                    # If validation fails (e.g., doctor is full, double booking)
                    msg.body(f"❌ Impossible de créer le rendez-vous.\nRaison : {str(e)}\n\nVeuillez choisir une autre date ou heure.\nFormat : *JJ/MM/AAAA* pour changer de date, ou tapez *Annuler*.")
                    session.state = 'ASK_DATE'
                    session.save()
            else:
                msg.body("Format d'heure invalide. ❌\nVeuillez utiliser le format *HH:MM* (ex: 10:30).")

        return HttpResponse(str(resp), content_type='text/xml')

    return HttpResponse("Méthode non autorisée.", status=405)
