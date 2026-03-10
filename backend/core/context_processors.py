from .models import SystemSettings


def site_settings(request):
    """Inyecta la configuración del sistema en todos los templates."""
    try:
        settings = SystemSettings.load()
        return {
            'system_name': settings.system_name,
            'university_name': settings.university_name,
            'primary_color': settings.primary_color,
            'secondary_color': settings.secondary_color,
            'site_logo': settings.logo if settings.logo else None,
        }
    except Exception:
        return {
            'system_name': 'Sistema Universitario',
            'university_name': 'Mi Universidad',
            'primary_color': '#1a237e',
            'secondary_color': '#283593',
            'site_logo': None,
        }
