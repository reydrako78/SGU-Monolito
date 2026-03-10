"""
Middleware del Sistema Universitario
─────────────────────────────────────
AdminAccessMiddleware:
    Protege la ruta /system-admin/ (panel técnico Django Admin).
    Permite acceso únicamente a:
      - Superusuarios (is_superuser=True)
      - Usuarios con can_access_django_admin=True
    Todos los demás son redirigidos al panel principal con un mensaje de error.
"""

from django.shortcuts import redirect
from django.contrib import messages


class AdminAccessMiddleware:
    """
    Intercepta peticiones al panel técnico (/system-admin/).
    Debe estar en MIDDLEWARE DESPUÉS de AuthenticationMiddleware
    para que request.user esté disponible.
    """

    PROTECTED_PATH = '/system-admin/'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(self.PROTECTED_PATH):
            user = getattr(request, 'user', None)

            # Usuario no autenticado → redirigir al login
            if user is None or not user.is_authenticated:
                return redirect(f'/accounts/login/?next={request.path}')

            # Usuario autenticado sin permiso → redirigir al panel
            has_access = user.is_superuser or getattr(user, 'can_access_django_admin', False)
            if not has_access:
                messages.error(
                    request,
                    'No tienes autorización para acceder al panel técnico del sistema.'
                )
                return redirect('/panel/')
        
        return self.get_response(request)

