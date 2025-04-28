from django.views.generic import TemplateView
from .models import LessonPackage

class LessonPackageManageView(TemplateView):
    template_name = 'lessonpackages/manage.html'

class LessonPackageProgressView(TemplateView):
    """
    Vue pour afficher tous les forfaits d'heures d'un étudiant,
    triés selon leur progression :
    - forfaits en cours (progression entre 0% et 100%)
    - forfaits non commencés (0%)
    - forfaits terminés (100% ou plus)
    Les forfaits en cours sont affichés en priorité,
    triés par progression croissante.
    """

    template_name = 'lessonpackages/progress.html'

    def get_context_data(self, **kwargs):
        """
        Prépare le contexte du template en fournissant la liste triée des forfaits d'heures :
        - Récupère tous les forfaits liés à l'étudiant connecté
        - Calcule la progression pour chaque forfait
        - Sépare les forfaits en : en cours, non commencés, terminés
        - Trie les forfaits en cours par progression ascendante
        - Retourne les forfaits dans l'ordre : en cours -> non commencés -> terminés
        """
        context = super().get_context_data(**kwargs)
        student = self.request.user

        # Récupération de tous les forfaits de l'étudiant
        lesson_packages = LessonPackage.objects.filter(student=student)

        progress_data = []

        for package in lesson_packages:
            heures_achetees = package.total_hours
            heures_utilisees = package.used_hours
            progression = (heures_utilisees / heures_achetees) * 100 if heures_achetees else 0

            progress_data.append({
                'package': package,
                'heures_achetees': heures_achetees,
                'heures_utilisees': heures_utilisees,
                'progression': progression,
            })

        # Séparation des forfaits selon leur état d'avancement
        started = [p for p in progress_data if 0 < p['progression'] < 100]
        not_started = [p for p in progress_data if p['progression'] == 0]
        completed = [p for p in progress_data if p['progression'] >= 100]

        # Tri des forfaits en cours par progression croissante
        started = sorted(started, key=lambda p: p['progression'])

        # Construction du contexte final
        context['progress_data'] = started + not_started + completed

        return context
