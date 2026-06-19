from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import HttpResponse
from .models import Prescription
from .serializers import PrescriptionSerializer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def get_queryset(self):
        qs = Prescription.objects.all().order_by('-created_at')
        user = self.request.user
        if user.is_authenticated and user.role == 'DOCTOR':
            return qs.filter(consultation__appointment__doctor=user)
        return qs

    @action(detail=True, methods=['get'], url_path='export-pdf')
    def export_pdf(self, request, pk=None):
        prescription = self.get_object()
        patient = prescription.consultation.appointment.patient
        doctor = request.user if hasattr(request.user, 'role') and request.user.role == 'DOCTOR' else prescription.consultation.appointment.doctor

        # Générer PDF avec ReportLab
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # En-tête (Header)
        p.setFillColor(colors.HexColor('#2563eb'))
        p.rect(0, height - 80, width, 80, fill=1, stroke=0)
        
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 22)
        p.drawString(40, height - 40, "CABINET MÉDICAL MEDPREDICT")
        p.setFont("Helvetica", 10)
        p.drawString(40, height - 60, "Spécialité : Médecine Générale & IA Assistée")
        
        # Infos Docteur (Right aligned)
        p.setFillColor(colors.HexColor('#111827'))
        p.setFont("Helvetica-Bold", 12)
        p.drawRightString(width - 40, height - 120, f"Dr. {doctor.first_name} {doctor.last_name}")
        p.setFont("Helvetica", 10)
        p.drawRightString(width - 40, height - 135, f"Email: {doctor.email}")
        p.drawRightString(width - 40, height - 150, "Ordre National des Médecins: 12345/M")
        
        # Ligne de séparation
        p.setStrokeColor(colors.lightgrey)
        p.line(40, height - 170, width - 40, height - 170)
        
        # Infos Patient
        p.setFont("Helvetica", 11)
        p.drawString(40, height - 200, f"Patient(e) : {patient.first_name} {patient.last_name}")
        p.drawString(40, height - 220, f"Date de naissance : {patient.date_of_birth}")
        if patient.cin:
            p.drawString(40, height - 240, f"CIN : {patient.cin}")
        
        # Date and Location
        city = getattr(patient, 'city', 'Casablanca')
        p.drawRightString(width - 40, height - 200, f"Le {prescription.created_at.strftime('%d/%m/%Y')}")
        p.drawRightString(width - 40, height - 220, f"Fait à {city}")
        
        # Titre ORDONNANCE
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(colors.HexColor('#2563eb'))
        p.drawCentredString(width / 2.0, height - 280, "ORDONNANCE MÉDICALE")
        
        # Ligne de séparation
        p.setStrokeColor(colors.HexColor('#2563eb'))
        p.setLineWidth(2)
        p.line(width / 2.0 - 100, height - 290, width / 2.0 + 100, height - 290)
        
        # Contenu
        p.setFillColor(colors.HexColor('#111827'))
        p.setFont("Helvetica", 11)
        textobject = p.beginText(40, height - 330)
        textobject.setLeading(18)
        
        textobject.setFont("Helvetica-Bold", 12)
        textobject.textLine("LISTE DES MÉDICAMENTS :")
        textobject.setFont("Helvetica", 11)
        
        meds = prescription.medications.split('\n')
        dosages = prescription.dosage.split('\n')
        
        for i in range(len(meds)):
            med = meds[i].strip() if i < len(meds) else ""
            dos = dosages[i].strip() if i < len(dosages) else ""
            if med:
                textobject.textLine(f"• {med}    ---    {dos}")
        
        textobject.textLine("")
        textobject.setFont("Helvetica-Bold", 12)
        textobject.textLine("POSOLOGIE DÉTAILLÉE :")
        textobject.setFont("Helvetica", 11)
        for line in prescription.posology.split('\n'):
            textobject.textLine(f"{line.strip()}")
            
        textobject.textLine("")
        textobject.setFont("Helvetica-Bold", 12)
        textobject.textLine("DURÉE DU TRAITEMENT :")
        textobject.setFont("Helvetica", 11)
        textobject.textLine(f"{prescription.duration}")
        
        if prescription.recommendations:
            textobject.textLine("")
            textobject.setFont("Helvetica-Bold", 12)
            textobject.textLine("RECOMMANDATIONS :")
            textobject.setFont("Helvetica", 11)
            for line in prescription.recommendations.split('\n'):
                textobject.textLine(f"{line.strip()}")
                
        p.drawText(textobject)
        
        # Signature
        p.setFont("Helvetica-Bold", 12)
        p.drawRightString(width - 40, 150, "Signature & Cachet du médecin")
        
        # Footer
        p.setFillColor(colors.grey)
        p.setFont("Helvetica", 8)
        p.drawCentredString(width / 2.0, 30, "Document généré par MedPredict - La plateforme médicale intelligente")
        p.drawCentredString(width / 2.0, 20, "Veuillez conserver ce document. Il ne peut être délivré qu'une seule fois.")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        filename = f"Ordonnance_{patient.last_name}_{prescription.created_at.strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
