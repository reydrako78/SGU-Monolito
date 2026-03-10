"""
Servicio de comunicación con otros microservicios.
Realiza llamadas HTTP para validar y obtener datos de Students y Courses services.
"""
import requests
from django.conf import settings


def _internal_headers():
    return {
        'Host': 'localhost',
        'X-Internal-Secret': settings.INTERNAL_API_KEY,
    }


def get_student(student_id):
    """Obtiene los datos de un estudiante desde el Students Service."""
    try:
        url = f"{settings.STUDENTS_SERVICE_URL}/api/students/{student_id}/"
        response = requests.get(url, headers=_internal_headers(), timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except (requests.ConnectionError, requests.Timeout):
        return None


def get_section(section_id):
    """Obtiene los datos de una sección desde el Courses Service."""
    try:
        url = f"{settings.COURSES_SERVICE_URL}/api/sections/{section_id}/"
        response = requests.get(url, headers=_internal_headers(), timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except (requests.ConnectionError, requests.Timeout):
        return None


def get_period(period_id):
    """Obtiene los datos de un período desde el Courses Service."""
    try:
        url = f"{settings.COURSES_SERVICE_URL}/api/periods/{period_id}/"
        response = requests.get(url, headers=_internal_headers(), timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except (requests.ConnectionError, requests.Timeout):
        return None


def update_section_enrollment(section_id, action):
    """
    Actualiza el conteo de inscritos en una sección.
    action: 'increment' o 'decrement'
    """
    try:
        url = f"{settings.COURSES_SERVICE_URL}/api/sections/{section_id}/enrollment/"
        response = requests.post(url, json={'action': action}, headers=_internal_headers(), timeout=5)
        return response.status_code == 200, response.json()
    except (requests.ConnectionError, requests.Timeout):
        return False, {'detail': 'Error de comunicación con Courses Service.'}
