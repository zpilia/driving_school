#!/usr/bin/env python
"""Utilitaire en ligne de commande pour les tâches administratives Django."""
import os
import sys


def main():
    """Lancer les tâches d’administration."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_driving_school.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Êtes-vous sûr qu'il est installé et "
            "disponible dans votre variable d'environnement PYTHONPATH ? "
            "Avez-vous oublié d'activer votre environnement virtuel ?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
