import os
from django.http import JsonResponse

class InternalServiceMiddleware:
    """
    Middleware que asegura que las peticiones a la API provengan de un servicio autorizado.
    Valida la cabecera X-Internal-Secret contra la clave INTERNAL_API_KEY.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.internal_key = os.environ.get('INTERNAL_API_KEY')

    def __call__(self, request):
        # SOLO validar para endpoints de la API /api/
        if request.path.startswith('/api/'):
            # Si el usuario ya está autenticado via JWT (RemoteJWTAuthentication), permitir.
            auth = request.headers.get('Authorization', '') or request.META.get('HTTP_AUTHORIZATION', '')
            if getattr(request.user, 'is_authenticated', False) or auth.startswith('Bearer '):
                return self.get_response(request)

            # Si no hay JWT, verificar el secreto compartido
            secret = request.headers.get('X-Internal-Secret')
            if self.internal_key and secret == self.internal_key:
                return self.get_response(request)
            
            # Si no hay secreto ni JWT, denegar acceso a la API
            return JsonResponse({'detail': 'Acceso prohibido: Se requiere autenticación válida o secreto interno.'}, status=403)

        return self.get_response(request)
