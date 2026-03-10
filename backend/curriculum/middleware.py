import os
from django.http import JsonResponse


class InternalServiceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.internal_key = os.environ.get('INTERNAL_API_KEY')

    def __call__(self, request):
        if request.path.startswith('/api/'):
            auth = request.headers.get('Authorization', '') or request.META.get('HTTP_AUTHORIZATION', '')
            if getattr(request.user, 'is_authenticated', False) or auth.startswith('Bearer '):
                return self.get_response(request)
            secret = request.headers.get('X-Internal-Secret')
            if self.internal_key and secret == self.internal_key:
                return self.get_response(request)
            return JsonResponse(
                {'detail': 'Acceso prohibido: se requiere autenticación JWT o secreto interno.'},
                status=403,
            )
        return self.get_response(request)
