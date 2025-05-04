from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def role_required(allowed_roles):
    """
    Vérifie que l'utilisateur connecté possède l'un des rôles autorisés.
    Si ce n'est pas le cas, renvoie une réponse 403 Forbidden.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
