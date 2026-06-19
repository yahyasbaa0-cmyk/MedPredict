# MedPredict - Solution Complète de Gestion de Cabinet Médical & IA

**MedPredict** est une application full-stack premium conçue pour l'administration d'un cabinet médical, intégrant un module d'intelligence artificielle pour l'aide au diagnostic clinique basé sur les symptômes. 

Ce projet a été développé avec une approche rigoureuse orientée **microservices** pour répondre aux attentes d'une soutenance académique / niveau ingénieur.

---

## 🏗️ Architecture et Stack Technique

L'application repose sur 4 conteneurs isolés via Docker Compose :

1. **Frontend (React + Vite + Zustand)** : 
   - Interface utilisateur premium "SaaS médical", avec un design Vanilla CSS.
   - Routage sécurisé basé sur les rôles JWT.
   - Dashboards interactifs avec `react-chartjs-2`.

2. **Backend Core (Django + Django REST Framework)** :
   - API REST complète gérant la logique métier (Patients, RDV, Consultations).
   - Authentification `SimpleJWT`.
   - Génération de PDF natifs via `ReportLab`.

3. **Microservice d'IA (Flask + Scikit-Learn)** :
   - API dédiée à la prédiction (`/predict`).
   - Modèle entraîné (Random Forest) sur un jeu de données médical (mapping symptômes-pathologies).
   - Architecture "Fail-safe" : si l'IA tombe en panne, le backend principal et la consultation restent fonctionnels.

4. **Base de Données (PostgreSQL)** :
   - Persistance sécurisée des données de santé.

---

## 🚀 Guide de Démarrage Rapide

Assurez-vous d'avoir installé **Docker** et **Docker Compose** sur votre machine.

### Étape 1 : Construire et lancer les conteneurs
Depuis le répertoire racine (`MedPredict`), exécutez :
```bash
docker-compose up --build -d
```
Docker va télécharger les images de base, construire l'API Django, initialiser le microservice Flask, et démarrer le serveur de développement Vite React.

### Étape 2 : Initialisation de la base de données
Une fois les conteneurs démarrés, appliquez les migrations et créez un administrateur :
```bash
# Appliquer les migrations de la base
docker-compose exec backend python manage.py makemigrations accounts patients appointments consultations prescriptions
docker-compose exec backend python manage.py migrate

# Créer l'utilisateur Administrateur / Médecin de test
docker-compose exec backend python manage.py createsuperuser
```

### Étape 3 : Entraîner le modèle d'IA
Le modèle d'IA doit être généré une première fois depuis le dataset CSV. Allez dans le service IA et lancez le script python :
```bash
docker-compose exec ai_service python model/train.py
```

### Étape 4 : Accès à l'application
- **Application Web (Frontend)** : [http://localhost:5173](http://localhost:5173)
- **API (Backend) & Swagger** : [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **Microservice IA (Direct)** : [http://localhost:5000/health](http://localhost:5000/health)

Connectez-vous sur le Frontend avec les identifiants créés lors du `createsuperuser`.

---

## 🎯 Scénario de Démonstration (Pour la soutenance)

Pour briller lors de la présentation, suivez ce cheminement :

1. **Dashboard** : Montrez l'interface d'accueil avec les graphiques interactifs pour prouver la gestion des datas croisées.
2. **Gestion des Patients** : Créez un patient, soulignez la fluidité de l'interface (Design System CSS sur-mesure) et la validation des formulaires.
3. **L'IA en action (La Consultation)** : 
   - Allez dans "Consultations". Tapez des symptômes (ex: `fever, cough, chest_pain`).
   - Cliquez sur "Solliciter l'IA Médicale".
   - Notez que l'IA répond quasi-instantanément avec des scores de confiance, et que **le message d'avertissement réglementaire (Ne remplace pas l'avis médical) est bien présent**.
4. **Génération d'ordonnance** : Terminez la consultation et générez une ordonnance. Montrez l'export PDF dynamique renvoyé par Django.

---

## 🛠️ Améliorations Futures (Perspectives)

Pour aller plus loin, vous pourriez évoquer devant le jury ces pistes futures :
- Création d'un portail "Patient" avec un système de prise de RDV automatique (type Doctolib).
- Remplacement du Scikit-learn embarqué par un véritable pipeline asynchrone NLP avec LLM (pour extraire les symptômes depuis le texte libre du médecin).
- Ajout de Redis et Celery pour le traitement asynchrone lourd (envoi des mails de rappel).
