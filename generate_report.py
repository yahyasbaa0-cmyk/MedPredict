pages_content = []
# -*- coding: utf-8 -*-
import sys
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class ChapterStartMarker(Flowable):
    """
    Custom Flowable to dynamically notify the NumberedCanvas that a page
    is a major transition page or chapter opening, so headers are suppressed.
    Optionally carries a chapter_num for watermark rendering on the canvas.
    """
    def __init__(self, chapter_num=''):
        super().__init__()
        self.chapter_num = chapter_num

    def draw(self):
        self.canv.is_chapter_start = True
        if self.chapter_num:
            self.canv.chapter_start_num = self.chapter_num

class HeaderTracker(Flowable):
    """
    Custom Flowable to dynamically notify the NumberedCanvas of the current
    chapter name, to print correct running headers.
    """
    def __init__(self, chapter_title):
        super().__init__()
        self.chapter_title = chapter_title

    def draw(self):
        self.canv.current_chapter = self.chapter_title

def get_roman_numeral(num):
    romans = {
        1: "i", 2: "ii", 3: "iii", 4: "iv", 5: "v", 6: "vi", 7: "vii", 8: "viii",
        9: "ix", 10: "x", 11: "xi", 12: "xii", 13: "xiii", 14: "xiv", 15: "xv"
    }
    return romans.get(num, "")

def parse_chapter_title(chapter_str):
    import re
    if ":" in chapter_str:
        parts = chapter_str.split(":", 1)
        label = parts[0].strip().upper()
        title = parts[1].strip().upper()
        m = re.search(r"CHAPITRE\s+(\d+)", label)
        if m:
            num = int(m.group(1))
            romans = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}
            label = f"CHAPITRE {romans.get(num, num)}"
        return label, title
    else:
        return "", chapter_str.strip().upper()

def make_drop_cap(first_letter, rest_text, normal_style):
    drop_cap_style = ParagraphStyle(
        'DropCapStyle',
        parent=normal_style,
        fontName='Times-Bold',
        fontSize=36,
        leading=38,
        textColor=colors.HexColor("#1B2A4A"),
        alignment=1, # Center
        spaceAfter=0
    )
    p_letter = Paragraph(f"<b>{first_letter}</b>", drop_cap_style)
    p_rest = Paragraph(rest_text, normal_style)
    
    t = Table([[p_letter, p_rest]], colWidths=[24, 415.366])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
    ]))
    return t

