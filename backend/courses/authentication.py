"""
Custom JWT authentication for the courses_service.
Unlike auth_service, this service does not have a local User table.
Instead, it validates the JWT token using the shared SECRET_KEY and
creates a lightweight AnonymousUser-like object with user data from the token.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed


class TokenUser:
    """
    A lightweight user-like object populated from JWT claims.
    Allows permission checks without requiring a local DB user table.
    """
    is_active = True
    is_authenticated = True

    def __init__(self, token):
        self.id = token.get('user_id')
        self.pk = self.id
        self.username = token.get('username', '')
        self.role = token.get('role', '')
        self.is_staff = token.get('is_staff', False)
        self.is_superuser = token.get('is_superuser', False)

    def __str__(self):
        return f'TokenUser(id={self.id}, role={self.role})'

    # Django auth interface stubs
    def has_perm(self, perm, obj=None): return self.is_superuser
    def has_module_perms(self, app_label): return self.is_superuser


class RemoteJWTAuthentication(JWTAuthentication):
    """
    JWT authentication that does NOT look up users in the local database.
    Validates the token signature and returns a TokenUser with claims from the token.
    """

    def get_user(self, validated_token):
        """Override to avoid DB lookup — build user from token claims only."""
        try:
            return TokenUser(validated_token)
        except Exception:
            raise AuthenticationFailed('Token inválido o usuario no identificable.')
