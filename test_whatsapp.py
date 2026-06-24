import requests
import json

URL = "http://localhost:8000/api/appointments/whatsapp/webhook/"

def send_message(body, phone="whatsapp:+212600000000"):
    data = {
        "Body": body,
        "From": phone
    }
    response = requests.post(URL, data=data)
    print(f"\n======================================")
    print(f"💬 Sent: '{body}'")
    print(f"======================================")
    print(response.text)
    return response

# Test new flow with the 5 quick actions
send_message("bonjour")
send_message("1")  # Prendre un rendez-vous (Book)
send_message("2")  # Suivre mes rendez-vous (Track)
send_message("3")  # Créneaux disponibles (Slots)
send_message("4")  # Médecins disponibles (Doctors)
send_message("5")  # Gérer mes rendez-vous (Manage)
send_message("invalid_option")  # Test fallback fallback text