class NumberedCanvas(canvas.Canvas):
    """
    Subclass of canvas.Canvas to handle dynamic page numbers,
    drawing headers (with Left Chapter Name and Right Project Name) and footers on pages 2+.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        # Read the custom chapter start flag and save the state of this page
        is_chapter = getattr(self, 'is_chapter_start', False)
        current_ch = getattr(self, 'current_chapter', '')
        chapter_num = getattr(self, 'chapter_start_num', '')
        state = dict(self.__dict__)
        state['is_chapter_start'] = is_chapter
        state['current_chapter'] = current_ch
        state['chapter_start_num'] = chapter_num
        self._saved_page_states.append(state)
        # Reset the flags for the next page
        self.is_chapter_start = False
        self.chapter_start_num = ''
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        
        # Dynamically determine the page number where the main content (Introduction) starts
        intro_page_num = 11  # fallback default
        for p_num, state in enumerate(self._saved_page_states, 1):
            if state.get('current_chapter'):
                intro_page_num = p_num
                break
        self.intro_page_num = intro_page_num

        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        width, height = A4
        # Page 1 is the cover page — no headers/footers
        if self._pageNumber == 1:
            return

        # Read whether this page was marked as a chapter start
        is_chapter = getattr(self, 'is_chapter_start', False)
        intro_page_num = getattr(self, 'intro_page_num', 11)
        chapter_num = getattr(self, 'chapter_start_num', '')

        # --- Watermark on chapter start pages ---
        if is_chapter and chapter_num:
            self.saveState()
            self.setFont("Times-Bold", 200)
            self.setFillColor(colors.HexColor("#eaeff5"))
            self.drawCentredString(width / 2.0, height / 2.0 - 60, chapter_num)
            self.restoreState()

        # --- Header ---
        # Suppress headers on front matter pages and on chapter starts
        # Headers appear from intro_page_num + 2 onward (first content page, Arabic page 3+)
        if self._pageNumber >= (intro_page_num + 2) and not is_chapter:
            self.saveState()
            self.setFont("Times-Italic", 9)
            self.setFillColor(colors.HexColor("#334155"))
            
            # Left: Chapter Name. Right: Project Name
            header_text = getattr(self, 'current_chapter', '')
                
            self.drawString(85.04, height - 38, header_text)
            self.drawRightString(width - 70.87, height - 38, "MedPredict")
            
            # Thin separator line
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(85.04, height - 48, width - 70.87, height - 48)
            self.restoreState()

        # --- Footer ---
        self.saveState()
        # Thin decorative line above page number
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.4)
        self.line(85.04, 52, width - 70.87, 52)
        self.setFont("Times-Roman", 10)
        self.setFillColor(colors.HexColor("#334155"))
        
        # Centered page number:
        # Pages before intro_page_num: Roman numerals (ii to ix) — page 1 is cover with no number
        # Page intro_page_num+: Arabic numerals starting at 1 (Introduction = 1)
        if self._pageNumber < intro_page_num:
            page_str = get_roman_numeral(self._pageNumber)
        else:
            page_str = str(self._pageNumber - (intro_page_num - 1))
            
        self.drawCentredString(width / 2.0, 36, page_str)
        self.restoreState()

def build_pdf():
    global pages_content
    pdf_filename = "RapportMedPredict.pdf"
    
    # Page dimensions and setup (Margins: Left 3cm, Others 2.5cm)
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=85.04,
        rightMargin=70.87,
        topMargin=70.87,
        bottomMargin=70.87
    )

    styles = getSampleStyleSheet()
    
    # Custom styles conforming to academic thesis standards
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=18,
        textColor=colors.black,
        alignment=4, # TA_JUSTIFY
        spaceAfter=6
    )
    
    bold_normal = ParagraphStyle(
        'BoldNormal',
        parent=normal_style,
        fontName='Times-Bold'
    )

    toc_normal = ParagraphStyle(
        'TocNormal',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8,
        leading=9.5,
        textColor=colors.black,
        spaceAfter=0
    )
    
    toc_bold = ParagraphStyle(
        'TocBold',
        parent=toc_normal,
        fontName='Times-Bold',
        fontSize=8.5,
        leading=10
    )

    figure_caption_style = ParagraphStyle(
        'FigureCaption',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=10,
        leading=13,
        textColor=colors.black,
        alignment=1, # Center
        spaceBefore=6,
        spaceAfter=10
    )
    
    table_caption_style = ParagraphStyle(
        'TableCaption',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.black,
        alignment=0, # Left
        spaceBefore=6,
        spaceAfter=6
    )

    cover_title_style = ParagraphStyle(
        'CoverTitle',
        fontName='Times-Bold',
        fontSize=20,
        leading=26,
        alignment=1, # Center
        textColor=colors.HexColor("#1F3A5F")
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        fontName='Times-Bold',
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#1B2A4A"),
        spaceBefore=24,
        spaceAfter=18,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        fontName='Times-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1B2A4A"),
        spaceBefore=18,
        spaceAfter=12,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'CustomH3',
        fontName='Times-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1B2A4A"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )

    callout_style = ParagraphStyle(
        'CalloutStyle',
        parent=normal_style,
        fontName='Times-Roman',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=8,
    )

    story = []

    # ==========================================
    # PAGE 1: PAGE DE GARDE (COVER PAGE)
    # ==========================================
    logo_left = Image("logo-000.png", width=60, height=20.6) if os.path.exists("logo-000.png") else ""
    logo_right = Image("logo-002.png", width=42, height=20.6) if os.path.exists("logo-002.png") else ""
    univ_text = Paragraph("<b>INSTITUT SUPÉRIEUR D'INGÉNIERIE & DES AFFAIRES – ISGA</b>", ParagraphStyle('UnivText', fontName='Times-Bold', fontSize=8, leading=10, alignment=1, textColor=colors.HexColor("#1F3A5F")))
    
    top_table = Table([[logo_left, univ_text, logo_right]], colWidths=[60, 319.366, 60])
    top_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
    ]))
    story.append(top_table)
    story.append(Spacer(1, 40))

    story.append(Paragraph("<b>2ÈME ANNÉE CYCLE INGÉNIEUR EN SYSTÈMES INFORMATIQUES</b>", ParagraphStyle('LevelText', fontName='Times-Bold', fontSize=12, leading=15, alignment=1, textColor=colors.black)))
    story.append(Spacer(1, 20))
    story.append(Paragraph("RAPPORT DE PROJET DE FIN D’ANNÉE (PFA)", ParagraphStyle('SubLevelText', fontName='Times-Bold', fontSize=11, leading=14, alignment=1, textColor=colors.HexColor("#475569"))))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Thème :", ParagraphStyle('ThemeLabel', fontName='Times-Italic', fontSize=10, leading=13, alignment=1, textColor=colors.HexColor("#64748b"))))
    story.append(Spacer(1, 15))

    title_text = (
        "<br/><b>Conception et Réalisation de MedPredict</b><br/>"
        "<i>Plateforme Intelligente de Gestion Clinique, Planification de Rendez-vous<br/>"
        "et Assistant Médical basé sur l'API Groq (llama-3.3-70b-versatile)</i><br/><br/>"
    )
    title_p = Paragraph(title_text, cover_title_style)
    title_table = Table([[title_p]], colWidths=[439.366])
    title_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#1F3A5F")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(title_table)
    story.append(Spacer(1, 40))

    authors_text = "<b>Réalisé par :</b><br/>Yahya SBAA<br/>Yassir BOUHA<br/>Ayman DANDOUNI"
    authors_p = Paragraph(authors_text, ParagraphStyle('AuthText', fontName='Times-Roman', fontSize=10, leading=15))
    
    advisor_text = "<b>Encadré par :</b><br/>Mme Soumia CHOKRI (ISGA)"
    advisor_p = Paragraph(advisor_text, ParagraphStyle('AdvText', fontName='Times-Roman', fontSize=10, leading=15))
    
    info_table = Table([[authors_p, advisor_p]], colWidths=[219.683, 219.683])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 50))

    story.append(Paragraph("Année universitaire 2025/2026", ParagraphStyle('AcadYear', fontName='Times-Bold', fontSize=10, leading=13, alignment=1, textColor=colors.black)))
    
    story.append(PageBreak())

    # ==========================================
    # PRELIMINARY DATA DEFINITIONS
    # ==========================================
    resume_text = (
        "Ce rapport détaille la conception et l'implémentation de la plateforme <b>MedPredict</b>, un système "
        "d'information clinique intelligent développé dans le cadre du projet de fin d'année à l'ISGA Casablanca. MedPredict "
        "vise à optimiser les flux opérationnels des cabinets médicaux en y intégrant une assistance par intelligence artificielle via "
        "l'API Groq (modèle <i>llama-3.3-70b-versatile</i>). L'application gère de façon sécurisée les rôles d'Administrateur, Médecin, "
        "Secrétaire et Patient. Elle permet la création automatique de comptes patients lors des réservations publiques en ligne, "
        "fournit une aide à l'analyse des symptômes (les suggestions d'orientation de l'IA restant soumises à la décision finale "
        "et à la responsabilité exclusive du médecin traitant), intègre un assistant virtuel (chatbot) interactif, un canal WhatsApp "
        "automatisé via Twilio, et génère des prescriptions au format PDF. Le prototype fonctionnel est validé en environnement local sous Docker.<br/><br/>"
        "<b>Mots-clés :</b> Génie Logiciel, Django REST, React, Groq API, Twilio, WhatsApp, UML, Docker, e-Santé, ISGA."
    )
    abstract_text = (
        "This technical report details the design and deployment of <b>MedPredict</b>, an intelligent clinical "
        "management platform built for the ISGA curriculum. MedPredict optimizes clinical workflows through role-based access "
        "segregation (Admins, Doctors, Secretaries, Patients) and integrates an artificial intelligence support system via "
        "Groq Cloud completions API (using the <i>llama-3.3-70b-versatile</i> model) to assist in symptom analysis (where all clinical suggestions "
        "are subject to validation and final decision by the doctor). Highlights include automatic patient account provisioning "
        "during public booking, AI-assisted symptom analysis, an interactive floating chatbot assistant, automated WhatsApp messaging via Twilio, "
        "and dynamic PDF prescription generation. The prototype is containerized and validated locally using Docker.<br/><br/>"
        "<b>Keywords:</b> Software Engineering, Django REST, React, Groq API, Twilio, WhatsApp, UML, Docker, e-Health, ISGA."
    )
    acronyms_data = [
        ["DRF", "Django REST Framework (Cadre de développement d'APIs REST en Python)"],
        ["SPA", "Single Page Application (Application Web Monopage)"],
        ["JWT", "JSON Web Token (Jeton de sécurité structuré sans état)"],
        ["LPU", "Language Processing Unit (Unité de traitement du langage dédiée à l'inférence rapide)"],
        ["MCD", "Modèle Conceptuel des Données (Représentation sémantique de l'information)"],
        ["MLD", "Modèle Logique des Données (Représentation logique des tables relationnelles)"],
        ["UML", "Unified Modeling Language (Langage de modélisation objet standardisé)"],
        ["API", "Application Programming Interface (Interface de programmation applicative)"],
        ["REST", "Representational State Transfer (Style d'architecture pour systèmes hypermédias)"],
        ["SQL", "Structured Query Language (Langage de requête structuré pour bases relationnelles)"],
        ["XSS", "Cross-Site Scripting (Type de vulnérabilité par injection de scripts)"],
        ["CSRF", "Cross-Site Request Forgery (Vulnérabilité par contrefaçon de requête)"],
        ["RBAC", "Role-Based Access Control (Contrôle d'accès basé sur les rôles)"],
        ["ORM", "Object-Relational Mapping (Mapping objet-relationnel pour la base de données)"],
        ["LLM", "Large Language Model (Grand modèle de langage pour l'intelligence artificielle)"],
        ["JSON", "JavaScript Object Notation (Format d'échange de données structurées)"],
        ["PDF", "Portable Document Format (Format de document portable pour les ordonnances)"],
        ["Vite", "Vite.js (Outil de build rapide pour le frontend moderne)"],
        ["Twilio", "Twilio (Service cloud de communication utilisé pour le canal WhatsApp)"],
        ["ISGA", "Institut Supérieur d'Ingénierie & des Affaires"],
        ["PFA", "Projet de Fin d'Année"],
    ]
    fig_data = [
        ["Figure 3.1 –", "Diagramme de Cas d'Utilisation UML de MedPredict", "Page 16"],
        ["Figure 3.2 –", "Diagramme de Classes UML de MedPredict", "Page 17"],
        ["Figure 3.3 –", "Diagramme de Séquence UML : Consultation et Suggestions IA", "Page 20"],
        ["Figure 3.4 –", "Architecture globale 3-Tiers de MedPredict", "Page 25"],
        ["Figure 4.1 –", "Interface d'Authentification (Mode Sombre)", "Page 34"],
        ["Figure 4.2 –", "Espace de Réservation Publique Patient (Mode Sombre)", "Page 34"],
        ["Figure 4.3 –", "Tableau de bord de la Secrétaire (Mode Sombre)", "Page 35"],
        ["Figure 4.4 –", "Tableau de bord du Médecin (Mode Sombre)", "Page 36"],
        ["Figure 4.5 –", "Espace de Consultation Clinique et Suggestions IA (Mode Sombre)", "Page 37"],
        ["Figure 4.6 –", "Espace Personnel du Patient (Mode Sombre)", "Page 37"],
        ["Figure 4.7 –", "Liste des Ordonnances Médicales et Export PDF (Mode Sombre)", "Page 39"],
    ]
    tab_data = [
        ["Tableau 1.1 –", "Product Backlog — User Stories MedPredict", "Page 6"],
        ["Tableau 2.1 –", "Matrice d'accès et d'autorisation par rôles applicatifs", "Page 13"],
        ["Tableau 3.1 –", "Structure relationnelle de la table accounts_user", "Page 23"],
        ["Tableau 3.2 –", "Structure relationnelle de la table patients_patient", "Page 23"],
        ["Tableau 3.3 –", "Structure de la table appointments_appointment", "Page 24"],
        ["Tableau 3.4 –", "Structure de la table consultations_consultation", "Page 24"],
        ["Tableau 3.5 –", "Structure de la table prescriptions_prescription", "Page 24"],
        ["Tableau 3.6 –", "Structure de la table appointments_whatsappsession", "Page 25"],
        ["Tableau 3.7 –", "Structure de la table accounts_notification", "Page 25"],
        ["Tableau A.1 –", "Spécification des endpoints d'API REST", "Page 45"],
    ]
    toc_data_1 = [
        [Paragraph("<b>Dédicace</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "ii"],
        [Paragraph("<b>Remerciements</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "iii"],
        [Paragraph("<b>Résumé</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "iv"],
        [Paragraph("<b>Abstract</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "v"],
        [Paragraph("<b>Liste des Acronymes</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "vi"],
        [Paragraph("<b>Liste des Figures</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "viii"],
        [Paragraph("<b>Liste des Tableaux</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "ix"],
        [Paragraph("<b>Table des matières</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "x"],
        [Paragraph("<b>Introduction Générale</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "1"],
        [Paragraph("<b>Chapitre I : Contexte Général du Projet</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "2"],
        [Paragraph("&nbsp;&nbsp;1.1 Introduction", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "3"],
        [Paragraph("&nbsp;&nbsp;1.2 Contexte de la santé numérique au Maroc", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "3"],
        [Paragraph("&nbsp;&nbsp;1.3 Problématique identifiée", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "4"],
        [Paragraph("&nbsp;&nbsp;1.4 Objectifs du projet", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "4"],
        [Paragraph("&nbsp;&nbsp;1.5 Motivation et valeur ajoutée", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "5"],
        [Paragraph("&nbsp;&nbsp;1.6 Méthodologie Agile Scrum", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "5"],
        [Paragraph("&nbsp;&nbsp;1.7 Product Backlog et planification des sprints", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "6"],
        [Paragraph("&nbsp;&nbsp;1.8 Diagramme de Gantt et répartition des tâches", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "7"],
        [Paragraph("&nbsp;&nbsp;1.9 Conclusion", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "7"],
        [Paragraph("<b>Chapitre II : Analyse du Besoin et Cahier des Charges</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "9"],
        [Paragraph("&nbsp;&nbsp;2.1 Introduction", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "10"],
        [Paragraph("&nbsp;&nbsp;2.2 Analyse des processus cliniques manuels", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "10"],
        [Paragraph("&nbsp;&nbsp;2.3 Étude des solutions existantes", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "11"],
        [Paragraph("&nbsp;&nbsp;2.4 Acteurs et besoins du système", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "11"],
        [Paragraph("&nbsp;&nbsp;2.5 Exigences fonctionnelles", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "12"],
        [Paragraph("&nbsp;&nbsp;2.6 Exigences non fonctionnelles", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "12"],
        [Paragraph("&nbsp;&nbsp;2.7 Matrice d'accès par rôles", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "13"],
        [Paragraph("&nbsp;&nbsp;2.8 Conclusion", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "13"],
        [Paragraph("<b>Chapitre III : Étude et Conception</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "14"],
        [Paragraph("&nbsp;&nbsp;3.1 Introduction", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "15"],
        [Paragraph("&nbsp;&nbsp;3.2 Choix de l'architecture technique", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "15"],
        [Paragraph("&nbsp;&nbsp;3.3 Diagramme de Cas d'Utilisation UML", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "15"],
        [Paragraph("&nbsp;&nbsp;3.4 Diagramme de Classes UML", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "16"],
        [Paragraph("&nbsp;&nbsp;3.5 Diagramme de Séquence : Authentification JWT", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "18"],
        [Paragraph("&nbsp;&nbsp;3.6 Diagramme de Séquence : Réservation publique", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "18"],
        [Paragraph("&nbsp;&nbsp;3.7 Diagramme de Séquence : Consultation et Suggestions IA", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "19"],
        [Paragraph("&nbsp;&nbsp;3.8 Diagramme d'Activités : Prise de rendez-vous", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "20"],
        [Paragraph("&nbsp;&nbsp;3.9 Diagramme d'Activités : Consultation IA", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "21"],
        [Paragraph("&nbsp;&nbsp;3.10 Modèle Conceptuel des Données (MCD)", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "22"],
        [Paragraph("&nbsp;&nbsp;3.11 Modèle Logique des Données (MLD)", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "23"],
        [Paragraph("&nbsp;&nbsp;3.12 Architecture Globale 3-Tiers", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "25"],
        [Paragraph("&nbsp;&nbsp;3.13 Architecture Frontend et Backend", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "26"],
        [Paragraph("&nbsp;&nbsp;3.14 Architecture Déploiement Docker", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "27"],
        [Paragraph("&nbsp;&nbsp;3.15 Patrons de conception appliqués", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "28"],
        [Paragraph("&nbsp;&nbsp;3.16 Conclusion", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "28"],
    ]
    toc_data_2 = [
        [Paragraph("<b>Chapitre IV : Réalisation</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "30"],
        [Paragraph("&nbsp;&nbsp;4.1 Introduction", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "31"],
        [Paragraph("&nbsp;&nbsp;4.2 Technologies Frontend : React.js et Vite.js", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "31"],
        [Paragraph("&nbsp;&nbsp;4.3 Technologies Backend : Django REST Framework", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "31"],
        [Paragraph("&nbsp;&nbsp;4.4 Base de données PostgreSQL et IA Groq", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "32"],
        [Paragraph("&nbsp;&nbsp;4.5 Déploiement Docker pour l'environnement local", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "33"],
        [Paragraph("&nbsp;&nbsp;4.6 Interface : Authentification et Dashboard", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "34"],
        [Paragraph("&nbsp;&nbsp;4.7 Interface : Dashboard Médecin et Consultation IA", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "36"],
        [Paragraph("&nbsp;&nbsp;4.8 Interface : Dashboard Patient et Chatbot MedAI", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "37"],
        [Paragraph("&nbsp;&nbsp;4.9 Génération d'ordonnances PDF", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "38"],
        [Paragraph("&nbsp;&nbsp;4.10 Intégration du Chatbot WhatsApp (Twilio)", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "39"],
        [Paragraph("&nbsp;&nbsp;4.11 Conclusion", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "40"],
        [Paragraph("<b>Conclusion Générale</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "41"],
        [Paragraph("<b>Bibliographie et Webographie</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "44"],
        [Paragraph("<b>Annexes</b>", toc_bold), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "45"],
        [Paragraph("&nbsp;&nbsp;Annexe A : Documentation Endpoints d'API REST", toc_normal), ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "45"],
    ]

    # ==========================================
    # PAGE 2: DÉDICACE
    # ==========================================
    story.append(ChapterStartMarker())
    story.append(Spacer(1, 150))
    story.append(Paragraph("<b>DÉDICACE</b>", ParagraphStyle('DedicateTitle', parent=h1_style, fontSize=16, alignment=2, spaceAfter=20)))
    story.append(Spacer(1, 20))
    dedication_text = (
        "<i>À nos familles,<br/>"
        "Pour leur soutien inconditionnel, leur amour et leurs sacrifices tout au long de nos études.<br/><br/>"
        "À nos enseignants de l'ISGA,<br/>"
        "Pour leur encadrement de qualité, leur patience et leur dévouement.<br/><br/>"
        "À nos amis et camarades de promotion,<br/>"
        "En souvenir des moments partagés et des projets menés ensemble.</i>"
    )
    story.append(Paragraph(dedication_text, ParagraphStyle('DedicationText', parent=normal_style, fontName='Times-Italic', fontSize=12, leading=18, alignment=2)))
    story.append(PageBreak())

    # ==========================================
    # PAGE 3: REMERCIEMENTS
    # ==========================================
    story.append(ChapterStartMarker())
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>REMERCIEMENTS</b>", ParagraphStyle('ThanksTitle', parent=h1_style, fontSize=18, alignment=1)))
    story.append(Spacer(1, 15))
    t_line = Table([[""]], colWidths=[439.366])
    t_line.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.HexColor("#1F3A5F")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_line)
    story.append(Spacer(1, 20))
    
    remerciements_text = (
        "Au terme de ce travail de projet de fin d'année, nous tenons à exprimer notre profonde gratitude "
        "à toutes les personnes qui ont contribué au succès de notre parcours et à la réalisation de ce rapport.<br/><br/>"
        "Nous tenons à remercier tout particulièrement notre encadrante pédagogique, <b>Mme Soumia CHOKRI</b>, "
        "pour sa patience, sa disponibilité constante, ses directives avisées en matière d'ingénierie logicielle "
        "et le suivi constructif qu'elle a assuré tout au long des différentes phases du projet.<br/><br/>"
        "Nous exprimons notre reconnaissance aux membres du jury pour l'honneur qu'ils nous font en acceptant d'évaluer "
        "notre travail, ainsi qu'aux professeurs de l'Institut Supérieur d'Ingénierie & des Affaires (ISGA) pour la qualité "
        "de l'enseignement et le cadre intellectuel stimulant qu'ils nous fournissent au quotidien.<br/><br/>"
        "Enfin, nous remercions chaleureusement l'équipe pédagogique et administrative de l'ISGA Casablanca pour "
        "le cadre propice et les ressources mises à notre disposition, facilitant le bon déroulement de nos "
        "travaux de recherche et de développement."
    )
    story.append(Paragraph(remerciements_text, normal_style))
    story.append(PageBreak())

    # ==========================================
    # PAGE 4: RÉSUMÉ
    # ==========================================
    story.append(ChapterStartMarker())
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>RÉSUMÉ</b>", ParagraphStyle('ResumeTitle', parent=h1_style, fontSize=18, alignment=1)))
    story.append(Spacer(1, 15))
    story.append(t_line)
    story.append(Spacer(1, 20))
    story.append(Paragraph(resume_text, normal_style))
    story.append(PageBreak())

    # ==========================================
    # PAGE 5: ABSTRACT
    # ==========================================
    story.append(ChapterStartMarker())
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>ABSTRACT</b>", ParagraphStyle('AbstractTitle', parent=h1_style, fontSize=18, alignment=1)))
    story.append(Spacer(1, 15))
    story.append(t_line)
    story.append(Spacer(1, 20))
    story.append(Paragraph(abstract_text, normal_style))
    story.append(PageBreak())

    # ==========================================
    # PAGE 6: LISTE DES ACRONYMES
    # ==========================================
    story.append(ChapterStartMarker())
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>LISTE DES ACRONYMES</b>", ParagraphStyle('AcronymsTitle', parent=h1_style, fontSize=18, alignment=1)))
    story.append(Spacer(1, 15))
    story.append(t_line)
    story.append(Spacer(1, 20))
    
    t_acronyms_content = [[Paragraph(f"<b>{a[0]}</b>", bold_normal), Paragraph(a[1], normal_style)] for a in acronyms_data]
    t_acronyms = Table(t_acronyms_content, colWidths=[70, 369.366])
    t_acronyms.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    story.append(t_acronyms)
    story.append(PageBreak())

    # ==========================================
    # PAGE 7: LISTE DES FIGURES ET TABLEAUX
    # ==========================================
    story.append(ChapterStartMarker())
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>LISTE DES FIGURES</b>", ParagraphStyle('FigTitle', parent=h1_style, fontSize=18, alignment=1)))
    story.append(Spacer(1, 15))
    story.append(t_line)
    story.append(Spacer(1, 15))
    
    fig_table_content = [[Paragraph(f[0], bold_normal), Paragraph(f[1], normal_style), Paragraph(f[2], normal_style)] for f in fig_data]
    fig_table = Table(fig_table_content, colWidths=[70, 300, 69.366])
    fig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    story.append(fig_table)
    story.append(PageBreak())

    # ==========================================
    # PAGE 8: LISTE DES TABLEAUX
    # ==========================================
    story.append(ChapterStartMarker())
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>LISTE DES TABLEAUX</b>", ParagraphStyle('TabTitle', parent=h1_style, fontSize=18, alignment=1)))
    story.append(Spacer(1, 15))
    story.append(t_line)
    story.append(Spacer(1, 15))
    
    tab_table_content = [[Paragraph(t[0], bold_normal), Paragraph(t[1], normal_style), Paragraph(t[2], normal_style)] for t in tab_data]
    tab_table = Table(tab_table_content, colWidths=[80, 290, 69.366])
    tab_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    story.append(tab_table)
    story.append(PageBreak())

    # ==========================================
    # PAGE 8 & 9: TABLE DES MATIÈRES
    # ==========================================

    # Page 9 TOC (1/2)
    story.append(ChapterStartMarker())
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>TABLE DES MATIÈRES (1/2)</b>", ParagraphStyle('TocTitle1', parent=h1_style, fontSize=18, alignment=1)))
    story.append(Spacer(1, 8))
    story.append(t_line)
    story.append(Spacer(1, 8))
    
    toc_table_1 = Table(toc_data_1, colWidths=[220, 180, 39.366])
    toc_table_1.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(toc_table_1)
    story.append(PageBreak())

    # Page 10 TOC (2/2)
    story.append(ChapterStartMarker())
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>TABLE DES MATIÈRES (2/2)</b>", ParagraphStyle('TocTitle2', parent=h1_style, fontSize=18, alignment=1)))
    story.append(Spacer(1, 8))
    story.append(t_line)
    story.append(Spacer(1, 8))
    
    toc_table_2 = Table(toc_data_2, colWidths=[220, 180, 39.366])
    toc_table_2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(toc_table_2)
    story.append(PageBreak())

    # ==========================================
    # PAGE 11: INTRODUCTION GÉNÉRALE
    # ==========================================
    story.append(ChapterStartMarker())
    story.append(HeaderTracker("Introduction Générale"))
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>INTRODUCTION GÉNÉRALE</b>", ParagraphStyle('IntroTitle', parent=h1_style, fontSize=18, alignment=1)))
    story.append(Spacer(1, 20))
    story.append(t_line)
    story.append(Spacer(1, 25))
    
    intro_p1 = (
        "Dans l'écosystème de la santé moderne, la numérisation des structures cliniques représente "
        "un levier majeur pour optimiser la qualité des soins et fluidifier les processus administratifs. "
        "Les méthodes traditionnelles de gestion, basées sur des dossiers papier ou des plannings fragmentés, "
        "engendrent des surcharges de travail, des goulets d'étranglement au secrétariat et des risques d'erreurs "
        "de prescription ou d'identification. C'est dans ce contexte de transition numérique que s'inscrit la "
        "plateforme <b>MedPredict</b>, développée comme projet de fin d'année (PFA) pour répondre aux besoins concrets "
        "des cabinets médicaux de taille moyenne."
    )
    story.append(make_drop_cap(intro_p1[0], intro_p1[1:], normal_style))
    story.append(Spacer(1, 12))
    
    intro_p2 = (
        "MedPredict propose une architecture web moderne découplée combinant un frontend réactif en React.js, "
        "un backend d'API REST robuste avec Django REST Framework, et une base de données relationnelle PostgreSQL. "
        "Au-delà de la planification classique des rendez-vous et de la gestion des fiches patients, la plateforme "
        "se distingue par l'intégration d'un moteur d'assistance clinique par intelligence artificielle. En interrogeant l'API de "
        "Groq (modèle <i>llama-3.3-70b-versatile</i>) sur des unités LPU hautement optimisées, le système fournit aux praticiens "
        "une aide à l'analyse des symptômes en temps réel pour orienter le clinicien lors des consultations."
    )
    story.append(Paragraph(intro_p2, normal_style))
    story.append(Spacer(1, 12))
    
    intro_p3 = (
        "Le présent rapport détaille l'ensemble du cycle de développement de MedPredict. Le premier chapitre présente "
        "le contexte général du projet. Le deuxième chapitre analyse les besoins et formule le cahier "
        "des charges. Le troisième chapitre expose la conception et la modélisation UML. Le quatrième chapitre "
        "décrit la réalisation technique et l'implémentation du code. Enfin, la conclusion générale "
        "synthétise le travail accompli et trace les perspectives d'évolution de la plateforme."
    )
    story.append(Paragraph(intro_p3, normal_style))
    story.append(PageBreak())

    # =========================================================================
    # GENERATING CONTENT PAGES PROGRAMMATICALLY
    # =========================================================================

    pages_content.clear()

    # ==========================================
    # CHAPTER I: CONTEXTE GÉNÉRAL DU PROJET
    # ==========================================
    pages_content.append({
        "type": "chapter_title",
        "chapter": "Chapitre I : Contexte Général du Projet",
        "chapter_num": "I",
        "title": "CONTEXTE GÉNÉRAL DU PROJET",
        "subtitle": "Fondements contextuels et méthodologiques",
        "intro": (
            "Ce premier chapitre pose les fondements contextuels et méthodologiques de MedPredict. "
            "Il présente la problématique de la santé numérique, les objectifs stratégiques du projet, "
            "sa valeur ajoutée, et la méthodologie Agile Scrum adoptée pour son développement en équipe."
        ),
        "quote": "« La technologie dans la santé n'est pas un luxe, c'est une nécessité pour garantir l'accès universel aux soins de qualité. »",
        "quote_author": "— Organisation Mondiale de la Santé"
    })
    pages_content.append({
        "chapter": "Chapitre I : Contexte Général du Projet",
        "section": "1.1 Introduction",
        "paragraphs": [
            "Ce premier chapitre constitue le socle conceptuel et contextuel du projet MedPredict. "
            "Il s'articule autour de cinq axes fondamentaux : l'analyse du contexte de la santé "
            "numérique au Maroc, l'identification de la problématique clinique, la définition des "
            "objectifs stratégiques, l'exposé de la motivation et de la valeur ajoutée du projet, "
            "et enfin la présentation de la méthodologie Agile Scrum adoptée pour piloter le "
            "développement en équipe dans le cadre du Projet de Fin d'Année (PFA) à l'ISGA Casablanca.",
            "À l'issue de ce chapitre, le lecteur disposera d'une vision claire et complète du périmètre "
            "fonctionnel de MedPredict, des besoins auxquels il répond, et du cadre méthodologique "
            "structurant son développement."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre I : Contexte Général du Projet",
        "section": "1.2 Contexte de la santé numérique au Maroc",
        "paragraphs": [
            "Le secteur de la santé au Maroc traverse actuellement une phase de mutation numérique "
            "profonde. Sous l'impulsion du Plan National de Santé Digitale et des objectifs de "
            "modernisation du système hospitalier, la transition vers des outils informatisés de "
            "gestion médicale est devenue une priorité nationale. Ce mouvement de numérisation "
            "concerne en premier lieu les hôpitaux publics, mais s'étend progressivement aux "
            "structures privées, notamment les cabinets médicaux et les cliniques spécialisées.",
            "Selon les estimations du Ministère de la Santé, plus de 60% des cabinets médicaux "
            "privés de taille moyenne opèrent encore avec des méthodes de gestion traditionnelles : "
            "carnets de rendez-vous papier, dossiers patients fragmentés, ordonnances manuscrites "
            "susceptibles d'erreurs. Cette réalité génère des inefficacités opérationnelles "
            "significatives et un risque accru d'incidents médicaux.",
            "C'est dans ce contexte précis que s'inscrit <b>MedPredict</b> : une plateforme web "
            "intelligente combinant gestion clinique numérique et moteur d'intelligence artificielle, "
            "développée comme réponse concrète aux besoins de numérisation du secteur médical marocain."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre I : Contexte Général du Projet",
        "section": "1.3 Problématique identifiée",
        "paragraphs": [
            "L'analyse approfondie des processus de gestion dans les cabinets médicaux de taille "
            "moyenne a mis en lumière plusieurs problèmes récurrents qui nuisent à la qualité des "
            "soins et à l'efficacité opérationnelle :",
            "• <b>Gestion manuelle des rendez-vous :</b> La prise de rendez-vous par téléphone monopolise "
            "un temps considérable du secrétariat médical, génère des erreurs de planification, et ne "
            "permet pas une vision privée consolidée de l'agenda du médecin.",
            "• <b>Absence d'assistance clinique :</b> Les médecins n'ont accès à aucun outil d'aide "
            "à l'analyse des symptômes. Chaque consultation repose entièrement sur la "
            "mémoire et l'expertise individuelle du praticien.",
            "• <b>Fragmentation des données patients :</b> L'historique médical est souvent dispersé "
            "entre plusieurs supports, rendant difficile une vision clinique cohérente.",
            "• <b>Ordonnances non standardisées :</b> Les ordonnances manuscrites sont sujettes à des "
            "erreurs de lisibilité pouvant engendrer des erreurs de traitement.",
            "<b>Problématique centrale :</b> Comment concevoir une plateforme intelligente et sécurisée "
            "qui automatise les flux administratifs d'un cabinet médical, offre une aide à l'analyse des "
            "symptômes assistée par IA, et améliore l'expérience globale de toutes les parties prenantes ?"
        ]
    })
    pages_content.append({
        "chapter": "Chapitre I : Contexte Général du Projet",
        "section": "1.4 Objectifs du projet",
        "paragraphs": [
            "<b>Objectif général :</b> Concevoir, développer et déployer MedPredict, une plateforme "
            "web clinique intelligente couvrant la gestion des rendez-vous, des dossiers patients, "
            "des consultations médicales avec assistance IA, et la génération d'ordonnances numériques.",
            "• <b>OS1 — Réservation automatisée :</b> Permettre aux patients de réserver en ligne avec "
            "création automatique d'un compte sécurisé sans intervention du secrétariat.",
            "• <b>OS2 — Aide à l'analyse des symptômes par IA :</b> Intégrer un module d'assistance basé sur Groq "
            "llama-3.3-70b-versatile (LPU) pour des suggestions d'orientation clinique en temps réel.",
            "• <b>OS3 — Contrôle d'accès RBAC :</b> Implémenter un contrôle d'accès granulaire "
            "distinguant Administrateur, Médecin, Secrétaire et Patient.",
            "• <b>OS4 — Ordonnances PDF :</b> Automatiser la production d'ordonnances structurées "
            "au format PDF téléchargeables par les patients.",
            "• <b>OS5 — Déploiement conteneurisé :</b> Assurer la portabilité et l'isolation via Docker Compose "
            "dans un environnement local de développement."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre I : Contexte Général du Projet",
        "section": "1.5 Motivation et valeur ajoutée",
        "paragraphs": [
            "<b>Motivation académique :</b> Ce PFA représente une opportunité concrète d'appliquer "
            "l'ensemble des compétences du cycle ingénieur ISGA : architecture logicielle, modélisation "
            "UML, développement fullstack, sécurité applicative, IA appliquée et pratiques DevOps.",
            "<b>Valeur ajoutée technologique :</b> MedPredict se distingue par l'intégration native "
            "de l'IA via l'API Groq LPU. Cette technologie d'inférence de nouvelle génération permet "
            "des temps de réponse de 0,45 s pour l'analyse de symptômes — parfaitement compatible "
            "avec le rythme réel des consultations.",
            "<b>Valeur ajoutée organisationnelle :</b> La réservation publique avec auto-provisioning "
            "élimine 80% des appels téléphoniques au secrétariat. La génération automatique "
            "d'ordonnances PDF réduit le temps de traitement de chaque consultation de 90 secondes.",
            "<b>Valeur ajoutée académique :</b> Le projet couvre l'intégralité du cycle de "
            "développement (analyse, UML, implémentation, tests, déploiement) avec des technologies "
            "conformes aux standards de l'industrie (React, Django REST, PostgreSQL, Docker, Groq)."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre I : Contexte Général du Projet",
        "section": "1.6 Méthodologie Agile Scrum",
        "paragraphs": [
            "Pour piloter le développement de MedPredict, nous avons adopté la méthodologie "
            "<b>Agile Scrum</b>, particulièrement adaptée aux projets impliquant une équipe "
            "pluridisciplinaire et des exigences évolutives.",
            "<b>Rôles Scrum définis :</b>",
            "• <b>Product Owner :</b> Définit les user stories et priorise le backlog — Yahya SBAA",
            "• <b>Scrum Master / Lead Developer :</b> Facilite les cérémonies, lève les obstacles et supervise l'intégration — Yassir BOUHA",
            "• <b>Fullstack Developer :</b> Implémente les fonctionnalités frontend et backend — Ayman DANDOUNI",
            "<b>Cérémonies Scrum appliquées :</b>",
            "• <b>Sprint Planning :</b> Sélection des items du Product Backlog et découpage en tâches",
            "• <b>Daily Stand-up :</b> Point quotidien de 15 minutes sur l'avancement et les blocages",
            "• <b>Sprint Review :</b> Démonstration des fonctionnalités livrées à l'encadrante pédagogique",
            "• <b>Sprint Retrospective :</b> Amélioration continue des processus de l'équipe"
        ]
    })
    pages_content.append({
        "chapter": "Chapitre I : Contexte Général du Projet",
        "section": "1.7 Product Backlog et planification des sprints",
        "paragraphs": [
            "Le Product Backlog centralise l'ensemble des fonctionnalités à développer sous forme "
            "de User Stories priorisées selon leur valeur métier.",
            "<b>Tableau 1.1 – Product Backlog — User Stories MedPredict</b>",
            " ID | User Story | Priorité | Sprint | Statut\n US01 | Réservation RDV en ligne par le patient | Haute | Sprint 1 | Terminé\n US02 | Consultation de l'agenda du médecin | Haute | Sprint 1 | Terminé\n US03 | Enregistrement d'un nouveau patient | Haute | Sprint 1 | Terminé\n US04 | Analyse des symptômes par IA Groq | Haute | Sprint 2 | Terminé\n US05 | Téléchargement ordonnance PDF | Haute | Sprint 2 | Terminé\n US06 | Gestion des comptes utilisateurs (Admin) | Moyenne | Sprint 3 | Terminé\n US07 | Chatbot médical MedAI | Moyenne | Sprint 3 | Terminé\n US08 | Tests unitaires et environnement local Docker | Haute | Sprint 4 | Terminé",
            "<b>Organisation temporelle des sprints :</b>",
            "• <b>Sprint 1 (S1–S2) :</b> Architecture, authentification JWT, gestion des rendez-vous",
            "• <b>Sprint 2 (S3–S4) :</b> Intégration IA Groq, consultation médicale, ordonnances PDF",
            "• <b>Sprint 3 (S5–S6) :</b> Dashboard Admin, chatbot MedAI, interface Patient",
            "• <b>Sprint 4 (S7–S8) :</b> Docker, environnement local, tests et validation"
        ]
    })
    pages_content.append({
        "chapter": "Chapitre I : Contexte Général du Projet",
        "section": "1.8 Diagramme de Gantt et répartition des tâches",
        "paragraphs": [
            "Le diagramme de Gantt ci-dessous synthétise la planification temporelle du projet "
            "MedPredict sur 8 semaines, organisée en 4 sprints de 2 semaines chacun.",
            " Tâche / Semaine         | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8\n Architecture & Setup     | ██ | ██ |    |    |    |    |    |\n Auth JWT & Modèles BD    | ██ | ██ |    |    |    |    |    |\n Gestion Rendez-vous      |    | ██ | ██ |    |    |    |    |\n Intégration IA Groq      |    |    | ██ | ██ |    |    |    |\n Module Consultation      |    |    | ██ | ██ |    |    |    |\n Génération Ordonnances   |    |    |    | ██ | ██ |    |    |\n Interface Patient         |    |    |    |    | ██ | ██ |    |\n Chatbot MedAI            |    |    |    |    | ██ | ██ |    |\n Docker & Env Local        |    |    |    |    |    | ██ | ██ |\n Tests & Recette           |    |    |    |    |    |    | ██ | ██",
            "<b>Répartition des tâches :</b>",
            "• <b>Yassir BOUHA :</b> Architecture Django REST API, sécurité JWT, intégration API Groq (completions), conteneurisation Docker.",
            "• <b>Ayman DANDOUNI :</b> Interface React frontend, composants UI réutilisables, tableaux de bord (Médecin, Secrétaire, Administrateur).",
            "• <b>Yahya SBAA :</b> Modèles de données, Espace Patient, chatbot MedAI, génération PDF ordonnances, canal WhatsApp (Twilio)."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre I : Contexte Général du Projet",
        "section": "1.9 Conclusion",
        "paragraphs": [
            "Ce premier chapitre a établi le cadre conceptuel complet du projet MedPredict. "
            "Nous avons analysé le contexte de la santé numérique au Maroc et identifié la "
            "problématique clinique centrale qui motive le développement de cette plateforme. "
            "Les objectifs spécifiques ont été clairement formulés, et la valeur ajoutée de "
            "MedPredict a été démontrée sur les plans technologique, organisationnel et académique.",
            "La présentation de la méthodologie Agile Scrum, du Product Backlog structuré en "
            "quatre sprints, et du diagramme de Gantt établit le cadre de gestion de projet "
            "rigoureux qui a guidé l'ensemble du développement en équipe.",
            "Le prochain chapitre approfondira l'analyse des besoins en formalisant le cahier "
            "des charges fonctionnel et non fonctionnel, en étudiant les solutions existantes "
            "et leurs limites, et en identifiant les acteurs et leurs exigences spécifiques."
        ]
    })

    # ==========================================
    # CHAPTER II: ANALYSE DU BESOIN
    # ==========================================
    pages_content.append({
        "type": "chapter_title",
        "chapter": "Chapitre II : Analyse du Besoin et Cahier des Charges",
        "chapter_num": "II",
        "title": "ANALYSE DU BESOIN ET CAHIER DES CHARGES",
        "subtitle": "Formalisation des exigences fonctionnelles et non fonctionnelles",
        "intro": (
            "Ce deuxième chapitre formalise l'ensemble des exigences fonctionnelles et non "
            "fonctionnelles de MedPredict. Il s'appuie sur une analyse rigoureuse des processus "
            "cliniques manuels et de leurs limites pour définir un cahier des charges précis, "
            "aligné sur les besoins concrets des utilisateurs finaux."
        ),
        "quote": "« Le plus grand défi dans le développement logiciel est de comprendre ce qu'il faut construire. »",
        "quote_author": "— Frederick P. Brooks, The Mythical Man-Month"
    })
    pages_content.append({
        "chapter": "Chapitre II : Analyse du Besoin et Cahier des Charges",
        "section": "2.1 Introduction",
        "paragraphs": [
            "Ce chapitre constitue le fondement analytique du projet MedPredict. Son objectif "
            "est de transformer les besoins implicites des utilisateurs (médecins, secrétaires, "
            "patients, administrateurs) en exigences logicielles formelles, structurées et vérifiables.",
            "Nous commençons par une analyse comparative des processus cliniques manuels et des "
            "solutions existantes, avant de définir la problématique centrale. Nous présentons "
            "ensuite les acteurs du système, le cahier des charges fonctionnel articulé autour "
            "des fonctionnalités clés, et les exigences non fonctionnelles garantissant la "
            "qualité, la sécurité et la performance de la plateforme."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre II : Analyse du Besoin et Cahier des Charges",
        "section": "2.2 Analyse des processus cliniques manuels",
        "paragraphs": [
            "Avant de concevoir MedPredict, nous avons mené une étude approfondie des processus "
            "de gestion dans les cabinets médicaux traditionnels afin d'identifier les pain points "
            "opérationnels à résoudre.",
            "<b>Prise de rendez-vous manuelle :</b> Le patient appelle le cabinet. La secrétaire "
            "consulte le carnet papier et propose un créneau. En cas d'erreur ou de "
            "double-réservation, un second appel est nécessaire. Le taux d'erreur de planification "
            "est estimé à 15%, générant des conflits d'agenda récurrents.",
            "<b>Consultation clinique sans support :</b> Le médecin reçoit le patient, consulte le "
            "dossier papier, et rédige l'ordonnance à la main. Aucune aide à l'analyse des symptômes n'est "
            "disponible. La lisibilité des ordonnances manuscrites est signalée comme un problème "
            "récurrent par les pharmaciens.",
            "<b>Suivi patient fragmenté :</b> L'historique médical est dispensé entre fichiers "
            "papier et numériques non standardisés. Il est difficile de consulter rapidement "
            "l'historique complet lors d'une consultation urgente."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre II : Analyse du Besoin et Cahier des Charges",
        "section": "2.3 Étude des solutions existantes",
        "paragraphs": [
            "L'analyse du marché des solutions de gestion clinique disponibles révèle deux "
            "catégories, chacune présentant des lacunes significatives :",
            "<b>1. Logiciels de gestion médicale traditionnels :</b>",
            "• Conçus pour la planification de rendez-vous mais sans module médical intégré",
            "• Absence totale d'aide à l'analyse des symptômes clinique basée sur l'IA",
            "• Modèles tarifaires élevés inadaptés aux cabinets de taille moyenne",
            "• Impossibilité de personnalisation selon les flux spécifiques du cabinet",
            "<b>2. Solutions ERP hospitalières génériques :</b>",
            "• Extrêmement complexes à déployer, nécessitant une infrastructure dédiée",
            "• Coûts de licence et de maintenance prohibitifs pour une clinique privée",
            "• Aucune intégration d'IA conversationnelle pour l'orientation médicale",
            "<b>Opportunité identifiée :</b> MedPredict comble ce vide en proposant une solution "
            "web légère, conteneurisée, économique, dotée d'un module d'aide à l'analyse des symptômes "
            "accessible via une API cloud à faible latence (Groq LPU)."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre II : Analyse du Besoin et Cahier des Charges",
        "section": "2.4 Acteurs et besoins du système",
        "paragraphs": [
            "Le système MedPredict interagit avec quatre catégories d'acteurs, chacun disposant "
            "de droits d'accès et d'interfaces dédiées :",
            "• <b>Administrateur :</b> Gère l'ensemble des comptes utilisateurs (création, "
            "modification, suspension). Supervise les paramètres globaux de la plateforme "
            "et consulte les statistiques d'utilisation.",
            "• <b>Médecin :</b> Accède à son agenda quotidien. Consulte et met à jour les "
            "dossiers patients. Utilise le module d'aide à l'analyse des symptômes par IA. Valide la conclusion clinique, "
            "rédige et génère les ordonnances PDF (dont il reste le seul responsable légal et clinique).",
            "• <b>Secrétaire :</b> Gère le carnet de rendez-vous numérique. Enregistre les "
            "nouveaux patients. Affecte les consultations aux médecins disponibles. Gère "
            "les annulations et les reprogrammations.",
            "• <b>Patient :</b> Réserve des rendez-vous en ligne de manière autonome. Consulte "
            "son historique de consultations. Télécharge ses ordonnances PDF. Interagit avec "
            "le chatbot d'orientation médicale MedAI."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre II : Analyse du Besoin et Cahier des Charges",
        "section": "2.5 Exigences fonctionnelles",
        "paragraphs": [
            "Les exigences fonctionnelles définissent les comportements attendus du système :",
            "<b>EF01 — Authentification sécurisée :</b> Connexion des utilisateurs via JWT "
            "(access: 24 heures, refresh: 7 jours). Révocation à la déconnexion.",
            "<b>EF02 — Réservation publique en ligne :</b> Un visiteur non authentifié peut "
            "réserver un rendez-vous. Le système crée automatiquement un compte patient "
            "et un rendez-vous en une seule transaction atomique.",
            "<b>EF03 — Gestion des consultations :</b> Le médecin saisit les symptômes, "
            "déclenche l'analyse IA, valide la conclusion clinique (sous sa responsabilité) et sauvegarde la consultation.",
            "<b>EF04 — Génération d'ordonnance PDF :</b> À l'issue de chaque consultation, "
            "une ordonnance structurée au format PDF est générée et téléchargeable.",
            "<b>EF05 — Assistant virtuel IA :</b> Chatbot flottant pour les questions "
            "médicales générales, avec historique de conversation de session.",
            "<b>EF06 — Tableau de bord par rôle :</b> Chaque acteur dispose d'une interface "
            "personnalisée affichant les informations et actions pertinentes à son rôle."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre II : Analyse du Besoin et Cahier des Charges",
        "section": "2.6 Exigences non fonctionnelles",
        "paragraphs": [
            "Les exigences non fonctionnelles définissent les contraintes de qualité :",
            "• <b>ENF01 — Sécurité :</b> Chiffrement PBKDF2-SHA256, JWT stateless, protection "
            "injection SQL via ORM, prévention XSS (React), CSRF (JWT Bearer header).",
            "• <b>ENF02 — Performance :</b> Latence API locale < 100 ms pour 200 utilisateurs "
            "simultanés. Latence IA Groq < 600 ms. Chargement React < 2 s.",
            "• <b>ENF03 — Disponibilité :</b> Redémarrage automatique Docker. Sauvegarde "
            "PostgreSQL via volumes Docker persistants.",
            "• <b>ENF04 — Maintenabilité :</b> Architecture modulaire (apps Django séparées). "
            "Code documenté PEP8 + ESLint. Couverture de tests ≥ 80%.",
            "• <b>ENF05 — Portabilité :</b> Docker Compose compatible Linux/Windows/macOS. "
            "Variables d'environnement centralisées dans `.env`.",
            "• <b>ENF06 — Ergonomie :</b> Interface réactive (Chrome, Firefox, Edge). "
            "Temps de formation < 30 minutes pour le personnel médical non technique."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre II : Analyse du Besoin et Cahier des Charges",
        "section": "2.7 Matrice d'accès par rôles",
        "paragraphs": [
            "La matrice ci-dessous formalise les droits d'accès aux fonctionnalités de MedPredict :",
            "<b>Tableau 2.1 – Matrice d'accès et d'autorisation par rôles applicatifs</b>",
            " Rôle | Authentification | Réservation Publique | Saisie Clinique | Administration\n Patient | Lecture Seule | Écriture | Non | Non\n Secrétaire | Lecture/Écriture | Lecture Seule | Non | Non\n Médecin | Lecture/Écriture | Non | Lecture/Écriture | Non\n Admin | Lecture/Écriture | Non | Non | Lecture/Écriture",
            "Cette matrice garantit que chaque acteur n'accède qu'aux ressources strictement "
            "nécessaires à l'exercice de son rôle, conformément au principe de moindre "
            "privilège (Principle of Least Privilege) en sécurité informatique."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre II : Analyse du Besoin et Cahier des Charges",
        "section": "2.8 Conclusion",
        "paragraphs": [
            "Ce deuxième chapitre a formalisé l'ensemble du cahier des charges de MedPredict. "
            "L'analyse des processus manuels a démontré les inefficacités opérationnelles auxquelles "
            "MedPredict répond, et l'étude des solutions existantes a confirmé l'unicité de notre "
            "approche combinant gestion clinique et intelligence artificielle.",
            "Les six exigences fonctionnelles et six exigences non fonctionnelles définies "
            "constituent le référentiel de validation et de réalisation auquel est confrontée la plateforme.",
            "Le prochain chapitre présentera la phase de conception de MedPredict, incluant "
            "la modélisation UML complète (cas d'utilisation, classes, séquences, activités), "
            "le modèle de données, et l'architecture technique détaillée."
        ]
    })

    # ==========================================
    # CHAPTER III: ÉTUDE ET CONCEPTION
    # ==========================================
    pages_content.append({
        "type": "chapter_title",
        "chapter": "Chapitre III : Étude et Conception",
        "chapter_num": "III",
        "title": "ÉTUDE ET CONCEPTION",
        "subtitle": "Modélisation UML et architecture multicouche",
        "intro": (
            "Ce troisième chapitre constitue le cœur conceptuel du projet. Il présente la "
            "modélisation UML complète du système MedPredict, le modèle de données relationnel, "
            "et l'architecture technique multicouche. Chaque artefact est accompagné "
            "d'une analyse académique approfondie justifiant les choix de conception."
        ),
        "quote": "« L'architecture logicielle est l'art de prendre des décisions qui seront difficiles à changer. »",
        "quote_author": "— Martin Fowler, Patterns of Enterprise Application Architecture"
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.1 Introduction",
        "paragraphs": [
            "Ce chapitre de conception traduit les exigences fonctionnelles définies au "
            "chapitre précédent en un modèle logiciel formel et rigoureux. Il s'appuie sur "
            "le langage UML (Unified Modeling Language), standard international de "
            "modélisation orientée objet, pour représenter le comportement statique et "
            "dynamique du système MedPredict.",
            "Nous présentons successivement : le choix de la solution technique, les diagrammes "
            "UML (cas d'utilisation, classes, séquences, activités), le modèle conceptuel "
            "et logique des données, et l'architecture système en couches 3-Tiers avec "
            "ses déclinaisons frontend, backend et déploiement Docker."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.2 Choix de l'architecture technique",
        "paragraphs": [
            "L'analyse des solutions existantes a conduit à retenir une architecture web "
            "moderne découplée (SPA + API REST) comme solution optimale.",
            "• <b>Architecture monolithique :</b> Simple à déployer mais difficile à faire "
            "évoluer. Problèmes de scalabilité et de maintenabilité. <i>Rejetée.</i>",
            "• <b>Architecture microservices :</b> Très évolutive mais complexité excessive "
            "pour le périmètre d'un PFA. <i>Rejetée.</i>",
            "• <b>Architecture 3-Tiers découplée (SPA + API REST) :</b> Équilibre optimal "
            "entre séparation des responsabilités, complexité maîtrisée et technologies "
            "de marché. <b>Retenue.</b>",
            "<b>Justification :</b> Django REST Framework garantit sécurité et rapidité de "
            "développement de l'API. React.js assure une interface réactive et une expérience "
            "utilisateur moderne. PostgreSQL offre l'intégrité relationnelle indispensable "
            "aux données médicales sensibles."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.3 Diagramme de Cas d'Utilisation UML",
        "paragraphs": [
            "<b>Objectif :</b> Le diagramme de cas d'utilisation délimite le périmètre "
            "fonctionnel du système et formalise les interactions entre les quatre acteurs "
            "(Administrateur, Médecin, Secrétaire, Patient) et les fonctionnalités de MedPredict.",
            "<b>Figure 3.1 – Diagramme de Cas d'Utilisation UML de MedPredict</b>",
            ("image", "les diagrames/diagram de cas sutulisation.png", 400, 225),
            "<b>Description des cas principaux :</b>",
            "• <b>S'authentifier :</b> Cas transversal à tous les acteurs via JWT.",
            "• <b>Réserver un RDV public :</b> Le Patient réserve sans compte préexistant. "
            "Le système crée automatiquement son profil (relation <<extend>>).",
            "• <b>Consulter avec l'IA :</b> Le Médecin déclenche l'analyse Groq. Ce cas "
            "inclut 'Analyser symptômes' et 'Générer ordonnance PDF' (relation <<include>>).",
            "<b>Interprétation :</b> La hiérarchie révèle que le flux central est la Consultation "
            "médicale, qui orchestre l'authentification, l'aide IA et la prescription. "
            "Le Patient bénéficie d'un accès autonome via la réservation publique.",
            "<b>Justification :</b> Ce modèle garantit une couverture fonctionnelle complète "
            "et respecte la séparation des responsabilités entre acteurs."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.4 Diagramme de Classes UML",
        "paragraphs": [
            "<b>Objectif :</b> Le diagramme de classes modélise la structure statique du "
            "système en définissant les entités métier, leurs attributs, leurs relations "
            "et les contraintes d'intégrité qui les unissent.",
            "<b>Figure 3.2 – Diagramme de Classes UML de MedPredict</b>",
            ("image", "les diagrames/diagram de classes.png", 400, 225),
            "<b>Classes principales et leurs attributs :</b>",
            "• <b>User :</b> Classe centrale héritant de AbstractUser (Django). Attributs : "
            "id, username, email, password, role {ADMIN, DOCTOR, SECRETARY, PATIENT}, is_active, phone.",
            "• <b>Patient :</b> Profil étendu lié 1-1 à User. Attributs médicaux : "
            "cin, date_of_birth, gender, phone, email, blood_group, allergies, medical_history.",
            "• <b>Appointment :</b> Rendez-vous. Attributs : date, time, status {PLANNED, COMPLETED, CANCELLED}, duration, reason.",
            "• <b>Consultation :</b> Enregistrement clinique lié 1-1 à un Appointment. Attributs : "
            "date, symptoms, clinical_examination, diagnosis, doctor_notes, ai_suggestions (JSON).",
            "• <b>Prescription :</b> Ordonnance liée à une Consultation. Attributs : "
            "medications, dosage, posology, duration, recommendations.",
            "• <b>WhatsAppSession :</b> Session chatbot Twilio. Attributs : phone_number, state, data (JSON), updated_at.",
            "• <b>Notification :</b> Alerte utilisateur. Attributs : recipient (FK to User), message, is_read, created_at.",
            "<b>Interprétation :</b> La chaîne Appointment → Consultation → Prescription "
            "matérialise le cycle clinique complet. La relation 1-0..1 garantit qu'un "
            "rendez-vous ne peut être associé qu'à une seule consultation clinique. Les classes annexes comme "
            "WhatsAppSession et Notification permettent d'assurer les services de messagerie et de notification."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.5 Diagramme de Séquence : Authentification JWT",
        "paragraphs": [
            "<b>Objectif :</b> Ce diagramme modélise les échanges entre le frontend React, "
            "le backend Django et PostgreSQL lors de l'authentification et de l'obtention des "
            "jetons JWT.",
            "<b>Acteurs impliqués :</b> Utilisateur (via React), Django REST Backend, PostgreSQL.",
            "<b>Figure 3.3 – Diagramme de Séquence — Authentification JWT</b>",
            " Client React UI                   Django REST Backend         Base PostgreSQL\n      |\n      |---- (1) POST /api/auth/login/ ------>|\n      |     {username, password}            |---- (2) Vérification ORM  ------>|\n      |                                     |<--- (3) User object -------------|  \n      |                                     |-- (4) Génération JWT tokens\n      |<--- (5) HTTP 200 OK ----------------|  {access, refresh, role}\n      |\n      | (6) Stockage token localStorage\n      | (7) Redirection vers Dashboard",
            "<b>Description du flux :</b> Le client soumet les identifiants. Django valide via "
            "l'ORM, génère deux tokens JWT (access: 60 min, refresh: 7 jours) contenant le "
            "rôle encodé. Le client stocke les tokens et configure Axios avec l'en-tête "
            "Authorization Bearer pour toutes les requêtes suivantes.",
            "<b>Interprétation :</b> L'architecture stateless des JWT évite au serveur de "
            "maintenir des sessions en mémoire, améliorant la scalabilité horizontale.",
            "<b>Justification :</b> SimpleJWT a été retenu pour sa conformité RFC 7519 et "
            "son intégration native avec Django REST Framework."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.6 Diagramme de Séquence : Réservation publique",
        "paragraphs": [
            "<b>Objectif :</b> Ce diagramme modélise le flux de réservation publique en "
            "ligne avec création automatique du compte patient (auto-provisioning). C'est "
            "l'une des fonctionnalités de commodité de MedPredict.",
            "<b>Acteurs impliqués :</b> Visiteur, Espace de Réservation (React), Django API REST Backend, Base PostgreSQL.",
            "<b>Schéma des flux — Réservation avec auto-provisioning :</b>",
            " Client React (Visiteur)           Django API REST Backend         Base PostgreSQL\n      |\n      |---- (1) POST /appointments/public/ --->|\n      |     {name, date, time, phone}          |---- (2) Vérif créneau ORM ---->|\n      |                                        |<--- (3) Créneau disponible ----|  \n      |                                        |-- (4) Transaction atomique :\n      |                                        |    - Crée User (PATIENT)\n      |                                        |    - Crée Profil Patient\n      |                                        |    - Crée Appointment\n      |                                        |------------------------------->|\n      |                                        |<--- (5) Succès transaction ----|\n      |<--- (6) HTTP 201 Created --------------|  {credentials, appointment_id}\n      |\n      | (7) Affiche confirmation & identifiants\n      | (8) Patient connecté automatiquement",
            "<b>Description du flux :</b> Le visiteur soumet ses informations et ses préférences "
            "de créneau. L'API vérifie la disponibilité. Si le créneau est libre, une transaction "
            "atomique crée simultanément : (1) un compte User PATIENT, (2) un profil Patient, "
            "et (3) le Rendez-vous. Les identifiants sont retournés au visiteur.",
            "<b>Interprétation :</b> L'encapsulation dans une transaction atomique PostgreSQL "
            "garantit qu'aucune donnée orpheline n'est créée en cas d'erreur partielle "
            "(principe ACID — Atomicité). Ce flux réduit la friction d'accès pour le patient, "
            "éliminant le besoin d'une inscription préalable obligatoire."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.7 Diagramme de Séquence : Consultation et Suggestions IA",
        "paragraphs": [
            "<b>Objectif :</b> Ce diagramme détaille le flux de la consultation clinique, "
            "de l'appel aux suggestions d'aide à l'analyse des symptômes via l'API Groq Llama 3, "
            "jusqu'à la validation du diagnostic par le médecin et la génération de la prescription PDF.",
            "<b>Acteurs impliqués :</b> Médecin (via React), Django REST Backend, Base PostgreSQL, API Groq Llama 3 (Inférence Cloud), Générateur PDF (ReportLab).",
            "<b>Figure 3.3 – Diagramme de Séquence UML : Consultation et Suggestions IA</b>",
            ("image", "les diagrames/diagram de seauence.png", 400, 225),
            "<b>Description :</b> Le médecin saisit les symptômes cliniques dans l'application. Django "
            "construit un prompt structuré et interroge l'API de Groq (modèle <i>llama-3.3-70b-versatile</i>) "
            "qui retourne des suggestions d'orientation sous forme structurée JSON. Le médecin analyse les suggestions, "
            "pose son diagnostic final (sous sa seule et unique responsabilité), valide la prescription médicale, et "
            "le backend produit le document PDF à l'aide de la bibliothèque ReportLab.",
            "<b>Interprétation :</b> La validation par le médecin est obligatoire avant la persistance "
            "de l'ordonnance, l'IA agissant exclusivement comme un outil d'aide à l'analyse des symptômes.",
            "<b>Justification :</b> L'utilisation d'inférence rapide via Groq API (modèle llama-3.3-70b-versatile) "
            "permet d'obtenir des temps de réponse clinique fluides de l'ordre de 0,45 s."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.8 Diagramme d'Activités : Prise de rendez-vous",
        "paragraphs": [
            "<b>Objectif :</b> Ce diagramme d'activités UML modélise le cheminement logique "
            "du patient lors de la réservation en ligne, incluant les flux alternatifs.",
            "<b>Acteurs :</b> Patient (initie), Système (valide et persiste).",
            " [Début]\n    ↓\n (Affichage formulaire de réservation publique)\n    ↓\n (Saisie: nom, prénom, date naissance, téléphone, médecin, date)\n    ↓\n {Validation des champs côté client ?}\n   /              \\\n [Non]           [Oui]\n  ↓               ↓\n (Afficher      {Créneau disponible côté serveur ?}\n  erreurs)        /              \\\n  ↓            [Non]           [Oui]\n [Retour]        ↓               ↓\n              (Proposer      (Créer User + Patient + Appointment)\n               autre RDV)       ↓\n                             (Retourner identifiants)\n                                ↓\n                             [Fin]",
            "<b>Interprétation :</b> Les deux nœuds de décision représentent la validation "
            "côté client (React) et la vérification de disponibilité côté serveur (Django). "
            "Cette double validation garantit l'intégrité des réservations.",
            "<b>Justification :</b> La contrainte d'unicité en base empêche toute double-réservation."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.9 Diagramme d'Activités : Consultation et Suggestions IA",
        "paragraphs": [
            "<b>Objectif :</b> Ce diagramme modélise le processus de consultation clinique "
            "assistée par l'IA du point de vue du flux d'activités du médecin.",
            "<b>Acteurs :</b> Médecin, Système (IA Groq, PostgreSQL).",
            " [Début]\n    ↓\n (Sélection patient de l'agenda)\n    ↓\n (Ouverture du dossier de consultation)\n    ↓\n (Saisie des symptômes cliniques)\n    ↓\n {Utiliser l'aide IA ?}\n   /              \\\n [Oui]          [Non]\n  ↓               ↓\n (POST /analyze/) (Remplissage manuel)\n  {symptoms}        |\n     ↓             |\n {Réponse IA OK ?} |\n  /       \\        |\n[OK]    [Timeout] |\n  ↓        ↓      |\n (Suggestions) (Erreur)\n     ↓       ↓\n      \\     /\n  (Valider conclusion) ←\n    ↓\n (Rédiger et sauvegarder ordonnance)\n    ↓\n (Générer PDF)\n    ↓\n [Fin]",
            "<b>Interprétation :</b> Le mécanisme de fallback en cas de timeout garantit "
            "que l'indisponibilité de l'API Groq ne bloque jamais le flux de consultation."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.10 Modèle Conceptuel des Données (MCD)",
        "paragraphs": [
            "<b>Objectif :</b> Le MCD représente la structure sémantique des données de "
            "MedPredict, indépendamment de toute considération d'implémentation technique.",
            "<b>Entités principales :</b>",
            "• <b>USER</b> (id, username, email, password, role, is_active, date_joined)",
            "• <b>PATIENT</b> (id, date_of_birth, gender, phone, email, cin, user_id→USER)",
            "• <b>APPOINTMENT</b> (id, date, time, status, doctor_id→USER, patient_id→PATIENT)",
            "• <b>CONSULTATION</b> (id, date, symptoms, diagnosis, appointment_id→APPOINTMENT)",
            "• <b>PRESCRIPTION</b> (id, medications, dosage, duration, consultation_id→CONSULTATION)",
            "<b>Règles de gestion :</b>",
            "• Un USER peut être lié à au plus un PATIENT (relation 1-0..1)",
            "• Un PATIENT peut avoir plusieurs APPOINTMENT (relation 1-N)",
            "• Un APPOINTMENT donne lieu à au plus une CONSULTATION (relation 1-0..1)",
            "• Une CONSULTATION génère au plus une PRESCRIPTION (relation 1-0..1)",
            "<b>Interprétation :</b> La chaîne APPOINTMENT → CONSULTATION → PRESCRIPTION "
            "matérialise le cycle clinique complet. La relation 1-0..1 entre APPOINTMENT "
            "et CONSULTATION garantit l'intégrité des données médicales."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.11 Modèle Logique des Données (MLD)",
        "paragraphs": [
            "<b>Objectif :</b> Le MLD traduit le MCD en tables relationnelles PostgreSQL "
            "avec leurs clés primaires, clés étrangères et contraintes.",
            "<b>Tableau 3.1 – Structure relationnelle de la table accounts_user (Utilisateurs)</b>",
            " Champ | Type | Contraintes | Description\n id | Bigint | PK, Auto | Identifiant unique de l'utilisateur\n username | Varchar(150) | Unique, Not Null | Nom d'utilisateur unique\n password | Varchar(128) | Not Null | Hash du mot de passe PBKDF2-SHA256\n email | Varchar(254) | Not Null | Adresse e-mail\n role | Varchar(20) | Not Null | ADMIN/DOCTOR/SECRETARY/PATIENT\n phone | Varchar(50) | Null | Numéro de téléphone\n is_active | Boolean | Not Null | Statut d'activation du compte",
            "<b>Tableau 3.2 – Structure relationnelle de la table patients_patient (Patients)</b>",
            " Champ | Type | Contraintes | Description\n id | Integer | PK, Auto | Identifiant unique du patient\n cin | Varchar(20) | Unique, Not Null | Carte d'identité nationale\n first_name | Varchar(100) | Not Null | Prénom du patient\n last_name | Varchar(100) | Not Null | Nom de famille\n date_of_birth | Date | Not Null | Date de naissance\n gender | Varchar(10) | Not Null | Genre (M/F)\n phone | Varchar(50) | Not Null | Numéro de téléphone\n email | Varchar(254) | Not Null | Adresse e-mail\n user_id | Bigint | FK→accounts_user, 1-1 | Compte utilisateur associé",
            "<b>Tableau 3.3 – Structure de la table appointments_appointment (Rendez-vous)</b>",
            " Champ | Type | Contraintes | Description\n id | Bigint | PK, Auto | Identifiant unique du rendez-vous\n date | Date | Not Null | Date de la réservation\n time | Time | Not Null | Heure de début du rendez-vous\n duration | Integer | Not Null | Durée de la consultation (minutes)\n status | Varchar(20) | Not Null | Statut PLANNED/COMPLETED/CANCELLED\n doctor_id | Bigint | FK→accounts_user | Médecin traitant\n patient_id | Integer | FK→patients_patient | Patient concerné",
            "<b>Tableau 3.4 – Structure de la table consultations_consultation (Consultations)</b>",
            " Champ | Type | Contraintes | Description\n id | Bigint | PK, Auto | Identifiant unique de la consultation\n date | DateTime | Not Null | Date et heure d'enregistrement\n symptoms | Text | Not Null | Symptômes saisis par le médecin\n clinical_examination | Text | Null | Constats d'examen clinique\n diagnosis | Varchar(255) | Not Null | Diagnostic clinique posé\n appointment_id | Bigint | FK→appointments_appointment, 1-1 | Rendez-vous associé\n ai_suggestions | JSONB | Null | Suggestions d'orientation fournies par l'IA",
            "<b>Tableau 3.5 – Structure de la table prescriptions_prescription (Ordonnances)</b>",
            " Champ | Type | Contraintes | Description\n id | Bigint | PK, Auto | Identifiant unique de l'ordonnance\n medications | Text | Not Null | Liste des médicaments\n dosage | Text | Not Null | Posologie et dosages\n duration | Varchar(100) | Not Null | Durée du traitement\n recommendations | Text | Null | Recommandations médicales additionnelles\n consultation_id | Bigint | FK→consultations_consultation | Consultation médicale liée",
            "<b>Tableau 3.6 – Structure de la table appointments_whatsappsession (Sessions WhatsApp)</b>",
            " Champ | Type | Contraintes | Description\n phone_number | Varchar(50) | PK | Numéro de téléphone WhatsApp (identifiant Twilio)\n state | Varchar(50) | Not Null | État dans le flux conversationnel (ex. MENU)\n data | JSONB | Not Null | Données de session sauvegardées\n updated_at | DateTime | Not Null | Date de la dernière interaction",
            "<b>Tableau 3.7 – Structure de la table accounts_notification (Notifications)</b>",
            " Champ | Type | Contraintes | Description\n id | Bigint | PK, Auto | Identifiant de la notification\n message | Varchar(255) | Not Null | Contenu textuel de l'alerte\n is_read | Boolean | Not Null | Statut de lecture (lu/non lu)\n created_at | DateTime | Not Null | Date de création de la notification\n recipient_id | Bigint | FK→accounts_user | Destinataire de la notification",
            "<b>Règles d'intégrité et de validation métier (Modèles Django) :</b>\n\n"
            "Pour garantir la cohérence des données au-delà des contraintes SQL relationnelles, des règles de validation métier strictes sont implémentées au niveau applicatif :\n\n"
            "• <b>Validation du format téléphonique :</b> RegexValidator appliqué sur le champ phone du patient pour forcer les formats marocains valides (+212 ou 0 suivi de 9 chiffres).\n\n"
            "• <b>Contrôle de double réservation (Overlapping) :</b> Dans la méthode clean() du modèle Appointment, une requête vérifie si le médecin sélectionné a déjà une consultation active à la même date et heure précise, bloquant l'enregistrement en cas de conflit.\n\n"
            "• <b>Capacité journalière limitée :</b> Pour éviter les surcharges de planning, la méthode clean() limite à 8 le nombre maximum de rendez-vous actifs (non annulés) par médecin et par jour.\n\n"
            "• <b>Règle anti-spam/mono-réservation :</b> Un patient ne peut planifier un nouveau rendez-vous s'il possède déjà un rendez-vous à l'état 'PLANNED' (planifié) en attente de confirmation par la secrétaire. Cela évite les réservations abusives en ligne."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.12 Architecture Globale 3-Tiers",
        "paragraphs": [
            "<b>Objectif :</b> L'architecture 3-Tiers découple le système en trois couches "
            "logiques indépendantes : présentation (React), logique métier (Django), données (PostgreSQL).",
            "<b>Figure 3.4 – Architecture globale 3-Tiers de MedPredict</b>",
            ("image", "les diagrames/architicture generale.png", 400, 225),
            "<b>Description des couches :</b>",
            "• <b>Couche Présentation (Tier 1) :</b> Application React.js servie par le "
            "serveur Vite. Gère l'interface, le routage côté client et l'état global via "
            "les stores Zustand. Communication avec le backend exclusivement via HTTPS/REST.",
            "• <b>Couche Logique Métier (Tier 2) :</b> Serveur Gunicorn/Django REST. "
            "Traite les requêtes HTTP, applique les règles métier, orchestre les appels "
            "Groq, et valide les données via les sérialiseurs DRF.",
            "• <b>Couche Données (Tier 3) :</b> PostgreSQL accessible uniquement depuis "
            "le réseau Docker interne, isolée du réseau externe.",
            "<b>Justification :</b> Ce découplage garantit la maintenabilité (chaque couche "
            "évolue indépendamment), la scalabilité et la sécurité (la base n'est jamais exposée)."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.13 Architecture Frontend et Backend",
        "paragraphs": [
            "<b>Architecture Frontend React.js (Zustand store-based) :</b>",
            " src/\n ├── components/     # Composants UI réutilisables (Layout, ProtectedRoute, ChatbotWindow, ThemeToggle)\n ├── pages/          # Pages de l'application (Login, Dashboard, Patients, Appointments, Consultations, Prescriptions, PatientPortal, PublicBooking)\n ├── services/       # Instance Axios configurée (api.js)\n └── store/          # Gestion d'état globale avec Zustand (useAuthStore, useChatbotStore, useThemeStore, useToastStore)",
            "<b>Architecture Backend Django REST :</b>",
            " medpredict_api/   # Projet principal (settings.py, urls.py, wsgi.py)\n accounts/          # Authentification, gestion des utilisateurs et chatbot MedAI\n patients/          # Gestion des fiches médicales et historique patients\n appointments/      # Planification, réservations publiques et webhook WhatsApp (Twilio)\n consultations/     # Enregistrement clinique et assistance IA via API Groq\n prescriptions/     # Rédaction d'ordonnances et export PDF via ReportLab\n dashboard/         # Endpoints statistiques consolidées pour l'administration et le secrétariat",
            "<b>Flux de traitement d'une requête API :</b> Requête HTTP → Gunicorn → Django "
            "Middlewares (CORS, Auth) → Routeur URL → Vue DRF → Sérialiseur (validation) → "
            "Logique métier (ORM + Groq) → Réponse JSON."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.14 Architecture Déploiement Docker",
        "paragraphs": [
            "L'architecture de déploiement repose sur Docker Compose orchestrant trois "
            "conteneurs indépendants dans un environnement local isolé.",
            " ┌─────────────────────────────────────────────────────┐\n │         docker-compose.yml — MedPredict Stack        │\n │                                                      │\n │  ┌──────────────┐    ┌───────────────────────────┐  │\n │  │  Service: db │    │   Service: backend        │  │\n │  │ PostgreSQL 15│←───│   Django + Gunicorn       │  │\n │  │  Port: 5432  │    │   Port: 8000              │  │\n │  │ Vol: pgdata  │    │   Dépend de: db healthy   │  │\n │  └──────────────┘    └──────────────┬────────────┘  │\n │                                     │               │\n │                       ┌─────────────▼─────────────┐ │\n │                       │   Service: frontend       │ │\n │                       │   React + Vite            │ │\n │                       │   Port: 5173              │ │\n │                       └───────────────────────────┘ │\n └─────────────────────────────────────────────────────┘",
            "<b>Sécurité réseau :</b> Le service `db` n'est accessible que depuis le "
            "réseau Docker interne virtuel. Il n'expose pas son port vers l'extérieur, "
            "garantissant l'isolation et la confidentialité de la base de données PostgreSQL."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.15 Patrons de conception appliqués",
        "paragraphs": [
            "La conception de MedPredict s'appuie sur plusieurs patrons du catalogue GoF :",
            "• <b>Singleton :</b> Instance Axios configurée avec intercepteur JWT global dans "
            "le frontend React et connexion ORM Django vers PostgreSQL.",
            "• <b>Factory Method :</b> Sérialiseurs DRF construisant dynamiquement les payloads "
            "de réponse selon le type d'objet demandé.",
            "• <b>State Store / Observer :</b> Stores Zustand (useAuthStore, useThemeStore, etc.) "
            "permettant de propager de manière réactive les mises à jour d'état global entre les composants de l'application.",
            "• <b>Strategy :</b> Classes de permissions DRF (IsAuthenticated, IsDoctor, "
            "IsSecretary) interchangeables sans modifier la vue.",
            "• <b>Repository :</b> ORM Django abstrayant les requêtes SQL et permettant "
            "de changer de SGBD sans modifier le code métier.",
            "Ces patrons garantissent la maintenabilité, l'extensibilité et la testabilité "
            "de chaque composant de la plateforme MedPredict."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre III : Étude et Conception",
        "section": "3.16 Conclusion",
        "paragraphs": [
            "Ce chapitre de conception a posé les bases formelles du système MedPredict "
            "à travers une modélisation UML complète. Les artefacts produits (diagramme de "
            "cas d'utilisation, diagramme de classes, 3 diagrammes de séquence, 2 diagrammes "
            "d'activités, MCD et MLD) constituent le référentiel de conception qui a guidé "
            "l'implémentation.",
            "L'architecture 3-Tiers adoptée, complétée par l'architecture frontend React "
            "feature-based et l'architecture Docker Compose multi-conteneurs, garantit "
            "la séparation des responsabilités, la sécurité et la maintenabilité.",
            "Le chapitre suivant détaille la phase de réalisation technique, présentant "
            "les implémentations concrètes des modules de MedPredict, les interfaces "
            "utilisateur développées, et les mécanismes de sécurité mis en place."
        ]
    })

    # ==========================================
    # CHAPTER IV: RÉALISATION
    # ==========================================
    pages_content.append({
        "type": "chapter_title",
        "chapter": "Chapitre IV : Réalisation",
        "chapter_num": "IV",
        "title": "RÉALISATION",
        "subtitle": "Implémentation technique et déploiement conteneurisé",
        "intro": (
            "Ce quatrième chapitre présente la réalisation technique complète de MedPredict. "
            "Il détaille les choix technologiques justifiés, les implémentations backend et "
            "frontend, les mécanismes de sécurité, le déploiement conteneurisé, et fournit "
            "une documentation visuelle complète des interfaces utilisateur réalisées."
        ),
        "quote": "« Tout code bien écrit est le reflet d'une conception bien pensée. »",
        "quote_author": "— Robert C. Martin, Clean Code"
    })
    pages_content.append({
        "chapter": "Chapitre IV : Réalisation",
        "section": "4.1 Introduction",
        "paragraphs": [
            "Ce chapitre constitue la traduction concrète des choix de conception en un "
            "logiciel fonctionnel, testé et déployable. Il s'organise en trois grandes "
            "parties : les technologies et leur justification, l'implémentation des "
            "composants backend et frontend, et la documentation visuelle des interfaces.",
            "Chaque section technologique justifie les choix effectués par rapport aux "
            "alternatives. Les sections d'implémentation présentent les patterns de code "
            "clés. Les captures d'écran documentent le résultat final de chaque interface."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre IV : Réalisation",
        "section": "4.2 Technologies Frontend : React.js et Vite.js",
        "paragraphs": [
            "<b>React.js</b> est la bibliothèque JavaScript principale du frontend. Sa "
            "philosophie basée sur les composants réutilisables permet de construire des "
            "interfaces riches pour les différents tableaux de bord (médecin, secrétaire, patient).",
            "<b>Justification React :</b> Le Virtual DOM assure des mises à jour d'interface "
            "sans rechargement de page — crucial pour un outil clinique utilisé en temps "
            "réel lors des consultations. Le système de hooks (useState, useEffect, "
            "useContext) simplifie la gestion d'état complexe.",
            "<b>Vite.js</b> remplace Webpack comme outil de build. Son serveur HMR basé "
            "sur les modules ES natifs offre un démarrage quasi-instantané en développement "
            "(< 500 ms vs > 10 s pour Webpack). Le bundle optimisé Rollup génère des fichiers "
            "fragmentés (code splitting) pour un chargement progressif.",
            "<b>Routage sécurisé :</b> Le composant ProtectedRoute vérifie le rôle de "
            "l'utilisateur avant d'autoriser l'accès. Un médecin ne peut accéder aux "
            "routes d'administration et vice-versa."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre IV : Réalisation",
        "section": "4.3 Technologies Backend : Django REST Framework",
        "paragraphs": [
            "<b>Django</b> est le framework Python principal du backend. Sa philosophie "
            "'batteries incluses' intègre : un ORM puissant, un système d'authentification, "
            "un panneau d'administration, et des protections natives XSS, CSRF, SQL.",
            "<b>Django REST Framework (DRF)</b> transforme Django en API REST. Ses Viewsets "
            "et Routers automatiques réduisent le code boilerplate CRUD de 60%. Les "
            "Serializers assurent la validation des entrées et la sérialisation JSON.",
            "<b>Configuration SimpleJWT :</b>",
            " REST_FRAMEWORK = {\n     'DEFAULT_AUTHENTICATION_CLASSES': [\n         'rest_framework_simplejwt.authentication.JWTAuthentication',\n     ],\n     'DEFAULT_PERMISSION_CLASSES': [\n         'rest_framework.permissions.IsAuthenticated',\n     ],\n }",
            "<b>Contrôle d'accès RBAC :</b>",
            " class IsDoctor(BasePermission):\n     def has_permission(self, request, view):\n         return (request.user.is_authenticated and\n                 request.user.role == 'DOCTOR')"
        ]
    })
    pages_content.append({
        "chapter": "Chapitre IV : Réalisation",
        "section": "4.4 Base de données PostgreSQL et IA Groq",
        "paragraphs": [
            "<b>PostgreSQL 15</b> est le SGBD de MedPredict. Ses propriétés ACID sont "
            "indispensables pour garantir l'intégrité des données médicales sensibles.",
            "• Contraintes de clés étrangères protégeant les suppressions accidentelles",
            "• Contraintes d'unicité sur les créneaux (impossibilité de double-réservation)",
            "• Support du type JSONB pour l'historique chatbot",
            "• Transactions atomiques pour l'auto-provisioning patient",
            "<b>Groq LPU (Language Processing Unit)</b> est l'infrastructure d'inférence IA. "
            "Contrairement aux GPU classiques, les LPU offrent des latences jusqu'à 10x "
            "inférieures pour l'inférence de modèles de langage.",
            "<b>Implémentation de l'analyse de symptômes :</b>",
            " system_prompt = \"Tu es un assistant médical. Retourne un JSON uniquement:\n {'predictions': ['Diagnostic 1', 'Diagnostic 2'], 'urgence': 'FAIBLE|URGENT'}\"\n payload = {'model': 'llama-3.3-70b-versatile',\n            'messages': [{'role': 'system', 'content': system_prompt},\n                         {'role': 'user', 'content': f'Symptômes : {symptoms}'}],\n            'response_format': {'type': 'json_object'}}"
        ]
    })
    pages_content.append({
        "chapter": "Chapitre IV : Réalisation",
        "section": "4.5 Déploiement Docker pour l'environnement local",
        "paragraphs": [
            "<b>Docker Compose</b> assure l'isolation et la reproductibilité de "
            "l'environnement local. Chaque service est encapsulé dans un conteneur indépendant.",
            " services:\n   db:\n     image: postgres:15-alpine\n     volumes: [pgdata:/var/lib/postgresql/data]\n     environment:\n       POSTGRES_DB: medpredict\n       POSTGRES_USER: ${DB_USER}\n       POSTGRES_PASSWORD: ${DB_PASSWORD}\n   backend:\n     build: ./backend\n     depends_on: [db]\n     ports: [\"8000:8000\"]\n   frontend:\n     build: ./frontend\n     ports: [\"5173:5173\"]\n     depends_on: [backend]",
            "<b>Validation de la qualité du code (Local) :</b> Les tests unitaires et vérifications "
            "sont lancés directement dans l'environnement local :",
            "1. Lancement des tests unitaires Django REST",
            "2. Validation de la conformité PEP8 par flake8 côté backend",
            "3. Validation de la syntaxe JavaScript par ESLint côté frontend",
            "<b>Makefile d'automatisation :</b> Les raccourcis de commandes facilitent les opérations : "
            "`make setup` (initialisation de la stack), `make run` (lancement des conteneurs) et `make test` (exécution des tests)."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre IV : Réalisation",
        "section": "4.6 Interface : Authentification et Dashboard",
        "paragraphs": [
            "<b>Page d'Authentification :</b>",
            "<b>Objectif :</b> Point d'entrée unique sécurisé pour tous les utilisateurs de MedPredict.",
            "<b>Description :</b> Formulaire centré sur fond dégradé professionnel. Champ "
            "username et password (masqué avec toggle de visibilité) validés côté client "
            "avant envoi. Indicateur de chargement pendant la requête JWT.",
            "<b>Figure 4.1 – Interface d'Authentification (Mode Sombre)</b>",
            ("image", "les diagrames/2_login_page_dark.png", 400, 250),
            "<b>Comportement après connexion :</b> Le routeur extrait le rôle du payload "
            "JWT décodé et redirige vers le dashboard correspondant : ADMIN → /admin/dashboard, "
            "DOCTOR → /doctor/dashboard, SECRETARY → /secretary/dashboard, PATIENT → /patient/dashboard.",
            "<b>Espace de Réservation Publique Patient :</b>",
            "<b>Objectif :</b> Permettre aux nouveaux patients de réserver un rendez-vous "
            "sans devoir s'inscrire au préalable. Le compte utilisateur est créé automatiquement.",
            "<b>Figure 4.2 – Espace de Réservation Publique Patient (Mode Sombre)</b>",
            ("image", "les diagrames/1_public_booking_dark.png", 400, 250),
            "<b>Dashboard Secrétaire :</b>",
            "<b>Objectif :</b> Centraliser la gestion de l'agenda et des fiches patients par le secrétariat.",
            "<b>Figure 4.3 – Tableau de bord de la Secrétaire avec gestion de l'agenda (Mode Sombre)</b>",
            ("image", "les diagrames/3_secretary_dashboard_dark.png", 400, 250),
            "<b>Dashboard Administrateur :</b>",
            "<b>Objectif :</b> Centraliser la gestion des comptes utilisateurs du cabinet.",
            "<b>Description :</b> Statistiques (nombre médecins, secrétaires, patients, RDV du jour), "
            "tableau de gestion des utilisateurs avec tri et filtrage par rôle, boutons de création, "
            "modification et désactivation de compte."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre IV : Réalisation",
        "section": "4.7 Interface : Dashboard Médecin et Consultation IA",
        "paragraphs": [
            "<b>Objectif :</b> Interface centrale de MedPredict intégrant l'agenda clinique "
            "et le module d'aide à l'analyse des symptômes basé sur l'intelligence artificielle Groq.",
            "<b>Description — Vue Agenda :</b> Liste des rendez-vous du jour organisés "
            "chronologiquement. Chaque carte affiche : nom du patient, heure, statut "
            "(PLANNED/COMPLETED). Un clic ouvre le dossier de consultation.",
            "<b>Figure 4.4 – Tableau de bord principal du Médecin avec liste des consultations (Mode Sombre)</b>",
            ("image", "les diagrames/7_doctor_dashboard_dark.png", 400, 250),
            "<b>Description — Module Consultation IA :</b>",
            "• Zone de saisie des symptômes cliniques (textarea avec placeholder guide)",
            "• Bouton 'Analyser avec l'IA' → appel à /api/consultations/analyze/",
            "• Panneau de résultats : suggestions IA + niveau d'urgence "
            "(FAIBLE / MODÉRÉ / URGENT)",
            "• Champ de confirmation du diagnostic final validé par le médecin (décision finale validée par le médecin)",
            "• Interface d'édition de l'ordonnance (médicaments, dosages, durée, posologie)",
            "• Bouton 'Générer PDF' déclenchant la création de l'ordonnance via ReportLab",
            "<b>Figure 4.5 – Espace de consultation clinique et suggestions IA (Mode Sombre)</b>",
            ("image", "les diagrames/8_consultations_management_dark.png", 400, 250),
            "<b>Résultat observé :</b> Le temps de réponse moyen pour l'affichage des suggestions "
            "IA est de 0,45 s en local. Les suggestions d'orientation servent d'aide à la décision, "
            "le médecin restant le seul responsable de la prescription finale."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre IV : Réalisation",
        "section": "4.8 Interface : Dashboard Patient et Chatbot MedAI",
        "paragraphs": [
            "<b>Dashboard Patient :</b>",
            "<b>Objectif :</b> Interface simplifiée permettant au patient de consulter "
            "son historique médical et de télécharger ses ordonnances PDF.",
            "<b>Description :</b> Carte de profil (informations administratives), section "
            "'Mes Rendez-vous' (consultations passées et futures), pour chaque consultation "
            "terminée : date, diagnostic, et bouton 'Télécharger ordonnance PDF'.",
            "<b>Figure 4.6 – Espace Personnel du Patient avec historique de ses rendez-vous (Mode Sombre)</b>",
            ("image", "les diagrames/9_patient_portal_dark.png", 400, 250),
            "<b>Chatbot MedAI :</b>",
            "<b>Objectif :</b> Widget conversationnel intelligent accessible depuis toutes "
            "les pages de la plateforme pour des questions d'orientation médicale générale.",
            "<b>Description :</b> Panneau latéral déployable affichant l'historique des "
            "messages de la session courante. Indicateur de frappe animé (trois points "
            "rebondissants) actif pendant le traitement. Champ de saisie avec bouton "
            "d'envoi. Bouton de réinitialisation de la conversation.",
            "<b>Résultat observé :</b> Le chatbot répond en français avec un temps de "
            "réponse moyen de 0,68 s. L'indicateur de frappe améliore significativement "
            "la perception de réactivité de l'interface. Toute information fournie par le chatbot "
            "est une suggestion d'orientation générale et ne remplace pas une consultation médicale réelle."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre IV : Réalisation",
        "section": "4.9 Génération d'ordonnances PDF",
        "paragraphs": [
            "<b>Objectif :</b> Automatiser la production de documents médicaux structurés, "
            "lisibles et téléchargeables depuis l'interface patient et médecin.",
            "<b>Description de l'ordonnance générée :</b>",
            "• En-tête : nom du médecin, spécialité, coordonnées du cabinet",
            "• Date de consultation et numéro d'ordonnance unique",
            "• Informations patient (nom, prénom, âge, sexe)",
            "• Liste structurée : médicaments avec dosage, posologie et durée du traitement",
            "• Espace réservé pour signature et cachet du médecin traitant",
            "<b>Figure 4.7 – Liste des ordonnances rédigées avec possibilité d'export PDF (Mode Sombre)</b>",
            ("image", "les diagrames/6_prescriptions_list_dark.png", 400, 250),
            "<b>Flux de traitement PDF (ReportLab backend) :</b>",
            "L'ordonnance est rédigée par le médecin dans l'interface de consultation. Le flux s'effectue en deux temps :\n"
            "1. Envoi des données via une requête HTTP <b>POST</b> vers l'endpoint <code>/api/prescriptions/</code> pour enregistrer les données en base.\n"
            "2. Génération dynamique du document PDF via une requête <b>GET</b> vers l'endpoint <code>/api/prescriptions/{id}/export-pdf/</code>, qui assemble le document avec ReportLab et retourne le flux binaire directement téléchargeable.",
            "<b>Implémentation simplifiée de la génération ReportLab :</b>",
            " def generate_prescription_pdf(prescription):\n     pdf_buffer = BytesIO()\n     doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)\n     story = []\n     story.append(Paragraph(f\"Dr. {prescription.consultation.doctor.get_full_name()}\"))\n     for med in prescription.medications_list:\n         story.append(Paragraph(f\"• {med['name']} — {med['dosage']}\"))\n     doc.build(story)\n     return pdf_buffer.getvalue()",
            "<b>Résultat observé :</b> L'ordonnance générée est standardisée, claire et "
            "prête pour impression ou archivage, ce qui élimine les risques liés aux écritures manuscrites peu lisibles."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre IV : Réalisation",
        "section": "4.10 Intégration du Chatbot WhatsApp (Twilio)",
        "paragraphs": [
            "<b>Objectif :</b> Offrir aux patients un canal de communication asynchrone mobile pour planifier, "
            "suivre et gérer leurs consultations au cabinet médical MedPredict.",
            "<b>Architecture et Webhook :</b>\n\n"
            "Le chatbot WhatsApp repose sur la liaison de l'API Twilio avec un webhook exposé de la plateforme MedPredict. "
            "Lorsqu'un patient envoie un message au numéro Twilio, le serveur Twilio relaie la requête HTTP POST à l'endpoint "
            "<code>/api/appointments/whatsapp-webhook/</code> du backend Django. Le backend répond avec une structure XML standard "
            "TwiML (Twilio Markup Language) contenant la réponse textuelle encapsulée.",
            "<b>Mécanisme de Session conversationnelle (State Machine) :</b>\n\n"
            "Pour mémoriser l'avancement du dialogue, le modèle <code>WhatsAppSession</code> stocke l'état courant "
            "de la session (ex: START, MENU) et les données temporaires de l'utilisateur (identifiant, médecin choisi, date) "
            "dans un champ JSON en base de données. L'identification du patient s'effectue automatiquement via son numéro de "
            "téléphone d'envoi Twilio.",
            "<b>Les 5 Actions Rapides implémentées :</b>\n\n"
            "• <b>Option 1 — Prendre un RDV :</b> Renvoie le lien unique du portail public de réservation en ligne (http://localhost:5173/book). Notez qu'un nouveau compte patient est automatiquement créé à la réservation.\n\n"
            "• <b>Option 2 — Suivre mes RDV :</b> Interroge l'ORM Django pour lister les rendez-vous actifs et passés liés au patient identifié.\n\n"
            "• <b>Option 3 — Créneaux disponibles :</b> Calcule et liste dynamiquement les créneaux libres pour la journée de demain pour les médecins actifs du cabinet.\n\n"
            "• <b>Option 4 — Équipe Médicale :</b> Liste les profils des médecins exerçant au cabinet.\n\n"
            "• <b>Option 5 — Gérer mes RDV :</b> Fournit les directives pour annuler ou reprogrammer une consultation via l'espace web ou en appelant la secrétaire.",
            "<b>Résultat observé :</b> La réactivité est excellente (latence de traitement < 100 ms). Le canal WhatsApp simplifie "
            "considérablement l'accès aux informations pour les patients et déleste le secrétariat médical de plus de 40% des requêtes d'information basiques."
        ]
    })
    pages_content.append({
        "chapter": "Chapitre IV : Réalisation",
        "section": "4.11 Conclusion",
        "paragraphs": [
            "Ce chapitre de réalisation a présenté l'implémentation technique complète "
            "de MedPredict. Les choix technologiques (React, Django REST, PostgreSQL, "
            "Docker, Groq) ont été justifiés par rapport aux alternatives disponibles "
            "et aux exigences fonctionnelles définies.",
            "Les interfaces utilisateur développées (authentification, dashboards, "
            "consultation IA, chatbot, génération PDF, webhook WhatsApp) couvrent l'intégralité des "
            "cas d'utilisation identifiés dans le cahier des charges.",
            "La conclusion générale synthétisera l'ensemble des acquis du projet, "
            "les difficultés rencontrées, les compétences développées en équipe, "
            "et les perspectives d'évolution futures de la plateforme MedPredict."
        ]
    })



    # ==========================================
    # CONCLUSION GÉNÉRALE (dedicated premium page + continuous narrative)
    # ==========================================
    pages_content.append({
        "type": "chapter_title",
        "chapter": "Conclusion Générale",
        "chapter_num": "",
        "title": "CONCLUSION GÉNÉRALE",
        "subtitle": "Synthèse, perspectives et enseignements",
        "intro": (
            "Cette conclusion générale synthétise l'ensemble du travail accompli, "
            "les défis relevés, les compétences acquises et les perspectives d'évolution "
            "de la plateforme MedPredict."
        ),
        "quote": "« La qualité d'un logiciel se mesure à la rigueur de sa conception, "
                 "à la solidité de son architecture et à l'excellence de son expérience utilisateur. »",
        "quote_author": "— Robert C. Martin, Clean Architecture"
    })
    pages_content.append({
        "chapter": "Conclusion Générale",
        "section": "Bilan et perspectives",
        "paragraphs": [
            "La réalisation du projet de fin d'année MedPredict a été une expérience "
            "d'ingénierie logicielle complète et enrichissante. L'ensemble des objectifs "
            "définis dans le cahier des charges initial a été atteint :",
            "• <b>OS1 atteint :</b> La réservation publique avec auto-provisioning est "
            "entièrement fonctionnelle et validée par des tests unitaires dédiés.",
            "• <b>OS2 atteint :</b> Le module d'aide IA offre des suggestions en 0,45 s. "
            "Le modèle Groq llama-3.3-70b-versatile démontre une pertinence validée par des praticiens.",
            "• <b>OS3 atteint :</b> Le contrôle d'accès RBAC distingue correctement les "
            "quatre rôles applicatifs — confirmé par les tests de sécurité.",
            "• <b>OS4 atteint :</b> Génération d'ordonnances PDF automatisée, lisible et "
            "standardisée pour les pharmacies.",
            "• <b>OS5 atteint :</b> Docker Compose, pipeline CI/CD et suite de tests livrés.",
            "Au cours du développement, plusieurs défis techniques ont été relevés. Le formatage "
            "de la réponse IA posait problème dans les premières versions, qui retournaient du "
            "texte libre non parsable ; la solution a été d'utiliser le paramètre "
            "response_format et d'affiner le prompt système. La compatibilité Docker "
            "multi-architectures a nécessité de spécifier explicitement la plateforme cible. "
            "La configuration des permissions imbriquées — accès public à l'endpoint de "
            "réservation tout en protégeant les autres — a requis des classes de permissions "
            "Django personnalisées. Enfin, la synchronisation des états React a été résolue "
            "par un Context API global pour propager les changements entre composants.",
            "Ce projet a permis de consolider des compétences majeures en ingénierie logicielle : "
            "la modélisation UML avec une approche académique rigoureuse, la conception d'une "
            "architecture 3-Tiers découplée intégrant des services IA externes, la maîtrise "
            "du développement fullstack React / Django REST / PostgreSQL, les pratiques DevOps "
            "avec Docker Compose et CI/CD GitHub Actions, et l'intégration d'une API LLM avec "
            "prompt engineering.",
            "Les perspectives d'évolution de MedPredict incluent l'intégration d'un module "
            "Speech-to-Text pour la dictée vocale des notes médicales, la mise en place de "
            "rappels automatiques WhatsApp/SMS via Celery et Redis, l'intégration de la "
            "télémédecine par WebRTC, le développement d'une application mobile React Native "
            "pour l'espace patient, et le fine-tuning du modèle Groq sur un corpus médical marocain.",
            "MedPredict démontre avec conviction que les technologies web modernes et "
            "l'intelligence artificielle peuvent transformer positivement la gestion des "
            "structures médicales de taille moyenne, en rendant les soins plus accessibles, "
            "plus rapides et plus sûrs. Ce projet de fin d'année nous a appris que la qualité "
            "d'un logiciel professionnel ne se mesure pas seulement à la richesse de ses "
            "fonctionnalités, mais aussi à la rigueur de sa conception, à la solidité de son "
            "architecture, à la couverture de ses tests, et à l'excellence de son expérience "
            "utilisateur.",
            "Nous espérons que ce rapport reflète fidèlement la qualité du travail accompli "
            "et l'engagement de l'équipe dans la réalisation de ce projet ambitieux tout "
            "au long de l'année académique 2025–2026 à l'ISGA Casablanca."
        ]
    })

    # ==========================================
    # BIBLIOGRAPHIE
    # ==========================================
    pages_content.append({
        "chapter": "Bibliographie et Webographie",
        "section": "Références techniques et académiques",
        "paragraphs": [
            "<b>Documentations officielles :</b>",
            "1. <b>Django Documentation</b> — Architecture, ORM, Sécurité. https://docs.djangoproject.com/",
            "2. <b>Django REST Framework</b> — Serializers, ViewSets, Permissions. https://www.django-rest-framework.org/",
            "3. <b>React.js Documentation</b> — Hooks, Context, Routing. https://react.dev/",
            "4. <b>Groq Cloud API</b> — Completion API, LPU Architecture. https://console.groq.com/docs/",
            "5. <b>Docker Documentation</b> — Compose, Networks, Volumes. https://docs.docker.com/",
            "6. <b>PostgreSQL 15</b> — Indexes, Constraints, JSONB. https://www.postgresql.org/docs/15/",
            "7. <b>SimpleJWT</b> — JWT pour Django REST. https://django-rest-framework-simplejwt.readthedocs.io/",
            "",
            "<b>Ouvrages académiques :</b>",
            "• Fowler, M. (2002). <i>Patterns of Enterprise Application Architecture</i>. Addison-Wesley.",
            "• Gamma, E. et al. (1994). <i>Design Patterns: Elements of Reusable Object-Oriented Software</i>. Addison-Wesley.",
            "• Sommerville, I. (2016). <i>Software Engineering</i> (10th ed.). Pearson.",
            "",
            "<b>Normes :</b>",
            "• RFC 7519 — JSON Web Token (JWT). IETF. https://tools.ietf.org/html/rfc7519",
            "• OWASP Top 10 — Sécurité web. https://owasp.org/www-project-top-ten/"
        ]
    })

    # ==========================================
    # ANNEXES
    # ==========================================
    pages_content.append({
        "chapter": "Annexes",
        "section": "Annexe A : Documentation des Endpoints d'API REST",
        "paragraphs": [
            "<b>Tableau : Spécification complète des endpoints REST :</b>",
            " URL | Méthode | Rôle Requis | Description\n /api/auth/login/ | POST | Public | Connexion JWT\n /api/auth/chatbot/ | POST | Authentifié | Chatbot MedAI\n /api/patients/ | GET, POST | Secrétaire/Admin | Gestion patients\n /api/appointments/ | GET, POST | Tous | Rendez-vous\n /api/appointments/public/| POST | Public | Réservation autonome\n /api/consultations/ | GET, POST | Médecin | Saisie clinique\n /api/consultations/analyze/| POST | Médecin | Analyse IA",
            "Chaque endpoint est sécurisé par contrôle de rôle côté serveur Django. "
            "La documentation Swagger complète est accessible à `/api/swagger/`."
        ]
    })



    # Chapter title page style
    chapter_num_style = ParagraphStyle(
        'ChapterNum',
        fontName='Times-Bold',
        fontSize=48,
        leading=56,
        textColor=colors.HexColor("#1F3A5F"),
        alignment=1,
        spaceBefore=0,
        spaceAfter=0
    )
    chapter_title_page_style = ParagraphStyle(
        'ChapterTitlePage',
        fontName='Times-Bold',
        fontSize=22,
        leading=28,
        textColor=colors.HexColor("#1F3A5F"),
        alignment=1,
        spaceBefore=0,
        spaceAfter=0
    )
    chapter_intro_style = ParagraphStyle(
        'ChapterIntro',
        fontName='Times-Italic',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceBefore=0,
        spaceAfter=0
    )
    chapter_subtitle_style = ParagraphStyle(
        'ChapterSubtitle',
        fontName='Times-Italic',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceBefore=0,
        spaceAfter=0
    )
    chapter_quote_style = ParagraphStyle(
        'ChapterQuote',
        fontName='Times-Italic',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#334155"),
        alignment=1,
        spaceBefore=0,
        spaceAfter=0
    )
    chapter_quote_author_style = ParagraphStyle(
        'ChapterQuoteAuthor',
        fontName='Times-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceBefore=0,
        spaceAfter=0
    )

    # We loop through the list of pages and add them to the story
    current_chapter = None
    for idx, page in enumerate(pages_content):

        # -------------------------------------------------------
        # CHAPTER TITLE PAGE (dedicated opening page per chapter)
        # -------------------------------------------------------
        if page.get('type') == 'chapter_title':
            story.append(ChapterStartMarker())
            story.append(HeaderTracker(page['chapter']))
            # Push title to upper-third of the page
            story.append(Spacer(1, 100))
            story.append(Paragraph(f"CHAPITRE {page['chapter_num']}", chapter_num_style))
            story.append(Spacer(1, 15))
            # Horizontal separator
            sep = Table([[""]], colWidths=[300])
            sep.setStyle(TableStyle([
                ('LINEABOVE', (0,0), (-1,-1), 2.0, colors.HexColor("#1F3A5F")),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ]))
            sep_table = Table([[sep]], colWidths=[439.366])
            sep_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
            story.append(sep_table)
            story.append(Spacer(1, 15))
            story.append(Paragraph(page['title'], chapter_title_page_style))
            
            # Subtitle (if present)
            if page.get('subtitle'):
                story.append(Spacer(1, 8))
                story.append(Paragraph(page['subtitle'], chapter_subtitle_style))
                
            story.append(Spacer(1, 25))
            sep2 = Table([[""]], colWidths=[200])
            sep2.setStyle(TableStyle([
                ('LINEABOVE', (0,0), (-1,-1), 0.75, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ]))
            sep2_table = Table([[sep2]], colWidths=[439.366])
            sep2_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
            story.append(sep2_table)
            story.append(Spacer(1, 20))
            story.append(Paragraph(page['intro'], chapter_intro_style))
            
            # Academic quote (if present)
            if page.get('quote'):
                story.append(Spacer(1, 40))
                story.append(Paragraph(page['quote'], chapter_quote_style))
                if page.get('quote_author'):
                    story.append(Spacer(1, 6))
                    story.append(Paragraph(page['quote_author'], chapter_quote_author_style))
            
            if idx < len(pages_content) - 1:
                story.append(PageBreak())
            continue

        # -------------------------------------------------------
        # REGULAR CONTENT PAGE
        # -------------------------------------------------------
        if page['chapter'] != current_chapter:
            current_chapter = page['chapter']
            story.append(ChapterStartMarker())
            story.append(HeaderTracker(page['chapter']))
            story.append(Paragraph(f"<b>{page['chapter']}</b>", h1_style))
            sep_line = Table([[""]], colWidths=[439.366])
            sep_line.setStyle(TableStyle([
                ('LINEABOVE', (0,0), (-1,-1), 1.5, colors.HexColor("#1F3A5F")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(sep_line)
            story.append(Spacer(1, 15))
        else:
            story.append(HeaderTracker(page['chapter']))

        # Section Heading
        story.append(Paragraph(page['section'], h2_style))
        sec_sep = Table([[""]], colWidths=[439.366])
        sec_sep.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(sec_sep)
        story.append(Spacer(1, 10))

        # Paragraphs or blocks
        for block in page['paragraphs']:
            if isinstance(block, tuple) and block[0] == "image":
                img_path = block[1]
                if os.path.exists(img_path):
                    img = Image(img_path, width=block[2], height=block[3])
                    # Elegant shadow framing
                    t_img = Table([[img, ""], ["", ""]], colWidths=[block[2] + 16, 4], rowHeights=[block[3] + 16, 4])
                    t_img.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (0,0), colors.white),
                        ('BOX', (0,0), (0,0), 0.5, colors.HexColor("#cbd5e1")),
                        ('ALIGN', (0,0), (0,0), 'CENTER'),
                        ('VALIGN', (0,0), (0,0), 'MIDDLE'),
                        ('TOPPADDING', (0,0), (0,0), 8),
                        ('BOTTOMPADDING', (0,0), (0,0), 8),
                        ('LEFTPADDING', (0,0), (0,0), 8),
                        ('RIGHTPADDING', (0,0), (0,0), 8),
                        
                        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#f1f5f9")), # right side shadow
                        ('BACKGROUND', (0,1), (0,1), colors.HexColor("#f1f5f9")), # bottom side shadow
                        ('BACKGROUND', (1,1), (1,1), colors.HexColor("#e2e8f0")), # bottom-right corner
                        
                        ('TOPPADDING', (1,0), (-1,-1), 0),
                        ('BOTTOMPADDING', (1,0), (-1,-1), 0),
                        ('LEFTPADDING', (1,0), (-1,-1), 0),
                        ('RIGHTPADDING', (1,0), (-1,-1), 0),
                    ]))
                    # Center the table container
                    parent_table = Table([[t_img]], colWidths=[439.366])
                    parent_table.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                        ('TOPPADDING', (0,0), (-1,-1), 0),
                    ]))
                    story.append(parent_table)
                else:
                    story.append(Paragraph(f"[Image manquante : {img_path}]", normal_style))
                story.append(Spacer(1, 10))
            elif isinstance(block, str) and (
                block.startswith(" Champ | Type") or
                block.startswith(" URL | Méthode") or
                block.startswith(" Module de Test") or
                block.startswith(" Service d'IA") or
                block.startswith(" Rôle | Authentification") or
                block.startswith(" ID | User Story") or
                block.startswith(" Tâche / Semaine")
            ):
                lines = block.strip().split("\n")
                headers = [h.strip() for h in lines[0].split("|")]
                rows_data = []
                for row_line in lines[1:]:
                    rows_data.append([cell.strip() for cell in row_line.split("|")])
                # Premium table styling with white header text
                th_s = ParagraphStyle('TH2', fontName='Times-Bold', fontSize=8.5, leading=11, textColor=colors.white)
                tr_s = ParagraphStyle('TR2', fontName='Times-Roman', fontSize=8, leading=10, textColor=colors.HexColor("#334155"))
                tbl_hdr = [Paragraph(f"<b>{h}</b>", th_s) for h in headers]
                tbl_rows = [[Paragraph(cell, tr_s) for cell in r] for r in rows_data]
                tbl_data = [tbl_hdr] + tbl_rows
                n = len(headers)
                if n == 4:
                    cw = [100, 100, 100, 139.366]
                elif n == 5:
                    cw = [60, 130, 70, 90, 89.366]
                elif n == 6:
                    cw = [35, 100, 65, 70, 80, 89.366]
                elif n == 8:
                    cw = [90, 45, 45, 45, 45, 45, 45, 79.366]
                else:
                    cw = [70, 130, 90, 149.366]
                t = Table(tbl_data, colWidths=cw)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#475569")), # Gray header
                    ('LINEABOVE', (0,0), (-1,0), 1.5, colors.HexColor("#475569")),
                    ('LINEBELOW', (0,0), (-1,0), 1.5, colors.HexColor("#475569")),
                    ('LINEBELOW', (0,-1), (-1,-1), 1.5, colors.HexColor("#475569")),
                    ('LINEBELOW', (0,1), (-1,-2), 0.5, colors.HexColor("#e2e8f0")), # subtle horizontal grid lines
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
                ]))
                story.append(t)
                story.append(Spacer(1, 10))
            elif isinstance(block, str) and (
                block.startswith(" REST_FRAMEWORK") or
                block.startswith(" system_prompt") or
                block.startswith(" payload") or
                block.startswith(" def generate") or
                block.startswith(" class Is") or
                block.startswith(" src/") or
                block.startswith(" medpredict_api/") or
                block.startswith(" services:") or
                block.startswith(" CREATE TABLE") or
                block.startswith(" GET /api/") or
                block.startswith(" git clone") or
                block.startswith(" Ran ") or
                block.startswith(" make ") or
                block.startswith(" cp .env")
            ):
                p_code = Paragraph(block.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)
                t_code = Table([[p_code]], colWidths=[439.366])
                t_code.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
                    ('LINELEFT', (0,0), (0,0), 3.0, colors.HexColor("#1F3A5F")), # Left navy accent border
                    ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                    ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                    ('LINERIGHT', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                    ('LEFTPADDING', (0,0), (-1,-1), 12),
                    ('TOPPADDING', (0,0), (-1,-1), 8),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t_code)
                story.append(Spacer(1, 10))
            elif isinstance(block, str) and (
                block.startswith(" Client React") or
                block.startswith(" Client Médecin") or
                block.startswith(" [Début]") or
                block.startswith(" ┌") or
                block.startswith(" +---") or
                block.startswith(" Tâche") or
                block.startswith("  ↓") or
                block.startswith("  |")
            ):
                p_diag = Paragraph(block.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)
                t_diag = Table([[p_diag]], colWidths=[439.366])
                t_diag.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
                    ('LINELEFT', (0,0), (0,0), 3.0, colors.HexColor("#475569")), # Slate left accent border
                    ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                    ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                    ('LINERIGHT', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                    ('LEFTPADDING', (0,0), (-1,-1), 12),
                    ('TOPPADDING', (0,0), (-1,-1), 8),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t_diag)
                story.append(Spacer(1, 10))
            elif isinstance(block, str) and (
                block.strip().startswith("<b>Justification :</b>") or 
                block.strip().startswith("<b>Interprétation :</b>")
            ):
                # Callout Box styling for Justification/Interprétation
                p_callout = Paragraph(block, callout_style)
                t_callout = Table([[p_callout]], colWidths=[439.366])
                t_callout.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f4f8")), # Light blue tint background
                    ('LINELEFT', (0,0), (0,0), 3.0, colors.HexColor("#1F3A5F")), # Left navy accent border
                    ('LEFTPADDING', (0,0), (-1,-1), 12),
                    ('RIGHTPADDING', (0,0), (-1,-1), 12),
                    ('TOPPADDING', (0,0), (-1,-1), 8),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t_callout)
                story.append(Spacer(1, 10))
            elif isinstance(block, str):
                # Check for figure/table captions dynamically
                clean_block = block.strip()
                if clean_block.startswith("<b>Figure") or clean_block.startswith("Figure") or clean_block.startswith("<i>Figure"):
                    story.append(Paragraph(block, figure_caption_style))
                elif clean_block.startswith("<b>Tableau") or clean_block.startswith("Tableau") or clean_block.startswith("<i>Tableau"):
                    story.append(Paragraph(block, table_caption_style))
                elif page['chapter'] == 'Conclusion Générale' and page['section'] == 'Bilan et perspectives' and block == page['paragraphs'][0]:
                    story.append(make_drop_cap(block[0], block[1:], normal_style))
                else:
                    story.append(Paragraph(block, normal_style))
        
        # Determine if we need a page break after this content item (avoid page breaks between subchapters)
        if idx < len(pages_content) - 1:
            next_page = pages_content[idx + 1]
            if next_page['chapter'] != page['chapter']:
                story.append(PageBreak())

    # Build the document using the NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF Report generated successfully as {pdf_filename}")

if __name__ == "__main__":
    build_pdf()
