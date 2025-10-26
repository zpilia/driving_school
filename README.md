# 🚗 DrivingSchool – Intranet de Gestion d'Auto-École

**DrivingSchool** est un intranet développé avec **Django**, destiné à la gestion complète d'une auto-école.  
Il centralise la gestion des comptes, des plannings, des rendez-vous et du suivi des élèves selon plusieurs rôles : **élèves**, **moniteurs**, **secrétaires** et **administrateurs**.

---

## 📌 Objectif

Offrir une plateforme web interne permettant :
- Aux élèves de suivre leur progression et de planifier leurs leçons.
- Aux moniteurs de gérer leur planning et leurs élèves.
- Aux secrétaires d’administrer les comptes, heures et rendez-vous.
- Aux administrateurs de superviser l’ensemble du système.

---

## 🧩 Fonctionnalités

### 👨‍🎓 Élève
- Visualisation du planning personnel
- Suivi des heures achetées / utilisées
- Prise de rendez-vous
- Réponse aux propositions de créneaux

### 👨‍🏫 Moniteur
- Consultation du planning
- Accès aux fiches élèves
- Gestion des rendez-vous

### 🧑‍💼 Secrétaire
- CRUD des comptes
- Consultation complète des fiches élèves
- Ajout de crédits d’heures
- Gestion des rendez-vous
- Visualisation des plannings

### 🛠️ Administrateur
- Dispose des droits secrétaire
- Gestion des comptes secrétaires
- Supervision totale

---

## 🎁 Bonus (Fonctionnalités avancées)

- Espace d’entraînement au code de la route
- Création de séries de questions
- Système interactif de demandes de rendez-vous
- Achat d’heures en ligne (PayPal / CB)

---

## 🛠️ Technologies Utilisées

- **Framework** : Django
- **Langage** : Python
- **Base de données** : SQLite
- **Templates** : Django Templates
- **Routing** : Django URL routing
- **Fixtures** : données préchargées

---

## 🗂️ Architecture du Projet

```
drivingschool/
├── students/
├── instructors/
├── secretaries/
├── core/
├── templates/
├── static/
├── db.sqlite3
└── manage.py
```

---

## 🚀 Démarrage Rapide

1. **Cloner le dépôt :**
```bash
git clone https://github.com/<votre-username>/drivingschool.git
cd drivingschool
```

2. **Créer l’environnement virtuel :**
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

3. **Appliquer les migrations et charger les fixtures :**
```bash
python manage.py migrate
python manage.py loaddata fixtures.json
```

4. **Lancer le serveur :**
```bash
python manage.py runserver
```

Application accessible sur :  
👉 **http://localhost:8000**

---

## 🖼️ Aperçu

<p align="center">
  <img src="./assets/drivingschool_1.png" width="900"/>
</p>

---

## 🤝 Auteur

Développé par [zpilia](https://github.com/zpilia), [Emilie20000](https://github.com/Emilie20000) et [Alexis072002](https://github.com/Alexis072002)  

Développé dans le cadre de la **formation Web@cadémie**, afin de démontrer la logique métier, la gestion des rôles utilisateurs et l’interface d’un intranet structuré.

---

## 🤝 Contributeurs

- [Emilie20000](https://github.com/Emilie20000)
- [Alexis072002](https://github.com/Alexis072002)

---

## 🪪 Licence

© zpilia — Tous droits réservés.  
L’usage, la reproduction ou la distribution sont soumis à autorisation.

---

# 🇬🇧 English Version

# 🚗 DrivingSchool – Driving School Management Intranet

**DrivingSchool** is an intranet built with **Django** to manage a driving school end‑to‑end.  
It centralizes accounts, scheduling, appointments, and student tracking across multiple roles.

---

## 📌 Objective

Provide an internal web system allowing:
- Students to track progress and book lessons
- Instructors to manage schedules and students
- Secretaries to manage accounts, credits and appointments
- Administrators to supervise everything

---

## 🧩 Features

### 👨‍🎓 Student
- Personal schedule
- Progress tracking
- Lesson booking
- Slot proposal responses

### 👨‍🏫 Instructor
- Schedule access
- Student profiles
- Appointment management

### 🧑‍💼 Secretary
- CRUD accounts
- Full student profiles
- Hours credit management
- Appointment management
- Global & personal calendars

### 🛠️ Administrator
- All secretary rights
- Secretary account management
- System supervision

---

## 🎁 Advanced Features

- Online driving theory training
- Custom quizzes
- Interactive appointment workflow
- Online hour purchase (PayPal / card)

---

## 🛠️ Technologies Used

- Django • Python • SQLite
- Django Templates • URL routing
- Fixtures (seed initial data)

---

## 🗂️ Project Architecture

```
drivingschool/
├── students/
├── instructors/
├── secretaries/
├── core/
├── templates/
├── static/
├── db.sqlite3
└── manage.py
```

---

## 🚀 Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/<your-username>/drivingschool.git
cd drivingschool
```

2. **Create a virtual environment:**
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

3. **Apply migrations and load fixtures:**
```bash
python manage.py migrate
python manage.py loaddata fixtures.json
```

4. **Run the server:**
```bash
python manage.py runserver
```

Access the app at:  
👉 **http://localhost:8000**

---

## 🖼️ Preview

<p align="center">
  <img src="./assets/drivingschool_1.png" width="900"/>
</p>

---

## 👤 Developed by

Developed by [zpilia](https://github.com/zpilia), [Emilie20000](https://github.com/Emilie20000) and [Alexis072002](https://github.com/Alexis072002)  
Built during the **Web@cadémie** training to showcase role management, business logic and structured intranet design.

---

## 🤝 Contributors

- [Emilie20000](https://github.com/Emilie20000)
- [Alexis072002](https://github.com/Alexis072002)

---

## 🪪 License

© zpilia — All rights reserved.  
Use, reproduction or distribution requires permission.
