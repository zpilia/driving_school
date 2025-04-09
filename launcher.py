import os
import subprocess
import sys
import shutil

def run_command(command, use_shell=False):
    """Exécute une commande et arrête le script en cas d'erreur.
    Si use_shell est True et que command est une liste, on la convertit en chaîne."""
    if use_shell and isinstance(command, list):
        command = " ".join(command)
    print(f"Exécution de : {command}")
    result = subprocess.run(command, shell=use_shell)
    if result.returncode != 0:
        print(f"La commande {command} a échoué.")
        sys.exit(result.returncode)

def run_command_capture(command, use_shell=False):
    """Exécute une commande et renvoie son code de retour, sans stopper le script."""
    if use_shell and isinstance(command, list):
        command = " ".join(command)
    print(f"Exécution de (capture) : {command}")
    result = subprocess.run(command, shell=use_shell)
    return result.returncode

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

    # Mettre à jour pip
    run_command([python_executable, "-m", "pip", "install", "--upgrade", "pip"])

    # Installer les dépendances si requirements.txt existe
    if os.path.exists("requirements.txt"):
        run_command([python_executable, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("Fichier requirements.txt introuvable, installation des dépendances ignorée.")

    # --- Gestion de TailwindCSS ---
    npm_cmd = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm_cmd:
        print("npm n'est pas installé ou n'est pas dans le PATH. Veuillez installer Node.js.")
        sys.exit(1)
    else:
        if os.path.exists("tailwind.config.js"):
            print("Configuration TailwindCSS trouvée. Mise à jour de TailwindCSS...")
            run_command([npm_cmd, "install", "tailwindcss@latest"])
        else:
            print("Configuration TailwindCSS introuvable. Installation et initialisation de TailwindCSS...")
            run_command([npm_cmd, "install", "-D", "tailwindcss"])
            # Tenter d'utiliser npx
            npx_cmd = shutil.which("npx") or shutil.which("npx.cmd")
            if npx_cmd:
                ret = run_command_capture([npx_cmd, "tailwindcss", "init"], use_shell=True)
                if ret != 0:
                    print("La commande npx tailwindcss init a échoué, tentative d'utilisation de l'exécutable dans node_modules/.bin...")
                    # Chercher tailwindcss.cmd d'abord (Windows), sinon tailwindcss (Linux/Mac)
                    tailwind_exe = os.path.join(os.getcwd(), "node_modules", ".bin", "tailwindcss.cmd")
                    if not os.path.exists(tailwind_exe):
                        tailwind_exe = os.path.join(os.getcwd(), "node_modules", ".bin", "tailwindcss")
                    if os.path.exists(tailwind_exe):
                        run_command([tailwind_exe, "init"], use_shell=True)
                    else:
                        print("Impossible de trouver l'exécutable tailwindcss dans node_modules/.bin.")
                        sys.exit(1)
            else:
                print("npx n'est pas disponible, tentative d'utilisation de 'npm exec'...")
                ret = run_command_capture([npm_cmd, "exec", "tailwindcss", "init"], use_shell=True)
                if ret != 0:
                    print("npm exec tailwindcss init a échoué, tentative d'utilisation de l'exécutable dans node_modules/.bin...")
                    tailwind_exe = os.path.join(os.getcwd(), "node_modules", ".bin", "tailwindcss.cmd")
                    if not os.path.exists(tailwind_exe):
                        tailwind_exe = os.path.join(os.getcwd(), "node_modules", ".bin", "tailwindcss")
                    if os.path.exists(tailwind_exe):
                        run_command([tailwind_exe, "init"], use_shell=True)
                    else:
                        print("Impossible de trouver l'exécutable tailwindcss dans node_modules/.bin.")
                        sys.exit(1)
    # --- Fin gestion TailwindCSS ---

    # Appliquer les migrations
    run_command([python_executable, "manage.py", "migrate"])

    # Lancer le serveur de développement
    run_command([python_executable, "manage.py", "runserver"])

if __name__ == "__main__":
    main()
