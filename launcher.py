import os
import subprocess
import sys

def run_command(command):
    """Exécute une commande et arrête le script en cas d'erreur."""
    print(f"Exécution de : {' '.join(command)}")
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"La commande {' '.join(command)} a échoué.")
        sys.exit(result.returncode)

def main():
    # Vérifier et créer l'environnement virtuel si nécessaire
    if not os.path.exists("env"):
        print("L'environnement virtuel 'env' n'existe pas. Création en cours...")
        run_command([sys.executable, "-m", "venv", "env"])
    else:
        print("L'environnement virtuel 'env' existe déjà.")

    # Déterminer le chemin vers l'exécutable Python dans l'environnement virtuel
    if os.name == "nt":
        python_executable = os.path.join("env", "Scripts", "python.exe")
    else:
        python_executable = os.path.join("env", "bin", "python")

    # Mettre à jour pip (facultatif)
    run_command([python_executable, "-m", "pip", "install", "--upgrade", "pip"])

    # Installer les dépendances si le fichier requirements.txt existe
    if os.path.exists("requirements.txt"):
        run_command([python_executable, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("Fichier requirements.txt introuvable, installation des dépendances ignorée.")

    # Appliquer les migrations
    run_command([python_executable, "manage.py", "migrate"])

    # Lancer le serveur de développement
    run_command([python_executable, "manage.py", "runserver"])

if __name__ == "__main__":
    main()
