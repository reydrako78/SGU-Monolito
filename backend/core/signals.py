from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added, pre_social_login
from allauth.account.signals import user_signed_up
from .models import Aspirant


@receiver(user_signed_up)
def on_user_signed_up(request, user, **kwargs):
    """
    Al registrarse un usuario nuevo vía OAuth:
    - Asigna rol 'aspirant'.
    - Crea un perfil Aspirant vacío (sin cédula) para que lo complete.
    """
    # Verificar que viene de social auth (no de registro manual)
    sociallogin = kwargs.get('sociallogin')
    if not sociallogin:
        return

    user.role = 'aspirant'
    user.save(update_fields=['role'])

    # Crear perfil aspirante vacío si no existe
    if not Aspirant.objects.filter(user=user).exists():
        extra = sociallogin.account.extra_data or {}
        # Intentar extraer nombre/apellido del perfil OAuth
        given_name = (
            extra.get('given_name') or
            extra.get('givenName') or
            (extra.get('name', '').split(' ')[0] if extra.get('name') else '') or
            user.first_name or ''
        )
        family_name = (
            extra.get('family_name') or
            extra.get('surname') or
            (' '.join(extra.get('name', '').split(' ')[1:]) if extra.get('name') else '') or
            user.last_name or ''
        )

        Aspirant.objects.create(
            user=user,
            first_name=given_name,
            last_name=family_name,
            email=user.email,
        )
