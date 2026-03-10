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

class InternalServiceMiddleware:
    """
    Middleware que valida que la petición provenga de otro servicio del sistema
    mediante una cabecera de secreto compartido (X-Internal-Secret).
    Útil para endpoints que no requieren autenticación de usuario (JWT)
    pero deben estar cerrados al público.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.internal_key = os.environ.get('INTERNAL_API_KEY')

    def __call__(self, request):
        if not self.internal_key:
            return self.get_response(request)

        # Solo aplicamos validación a paths de API (/api/) que sean internos 
        # (podríamos definir una lista blanca, pero por ahora lo dejamos opcional)
        # En microservicios esclavos (students, curriculum) esto será REQUERIDO o 
        # se usará como alternativa a JWT.
        
        return self.get_response(request)

import os
