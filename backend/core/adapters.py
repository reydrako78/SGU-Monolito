import logging
from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

logger = logging.getLogger(__name__)

# Dominios de correo desechable conocidos
_DISPOSABLE_DOMAINS = frozenset([
    "mailinator.com", "guerrillamail.com", "tempmail.com", "throwaway.email",
    "yopmail.com", "trashmail.com", "fakeinbox.com", "sharklasers.com",
    "guerrillamail.info", "guerrillamail.biz", "guerrillamail.de",
    "spam4.me", "maildrop.cc", "dispostable.com", "spamgourmet.com",
    "dodgit.com", "10minutemail.com", "20minutemail.com", "tempr.email",
    "discard.email", "getnada.com", "mytemp.email", "temp-mail.org",
    "anonbox.net", "moakt.cc", "mailtemp.net", "filzmail.com",
    "throwam.com", "tempemail.net", "spamfree24.org", "crazymailing.com",
])

_IP_SIGNUP_LIMIT  = 5
_IP_SIGNUP_WINDOW = 3600


def _is_disposable_email(email):
    try:
        domain = email.strip().lower().split("@")[1]
        return domain in _DISPOSABLE_DOMAINS
    except IndexError:
        return False


def _check_ip_rate_limit(request):
    ip = (
        request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or
        request.META.get("REMOTE_ADDR", "unknown")
    )
    cache_key = f"oauth_signup_ip:{ip}"
    count = cache.get(cache_key, 0)
    if count >= _IP_SIGNUP_LIMIT:
        logger.warning("Rate limit OAuth signup: IP %s (%d intentos)", ip, count)
        return True
    cache.set(cache_key, count + 1, timeout=_IP_SIGNUP_WINDOW)
    return False


class AspirantSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter para login social de aspirantes.

    Controles de seguridad:
    1. Bloqueo de correos de dominios desechables/temporales.
    2. Limite de 5 registros por IP por hora (via Django cache/Redis).
    3. Solo correos verificados por el proveedor OAuth.
    4. Log completo de cada intento con email, proveedor e IP.
    """

    def is_open_for_signup(self, request, sociallogin):
        email = ""
        if sociallogin.account.extra_data:
            email = sociallogin.account.extra_data.get("email", "") or ""
        if not email and hasattr(sociallogin, "user"):
            email = getattr(sociallogin.user, "email", "") or ""

        if _is_disposable_email(email):
            logger.warning("OAuth bloqueado - correo desechable: %s", email)
            return False

        verified = sociallogin.account.extra_data.get("verified_email", True)
        if verified is False:
            logger.warning("OAuth bloqueado - correo no verificado: %s", email)
            return False

        # Rate limit: check IP before allowing new registrations
        if _check_ip_rate_limit(request):
            logger.warning("OAuth bloqueado - rate limit IP: %s", email)
            return False

        return True

    def save_user(self, request, sociallogin, form=None):
        # Rate limit already checked in is_open_for_signup; log here for audit trail

        email    = (sociallogin.account.extra_data or {}).get("email", "")
        provider = sociallogin.account.provider
        ip       = (
            request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or
            request.META.get("REMOTE_ADDR", "unknown")
        )
        logger.info("Nuevo aspirante OAuth: email=%s proveedor=%s ip=%s", email, provider, ip)

        user = super().save_user(request, sociallogin, form)
        if not user.role or user.role == "student":
            user.role = "aspirant"
            user.save(update_fields=["role"])
        return user

    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_authenticated and user.role == "aspirant":
            try:
                aspirant = user.aspirant_profile
                if aspirant.national_id:
                    return reverse("aspirant_dashboard")
            except Exception:
                pass
            return reverse("aspirant_complete_profile")
        return reverse("home")
