import requests as _requests_lib
import os
from urllib.parse import quote as _url_quote

CURRICULUM_SERVICE_URL  = os.environ.get('CURRICULUM_SERVICE_URL',  'http://curriculum_service:8005')
STUDENTS_SERVICE_URL    = os.environ.get('STUDENTS_SERVICE_URL',    'http://students_service:8001')
ENROLLMENT_SERVICE_URL  = os.environ.get('ENROLLMENT_SERVICE_URL',  'http://enrollment_service:8003')
GRADES_SERVICE_URL      = os.environ.get('GRADES_SERVICE_URL',      'http://grades_service:8004')
COURSES_SERVICE_URL     = os.environ.get('COURSES_SERVICE_URL',     'http://courses_service:8002')


class _SvcSession(_requests_lib.Session):
    """Session para llamadas inter-servicio que fuerza Host: localhost y X-Internal-Secret.
    Django rechaza hostnames con guión bajo (students_service, etc.) por RFC 1034/1035.
    Al enviar Host: localhost se bypassa esa validación sin tocar ALLOWED_HOSTS."""
    def request(self, method, url, **kwargs):
        headers = kwargs.pop('headers', None) or {}
        headers.setdefault('Host', 'localhost')
        internal_key = os.environ.get('INTERNAL_API_KEY', '')
        if internal_key:
            headers.setdefault('X-Internal-Secret', internal_key)
        return super().request(method, url, headers=headers, **kwargs)


http_requests = _SvcSession()
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.throttling import AnonRateThrottle
from .forms import CustomAuthenticationForm
from .models import (
    CustomUser, SystemSettings, Aspirant, Sede, Nucleo,
    SystemRole, RolePermission, SERVICE_CHOICES, ACTION_CHOICES,
    ConvalidacionItem, DocumentAttachment, CertificateRequest,
    Authority
)
from .serializers import (
    UserSerializer, UserCreateSerializer,
    SystemSettingsSerializer,
    AspirantSerializer, AspirantUpdateSerializer, AspirantRegisterSerializer,
    SystemRoleSerializer, RolePermissionSerializer, RolePermissionBulkSerializer,
    CertificateRequestSerializer, SedeSerializer, NucleoSerializer, AuthoritySerializer
)


# ─────────────────────────────────────────────
# Helper: obtener permisos del usuario
# ─────────────────────────────────────────────

def get_user_permissions(user):
    """
    Retorna dict de permisos por servicio/acción:
    { 'students': {'view': True, 'create': False, ...}, ... }
    """
    from .models import SERVICE_CHOICES, ACTION_CHOICES
    services = [s[0] for s in SERVICE_CHOICES]
    actions = [a[0] for a in ACTION_CHOICES]

    if user.is_superuser or user.role == 'admin':
        return {svc: {act: True for act in actions} for svc in services}

    try:
        role = SystemRole.objects.get(name=user.role, is_active=True)
        perms = RolePermission.objects.filter(role=role)
        result = {svc: {act: False for act in actions} for svc in services}
        for p in perms:
            if p.service in result and p.action in result[p.service]:
                result[p.service][p.action] = p.allowed
        return result
    except SystemRole.DoesNotExist:
        return {svc: {act: False for act in actions} for svc in services}


# ─────────────────────────────────────────────
# Helper: obtener carreras desde el students_service
# ─────────────────────────────────────────────

def _get_careers():
    """
    Llama al students_service para obtener las carreras activas.
    Retorna una lista de dicts o lista vacía si el servicio no está disponible.
    """
    try:
        url = f"{settings.STUDENTS_SERVICE_URL}/api/careers/"
        response = http_requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # La API puede retornar lista directa o {'results': [...]}
            if isinstance(data, list):
                return data
            return data.get('results', data)
    except Exception:
        pass
    return []


# ─────────────────────────────────────────────
# Vistas HTML — Autenticación general
# ─────────────────────────────────────────────

def index(request):
    if request.user.is_authenticated:
        if request.user.role == 'aspirant':
            return redirect('aspirant_dashboard')
        if request.user.role == 'student':
            return redirect('student_dashboard')
        if request.user.role == 'professor':
            return redirect('professor_dashboard')
        return redirect('home')
    form = CustomAuthenticationForm()
    return render(request, 'index.html', {'form': form})


@login_required
def home(request):
    if request.user.role == 'aspirant':
        return redirect('aspirant_dashboard')
    if request.user.role == 'student':
        return redirect('student_dashboard')
    if request.user.role == 'professor':
        return redirect('professor_dashboard')

    # Stats filtradas por ámbito del usuario autenticado
    from .models import Sede, SystemRole
    u = request.user
    scope_asp  = u.scope_filter_for('aspirant')
    scope_user = u.scope_filter_for('user')

    # ── Estudiantes desde students_service ──────────────────
    _STUDENTS_URL = os.environ.get('STUDENTS_SERVICE_URL', 'http://students_service:8001')
    recent_students = []
    total_students  = 0
    try:
        resp = http_requests.get(
            f'{_STUDENTS_URL}/api/students/',
            params={'page_size': 6, 'ordering': '-created_at'},
            timeout=2,
        )
        if resp.status_code == 200:
            data = resp.json()
            # Soporte para respuesta paginada o lista plana
            if isinstance(data, dict):
                total_students  = data.get('count', 0)
                recent_students = data.get('results', [])[:6]
            else:
                total_students  = len(data)
                recent_students = data[:6]
            # Enriquecer con datos del auth_service (nombre, email)
            user_ids = [s['user_id'] for s in recent_students if s.get('user_id')]
            user_map = {
                u_obj.id: u_obj
                for u_obj in CustomUser.objects.filter(id__in=user_ids)
            }
            for s in recent_students:
                u_obj = user_map.get(s.get('user_id'))
                s['full_name'] = (
                    u_obj.get_full_name() or u_obj.username if u_obj else '—'
                )
                s['email'] = u_obj.email if u_obj else '—'
                s['initials'] = (
                    (u_obj.first_name[:1] + u_obj.last_name[:1]).upper()
                    if u_obj and (u_obj.first_name or u_obj.last_name)
                    else (u_obj.username[:2].upper() if u_obj else '?')
                )
    except Exception:
        pass  # students_service no disponible; mostramos vacío

    stats = {
        'total_users':     CustomUser.objects.filter(**scope_user).count(),
        'total_aspirants': Aspirant.objects.filter(**scope_asp).count(),
        'total_students':  total_students,
        'active_sedes':    u.get_visible_sedes_qs().filter(is_active=True).count(),
        'total_roles':     SystemRole.objects.count(),
        'is_global':       u.scope_level == 'global',
        'scope_label':     u.scope_display,
    }
    recent_aspirants = (
        Aspirant.objects
        .filter(**scope_asp)
        .select_related('sede')
        .order_by('-registered_at')[:5]
    )

    # Service health checks — Host: localhost evita DisallowedHost en los servicios
    _hdr = {'Host': 'localhost'}
    service_defs = [
        {'name': 'Auth',          'port': 8000, 'url': 'http://localhost:8000/',           'icon': 'bi bi-key'},
        {'name': 'Estudiantes',   'port': 8001, 'url': 'http://students_service:8001/',    'icon': 'bi bi-mortarboard'},
        {'name': 'Cursos',        'port': 8002, 'url': 'http://courses_service:8002/',     'icon': 'bi bi-book'},
        {'name': 'Inscripciones', 'port': 8003, 'url': 'http://enrollment_service:8003/', 'icon': 'bi bi-pencil-square'},
        {'name': 'Calificaciones','port': 8004, 'url': 'http://grades_service:8004/',     'icon': 'bi bi-bar-chart-line'},
    ]
    services = []
    for svc in service_defs:
        try:
            r = http_requests.head(svc['url'], timeout=1.5, headers=_hdr)
            ok = r.status_code < 500
        except Exception:
            ok = False
        services.append({**svc, 'ok': ok})

    return render(request, 'home.html', {
        'stats':            stats,
        'recent_aspirants': recent_aspirants,
        'recent_students':  recent_students,
        'services':         services,
    })


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'aspirant':
                return redirect('aspirant_dashboard')
            if user.role == 'student':
                return redirect('student_dashboard')
            if user.role == 'professor':
                return redirect('professor_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Nombre de usuario o contraseña inválidos.')
    return redirect('index')


def user_logout(request):
    logout(request)
    return redirect('index')


# ─────────────────────────────────────────────
# Vistas HTML — Aspirantes (solo acceso por OAuth)
# ─────────────────────────────────────────────

@login_required
def aspirant_complete_profile(request):
    """
    Paso post-OAuth: el aspirante completa su perfil (cédula, sede, núcleo, carrera).
    Solo accesible para usuarios con rol 'aspirant' sin perfil completo.
    """
    if request.user.role != 'aspirant':
        return redirect('home')

    # Obtener o crear el aspirant_profile (puede ya existir desde la señal OAuth)
    try:
        aspirant = request.user.aspirant_profile
    except Aspirant.DoesNotExist:
        aspirant = Aspirant.objects.create(
            user=request.user,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email,
        )

    # Si ya completó el perfil, ir al dashboard
    if aspirant.national_id:
        return redirect('aspirant_dashboard')

    sedes = Sede.objects.filter(is_active=True).prefetch_related('nucleos')
    careers = _get_careers()
    errors = []

    VALID_ADMISSION_TYPES = [t[0] for t in Aspirant.ADMISSION_TYPE_CHOICES]

    if request.method == 'POST':
        national_id    = request.POST.get('national_id', '').strip()
        sede_id        = request.POST.get('sede', '').strip()
        nucleo_id      = request.POST.get('nucleo', '').strip()
        phone          = request.POST.get('phone', '').strip()
        birth_date     = request.POST.get('birth_date', '').strip()
        first_name     = request.POST.get('first_name', '').strip()
        last_name      = request.POST.get('last_name', '').strip()
        career_id_val  = request.POST.get('career_id', '').strip()
        career_id_2    = request.POST.get('career_id_2', '').strip()
        career_id_3    = request.POST.get('career_id_3', '').strip()
        admission_type = request.POST.get('admission_type', 'ordinario').strip()

        # Campos de convalidación / traslado externo
        prev_institution     = request.POST.get('prev_institution', '').strip()
        prev_career          = request.POST.get('prev_career', '').strip()
        prev_degree          = request.POST.get('prev_degree', '').strip()
        prev_graduation_year = request.POST.get('prev_graduation_year', '').strip()

        # Campos de traslado interno / externo / reingreso
        origin_carnet           = request.POST.get('origin_carnet', '').strip()
        origin_sede_id          = request.POST.get('origin_sede', '').strip()
        last_semester_completed = request.POST.get('last_semester_completed', '').strip()
        reinstatement_reason    = request.POST.get('reinstatement_reason', '').strip()

        # ── Validaciones ──────────────────────────────────────────
        import re as _re
        if not national_id:
            errors.append('La cédula / documento es obligatorio.')
        elif not _re.match(r'^[VEJGPvejgp][-\s]?\d{6,9}$', national_id.replace('.', '').replace(',', '')):
            errors.append(
                'Formato de cédula inválido. Use el formato venezolano: V-12345678, E-12345678, J-123456789, etc.'
            )
        elif Aspirant.objects.filter(national_id=national_id).exclude(pk=aspirant.pk).exists():
            errors.append('Ya existe un aspirante registrado con esa cédula.')

        if not sede_id:
            errors.append('Debe seleccionar una sede de destino.')

        if careers and not career_id_val:
            errors.append('Debe seleccionar al menos la primera opción de especialidad.')

        if admission_type == 'convalidacion':
            if not prev_institution:
                errors.append('Para convalidación debe indicar la institución de procedencia.')
            if not prev_career:
                errors.append('Para convalidación debe indicar la carrera cursada.')

        if admission_type == 'traslado_externo':
            if not prev_institution:
                errors.append('Para traslado externo debe indicar la universidad de procedencia.')
            if not prev_career:
                errors.append('Para traslado externo debe indicar la carrera cursada.')

        if admission_type == 'traslado_interno':
            if not origin_carnet:
                errors.append('Para traslado interno debe indicar su carnet en la sede de origen.')

        if admission_type == 'reingreso':
            if not origin_carnet:
                errors.append('Para reingreso debe indicar su carnet anterior en la UPEL.')
            if not reinstatement_reason:
                errors.append('Para reingreso debe indicar el motivo de retiro.')

        if not errors:
            aspirant.national_id    = national_id
            aspirant.admission_type = admission_type if admission_type in VALID_ADMISSION_TYPES else 'ordinario'
            if first_name:
                aspirant.first_name = first_name
            if last_name:
                aspirant.last_name = last_name
            aspirant.phone = phone
            if birth_date:
                aspirant.birth_date = birth_date

            # Campos convalidación / traslado externo
            aspirant.prev_institution = prev_institution
            aspirant.prev_career      = prev_career
            aspirant.prev_degree      = prev_degree
            if prev_graduation_year:
                try:
                    aspirant.prev_graduation_year = int(prev_graduation_year)
                except ValueError:
                    pass

            # Campos traslado / reingreso
            aspirant.origin_carnet        = origin_carnet
            aspirant.reinstatement_reason = reinstatement_reason
            if last_semester_completed:
                try:
                    aspirant.last_semester_completed = int(last_semester_completed)
                except ValueError:
                    pass

            if origin_sede_id:
                try:
                    aspirant.origin_sede = Sede.objects.get(pk=origin_sede_id)
                except Sede.DoesNotExist:
                    pass

            # Sede / núcleo de destino
            if sede_id:
                try:
                    aspirant.sede = Sede.objects.get(pk=sede_id)
                except Sede.DoesNotExist:
                    pass

            if nucleo_id:
                try:
                    aspirant.nucleo = Nucleo.objects.get(pk=nucleo_id, sede=aspirant.sede)
                except Nucleo.DoesNotExist:
                    pass

            # Guardar 1ª opción de carrera
            if career_id_val:
                try:
                    aspirant.career_id = int(career_id_val)
                    career_obj = next((c for c in careers if str(c.get('id')) == career_id_val), None)
                    aspirant.career_name = career_obj['name'] if career_obj else ''
                except (ValueError, TypeError):
                    pass

            # Guardar 2ª opción
            if career_id_2:
                try:
                    aspirant.career_id_2 = int(career_id_2)
                    career_obj2 = next((c for c in careers if str(c.get('id')) == career_id_2), None)
                    aspirant.career_name_2 = career_obj2['name'] if career_obj2 else ''
                except (ValueError, TypeError):
                    pass
            else:
                aspirant.career_id_2 = None
                aspirant.career_name_2 = ''

            # Guardar 3ª opción
            if career_id_3:
                try:
                    aspirant.career_id_3 = int(career_id_3)
                    career_obj3 = next((c for c in careers if str(c.get('id')) == career_id_3), None)
                    aspirant.career_name_3 = career_obj3['name'] if career_obj3 else ''
                except (ValueError, TypeError):
                    pass
            else:
                aspirant.career_id_3 = None
                aspirant.career_name_3 = ''

            aspirant.save()
            request.user.first_name = aspirant.first_name
            request.user.last_name  = aspirant.last_name
            request.user.save()

            tipo_label = dict(Aspirant.ADMISSION_TYPE_CHOICES).get(aspirant.admission_type, aspirant.admission_type)
            messages.success(
                request,
                f'¡Perfil completado! Tu código de aspirante es: {aspirant.code}. '
                f'Tipo de admisión: {tipo_label}.'
            )
            return redirect('aspirant_dashboard')

    return render(request, 'aspirant_complete_profile.html', {
        'aspirant':              aspirant,
        'sedes':                 sedes,
        'careers':               careers,
        'errors':                errors,
        'admission_type_choices': Aspirant.ADMISSION_TYPE_CHOICES,
    })


@login_required
def aspirant_dashboard(request):
    """Dashboard del aspirante — ver y editar perfil (cédula inmutable)."""
    if request.user.role != 'aspirant':
        return redirect('home')

    try:
        aspirant = request.user.aspirant_profile
    except Aspirant.DoesNotExist:
        return redirect('aspirant_complete_profile')

    # Si no ha completado el perfil, forzar completado
    if not aspirant.national_id:
        return redirect('aspirant_complete_profile')

    sedes = Sede.objects.filter(is_active=True).prefetch_related('nucleos')
    careers = _get_careers()
    update_errors = []

    if request.method == 'POST':
        for field in ['first_name', 'last_name', 'phone', 'address']:
            value = request.POST.get(field, '').strip()
            if value:
                setattr(aspirant, field, value)

        birth_date = request.POST.get('birth_date', '').strip()
        if birth_date:
            aspirant.birth_date = birth_date

        sede_id = request.POST.get('sede', '').strip()
        nucleo_id = request.POST.get('nucleo', '').strip()
        if sede_id:
            try:
                aspirant.sede = Sede.objects.get(pk=sede_id)
                aspirant.nucleo = None  # Resetear núcleo al cambiar sede
            except Sede.DoesNotExist:
                pass
        if nucleo_id:
            try:
                aspirant.nucleo = Nucleo.objects.get(pk=nucleo_id)
            except Nucleo.DoesNotExist:
                pass

        # Actualizar 1ª opción de carrera
        career_id_val = request.POST.get('career_id', '').strip()
        career_id_2   = request.POST.get('career_id_2', '').strip()
        career_id_3   = request.POST.get('career_id_3', '').strip()

        # No permitir cambiar opciones si ya está admitido
        if aspirant.admission_status != 'approved':
            if career_id_val:
                try:
                    aspirant.career_id = int(career_id_val)
                    career_obj = next((c for c in careers if str(c.get('id')) == career_id_val), None)
                    aspirant.career_name = career_obj['name'] if career_obj else aspirant.career_name
                except (ValueError, TypeError):
                    pass
            else:
                aspirant.career_id = None
                aspirant.career_name = ''

            if career_id_2:
                try:
                    aspirant.career_id_2 = int(career_id_2)
                    career_obj2 = next((c for c in careers if str(c.get('id')) == career_id_2), None)
                    aspirant.career_name_2 = career_obj2['name'] if career_obj2 else ''
                except (ValueError, TypeError):
                    pass
            else:
                aspirant.career_id_2 = None
                aspirant.career_name_2 = ''

            if career_id_3:
                try:
                    aspirant.career_id_3 = int(career_id_3)
                    career_obj3 = next((c for c in careers if str(c.get('id')) == career_id_3), None)
                    aspirant.career_name_3 = career_obj3['name'] if career_obj3 else ''
                except (ValueError, TypeError):
                    pass
            else:
                aspirant.career_id_3 = None
                aspirant.career_name_3 = ''

        aspirant.save()
        request.user.first_name = aspirant.first_name
        request.user.last_name = aspirant.last_name
        request.user.save()

        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('aspirant_dashboard')

    uploaded_docs  = list(aspirant.documents.all())
    uploaded_types = {d.doc_type for d in uploaded_docs}

    return render(request, 'aspirant_dashboard.html', {
        'aspirant':         aspirant,
        'sedes':            sedes,
        'careers':          careers,
        'update_errors':    update_errors,
        'doc_type_choices': DocumentAttachment.DOC_TYPE_CHOICES,
        'uploaded_docs':    uploaded_docs,
        'uploaded_types':   uploaded_types,
    })


# ─────────────────────────────────────────────
# Vistas HTML — Panel de Administración
# ─────────────────────────────────────────────

_ADMIN_ROLES = {'admin', 'control_estudios', 'docencia', 'secretaria'}

def _admin_required(request):
    """Retorna True si el usuario puede acceder al panel."""
    return (request.user.is_authenticated and
            (request.user.is_superuser or request.user.role in _ADMIN_ROLES))


@login_required
def panel_users(request):
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    u             = request.user
    role_filter   = request.GET.get('role', '').strip()
    active_filter = request.GET.get('is_active', '').strip()
    search_q      = request.GET.get('q', '').strip()

    # Base queryset filtrado por ámbito organizacional
    scope_kwargs = u.scope_filter_for('user')
    qs = (
        CustomUser.objects
        .filter(**scope_kwargs)
        .select_related('scope_sede', 'scope_nucleo')
        .order_by('-date_joined')
    )

    if role_filter:
        qs = qs.filter(role=role_filter)
    if active_filter == '1':
        qs = qs.filter(is_active=True)
    elif active_filter == '0':
        qs = qs.filter(is_active=False)
    if search_q:
        from django.db.models import Q
        qs = qs.filter(
            Q(first_name__icontains=search_q) |
            Q(last_name__icontains=search_q) |
            Q(username__icontains=search_q) |
            Q(email__icontains=search_q)
        )

    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_users.html', {
        'users':          page_obj,
        'page_obj':       page_obj,
        'role_filter':    role_filter,
        'active_filter':  active_filter,
        'search_q':       search_q,
        'role_choices':   CustomUser.ROLE_CHOICES,
        'scope_choices':  CustomUser.SCOPE_CHOICES,
    })


@login_required
def panel_aspirants(request):
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    u             = request.user
    status_filter = request.GET.get('status', '').strip()
    sede_filter   = request.GET.get('sede', '').strip()
    search_q      = request.GET.get('q', '').strip()

    # Base queryset filtrado por ámbito del usuario
    scope_kwargs = u.scope_filter_for('aspirant')
    qs = (
        Aspirant.objects
        .filter(**scope_kwargs)
        .select_related('sede', 'nucleo')
        .order_by('-registered_at')
    )

    if status_filter:
        qs = qs.filter(status=status_filter)
    # Solo permitir filtrar por sedes/núcleos visibles al usuario
    if sede_filter:
        visible_sede_ids = u.get_visible_sedes_qs().values_list('pk', flat=True)
        if int(sede_filter) in list(visible_sede_ids):
            qs = qs.filter(sede_id=sede_filter)
    if search_q:
        from django.db.models import Q
        qs = qs.filter(
            Q(first_name__icontains=search_q) |
            Q(last_name__icontains=search_q) |
            Q(email__icontains=search_q) |
            Q(national_id__icontains=search_q)
        )

    # Solo mostrar sedes visibles en el dropdown
    sedes = u.get_visible_sedes_qs().filter(is_active=True)

    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_aspirants.html', {
        'aspirants':       page_obj,
        'page_obj':        page_obj,
        'status_filter':   status_filter,
        'sede_filter':     sede_filter,
        'search_q':        search_q,
        'sedes':           sedes,
        'status_choices':  Aspirant.STATUS_CHOICES,
        'scope_fixed':     u.scope_level == 'nucleo',   # deshabilitar filtro sede en nivel núcleo
    })


# ─────────────────────────────────────────────────────────────
# Panel Estudiantes — lista con filtros y paginación
# ─────────────────────────────────────────────────────────────
@login_required
def panel_students(request):
    """Lista de estudiantes obtenida del students_service con filtros y paginación."""
    if not _admin_required(request):
        return redirect('home')

    _STUDENTS_URL = os.environ.get('STUDENTS_SERVICE_URL', 'http://students_service:8001')

    # ── Parámetros de filtro / paginación ──
    q         = request.GET.get('q', '').strip()
    status_f  = request.GET.get('status', '').strip()
    career_f  = request.GET.get('career', '').strip()
    page      = max(int(request.GET.get('page', 1)), 1)
    page_size = 15

    # ── Obtener carreras para el select de filtro ──
    careers = []
    try:
        r_c = http_requests.get(f'{_STUDENTS_URL}/api/careers/', timeout=2)
        if r_c.status_code == 200:
            careers = r_c.json() if isinstance(r_c.json(), list) else r_c.json().get('results', [])
    except Exception:
        pass

    # ── Obtener estudiantes con parámetros ──
    students    = []
    total_count = 0
    service_ok  = False
    try:
        params = {
            'page':      page,
            'page_size': page_size,
            'ordering':  '-created_at',
        }
        if status_f:
            params['status'] = status_f
        if career_f:
            params['career'] = career_f

        r_s = http_requests.get(f'{_STUDENTS_URL}/api/students/', params=params, timeout=3)
        service_ok = True
        if r_s.status_code == 200:
            data = r_s.json()
            if isinstance(data, dict):
                total_count = data.get('count', 0)
                students    = data.get('results', [])
            else:
                total_count = len(data)
                students    = data

            # Enriquecer con nombre/email del auth_service
            user_ids = [s['user_id'] for s in students if s.get('user_id')]
            user_map = {
                u_obj.id: u_obj
                for u_obj in CustomUser.objects.filter(id__in=user_ids)
            }
            for s in students:
                u_obj = user_map.get(s.get('user_id'))
                s['full_name'] = (
                    u_obj.get_full_name() or u_obj.username if u_obj else '—'
                )
                s['email']    = u_obj.email if u_obj else '—'
                s['initials'] = (
                    (u_obj.first_name[:1] + u_obj.last_name[:1]).upper()
                    if u_obj and (u_obj.first_name or u_obj.last_name)
                    else (u_obj.username[:2].upper() if u_obj else '?')
                )

            # Filtro local por búsqueda de texto (nombre/carnet/email)
            if q:
                q_lower = q.lower()
                students = [
                    s for s in students
                    if q_lower in s.get('full_name', '').lower()
                    or q_lower in s.get('carnet', '').lower()
                    or q_lower in s.get('email', '').lower()
                    or q_lower in s.get('career_name', '').lower()
                ]
                total_count = len(students)

    except Exception:
        service_ok = False

    # ── Paginación simple ──
    total_pages  = max((total_count + page_size - 1) // page_size, 1)
    page_range   = range(max(1, page - 2), min(total_pages + 1, page + 3))

    STATUS_CHOICES = [
        ('active',    'Activo'),
        ('inactive',  'Inactivo'),
        ('graduated', 'Egresado'),
        ('suspended', 'Suspendido'),
    ]

    return render(request, 'admin_students.html', {
        'students':       students,
        'total_count':    total_count,
        'page':           page,
        'total_pages':    total_pages,
        'page_range':     page_range,
        'q':              q,
        'status_f':       status_f,
        'career_f':       career_f,
        'careers':        careers,
        'status_choices': STATUS_CHOICES,
        'service_ok':     service_ok,
    })


@login_required
def panel_user_create(request):
    """Crear un nuevo usuario desde el panel custom."""
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    sedes  = Sede.objects.filter(is_active=True).prefetch_related('nucleos')
    errors = []

    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        password1  = request.POST.get('password1', '').strip()
        password2  = request.POST.get('password2', '').strip()
        role       = request.POST.get('role', 'student').strip()
        scope_level = request.POST.get('scope_level', 'global').strip()

        if not username:
            errors.append('El nombre de usuario es obligatorio.')
        elif CustomUser.objects.filter(username=username).exists():
            errors.append('Ya existe un usuario con ese nombre de usuario.')
        if not email:
            errors.append('El correo electrónico es obligatorio.')
        elif CustomUser.objects.filter(email=email).exists():
            errors.append('Ya existe un usuario con ese correo electrónico.')
        if not first_name:
            errors.append('El nombre es obligatorio.')
        if not last_name:
            errors.append('El apellido es obligatorio.')
        if not password1:
            errors.append('La contraseña es obligatoria.')
        elif password1 != password2:
            errors.append('Las contraseñas no coinciden.')
        elif len(password1) < 8:
            errors.append('La contraseña debe tener al menos 8 caracteres.')

        if not errors:
            new_user = CustomUser(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role if role in [r[0] for r in CustomUser.ROLE_CHOICES] else 'student',
                scope_level=scope_level if scope_level in ('global', 'sede', 'nucleo') else 'global',
            )
            sede_id   = request.POST.get('scope_sede', '').strip()
            nucleo_id = request.POST.get('scope_nucleo', '').strip()
            if sede_id:
                try:
                    new_user.scope_sede = Sede.objects.get(pk=sede_id)
                except Sede.DoesNotExist:
                    pass
            if nucleo_id:
                try:
                    new_user.scope_nucleo = Nucleo.objects.get(pk=nucleo_id)
                except Nucleo.DoesNotExist:
                    pass
            new_user.set_password(password1)
            new_user.save()
            messages.success(request, f'Usuario {new_user.get_full_name()} creado correctamente.')
            return redirect('panel_users')

    return render(request, 'panel_user_create.html', {
        'sedes':         sedes,
        'role_choices':  CustomUser.ROLE_CHOICES,
        'scope_choices': CustomUser.SCOPE_CHOICES,
        'errors':        errors,
        'form_data':     request.POST,
    })


@login_required
def panel_user_edit(request, user_id):
    """Editar un usuario desde el panel custom (sin Django Admin)."""
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    target = get_object_or_404(CustomUser, pk=user_id)
    sedes  = Sede.objects.filter(is_active=True).prefetch_related('nucleos')
    errors = []

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        role       = request.POST.get('role', '').strip()
        is_active  = request.POST.get('is_active') == '1'
        scope_level = request.POST.get('scope_level', 'global').strip()

        if not first_name:
            errors.append('El nombre es obligatorio.')
        if not last_name:
            errors.append('El apellido es obligatorio.')

        if not errors:
            target.first_name = first_name
            target.last_name  = last_name
            target.is_active  = is_active

            if role in [r[0] for r in CustomUser.ROLE_CHOICES]:
                old_role = target.role
                target.role = role
                # Si cambia A aspirant y no tiene perfil, la señal post_save no aplica
                # porque no es usuario nuevo. Crear el Aspirant manualmente.
                if role == 'aspirant' and old_role != 'aspirant':
                    from .models import Aspirant as AspirantModel
                    try:
                        AspirantModel.objects.get_or_create(
                            user=target,
                            defaults={
                                'email':      target.email,
                                'first_name': target.first_name,
                                'last_name':  target.last_name,
                            },
                        )
                    except Exception:
                        pass

            if scope_level in ('global', 'sede', 'nucleo'):
                target.scope_level = scope_level

            sede_id   = request.POST.get('scope_sede', '').strip()
            nucleo_id = request.POST.get('scope_nucleo', '').strip()

            if sede_id:
                try:
                    target.scope_sede = Sede.objects.get(pk=sede_id)
                except Sede.DoesNotExist:
                    target.scope_sede = None
            else:
                target.scope_sede = None

            if nucleo_id:
                try:
                    target.scope_nucleo = Nucleo.objects.get(pk=nucleo_id)
                except Nucleo.DoesNotExist:
                    target.scope_nucleo = None
            else:
                target.scope_nucleo = None

            target.save()
            messages.success(request, f'Usuario {target.get_full_name()} actualizado correctamente.')
            return redirect('panel_users')

    return render(request, 'panel_user_edit.html', {
        'target':        target,
        'sedes':         sedes,
        'role_choices':  CustomUser.ROLE_CHOICES,
        'scope_choices': CustomUser.SCOPE_CHOICES,
        'errors':        errors,
    })


@login_required
def panel_aspirant_edit(request, aspirant_id):
    """Editar un aspirante desde el panel custom (sin Django Admin)."""
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    aspirant = get_object_or_404(Aspirant, pk=aspirant_id)
    sedes    = Sede.objects.filter(is_active=True).prefetch_related('nucleos')
    errors   = []

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        phone      = request.POST.get('phone', '').strip()
        address    = request.POST.get('address', '').strip()
        birth_date = request.POST.get('birth_date', '').strip()
        status     = request.POST.get('status', '').strip()
        sede_id    = request.POST.get('sede', '').strip()
        nucleo_id  = request.POST.get('nucleo', '').strip()

        if not first_name:
            errors.append('El nombre es obligatorio.')
        if not last_name:
            errors.append('El apellido es obligatorio.')

        if not errors:
            aspirant.first_name = first_name
            aspirant.last_name  = last_name
            aspirant.phone      = phone
            aspirant.address    = address

            if birth_date:
                aspirant.birth_date = birth_date

            if status in ('active', 'inactive'):
                aspirant.status = status

            if sede_id:
                try:
                    aspirant.sede   = Sede.objects.get(pk=sede_id)
                    aspirant.nucleo = None
                except Sede.DoesNotExist:
                    pass
            else:
                aspirant.sede   = None
                aspirant.nucleo = None

            if nucleo_id:
                try:
                    aspirant.nucleo = Nucleo.objects.get(pk=nucleo_id)
                except Nucleo.DoesNotExist:
                    pass

            aspirant.save()
            # Sincronizar nombre con el usuario vinculado
            if aspirant.user_id:
                try:
                    u_linked = CustomUser.objects.get(pk=aspirant.user_id)
                    u_linked.first_name = aspirant.first_name
                    u_linked.last_name  = aspirant.last_name
                    u_linked.save(update_fields=['first_name', 'last_name'])
                except CustomUser.DoesNotExist:
                    pass

            messages.success(request, f'Aspirante {aspirant.get_full_name()} actualizado correctamente.')
            return redirect('panel_aspirants')

    return render(request, 'panel_aspirant_edit.html', {
        'aspirant':       aspirant,
        'sedes':          sedes,
        'status_choices': Aspirant.STATUS_CHOICES,
        'errors':         errors,
    })


@login_required
def panel_settings(request):
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    settings_obj = SystemSettings.load()
    save_ok = False
    save_errors = []

    if request.method == 'POST' and (request.user.is_staff or request.user.role == 'admin'):
        system_name      = request.POST.get('system_name', '').strip()
        university_name  = request.POST.get('university_name', '').strip()
        primary_color    = request.POST.get('primary_color', '').strip()
        secondary_color  = request.POST.get('secondary_color', '').strip()

        if not system_name:
            save_errors.append('El nombre del sistema es obligatorio.')
        if not university_name:
            save_errors.append('El nombre de la universidad es obligatorio.')

        import re
        hex_re = re.compile(r'^#[0-9A-Fa-f]{6}$')
        if primary_color and not hex_re.match(primary_color):
            save_errors.append('El color primario debe ser un valor hexadecimal válido (#RRGGBB).')
        if secondary_color and not hex_re.match(secondary_color):
            save_errors.append('El color secundario debe ser un valor hexadecimal válido (#RRGGBB).')

        if not save_errors:
            if system_name:
                settings_obj.system_name = system_name
            if university_name:
                settings_obj.university_name = university_name
            if primary_color:
                settings_obj.primary_color = primary_color
            if secondary_color:
                settings_obj.secondary_color = secondary_color
            if 'logo' in request.FILES:
                settings_obj.logo = request.FILES['logo']
            settings_obj.save()
            save_ok = True

    return render(request, 'admin_settings.html', {
        'settings_obj':  settings_obj,
        'save_ok':       save_ok,
        'save_errors':   save_errors,
    })


@login_required
def panel_sedes(request):
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    u = request.user
    sedes = (
        u.get_visible_sedes_qs()
        .prefetch_related('nucleos')
        .order_by('name')
    )
    # Para scope=nucleo, pasar el núcleo específico para destacarlo en la vista
    highlight_nucleo_id = u.scope_nucleo_id if u.scope_level == 'nucleo' else None

    return render(request, 'admin_sedes.html', {
        'sedes':              sedes,
        'highlight_nucleo_id': highlight_nucleo_id,
        'scope_level':        u.scope_level,
    })


@login_required
def panel_roles(request):
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    roles = SystemRole.objects.prefetch_related('permissions').all()

    return render(request, 'admin_roles.html', {
        'roles':           roles,
        'service_choices': SERVICE_CHOICES,
        'action_choices':  ACTION_CHOICES,
    })


# ─────────────────────────────────────────────
# Panel — Admisión de Aspirantes
# ─────────────────────────────────────────────

@login_required
def panel_admision(request):
    """
    Lista de aspirantes para el proceso de admisión.
    Accesible para admin, control_estudios y secretaria.
    """
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    ALLOWED_ROLES = ('admin', 'control_estudios', 'secretaria')
    if not (request.user.is_superuser or request.user.role in ALLOWED_ROLES):
        messages.error(request, 'No tienes permiso para acceder al módulo de admisión.')
        return redirect('home')

    u = request.user
    admission_filter = request.GET.get('admission_status', '').strip()
    type_filter      = request.GET.get('admission_type', '').strip()
    sede_filter      = request.GET.get('sede', '').strip()
    search_q         = request.GET.get('q', '').strip()

    # Tipos que van en este panel (todos excepto convalidación, que tiene su propio panel)
    NON_CONV_TYPES = ['ordinario', 'traslado_interno', 'traslado_externo', 'reingreso']

    scope_kwargs = u.scope_filter_for('aspirant')
    qs = (
        Aspirant.objects
        .filter(**scope_kwargs, admission_type__in=NON_CONV_TYPES)
        .select_related('sede', 'nucleo', 'reviewed_by')
        .order_by('-registered_at')
    )

    # Excluir aspirantes sin perfil completo (sin cédula)
    qs = qs.filter(national_id__isnull=False).exclude(national_id='')

    if admission_filter:
        qs = qs.filter(admission_status=admission_filter)
    if type_filter and type_filter in NON_CONV_TYPES:
        qs = qs.filter(admission_type=type_filter)
    if sede_filter:
        visible_sede_ids = u.get_visible_sedes_qs().values_list('pk', flat=True)
        try:
            if int(sede_filter) in list(visible_sede_ids):
                qs = qs.filter(sede_id=sede_filter)
        except (ValueError, TypeError):
            pass
    if search_q:
        from django.db.models import Q
        qs = qs.filter(
            Q(first_name__icontains=search_q) |
            Q(last_name__icontains=search_q) |
            Q(email__icontains=search_q) |
            Q(national_id__icontains=search_q) |
            Q(code__icontains=search_q)
        )

    # Base para contadores (todos los tipos no-convalidación)
    base_qs = (
        Aspirant.objects.filter(**scope_kwargs, admission_type__in=NON_CONV_TYPES)
        .filter(national_id__isnull=False).exclude(national_id='')
    )
    # Aplicar filtro de tipo también a los contadores de estado
    if type_filter and type_filter in NON_CONV_TYPES:
        base_qs = base_qs.filter(admission_type=type_filter)

    counts = {
        'all':        base_qs.count(),
        'pending':    base_qs.filter(admission_status='pending').count(),
        'in_review':  base_qs.filter(admission_status='in_review').count(),
        'approved':   base_qs.filter(admission_status='approved').count(),
        'rejected':   base_qs.filter(admission_status='rejected').count(),
        'waitlisted': base_qs.filter(admission_status='waitlisted').count(),
    }

    # Contadores por tipo de admisión (para filtro de tipo) — una sola query
    from django.db.models import Count as _Count
    _tc_raw = dict(
        Aspirant.objects.filter(
            **scope_kwargs, admission_type__in=NON_CONV_TYPES,
            national_id__isnull=False
        ).exclude(national_id='')
        .values('admission_type')
        .annotate(n=_Count('id'))
        .values_list('admission_type', 'n')
    )
    type_counts = {t: _tc_raw.get(t, 0) for t in NON_CONV_TYPES}

    sedes = u.get_visible_sedes_qs().filter(is_active=True)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'admin_admision.html', {
        'aspirants':          page_obj,
        'page_obj':           page_obj,
        'admission_filter':   admission_filter,
        'type_filter':        type_filter,
        'sede_filter':        sede_filter,
        'search_q':           search_q,
        'sedes':              sedes,
        'counts':             counts,
        'type_counts':        type_counts,
        'admission_choices':  Aspirant.ADMISSION_STATUS_CHOICES,
        'admission_type_choices': [(t, l) for t, l in Aspirant.ADMISSION_TYPE_CHOICES if t != 'convalidacion'],
    })


@login_required
def panel_admision_detail(request, code):
    """
    Detalle y procesamiento de un aspirante en el proceso de admisión.
    Permite cambiar estado, asignar carrera admitida y dejar observaciones.
    """
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    ALLOWED_ROLES = ('admin', 'control_estudios', 'secretaria')
    if not (request.user.is_superuser or request.user.role in ALLOWED_ROLES):
        messages.error(request, 'No tienes permiso para procesar admisiones.')
        return redirect('home')

    aspirant = get_object_or_404(Aspirant, code=code)
    careers  = _get_careers()

    # Construir diccionario de carreras para lookup rápido
    careers_map = {str(c['id']): c['name'] for c in careers}

    # Enriquecer opciones con nombres resueltos
    options = []
    for i, (cid, cname) in enumerate([
        (aspirant.career_id,   aspirant.career_name),
        (aspirant.career_id_2, aspirant.career_name_2),
        (aspirant.career_id_3, aspirant.career_name_3),
    ], start=1):
        if cid:
            options.append({
                'num':  i,
                'id':   cid,
                'name': cname or careers_map.get(str(cid), f'Carrera #{cid}'),
            })

    if request.method == 'POST':
        action           = request.POST.get('action', '').strip()
        new_status       = request.POST.get('admission_status', '').strip()
        notes            = request.POST.get('admission_notes', '').strip()
        admitted_opt_str = request.POST.get('admitted_option', '').strip()

        valid_statuses = [s[0] for s in Aspirant.ADMISSION_STATUS_CHOICES]
        if new_status not in valid_statuses:
            messages.error(request, 'Estado de admisión inválido.')
            return redirect('panel_admision_detail', code=code)

        from django.utils import timezone
        from django.db import transaction
        try:
            with transaction.atomic():
                aspirant.admission_status = new_status
                aspirant.admission_notes  = notes
                aspirant.reviewed_by      = request.user
                aspirant.reviewed_at      = timezone.now()

                # Si se aprueba, registrar la opción y carrera admitida
                # ── Notificación por email (no bloqueante) ────────────────────
                from .email_utils import notify_admission_status_change
                notify_admission_status_change(aspirant, new_status)

                if new_status == 'approved':
                    try:
                        opt_num = int(admitted_opt_str)
                        if opt_num not in (1, 2, 3):
                            raise ValueError
                    except (ValueError, TypeError):
                        messages.error(request, 'Debe seleccionar la opción admitida (1ª, 2ª o 3ª).')
                        return redirect('panel_admision_detail', code=code)

                    aspirant.admitted_option = opt_num
                    if opt_num == 1:
                        aspirant.admitted_career_id   = aspirant.career_id
                        aspirant.admitted_career_name = aspirant.career_name
                    elif opt_num == 2:
                        aspirant.admitted_career_id   = aspirant.career_id_2
                        aspirant.admitted_career_name = aspirant.career_name_2
                    elif opt_num == 3:
                        aspirant.admitted_career_id   = aspirant.career_id_3
                        aspirant.admitted_career_name = aspirant.career_name_3

                    # Crear estudiante en students_service
                    if aspirant.admitted_career_id and aspirant.user_id:
                        import datetime
                        payload = {
                            'user_id':        aspirant.user_id,
                            'career':         aspirant.admitted_career_id,
                            'semester':       1,
                            'status':         'active',
                            'enrollment_date': datetime.date.today().isoformat(),
                            'national_id':    aspirant.national_id or '',
                            'phone':          aspirant.phone or '',
                            'address':        aspirant.address or '',
                        }
                        if aspirant.birth_date:
                            payload['birth_date'] = aspirant.birth_date.isoformat()

                        st_code, st_resp = _post_json(
                            f'{STUDENTS_SERVICE_URL}/api/students/', payload
                        )

                        if st_code in (200, 201):
                            # Cambiar rol del usuario a 'student'
                            try:
                                u_obj = CustomUser.objects.get(pk=aspirant.user_id)
                                u_obj.role = 'student'
                                u_obj.save()
                            except CustomUser.DoesNotExist:
                                pass
                            
                            aspirant.save()
                            messages.success(
                                request,
                                f'✅ {aspirant.get_full_name()} ha sido admitido/a en '
                                f'"{aspirant.admitted_career_name}". '
                                f'Se creó el registro de estudiante correctamente.'
                            )
                            return redirect('panel_admision')
                        else:
                            # Si falla el microservicio externo, forzamos un rollback del estado local
                            # para mantener la consistencia (aspirante sigue como pending o previo)
                            err_detail = st_resp.get('detail') or st_resp.get('user_id', [''])[0] if isinstance(st_resp, dict) else str(st_resp)
                            
                            if 'already' in str(err_detail).lower():
                                # El estudiante ya existía — considerar admisión válida
                                aspirant.save()
                                messages.warning(
                                    request,
                                    f'Estado actualizado, pero hubo un aviso del servicio de alumnos: {err_detail}'
                                )
                                return redirect('panel_admision')
                            else:
                                raise Exception(f"Microservicio de Alumnos respondió con error {st_code}: {err_detail}")
                    else:
                        aspirant.save()
                        messages.warning(request, 'Aspirante admitido localmente, pero faltan datos para crear el registro de estudiante.')
                        return redirect('panel_admision')
                else:
                    # No es aprobación — solo guardar estado
                    aspirant.admitted_option      = None
                    aspirant.admitted_career_id   = None
                    aspirant.admitted_career_name = ''
                    aspirant.save()
                    label = dict(Aspirant.ADMISSION_STATUS_CHOICES).get(new_status, new_status)
                    messages.success(request, f'Estado de {aspirant.get_full_name()} actualizado a "{label}".')
                    return redirect('panel_admision')
        except Exception as e:
            messages.error(request, f'Error al procesar la admisión: {str(e)}')
            return redirect('panel_admision_detail', code=code)

    # ── Checklist de documentos requeridos por tipo de admisión ──────
    REQUIRED_DOCS_BY_TYPE = {
        'ordinario': [
            ('cedula',           'Cédula de Identidad'),
            ('foto',             'Fotografía tipo carnet'),
            ('partida',          'Partida de Nacimiento'),
            ('notas_cert',       'Notas Certificadas de Bachillerato'),
            ('comprobante_pago', 'Comprobante de Pago de Arancel'),
        ],
        'convalidacion': [
            ('cedula',           'Cédula de Identidad'),
            ('foto',             'Fotografía tipo carnet'),
            ('titulo_prev',      'Título o constancia de egresado (origen)'),
            ('record_prev',      'Récord Académico certificado (origen)'),
            ('carta_motivos',    'Carta de Exposición de Motivos'),
            ('comprobante_pago', 'Comprobante de Pago de Arancel'),
        ],
        'traslado_interno': [
            ('cedula',           'Cédula de Identidad'),
            ('foto',             'Fotografía tipo carnet'),
            ('notas_cert',       'Récord Académico UPEL (sede de origen)'),
            ('comprobante_pago', 'Comprobante de Pago de Arancel'),
        ],
        'traslado_externo': [
            ('cedula',           'Cédula de Identidad'),
            ('foto',             'Fotografía tipo carnet'),
            ('record_prev',      'Récord Académico (universidad de origen)'),
            ('titulo_prev',      'Constancia de estudios o título (origen)'),
            ('carta_motivos',    'Carta de Exposición de Motivos'),
            ('comprobante_pago', 'Comprobante de Pago de Arancel'),
        ],
        'reingreso': [
            ('cedula',           'Cédula de Identidad'),
            ('foto',             'Fotografía tipo carnet'),
            ('notas_cert',       'Récord Académico UPEL (período cursado)'),
            ('comprobante_pago', 'Comprobante de Pago de Arancel'),
        ],
    }

    uploaded_docs = list(aspirant.documents.all())
    uploaded_types = {d.doc_type for d in uploaded_docs}
    required_list  = REQUIRED_DOCS_BY_TYPE.get(aspirant.admission_type, [])

    doc_checklist = []
    for dt, lbl in required_list:
        doc_obj = next((d for d in uploaded_docs if d.doc_type == dt), None)
        doc_checklist.append({
            'doc_type': dt,
            'label':    lbl,
            'uploaded': doc_obj is not None,
            'doc':      doc_obj,
        })

    # Documentos adicionales no incluidos en la lista requerida
    required_types = {dt for dt, _ in required_list}
    extra_docs = [d for d in uploaded_docs if d.doc_type not in required_types]

    docs_ok    = sum(1 for item in doc_checklist if item['uploaded'])
    docs_total = len(doc_checklist)

    return render(request, 'admin_admision_detail.html', {
        'aspirant':          aspirant,
        'options':           options,
        'careers':           careers,
        'admission_choices': Aspirant.ADMISSION_STATUS_CHOICES,
        'doc_checklist':     doc_checklist,
        'extra_docs':        extra_docs,
        'docs_ok':           docs_ok,
        'docs_total':        docs_total,
    })


# ─────────────────────────────────────────────
# Helpers — llamadas inter-servicio
# ─────────────────────────────────────────────

def _get_json(url, timeout=4):
    """GET a un servicio interno. Retorna lista/dict o [] en caso de error."""
    try:
        r = http_requests.get(url, timeout=timeout, headers={'Host': 'localhost'})
        if r.status_code == 200:
            data = r.json()
            # DRF paginado → extraer results
            if isinstance(data, dict) and 'results' in data:
                return data['results']
            return data
    except (_requests_lib.ConnectionError, _requests_lib.Timeout, _requests_lib.HTTPError):
        return []
    return []


def _post_json(url, payload, timeout=4):
    try:
        r = http_requests.post(url, json=payload, timeout=timeout, headers={'Host': 'localhost'})
        return r.status_code, r.json() if r.content else {}
    except (_requests_lib.ConnectionError, _requests_lib.Timeout, _requests_lib.HTTPError) as e:
        return 500, {'error': str(e)}


def _delete_url(url, timeout=4):
    try:
        r = http_requests.delete(url, timeout=timeout, headers={'Host': 'localhost'})
        return r.status_code
    except (_requests_lib.ConnectionError, _requests_lib.Timeout, _requests_lib.HTTPError):
        return 500


# ─────────────────────────────────────────────
# Panel — Gestión Curricular
# ─────────────────────────────────────────────

@login_required
def panel_careers(request):
    """Lista de carreras con asignaciones de sedes/núcleos filtradas por scope."""
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    u = request.user

    # Obtener todas las carreras del students_service
    all_careers = _get_json(f'{STUDENTS_SERVICE_URL}/api/careers/')

    # Obtener asignaciones del curriculum_service
    all_sede_assignments   = _get_json(f'{CURRICULUM_SERVICE_URL}/api/career-sede/')
    all_nucleo_assignments = _get_json(f'{CURRICULUM_SERVICE_URL}/api/career-nucleo/')

    # Indexar asignaciones por career_id
    sede_map   = {}  # career_id → [sede_id, ...]
    nucleo_map = {}  # career_id → [nucleo_id, ...]
    for a in all_sede_assignments:
        cid = a['career_id']
        sede_map.setdefault(cid, []).append(a)
    for a in all_nucleo_assignments:
        cid = a['career_id']
        nucleo_map.setdefault(cid, []).append(a)

    # Filtrar carreras según scope
    if u.scope_level == 'sede' and u.scope_sede_id:
        assigned_ids = {a['career_id'] for a in all_sede_assignments if a['sede_id'] == u.scope_sede_id}
        careers = [c for c in all_careers if c['id'] in assigned_ids]
    elif u.scope_level == 'nucleo' and u.scope_nucleo_id:
        assigned_ids = {a['career_id'] for a in all_nucleo_assignments if a['nucleo_id'] == u.scope_nucleo_id}
        careers = [c for c in all_careers if c['id'] in assigned_ids]
    else:
        careers = all_careers

    # Mapas de nombres de sedes y núcleos (modelos locales del auth_service)
    sede_names   = {s['id']: s['name'] for s in Sede.objects.values('id', 'name')}
    from .models import Nucleo as NucleoModel
    nucleo_names = {n['id']: n['name'] for n in NucleoModel.objects.values('id', 'name')}

    # Enriquecer cada carrera con sus asignaciones
    for c in careers:
        cid = c['id']
        c['sede_assignments']   = sede_map.get(cid, [])
        c['nucleo_assignments']  = nucleo_map.get(cid, [])
        c['sede_count']         = len(c['sede_assignments'])
        c['nucleo_count']        = len(c['nucleo_assignments'])
        c['plan_item_count']    = 0  # se carga en el detalle del plan
        # Nombres resueltos para mostrar en la tabla
        c['sede_names_list']    = [
            sede_names.get(a['sede_id'], f'Sede #{a["sede_id"]}')
            for a in c['sede_assignments'] if a.get('is_active', True)
        ]
        c['nucleo_names_list']  = [
            nucleo_names.get(a['nucleo_id'], f'Núcleo #{a["nucleo_id"]}')
            for a in c['nucleo_assignments'] if a.get('is_active', True)
        ]

    faculties = sorted({c.get('faculty', '') for c in careers if c.get('faculty')})

    return render(request, 'admin_careers.html', {
        'careers':   careers,
        'faculties': faculties,
        'is_global': u.scope_level == 'global',
    })


@login_required
def panel_curricular_units(request):
    """Catálogo global de Unidades Curriculares. Solo accesible para scope=global."""
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    u = request.user
    if u.scope_level != 'global':
        messages.warning(request, 'Solo el nivel Rectorado / Global puede administrar el catálogo de Unidades Curriculares.')
        return redirect('home')

    # Filtros GET
    component_filter = request.GET.get('component', '')
    uc_type_filter   = request.GET.get('uc_type', '')
    search_q         = request.GET.get('q', '')

    params = '?active=true'
    if component_filter:
        params += f'&component={_url_quote(str(component_filter))}'
    if uc_type_filter:
        params += f'&uc_type={_url_quote(str(uc_type_filter))}'
    if search_q:
        params += f'&search={_url_quote(str(search_q))}'

    units = _get_json(f'{CURRICULUM_SERVICE_URL}/api/curricular-units/{params}')

    # Choices para los filtros
    component_choices = [
        ('CFPE', 'Formación Profesional Específico'),
        ('CFD',  'Formación Docente'),
        ('CFC',  'Formación Contextualizado'),
        ('ECU',  'Eje Curricular'),
    ]
    uc_type_choices = [
        ('UNCO',  'Obligatoria'),
        ('UNCLE', 'Libre Elección'),
    ]
    level_choices = [
        ('FUND',  'Fundamentación'),
        ('INTEG', 'Integración'),
        ('PROF',  'Profundización'),
    ]
    color_map = {'CFPE': 'primary', 'CFD': 'warning', 'CFC': 'success', 'ECU': 'info'}
    for u_item in units:
        u_item['component_color'] = color_map.get(u_item.get('component', ''), 'secondary')

    import json as _json
    uc_data_json = _json.dumps({str(uu['id']): uu for uu in units}, ensure_ascii=False)

    return render(request, 'admin_curricular_units.html', {
        'units':             units,
        'component_choices': component_choices,
        'uc_type_choices':   uc_type_choices,
        'level_choices':     level_choices,
        'component_filter':  component_filter,
        'uc_type_filter':    uc_type_filter,
        'search_q':          search_q,
        'curriculum_api':    CURRICULUM_SERVICE_URL,
        'uc_data_json':      uc_data_json,
    })


@login_required
def panel_career_plan(request, career_id):
    """Vista visual del plan curricular de una carrera (8 períodos académicos)."""
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    u = request.user

    # Obtener datos de la carrera
    career = None
    careers_list = _get_json(f'{STUDENTS_SERVICE_URL}/api/careers/')
    for c in careers_list:
        if c['id'] == career_id:
            career = c
            break

    if not career:
        messages.error(request, 'Carrera no encontrada.')
        return redirect('panel_careers')

    # Obtener plan curricular de curriculum_service
    plan_items = _get_json(f'{CURRICULUM_SERVICE_URL}/api/career-plan/?career_id={career_id}')

    # Organizar por período académico {1: [...], 2: [...], ...}
    periods = {i: [] for i in range(1, 9)}
    for item in plan_items:
        p = item.get('academic_period', 0)
        if 1 <= p <= 8:
            periods[p].append(item)

    # Catálogo de UCs disponibles para agregar (filtrado: no añadir las que ya están)
    all_units_resp = _get_json(f'{CURRICULUM_SERVICE_URL}/api/curricular-units/?active=true')
    # IDs ya en el plan para esta carrera
    used_unit_ids = {item['curricular_unit'] for item in plan_items}
    available_units = [uu for uu in all_units_resp if uu['id'] not in used_unit_ids]

    color_map = {'CFPE': 'primary', 'CFD': 'warning', 'CFC': 'success', 'ECU': 'info'}
    for item in plan_items:
        unit = item.get('unit', {})
        item['component_color'] = color_map.get(unit.get('component', ''), 'secondary')
    for uu in available_units:
        uu['component_color'] = color_map.get(uu.get('component', ''), 'secondary')

    # Nombres de períodos académicos en romano
    period_names = {1:'I', 2:'II', 3:'III', 4:'IV', 5:'V', 6:'VI', 7:'VII', 8:'VIII'}

    import json as _json
    # Serializar datos para uso seguro en JavaScript (evita problemas de escapado en templates)
    periods_json        = _json.dumps(periods, ensure_ascii=False)
    available_units_json = _json.dumps(available_units, ensure_ascii=False)

    return render(request, 'admin_career_plan.html', {
        'career':               career,
        'periods':              periods,
        'period_names':         period_names,
        'available_units':      available_units,
        'is_global':            u.scope_level == 'global',
        'total_items':          len(plan_items),
        'curriculum_api':       CURRICULUM_SERVICE_URL,
        'periods_json':         periods_json,
        'available_units_json': available_units_json,
    })


@login_required
def panel_career_assignments(request):
    """Módulo de asignación de carreras a sedes/núcleos. Solo scope=global."""
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    u = request.user
    if u.scope_level != 'global':
        messages.warning(request, 'Solo el nivel Rectorado / Global puede gestionar las asignaciones.')
        return redirect('panel_careers')

    # Carreras, sedes, nucleos, asignaciones
    all_careers = _get_json(f'{STUDENTS_SERVICE_URL}/api/careers/')
    all_sedes   = list(u.get_visible_sedes_qs().prefetch_related('nucleos').values(
        'id', 'name', 'city', 'is_active'
    ))
    nucleos_by_sede_map = {}
    from .models import Nucleo as NucleoModel
    for sede in u.get_visible_sedes_qs():
        nucleos_by_sede_map[sede.id] = list(sede.nucleos.filter(is_active=True).values('id', 'name'))

    all_sede_assignments   = _get_json(f'{CURRICULUM_SERVICE_URL}/api/career-sede/')
    all_nucleo_assignments = _get_json(f'{CURRICULUM_SERVICE_URL}/api/career-nucleo/')

    # Sets para lookup rápido
    sede_assigned   = {(a['career_id'], a['sede_id']): a['id']   for a in all_sede_assignments}
    nucleo_assigned = {(a['career_id'], a['nucleo_id']): a['id'] for a in all_nucleo_assignments}

    # Serializar como strings para uso en JavaScript (claves de objeto JS)
    import json as _json
    sede_assigned_js   = {f'{cid}_{sid}': aid for (cid, sid), aid in sede_assigned.items()}
    nucleo_assigned_js = {f'{cid}_{nid}': aid for (cid, nid), aid in nucleo_assigned.items()}

    return render(request, 'admin_career_assignments.html', {
        'careers':                 all_careers,
        'sedes':                   all_sedes,
        'nucleos_by_sede':         nucleos_by_sede_map,
        'sede_assigned_json':      _json.dumps(sede_assigned_js),
        'nucleo_assigned_json':    _json.dumps(nucleo_assigned_js),
        'careers_json':            _json.dumps(all_careers, ensure_ascii=False),
        'nucleos_by_sede_json':    _json.dumps({str(k): v for k, v in nucleos_by_sede_map.items()}, ensure_ascii=False),
        'curriculum_api':          CURRICULUM_SERVICE_URL,
        'current_user_id':         u.id,
    })


# ─────────────────────────────────────────────────────────────
# Panel — Períodos Académicos (courses_service)
# ─────────────────────────────────────────────────────────────

@login_required
def panel_periods(request):
    """CRUD de períodos académicos desde el panel admin."""
    if not _admin_required(request):
        return redirect('home')

    _C = COURSES_SERVICE_URL
    msg_ok = msg_err = None

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()

        if action == 'create':
            payload = {
                'name':        request.POST.get('name', '').strip(),
                'period_type': request.POST.get('period_type', 'lapso_i'),
                'start_date':  request.POST.get('start_date', ''),
                'end_date':    request.POST.get('end_date', ''),
                'is_active':   request.POST.get('is_active') == 'on',
            }
            try:
                r = http_requests.post(f'{_C}/api/periods/', json=payload, timeout=4)
                if r.status_code == 201:
                    msg_ok = f'Período "{payload["name"]}" creado exitosamente.'
                else:
                    msg_err = f'Error al crear: {r.json()}'
            except Exception as e:
                msg_err = f'Error de conexión: {e}'

        elif action == 'activate':
            period_id = request.POST.get('period_id', '').strip()
            try:
                r = http_requests.patch(
                    f'{_C}/api/periods/{period_id}/',
                    json={'is_active': True}, timeout=4,
                )
                msg_ok = 'Período activado.' if r.status_code == 200 else f'Error: {r.json()}'
            except Exception as e:
                msg_err = f'Error de conexión: {e}'

        elif action == 'deactivate':
            period_id = request.POST.get('period_id', '').strip()
            try:
                r = http_requests.patch(
                    f'{_C}/api/periods/{period_id}/',
                    json={'is_active': False}, timeout=4,
                )
                msg_ok = 'Período desactivado.' if r.status_code == 200 else f'Error: {r.json()}'
            except Exception as e:
                msg_err = f'Error de conexión: {e}'

        elif action == 'delete':
            period_id = request.POST.get('period_id', '').strip()
            try:
                r = http_requests.delete(f'{_C}/api/periods/{period_id}/', timeout=4)
                msg_ok = 'Período eliminado.' if r.status_code == 204 else f'Error: {r.json()}'
            except Exception as e:
                msg_err = f'Error de conexión: {e}'

        if msg_ok:
            messages.success(request, msg_ok)
        if msg_err:
            messages.error(request, msg_err)
        return redirect('panel_periods')

    periods = _get_json(f'{_C}/api/periods/')
    # Obtener el período activo por separado
    active_period = None
    try:
        r = http_requests.get(f'{_C}/api/periods/active/', timeout=3)
        if r.status_code == 200:
            active_period = r.json()
    except Exception:
        pass

    PERIOD_TYPE_CHOICES = [
        ('lapso_i',   'Lapso I'),
        ('lapso_ii',  'Lapso II'),
        ('intensivo', 'Intensivo de Verano'),
    ]

    return render(request, 'admin_periods.html', {
        'periods':             periods,
        'active_period':       active_period,
        'period_type_choices': PERIOD_TYPE_CHOICES,
    })


# ─────────────────────────────────────────────────────────────
# Panel — Secciones / Oferta Académica (courses_service)
# ─────────────────────────────────────────────────────────────

@login_required
def panel_sections(request):
    """
    Lista y creación de secciones de la oferta académica.
    Cada sección vincula: UC + Carrera + Período + Sede/Núcleo.
    """
    if not _admin_required(request):
        return redirect('home')

    from .models import Sede

    _C  = COURSES_SERVICE_URL
    _CU = CURRICULUM_SERVICE_URL
    _ST = os.environ.get('STUDENTS_SERVICE_URL', 'http://students_service:8001')
    u   = request.user

    # ── Filtros de la request ──
    q          = request.GET.get('q', '').strip()
    period_f   = request.GET.get('period', '').strip()
    sede_f     = request.GET.get('sede', '').strip()
    career_f   = request.GET.get('career', '').strip()
    active_f   = request.GET.get('active', 'true').strip()

    # ── Datos para selectores ──
    periods  = _get_json(f'{_C}/api/periods/')
    careers  = _get_json(f'{_ST}/api/careers/')
    uc_list  = _get_json(f'{_CU}/api/curricular-units/?active=true')
    sedes    = list(u.get_visible_sedes_qs().filter(is_active=True).values('id', 'name'))

    # ── Secciones con filtros ──
    params = {}
    if period_f:
        params['period'] = period_f
    if sede_f:
        params['sede']   = sede_f
    if career_f:
        params['career'] = career_f
    if active_f in ('true', 'false'):
        params['active'] = active_f
    if q:
        params['search'] = q

    sections_raw = []
    service_ok   = False
    total_count  = 0
    try:
        r = http_requests.get(f'{_C}/api/sections/', params=params, timeout=4)
        service_ok = True
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                total_count  = data.get('count', 0)
                sections_raw = data.get('results', [])
            else:
                sections_raw = data
                total_count  = len(data)
    except Exception:
        pass

    # Período activo
    active_period = None
    try:
        r2 = http_requests.get(f'{_C}/api/periods/active/', timeout=2)
        if r2.status_code == 200:
            active_period = r2.json()
    except Exception:
        pass

    return render(request, 'admin_sections.html', {
        'sections':     sections_raw,
        'total_count':  total_count,
        'periods':      periods,
        'active_period': active_period,
        'careers':      careers,
        'uc_list':      uc_list,
        'sedes':        sedes,
        'q':            q,
        'period_f':     period_f,
        'sede_f':       sede_f,
        'career_f':     career_f,
        'active_f':     active_f,
        'service_ok':   service_ok,
        'courses_api':  _C,
    })


# ─────────────────────────────────────────────
# Panel — Convalidación de Estudios (UPEL)
# ─────────────────────────────────────────────

@login_required
def panel_convalidacion(request):
    """
    Lista de aspirantes que solicitan convalidación de estudios previos.
    Proceso UPEL: aspirante admitido con estudios universitarios previos que solicita
    reconocimiento de asignaturas ante la Comisión de Convalidaciones y Consejo Directivo.
    """
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    ALLOWED_ROLES = ('admin', 'control_estudios', 'secretaria', 'docencia')
    if not (request.user.is_superuser or request.user.role in ALLOWED_ROLES):
        messages.error(request, 'No tienes permiso para acceder al módulo de convalidaciones.')
        return redirect('home')

    u            = request.user
    status_filter = request.GET.get('admission_status', '').strip()
    sede_filter   = request.GET.get('sede', '').strip()
    search_q      = request.GET.get('q', '').strip()

    scope_kwargs = u.scope_filter_for('aspirant')
    qs = (
        Aspirant.objects
        .filter(**scope_kwargs, admission_type='convalidacion')
        .select_related('sede', 'nucleo', 'reviewed_by')
        .prefetch_related('convalidacion_items')
        .order_by('-registered_at')
    )
    qs = qs.filter(national_id__isnull=False).exclude(national_id='')

    if status_filter:
        qs = qs.filter(admission_status=status_filter)
    if sede_filter:
        visible_sede_ids = u.get_visible_sedes_qs().values_list('pk', flat=True)
        try:
            if int(sede_filter) in list(visible_sede_ids):
                qs = qs.filter(sede_id=sede_filter)
        except (ValueError, TypeError):
            pass
    if search_q:
        from django.db.models import Q
        qs = qs.filter(
            Q(first_name__icontains=search_q) |
            Q(last_name__icontains=search_q) |
            Q(national_id__icontains=search_q) |
            Q(email__icontains=search_q) |
            Q(code__icontains=search_q) |
            Q(prev_institution__icontains=search_q)
        )

    base_qs = (
        Aspirant.objects.filter(**scope_kwargs, admission_type='convalidacion')
        .filter(national_id__isnull=False).exclude(national_id='')
    )
    counts = {
        'all':        base_qs.count(),
        'pending':    base_qs.filter(admission_status='pending').count(),
        'in_review':  base_qs.filter(admission_status='in_review').count(),
        'approved':   base_qs.filter(admission_status='approved').count(),
        'rejected':   base_qs.filter(admission_status='rejected').count(),
        'waitlisted': base_qs.filter(admission_status='waitlisted').count(),
    }

    sedes = u.get_visible_sedes_qs().filter(is_active=True)
    paginator = Paginator(qs, 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'admin_convalidacion.html', {
        'aspirants':         page_obj,
        'page_obj':          page_obj,
        'status_filter':     status_filter,
        'sede_filter':       sede_filter,
        'search_q':          search_q,
        'sedes':             sedes,
        'counts':            counts,
        'admission_choices': Aspirant.ADMISSION_STATUS_CHOICES,
    })


@login_required
def panel_convalidacion_detail(request, code):
    """
    Detalle de una solicitud de convalidación.
    Permite:
      - Gestionar items de convalidación (asignaturas) uno a uno
      - Cambiar estado de cada item (Comisión de Convalidaciones)
      - Registrar Resolución del Consejo Directivo
      - Al aprobar: crear estudiante + marcar asignaturas convalidadas en grades_service
    """
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    ALLOWED_ROLES = ('admin', 'control_estudios', 'secretaria', 'docencia')
    if not (request.user.is_superuser or request.user.role in ALLOWED_ROLES):
        messages.error(request, 'No tienes permiso para gestionar convalidaciones.')
        return redirect('home')

    aspirant = get_object_or_404(Aspirant, code=code, admission_type='convalidacion')
    careers  = _get_careers()
    items    = aspirant.convalidacion_items.select_related('evaluator').order_by('origin_subject_name')

    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        from django.utils import timezone

        # ── Agregar item de convalidación ─────────────────────────
        if action == 'add_item':
            origin_name  = request.POST.get('origin_subject_name', '').strip()
            origin_code  = request.POST.get('origin_subject_code', '').strip()
            origin_cred  = request.POST.get('origin_credits', '').strip()
            origin_hours = request.POST.get('origin_hours', '').strip()
            origin_grade = request.POST.get('origin_grade', '').strip()
            origin_year  = request.POST.get('origin_year', '').strip()
            upel_name    = request.POST.get('upel_course_name', '').strip()
            upel_code    = request.POST.get('upel_course_code', '').strip()
            upel_cred    = request.POST.get('upel_credits', '').strip()

            if not origin_name:
                messages.error(request, 'El nombre de la asignatura de origen es obligatorio.')
            else:
                item = ConvalidacionItem(
                    aspirant=aspirant,
                    origin_subject_name=origin_name,
                    origin_subject_code=origin_code,
                    origin_grade=origin_grade,
                    upel_course_name=upel_name,
                    upel_course_code=upel_code,
                )
                if origin_cred:
                    try:
                        item.origin_credits = float(origin_cred)
                    except ValueError:
                        pass
                if origin_hours:
                    try:
                        item.origin_hours = int(origin_hours)
                    except ValueError:
                        pass
                if origin_year:
                    try:
                        item.origin_year = int(origin_year)
                    except ValueError:
                        pass
                if upel_cred:
                    try:
                        item.upel_credits = float(upel_cred)
                    except ValueError:
                        pass
                item.save()
                messages.success(request, f'Asignatura "{origin_name}" agregada a la solicitud.')

        # ── Actualizar estado de un item ──────────────────────────
        elif action == 'update_item':
            item_id         = request.POST.get('item_id', '').strip()
            new_item_status = request.POST.get('item_status', '').strip()
            committee_notes = request.POST.get('committee_notes', '').strip()
            council_res     = request.POST.get('council_resolution', '').strip()
            council_date    = request.POST.get('council_resolution_date', '').strip()

            try:
                item = ConvalidacionItem.objects.get(pk=item_id, aspirant=aspirant)
                valid_statuses = [s[0] for s in ConvalidacionItem.ITEM_STATUS_CHOICES]
                if new_item_status in valid_statuses:
                    item.status = new_item_status
                item.committee_notes = committee_notes
                item.council_resolution = council_res
                if council_date:
                    try:
                        from datetime import date
                        item.council_resolution_date = date.fromisoformat(council_date)
                    except ValueError:
                        pass
                item.evaluator    = request.user
                item.evaluated_at = timezone.now()
                item.save()
                messages.success(request, f'Item "{item.origin_subject_name}" actualizado.')
            except ConvalidacionItem.DoesNotExist:
                messages.error(request, 'Item no encontrado.')

        # ── Eliminar item ─────────────────────────────────────────
        elif action == 'delete_item':
            item_id = request.POST.get('item_id', '').strip()
            try:
                item = ConvalidacionItem.objects.get(pk=item_id, aspirant=aspirant)
                nombre = item.origin_subject_name
                item.delete()
                messages.success(request, f'Asignatura "{nombre}" eliminada de la solicitud.')
            except ConvalidacionItem.DoesNotExist:
                messages.error(request, 'Item no encontrado.')

        # ── Actualizar estado general del expediente ──────────────
        elif action == 'update_status':
            new_status = request.POST.get('admission_status', '').strip()
            notes      = request.POST.get('admission_notes', '').strip()
            valid_statuses = [s[0] for s in Aspirant.ADMISSION_STATUS_CHOICES]

            if new_status not in valid_statuses:
                messages.error(request, 'Estado de admisión inválido.')
                return redirect('panel_convalidacion_detail', code=code)

            aspirant.admission_status = new_status
            aspirant.admission_notes  = notes
            aspirant.reviewed_by      = request.user
            aspirant.reviewed_at      = timezone.now()

            # ── Si se aprueba: crear estudiante + registrar convalidaciones ──
            if new_status == 'approved':
                admitted_opt_str = request.POST.get('admitted_option', '').strip()
                try:
                    opt_num = int(admitted_opt_str)
                    if opt_num not in (1, 2, 3):
                        raise ValueError
                except (ValueError, TypeError):
                    messages.error(request, 'Debe seleccionar la opción de carrera admitida (1ª, 2ª o 3ª).')
                    return redirect('panel_convalidacion_detail', code=code)

                aspirant.admitted_option = opt_num
                if opt_num == 1:
                    aspirant.admitted_career_id   = aspirant.career_id
                    aspirant.admitted_career_name = aspirant.career_name
                elif opt_num == 2:
                    aspirant.admitted_career_id   = aspirant.career_id_2
                    aspirant.admitted_career_name = aspirant.career_name_2
                elif opt_num == 3:
                    aspirant.admitted_career_id   = aspirant.career_id_3
                    aspirant.admitted_career_name = aspirant.career_name_3

                if aspirant.admitted_career_id and aspirant.user_id:
                    import datetime
                    payload = {
                        'user_id':        aspirant.user_id,
                        'career':         aspirant.admitted_career_id,
                        'semester':       1,
                        'status':         'active',
                        'enrollment_date': datetime.date.today().isoformat(),
                        'national_id':    aspirant.national_id or '',
                        'phone':          aspirant.phone or '',
                        'address':        aspirant.address or '',
                    }
                    if aspirant.birth_date:
                        payload['birth_date'] = aspirant.birth_date.isoformat()

                    st_code, st_resp = _post_json(
                        f'{STUDENTS_SERVICE_URL}/api/students/', payload
                    )

                    if st_code in (200, 201):
                        # Cambiar rol del usuario a 'student'
                        try:
                            u_obj = CustomUser.objects.get(pk=aspirant.user_id)
                            u_obj.role = 'student'
                            u_obj.save()
                        except CustomUser.DoesNotExist:
                            pass

                        # Registrar asignaturas convalidadas en grades_service
                        items_convalidadas = aspirant.convalidacion_items.filter(
                            status__in=('convalidada', 'convalidada_condicion')
                        )
                        conv_count = 0
                        for ci in items_convalidadas:
                            if ci.upel_course_id:
                                grade_payload = {
                                    'student_id': aspirant.user_id,
                                    'course_id':  ci.upel_course_id,
                                    'is_convalidated': True,
                                    'convalidation_note': ci.origin_grade or '',
                                    'council_resolution': ci.council_resolution or '',
                                    'final_grade': _parse_grade(ci.origin_grade),
                                }
                                g_code, _ = _post_json(
                                    f'{os.environ.get("GRADES_SERVICE_URL", "http://grades_service:8004")}/api/grades/convalidated/',
                                    grade_payload
                                )
                                if g_code in (200, 201):
                                    conv_count += 1

                        aspirant.save()
                        conv_msg = f' Se registraron {conv_count} asignatura(s) convalidada(s).' if conv_count else ''
                        messages.success(
                            request,
                            f'✅ {aspirant.get_full_name()} admitido/a en '
                            f'"{aspirant.admitted_career_name}".{conv_msg}'
                        )
                        return redirect('panel_convalidacion')
                    else:
                        err_detail = st_resp.get('detail') or str(st_resp) if isinstance(st_resp, dict) else str(st_resp)
                        if 'already' in str(err_detail).lower() or st_code == 400:
                            aspirant.save()
                            messages.warning(request, f'Estado actualizado, pero hubo un problema con el registro de estudiante: {err_detail}')
                            return redirect('panel_convalidacion')
                        messages.error(request, f'Error al crear el estudiante ({st_code}): {err_detail}')
                        return redirect('panel_convalidacion_detail', code=code)
                else:
                    aspirant.save()
                    messages.warning(request, 'Admitido, pero sin usuario o carrera asignada para crear el estudiante.')
                    return redirect('panel_convalidacion')
            else:
                if new_status != 'approved':
                    aspirant.admitted_option      = None
                    aspirant.admitted_career_id   = None
                    aspirant.admitted_career_name = ''
                aspirant.save()
                label = dict(Aspirant.ADMISSION_STATUS_CHOICES).get(new_status, new_status)
                messages.success(request, f'Expediente de {aspirant.get_full_name()} actualizado a "{label}".')

        return redirect('panel_convalidacion_detail', code=code)

    # Estadísticas del expediente
    total_items      = items.count()
    convalidadas     = items.filter(status__in=('convalidada', 'convalidada_condicion')).count()
    no_convalidadas  = items.filter(status='no_convalidada').count()
    pendientes       = items.filter(status__in=('solicitada', 'en_revision', 'prueba_requerida')).count()

    # Opciones de carrera del aspirante
    options = []
    for i, (cid, cname) in enumerate([
        (aspirant.career_id,   aspirant.career_name),
        (aspirant.career_id_2, aspirant.career_name_2),
        (aspirant.career_id_3, aspirant.career_name_3),
    ], start=1):
        if cid:
            options.append({'num': i, 'id': cid, 'name': cname or f'Especialidad #{cid}'})

    return render(request, 'admin_convalidacion_detail.html', {
        'aspirant':          aspirant,
        'items':             items,
        'options':           options,
        'careers':           careers,
        'admission_choices': Aspirant.ADMISSION_STATUS_CHOICES,
        'item_status_choices': ConvalidacionItem.ITEM_STATUS_CHOICES,
        'convalidacion_steps': [
            'Recibido',
            'Rev. Documental',
            'Comisión Convalidaciones',
            'Consejo Directivo',
            'Notificación',
        ],
        'stats': {
            'total':         total_items,
            'convalidadas':  convalidadas,
            'no_conv':       no_convalidadas,
            'pendientes':    pendientes,
        },
    })


def _parse_grade(grade_str):
    """Convierte la calificación de origen a escala 0-20 para grades_service."""
    if not grade_str:
        return None
    try:
        val = float(str(grade_str).replace(',', '.').replace('/', ' ').split()[0])
        # Si está en escala 0-100, convertir a 0-20
        if val > 20:
            val = round(val * 20 / 100, 1)
        return val
    except (ValueError, IndexError):
        return None


# ─────────────────────────────────────────────
# Portal del Estudiante
# ─────────────────────────────────────────────

@login_required
def student_dashboard(request):
    """Dashboard principal del estudiante regular (role=student)."""
    if request.user.role != 'student':
        if request.user.role == 'aspirant':
            return redirect('aspirant_dashboard')
        return redirect('home')

    user_id = request.user.id
    _hdr = {'Host': 'localhost'}

    # ── Datos del estudiante desde students_service ──────────────
    student_data = None
    try:
        r = http_requests.get(
            f'{STUDENTS_SERVICE_URL}/api/students/by-user/{user_id}/',
            timeout=4, headers=_hdr,
        )
        if r.status_code == 200:
            student_data = r.json()
    except Exception:
        pass

    student_id = student_data.get('id') if student_data else None

    # ── Período activo desde courses_service ─────────────────────
    active_period = None
    try:
        r = http_requests.get(
            f'{COURSES_SERVICE_URL}/api/periods/active/',
            timeout=4, headers=_hdr,
        )
        if r.status_code == 200:
            active_period = r.json()
    except Exception:
        pass

    # ── Inscripción actual desde enrollment_service ──────────────
    current_enrollment = None
    enrollment_details = []
    if student_id:
        try:
            r = http_requests.get(
                f'{ENROLLMENT_SERVICE_URL}/api/enrollments/student/{student_id}/',
                timeout=4, headers=_hdr,
            )
            if r.status_code == 200:
                enrollments = r.json()
                if isinstance(enrollments, dict) and 'results' in enrollments:
                    enrollments = enrollments['results']
                # Tomar la inscripción del período activo o la más reciente
                if enrollments:
                    if active_period:
                        period_id = active_period.get('id')
                        current_enrollment = next(
                            (e for e in enrollments if e.get('period_id') == period_id),
                            enrollments[0],
                        )
                    else:
                        current_enrollment = enrollments[0]
                    enrollment_details = current_enrollment.get('details', [])
        except Exception:
            pass

    # ── Enriquecer detalles con nombres de UC ────────────────────
    enriched_details = []
    for det in enrollment_details:
        section_id  = det.get('section_id') or det.get('section')
        uc_name     = det.get('uc_name', '')
        uc_code     = det.get('uc_code', '')
        uc_credits  = det.get('uc_credits', 0)
        section_num = det.get('section_number', '')
        # Si no traen el nombre UC, intentar consultarlo desde courses_service
        if not uc_name and section_id:
            try:
                r2 = http_requests.get(
                    f'{COURSES_SERVICE_URL}/api/sections/{section_id}/',
                    timeout=3, headers=_hdr,
                )
                if r2.status_code == 200:
                    sec = r2.json()
                    uc_name     = sec.get('uc_name', '')
                    uc_code     = sec.get('uc_code', '')
                    uc_credits  = sec.get('uc_credits', 0)
                    section_num = sec.get('section_number', '')
            except Exception:
                pass
        enriched_details.append({
            **det,
            'uc_name':        uc_name or f'Sección #{section_id}',
            'uc_code':        uc_code,
            'uc_credits':     uc_credits,
            'section_number': section_num,
        })

    # ── Calificaciones desde grades_service ──────────────────────
    grades = []
    academic_index = None
    if student_id:
        try:
            r = http_requests.get(
                f'{GRADES_SERVICE_URL}/api/grades/student/{student_id}/',
                timeout=4, headers=_hdr,
            )
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict) and 'results' in data:
                    data = data['results']
                grades = data if isinstance(data, list) else []
                # Calcular índice acumulado
                if grades:
                    approved = [g for g in grades if g.get('final_grade') is not None]
                    if approved:
                        total_w = sum(
                            float(g.get('final_grade', 0)) * float(g.get('credits', 1))
                            for g in approved
                        )
                        total_c = sum(float(g.get('credits', 1)) for g in approved)
                        academic_index = round(total_w / total_c, 2) if total_c else None
        except Exception:
            pass

    # Separar notas aprobadas y reprobadas
    approved_grades = [g for g in grades if g.get('final_grade') is not None and float(g.get('final_grade', 0)) >= 10]
    failed_grades   = [g for g in grades if g.get('final_grade') is not None and float(g.get('final_grade', 0)) < 10]

    return render(request, 'student_dashboard.html', {
        'student':           student_data,
        'student_id':        student_id,
        'active_period':     active_period,
        'current_enrollment': current_enrollment,
        'enrollment_details': enriched_details,
        'grades':            grades,
        'approved_grades':   approved_grades,
        'failed_grades':     failed_grades,
        'academic_index':    academic_index,
        'total_approved_uc': len(approved_grades),
    })


# ─────────────────────────────────────────────
# Documentos del Expediente (Upload/Delete)
# ─────────────────────────────────────────────

@login_required
def aspirant_upload_document(request):
    """Recibe el upload de un documento del expediente desde el aspirant_dashboard."""
    if request.method != 'POST':
        return redirect('aspirant_dashboard')

    try:
        aspirant = request.user.aspirant_profile
    except Aspirant.DoesNotExist:
        messages.error(request, 'No se encontró tu perfil de aspirante.')
        return redirect('aspirant_dashboard')

    uploaded_file = request.FILES.get('file')
    doc_type      = request.POST.get('doc_type', 'otro')
    notes         = request.POST.get('notes', '').strip()

    if not uploaded_file:
        messages.error(request, 'No se recibió ningún archivo.')
        return redirect('aspirant_dashboard')

    # Validar extensión permitida
    allowed_ext = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.doc', '.docx'}
    import os as _os
    ext = _os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in allowed_ext:
        messages.error(request, f'Formato de archivo no permitido: {ext}. Use PDF, imagen o Word.')
        return redirect('aspirant_dashboard')

    # Validar tamaño máximo 10 MB
    if uploaded_file.size > 10 * 1024 * 1024:
        messages.error(request, 'El archivo supera el límite de 10 MB.')
        return redirect('aspirant_dashboard')

    doc = DocumentAttachment(
        aspirant=aspirant,
        doc_type=doc_type,
        original_filename=uploaded_file.name,
        file_size=uploaded_file.size,
        notes=notes,
    )
    doc.file = uploaded_file
    doc.save()

    messages.success(request, f'Documento "{doc.get_doc_type_display()}" subido correctamente.')
    return redirect('aspirant_dashboard')


@login_required
def aspirant_delete_document(request, doc_id):
    """Elimina un documento del expediente (solo el dueño o admin)."""
    if request.method != 'POST':
        return redirect('aspirant_dashboard')

    doc = get_object_or_404(DocumentAttachment, pk=doc_id)

    is_owner = (
        hasattr(request.user, 'aspirant_profile')
        and doc.aspirant == request.user.aspirant_profile
    )
    is_admin = request.user.role in ('admin', 'control_estudios') or request.user.is_staff

    if not (is_owner or is_admin):
        messages.error(request, 'No tienes permiso para eliminar este documento.')
        return redirect('aspirant_dashboard')

    doc_label = doc.get_doc_type_display()
    doc.file.delete(save=False)  # Eliminar archivo físico
    doc.delete()
    messages.success(request, f'Documento "{doc_label}" eliminado.')

    # Redirigir a donde corresponda
    if is_admin and not is_owner:
        return redirect('panel_admision_detail', code=doc.aspirant.code)
    return redirect('aspirant_dashboard')


# ─────────────────────────────────────────────
# Vista AJAX — Núcleos por Sede
# ─────────────────────────────────────────────

def nucleos_by_sede(request, sede_id):
    """Retorna los núcleos activos de una sede en formato JSON (para carga dinámica)."""
    nucleos = Nucleo.objects.filter(sede_id=sede_id, is_active=True).values('id', 'name')
    return JsonResponse({'nucleos': list(nucleos)})


# ─────────────────────────────────────────────
# Portal del Estudiante — Solicitud de Constancias
# ─────────────────────────────────────────────

@login_required
def student_certificates(request):
    """
    Portal del estudiante: listar sus solicitudes de constancia y crear nuevas.
    GET  → muestra lista de solicitudes + formulario nuevo
    POST → crea nueva solicitud
    """
    if request.user.role != 'student':
        if request.user.role == 'aspirant':
            return redirect('aspirant_dashboard')
        return redirect('home')

    user = request.user
    requests_qs = (
        CertificateRequest.objects
        .filter(user=user)
        .order_by('-created_at')
    )

    if request.method == 'POST':
        cert_type    = request.POST.get('cert_type', '').strip()
        purpose      = request.POST.get('purpose', '').strip()
        copies_raw   = request.POST.get('copies', '1').strip()
        period_ref   = request.POST.get('period_ref', '').strip()
        student_notes= request.POST.get('student_notes', '').strip()

        # Validaciones básicas
        valid_types   = [c[0] for c in CertificateRequest.CERT_TYPE_CHOICES]
        valid_purposes= [c[0] for c in CertificateRequest.PURPOSE_CHOICES]

        error = None
        if cert_type not in valid_types:
            error = 'Tipo de constancia inválido.'
        elif purpose not in valid_purposes:
            error = 'Propósito inválido.'
        else:
            try:
                copies = max(1, min(10, int(copies_raw)))
            except (ValueError, TypeError):
                copies = 1

        if error:
            messages.error(request, error)
        else:
            # Obtener datos del estudiante desde students_service (denormalizados)
            _hdr = {'Host': 'localhost'}
            student_carnet  = ''
            student_career  = ''
            student_semester= None
            try:
                r = http_requests.get(
                    f'{STUDENTS_SERVICE_URL}/api/students/by-user/{user.id}/',
                    timeout=4, headers=_hdr,
                )
                if r.status_code == 200:
                    sd = r.json()
                    student_carnet   = sd.get('carnet', '')
                    student_career   = sd.get('career_name', '') or str(sd.get('career', ''))
                    student_semester = sd.get('semester')
            except Exception:
                pass

            cert = CertificateRequest(
                user            = user,
                student_carnet  = student_carnet,
                student_career  = student_career,
                student_semester= student_semester,
                cert_type       = cert_type,
                purpose         = purpose,
                copies          = copies,
                period_ref      = period_ref,
                student_notes   = student_notes,
            )
            cert.save()
            messages.success(
                request,
                f'Solicitud de "{cert.get_cert_type_display()}" registrada con código {cert.code}.'
            )
            return redirect('student_certificates')

    return render(request, 'student_certificates.html', {
        'cert_requests':    requests_qs,
        'cert_type_choices': CertificateRequest.CERT_TYPE_CHOICES,
        'purpose_choices':   CertificateRequest.PURPOSE_CHOICES,
    })


# ─────────────────────────────────────────────
# Panel de Administración — Módulo Constancias
# ─────────────────────────────────────────────

@login_required
def panel_certificates(request):
    """
    Lista todas las solicitudes de constancia.
    Roles permitidos: admin, control_estudios, secretaria.
    """
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    ALLOWED_ROLES = ('admin', 'control_estudios', 'secretaria')
    if not (request.user.is_superuser or request.user.role in ALLOWED_ROLES):
        messages.error(request, 'No tienes permiso para acceder al módulo de constancias.')
        return redirect('home')

    u              = request.user
    status_filter  = request.GET.get('status', '').strip()
    type_filter    = request.GET.get('cert_type', '').strip()
    search_q       = request.GET.get('q', '').strip()

    # Filtrado por scope (sede/nucleo del usuario solicitante)
    qs = (
        CertificateRequest.objects
        .select_related('user', 'processed_by')
        .order_by('-created_at')
    )

    # Scope: si el usuario tiene scope sede/nucleo, filtrar por usuarios de esa sede
    # (Simplificado: filtrar por sede del aspirant_profile del user si existe,
    # o bien mostrar todo para global)
    if u.scope_level == 'sede' and u.scope_sede_id:
        # Mostrar solicitudes de usuarios cuyo aspirant_profile.sede coincide
        qs = qs.filter(
            user__aspirant_profile__sede_id=u.scope_sede_id
        )
    elif u.scope_level == 'nucleo' and u.scope_nucleo_id:
        qs = qs.filter(
            user__aspirant_profile__nucleo_id=u.scope_nucleo_id
        )

    if status_filter:
        qs = qs.filter(status=status_filter)
    if type_filter:
        qs = qs.filter(cert_type=type_filter)
    if search_q:
        from django.db.models import Q
        qs = qs.filter(
            Q(code__icontains=search_q) |
            Q(user__first_name__icontains=search_q) |
            Q(user__last_name__icontains=search_q) |
            Q(user__email__icontains=search_q) |
            Q(student_carnet__icontains=search_q)
        )

    # Contadores por estado (sobre el qs sin filtro de estado)
    base_qs = CertificateRequest.objects.all()
    if u.scope_level == 'sede' and u.scope_sede_id:
        base_qs = base_qs.filter(user__aspirant_profile__sede_id=u.scope_sede_id)
    elif u.scope_level == 'nucleo' and u.scope_nucleo_id:
        base_qs = base_qs.filter(user__aspirant_profile__nucleo_id=u.scope_nucleo_id)

    counts = {
        'all':        base_qs.count(),
        'pending':    base_qs.filter(status='pending').count(),
        'processing': base_qs.filter(status='processing').count(),
        'ready':      base_qs.filter(status='ready').count(),
        'delivered':  base_qs.filter(status='delivered').count(),
        'rejected':   base_qs.filter(status='rejected').count(),
    }

    paginator = Paginator(qs, 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'admin_certificates.html', {
        'cert_requests':     page_obj,
        'page_obj':          page_obj,
        'status_filter':     status_filter,
        'type_filter':       type_filter,
        'search_q':          search_q,
        'counts':            counts,
        'status_choices':    CertificateRequest.STATUS_CHOICES,
        'cert_type_choices': CertificateRequest.CERT_TYPE_CHOICES,
    })


@login_required
def panel_certificate_detail(request, code):
    """
    Detalle/gestión de una solicitud de constancia.
    Permite cambiar estado y agregar notas del personal.
    """
    if not _admin_required(request):
        return redirect('aspirant_dashboard')

    ALLOWED_ROLES = ('admin', 'control_estudios', 'secretaria')
    if not (request.user.is_superuser or request.user.role in ALLOWED_ROLES):
        messages.error(request, 'No tienes permiso para gestionar constancias.')
        return redirect('home')

    cert = get_object_or_404(CertificateRequest, code=code)

    if request.method == 'POST':
        new_status  = request.POST.get('status', '').strip()
        staff_notes = request.POST.get('staff_notes', '').strip()

        valid_statuses = [s[0] for s in CertificateRequest.STATUS_CHOICES]
        if new_status not in valid_statuses:
            messages.error(request, 'Estado inválido.')
            return redirect('panel_certificate_detail', code=code)

        from django.utils import timezone
        old_status         = cert.status
        cert.status        = new_status
        cert.staff_notes   = staff_notes
        cert.processed_by  = request.user
        cert.processed_at  = timezone.now()
        cert.save()

        label = dict(CertificateRequest.STATUS_CHOICES).get(new_status, new_status)
        messages.success(
            request,
            f'Solicitud {cert.code} actualizada a "{label}".'
        )

        # Notificar al estudiante si el estado cambió y es significativo
        if new_status != old_status:
            from .email_utils import notify_certificate_status
            notify_certificate_status(cert, new_status)


        return redirect('panel_certificate_detail', code=code)

    return render(request, 'admin_certificate_detail.html', {
        'cert':           cert,
        'status_choices': CertificateRequest.STATUS_CHOICES,
    })


def certificate_pdf(request, code):
    """
    Genera y devuelve el PDF de la constancia (solo lectura/preview).
    Permitido para admins y para el propio estudiante dueño de la constancia.
    """
    from django.http import HttpResponse
    from rest_framework_simplejwt.tokens import AccessToken
    from django.contrib.auth import get_user_model

    User = get_user_model()
    token = request.GET.get('token')
    user = None

    if token:
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
        except Exception:
            pass

    if not user and request.user.is_authenticated:
        user = request.user

    if not user:
        return HttpResponse("No autorizado. Token inválido o sesión expirada.", status=401)

    cert = get_object_or_404(CertificateRequest, code=code)

    ALLOWED_ROLES = ('admin', 'control_estudios', 'secretaria')
    is_staff = user.is_superuser or user.role in ALLOWED_ROLES
    is_owner = cert.user == user

    if not (is_staff or is_owner):
        return HttpResponse("No autorizado", status=403)
        
    # Si es el estudiante, solo puede descargarla si está 'ready' o 'delivered'
    if is_owner and not is_staff and cert.status not in ['ready', 'delivered']:
        return HttpResponse("El documento aún no está listo para su descarga.", status=403)
    
    from .pdf_utils import generate_certificate_pdf
    pdf_buffer = generate_certificate_pdf(cert)
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    # inline para verlo embebido en el navegador
    response['Content-Disposition'] = f'inline; filename="{cert.code}.pdf"'
    return response


# ─────────────────────────────────────────────
# Vistas API — Usuarios
# ─────────────────────────────────────────────

class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ValidateTokenAPIView(APIView):
    """Valida token JWT y retorna datos + permisos del usuario (para otros servicios)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            'valid':       True,
            'user_id':     u.id,
            'code':        u.code,
            'username':    u.username,
            'email':       u.email,
            'role':        u.role,
            'is_admin':    u.is_superuser or u.role == 'admin',
            'permissions': get_user_permissions(u),
            # ── Ámbito organizacional ──────────────────────────────
            'scope': {
                'level':      u.scope_level,
                'sede_id':    u.scope_sede_id,
                'sede_name':  u.scope_sede.name if u.scope_sede_id else None,
                'nucleo_id':  u.scope_nucleo_id,
                'nucleo_name': u.scope_nucleo.name if u.scope_nucleo_id else None,
                'display':    u.scope_display,
            },
        })


# ─────────────────────────────────────────────
# Vistas API — Configuración del Sistema
# ─────────────────────────────────────────────

class SystemSettingsAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        site = SystemSettings.load()
        serializer = SystemSettingsSerializer(site, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        site = SystemSettings.load()
        serializer = SystemSettingsSerializer(site, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def put(self, request):
        return self.patch(request)


# ─────────────────────────────────────────────
# Vistas API — Aspirantes
# ─────────────────────────────────────────────

class AspirantRegisterAPIView(generics.CreateAPIView):
    """
    Endpoint público para que los aspirantes creen su cuenta inicial (registro).
    No requiere autenticación. Crea el usuario CustomUser y el registro base de Aspirant.
    """
    queryset = Aspirant.objects.all()
    serializer_class = AspirantRegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]


STAFF_ROLES = ('admin', 'secretaria', 'coordinacion', 'control_estudios', 'director', 'coordinador')

class IsStaffOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser or
             getattr(request.user, 'role', '') in STAFF_ROLES)
        )


class AspirantListAPIView(generics.ListAPIView):
    queryset = Aspirant.objects.select_related('user').all()
    serializer_class = AspirantSerializer
    permission_classes = [IsStaffOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class AspirantDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_aspirant_and_check(self, request, code):
        aspirant = get_object_or_404(Aspirant, code=code)
        is_owner = hasattr(request.user, 'aspirant_profile') and request.user.aspirant_profile.code == code
        is_admin = (
            request.user.is_staff or request.user.is_superuser or
            getattr(request.user, 'role', '') in STAFF_ROLES
        )
        if not (is_owner or is_admin):
            return aspirant, False
        return aspirant, True

    def get(self, request, code):
        aspirant, allowed = self._get_aspirant_and_check(request, code)
        if not allowed:
            return Response({'detail': 'No tiene permiso para ver este perfil.'}, status=403)
        return Response(AspirantSerializer(aspirant, context={'request': request}).data)

    def patch(self, request, code):
        aspirant, allowed = self._get_aspirant_and_check(request, code)
        if not allowed:
            return Response({'detail': 'No tiene permiso para editar este perfil.'}, status=403)
        serializer = AspirantUpdateSerializer(aspirant, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(AspirantSerializer(aspirant, context={'request': request}).data)
        return Response(serializer.errors, status=400)


class AspirantSubmitAPIView(APIView):
    """Marca el perfil del aspirante como enviado para revisión formal."""
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        from core.models import Aspirant
        aspirant = get_object_or_404(Aspirant, code=code)
        # Verificar propiedad
        is_owner = hasattr(request.user, 'aspirant_profile') and request.user.aspirant_profile.code == code
        is_admin = request.user.is_staff or request.user.role == 'admin'
        
        if not (is_owner or is_admin):
            return Response({'detail': 'No tiene permiso para realizar esta acción.'}, status=403)
        
        aspirant.admission_status = 'in_review'
        aspirant.save()
        
        return Response({
            'detail': 'Expediente enviado exitosamente para revisión.',
            'status': aspirant.admission_status,
            'status_display': aspirant.get_admission_status_display()
        })


class AspirantDocumentUploadAPIView(APIView):
    """Sube un documento del expediente para un aspirante específico."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, code):
        aspirant = get_object_or_404(Aspirant, code=code)
        
        # Permisos: dueño o admin
        is_owner = hasattr(request.user, 'aspirant_profile') and request.user.aspirant_profile.code == code
        is_admin = request.user.is_staff or request.user.role == 'admin'
        
        if not (is_owner or is_admin):
            return Response({'detail': 'No tiene permiso para subir documentos a este perfil.'}, status=403)

        uploaded_file = request.FILES.get('file')
        doc_type      = request.data.get('doc_type', 'otro')
        notes         = request.data.get('notes', '').strip()

        if not uploaded_file:
            return Response({'detail': 'No se recibió ningún archivo.'}, status=400)

        # Validaciones básicas
        allowed_ext = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.doc', '.docx'}
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in allowed_ext:
            return Response({'detail': f'Formato no permitido: {ext}'}, status=400)

        if uploaded_file.size > 10 * 1024 * 1024:
            return Response({'detail': 'El archivo supera el límite de 10 MB.'}, status=400)

        doc = DocumentAttachment(
            aspirant=aspirant,
            doc_type=doc_type,
            original_filename=uploaded_file.name,
            file_size=uploaded_file.size,
            notes=notes,
        )
        doc.file = uploaded_file
        doc.save()

        return Response(DocumentAttachmentSerializer(doc).data, status=201)


class SedeListAPIView(generics.ListCreateAPIView):
    queryset = Sede.objects.all()
    serializer_class = SedeSerializer
    permission_classes = [AllowAny] # Listar es público, crear debería ser IsAdminUser

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class SedeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sede.objects.all()
    serializer_class = SedeSerializer
    permission_classes = [permissions.IsAdminUser]


class NucleoListAPIView(generics.ListCreateAPIView):
    serializer_class = NucleoSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        sede_id = self.request.query_params.get('sede_id')
        qs = Nucleo.objects.all()
        if sede_id:
            qs = qs.filter(sede_id=sede_id)
        return qs


class NucleoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Nucleo.objects.all()
    serializer_class = NucleoSerializer
    permission_classes = [permissions.IsAdminUser]


class AuthorityListCreateAPIView(generics.ListCreateAPIView):
    queryset = Authority.objects.all()
    serializer_class = AuthoritySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        sede_id = self.request.query_params.get('sede_id')
        qs = Authority.objects.filter(is_active=True)
        if sede_id:
            qs = qs.filter(sede_id=sede_id)
        return qs


class AuthorityDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Authority.objects.all()
    serializer_class = AuthoritySerializer
    permission_classes = [permissions.IsAdminUser]


# ─────────────────────────────────────────────
# Vistas API — Roles y Permisos RBAC
# ─────────────────────────────────────────────

class SystemRoleListCreateAPIView(generics.ListCreateAPIView):
    queryset = SystemRole.objects.prefetch_related('permissions').all()
    serializer_class = SystemRoleSerializer
    permission_classes = [IsAdminUser]


class SystemRoleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SystemRole.objects.prefetch_related('permissions').all()
    serializer_class = SystemRoleSerializer
    permission_classes = [IsAdminUser]


class RolePermissionBulkAPIView(APIView):
    """Asigna o actualiza permisos en lote para un rol específico."""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        role = get_object_or_404(SystemRole, pk=pk)
        serializer = RolePermissionBulkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        created, updated = 0, 0
        for perm_data in serializer.validated_data['permissions']:
            allowed_val = perm_data.get('allowed', 'true')
            if isinstance(allowed_val, str):
                allowed_val = allowed_val.lower() == 'true'
            obj, was_created = RolePermission.objects.update_or_create(
                role=role,
                service=perm_data['service'],
                action=perm_data['action'],
                defaults={'allowed': allowed_val},
            )
            if was_created:
                created += 1
            else:
                updated += 1

        return Response({
            'message': f'Permisos actualizados para el rol "{role.name}".',
            'created': created,
            'updated': updated,
            'role': SystemRoleSerializer(role).data,
        })

    def delete(self, request, pk):
        role = get_object_or_404(SystemRole, pk=pk)
        count, _ = RolePermission.objects.filter(role=role).delete()
        return Response({'message': f'{count} permisos eliminados del rol "{role.name}".'})

# ══════════════════════════════════════════════════════════════════════════════
# SPRINT 5 — INSCRIPCIONES
# ══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
# Portal del Estudiante — Inscripción de Materias
# ─────────────────────────────────────────────

@login_required
def student_enroll(request):
    """
    Portal de auto-inscripción del estudiante.
    GET  → muestra oferta académica del período activo filtrada por su carrera/sede.
    POST → inscribirse (crea Enrollment + EnrollmentDetail en enrollment_service).
    """
    if request.user.role != 'student' and not request.user.is_superuser:
        messages.error(request, 'Acceso restringido a estudiantes.')
        return redirect('home')

    _E = ENROLLMENT_SERVICE_URL
    _C = COURSES_SERVICE_URL
    _S = STUDENTS_SERVICE_URL

    # ── Datos del estudiante ──────────────────────────────────────────────────
    student = None
    try:
        r = http_requests.get(
            f'{_S}/api/students/', params={'user_id': request.user.id}, timeout=3,
        )
        if r.status_code == 200:
            data = r.json()
            results = data.get('results', data) if isinstance(data, dict) else data
            student = results[0] if results else None
    except Exception:
        pass

    if not student:
        messages.error(request, 'No se encontró tu expediente de estudiante. Contacta a Control de Estudios.')
        return redirect('student_dashboard')

    # ── Período activo ────────────────────────────────────────────────────────
    active_period = None
    try:
        r = http_requests.get(f'{_C}/api/periods/active/', timeout=2)
        if r.status_code == 200:
            active_period = r.json()
    except Exception:
        pass

    # ── Inscripción actual del estudiante en este período ─────────────────────
    current_enrollment = None
    enrolled_section_ids = set()
    if active_period:
        try:
            r = http_requests.get(
                f'{_E}/api/enrollments/',
                params={'student_id': student['id'], 'period_id': active_period['id']},
                timeout=3,
            )
            if r.status_code == 200:
                data = r.json()
                results = data.get('results', data) if isinstance(data, dict) else data
                if results:
                    current_enrollment = results[0]
                    enrolled_section_ids = {
                        d['section_id'] for d in current_enrollment.get('details', [])
                        if d.get('status') == 'active'
                    }
        except Exception:
            pass

    # ── Oferta académica del período activo (filtrada por carrera) ────────────
    available_sections = []
    if active_period:
        params = {'period': active_period['id'], 'active': 'true'}
        career_id = student.get('career_id') or student.get('career')
        if career_id:
            params['career'] = career_id
        try:
            r = http_requests.get(f'{_C}/api/sections/', params=params, timeout=4)
            if r.status_code == 200:
                data = r.json()
                available_sections = data.get('results', data) if isinstance(data, dict) else data
        except Exception:
            pass

    # ── POST: inscribirse o retirar sección ───────────────────────────────────
    if request.method == 'POST':
        action = request.POST.get('action', 'enroll')

        if action == 'withdraw_section':
            section_id    = request.POST.get('section_id', '')
            enrollment_id = request.POST.get('enrollment_id', '')
            if not section_id or not enrollment_id:
                messages.error(request, 'Datos incompletos para el retiro.')
                return redirect('student_enroll')
            try:
                r = http_requests.post(
                    f'{_E}/api/enrollments/{enrollment_id}/withdraw/',
                    json={'section_id': int(section_id)}, timeout=5,
                )
                if r.status_code == 200:
                    messages.success(request, 'Sección retirada exitosamente.')
                else:
                    err = r.json().get('detail', 'Error al retirar la sección.')
                    messages.error(request, err)
            except Exception:
                messages.error(request, 'No se pudo conectar con el servicio de inscripciones.')
            return redirect('student_enroll')

        # Inscribirse en nuevas secciones
        try:
            section_ids = [int(s) for s in request.POST.getlist('section_ids')]
        except ValueError:
            messages.error(request, 'Selección de secciones inválida.')
            return redirect('student_enroll')

        if not section_ids:
            messages.error(request, 'Debes seleccionar al menos una sección.')
            return redirect('student_enroll')

        if not active_period:
            messages.error(request, 'No hay período académico activo.')
            return redirect('student_enroll')

        payload = {
            'student_id':  student['id'],
            'period_id':   active_period['id'],
            'section_ids': section_ids,
        }
        try:
            r = http_requests.post(f'{_E}/api/enrollments/enroll/', json=payload, timeout=6)
            if r.status_code == 201:
                total = len(r.json().get('details', []))
                messages.success(request, f'Inscripción realizada. {total} sección(es) registradas.')
            else:
                err = r.json().get('detail', 'Error al procesar la inscripción.')
                messages.error(request, err)
        except Exception:
            messages.error(request, 'No se pudo conectar con el servicio de inscripciones.')
        return redirect('student_enroll')

    # ── Agrupar secciones por UC para la UI ───────────────────────────────────
    sections_by_uc = {}
    for sec in available_sections:
        uc_id   = sec.get('curricular_unit_id', 0)
        uc_name = sec.get('uc_name', f'UC-{uc_id}')
        uc_code = sec.get('uc_code', '')
        key = (uc_id, uc_code, uc_name)
        sections_by_uc.setdefault(key, []).append(sec)

    total_credits = sum(
        d.get('uc_credits', 0)
        for d in (current_enrollment.get('details', []) if current_enrollment else [])
        if d.get('status') == 'active'
    )

    return render(request, 'student_enroll.html', {
        'student':              student,
        'active_period':        active_period,
        'current_enrollment':   current_enrollment,
        'enrolled_section_ids': enrolled_section_ids,
        'sections_by_uc':       sections_by_uc,
        'total_credits':        total_credits,
        'available_sections':   available_sections,
    })


# ─────────────────────────────────────────────
# Panel Staff — Módulo de Inscripciones
# ─────────────────────────────────────────────

ENROLLMENT_ALLOWED_ROLES = ('admin', 'control_estudios', 'secretaria')

_ENROLLMENT_STATUS_CHOICES = [
    ('enrolled',  'Inscrito'),
    ('withdrawn', 'Retirado'),
    ('completed', 'Completado'),
]


@login_required
def panel_enrollments(request):
    """
    Lista todas las inscripciones del período seleccionado (default: activo).
    Roles permitidos: admin, control_estudios, secretaria.
    """
    if not _admin_required(request):
        return redirect('home')
    if not (request.user.is_superuser or request.user.role in ENROLLMENT_ALLOWED_ROLES):
        messages.error(request, 'No tienes permiso para acceder al módulo de inscripciones.')
        return redirect('home')

    _E = ENROLLMENT_SERVICE_URL
    _C = COURSES_SERVICE_URL
    _S = STUDENTS_SERVICE_URL

    # Filtros
    period_f = request.GET.get('period', '').strip()
    status_f = request.GET.get('status', '').strip()
    career_f = request.GET.get('career', '').strip()
    q        = request.GET.get('q', '').strip()

    # Período activo
    active_period = None
    try:
        r = http_requests.get(f'{_C}/api/periods/active/', timeout=2)
        if r.status_code == 200:
            active_period = r.json()
    except Exception:
        pass

    periods = _get_json(f'{_C}/api/periods/')
    careers = _get_json(f'{_S}/api/careers/')
    period_id = period_f or (str(active_period['id']) if active_period else '')

    # Obtener inscripciones
    enrollments = []
    total_count = 0
    service_ok  = False

    if period_id:
        params = {'period_id': period_id}
        if status_f:
            params['status'] = status_f
        try:
            r = http_requests.get(f'{_E}/api/enrollments/', params=params, timeout=5)
            service_ok = True
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    total_count = data.get('count', 0)
                    enrollments = data.get('results', [])
                elif isinstance(data, list):
                    enrollments = data
                    total_count = len(data)
        except Exception as e:
            print(f"Error fetching enrollments: {e}")
            service_ok = False

    # Enriquecer con datos de estudiante / usuario
    if enrollments:
        student_ids  = list({e['student_id'] for e in enrollments})
        students_map = {}
        for sid in student_ids:
            try:
                r = http_requests.get(f'{_S}/api/students/{sid}/', timeout=2)
                if r.status_code == 200:
                    students_map[sid] = r.json()
            except Exception:
                pass

        user_ids  = [s.get('user_id') for s in students_map.values() if s.get('user_id')]
        users_map = {u.id: u for u in CustomUser.objects.filter(id__in=user_ids)}

        for e in enrollments:
            sid  = e['student_id']
            s    = students_map.get(sid, {})
            uid  = s.get('user_id')
            user = users_map.get(uid)
            e['_student'] = s
            if user:
                fn = user.first_name or ''
                ln = user.last_name  or ''
                e['_user'] = {
                    'full_name': f'{fn} {ln}'.strip() or user.email,
                    'email':     user.email,
                    'initials':  ((fn[0] + ln[0]).upper() if fn and ln
                                  else user.email[0].upper()),
                }
            else:
                e['_user'] = {
                    'full_name': f'Estudiante #{sid}',
                    'email':     '—',
                    'initials':  '?',
                }

        # Filtros en memoria
        if q:
            q_l = q.lower()
            enrollments = [
                e for e in enrollments
                if q_l in e['_user']['full_name'].lower()
                or q_l in (e.get('student_carnet') or '').lower()
                or q_l in e['_user']['email'].lower()
            ]
        if career_f:
            try:
                cid = int(career_f)
                enrollments = [
                    e for e in enrollments
                    if (e.get('_student', {}).get('career_id') == cid
                        or e.get('_student', {}).get('career') == cid)
                ]
            except ValueError:
                pass

    stats = {
        'total':     len(enrollments),
        'enrolled':  sum(1 for e in enrollments if e.get('status') == 'enrolled'),
        'withdrawn': sum(1 for e in enrollments if e.get('status') == 'withdrawn'),
        'completed': sum(1 for e in enrollments if e.get('status') == 'completed'),
    }

    return render(request, 'admin_enrollments.html', {
        'enrollments':    enrollments,
        'total_count':    total_count,
        'stats':          stats,
        'periods':        periods,
        'careers':        careers,
        'active_period':  active_period,
        'period_f':       period_id,
        'status_f':       status_f,
        'career_f':       career_f,
        'q':              q,
        'service_ok':     service_ok,
        'STATUS_CHOICES': _ENROLLMENT_STATUS_CHOICES,
    })


@login_required
def panel_enrollment_detail(request, enrollment_id):
    """
    Detalle de una inscripción: ver secciones inscritas, cambiar estado, retirar sección.
    """
    if not _admin_required(request):
        return redirect('home')
    if not (request.user.is_superuser or request.user.role in ENROLLMENT_ALLOWED_ROLES):
        messages.error(request, 'No tienes permiso.')
        return redirect('home')

    _E = ENROLLMENT_SERVICE_URL
    _S = STUDENTS_SERVICE_URL

    # Obtener inscripción
    enrollment = None
    try:
        r = http_requests.get(f'{_E}/api/enrollments/{enrollment_id}/', timeout=3)
        if r.status_code == 200:
            enrollment = r.json()
        else:
            messages.error(request, 'Inscripción no encontrada.')
            return redirect('panel_enrollments')
    except Exception:
        messages.error(request, 'No se pudo obtener la inscripción.')
        return redirect('panel_enrollments')

    # Datos del estudiante
    student  = None
    user_obj = None
    try:
        r = http_requests.get(f'{_S}/api/students/{enrollment["student_id"]}/', timeout=2)
        if r.status_code == 200:
            student = r.json()
            uid = student.get('user_id')
            if uid:
                try:
                    user_obj = CustomUser.objects.get(pk=uid)
                except CustomUser.DoesNotExist:
                    pass
    except Exception:
        pass

    # POST: cambiar estado de inscripción o retirar sección
    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'change_status':
            new_status = request.POST.get('status', '')
            valid_statuses = [s[0] for s in _ENROLLMENT_STATUS_CHOICES]
            if new_status not in valid_statuses:
                messages.error(request, 'Estado inválido.')
                return redirect('panel_enrollment_detail', enrollment_id=enrollment_id)
            try:
                r = http_requests.patch(
                    f'{_E}/api/enrollments/{enrollment_id}/',
                    json={'status': new_status}, timeout=4,
                )
                if r.status_code == 200:
                    messages.success(request, 'Estado de inscripción actualizado.')
                else:
                    messages.error(request, 'No se pudo actualizar el estado.')
            except Exception:
                messages.error(request, 'Error de conexión con el servicio.')

        elif action == 'withdraw_section':
            section_id = request.POST.get('section_id', '')
            try:
                r = http_requests.post(
                    f'{_E}/api/enrollments/{enrollment_id}/withdraw/',
                    json={'section_id': int(section_id)}, timeout=4,
                )
                if r.status_code == 200:
                    messages.success(request, 'Sección retirada exitosamente.')
                else:
                    err = r.json().get('detail', 'Error al retirar sección.')
                    messages.error(request, err)
            except Exception:
                messages.error(request, 'Error de conexión.')

        return redirect('panel_enrollment_detail', enrollment_id=enrollment_id)

    return render(request, 'admin_enrollment_detail.html', {
        'enrollment':     enrollment,
        'student':        student,
        'user_obj':       user_obj,
        'STATUS_CHOICES': _ENROLLMENT_STATUS_CHOICES,
    })



# ═══════════════════════════════════════════════════════
# API — Profesores (busqueda para asignacion en secciones)
# ═══════════════════════════════════════════════════════

class ProfessorsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Q
        qs = CustomUser.objects.filter(role='professor', is_active=True)
        q = request.query_params.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q)
            )
        data = [
            {'id': u.id, 'name': u.get_full_name(), 'email': u.email}
            for u in qs.order_by('last_name', 'first_name')[:25]
        ]
        return Response(data)

# ════════════════════════════════════════════════════════════════════
# Portal del Profesor — Dashboard
# ════════════════════════════════════════════════════════════════════

@login_required
def professor_dashboard(request):
    """
    Dashboard principal del profesor.
    Muestra sus secciones asignadas en el periodo activo.
    """
    u = request.user
    if u.role not in ('professor',) and not (u.is_superuser or u.role == 'admin'):
        return redirect('home')

    _C = COURSES_SERVICE_URL
    _E = ENROLLMENT_SERVICE_URL

    # Periodo activo
    active_period = None
    try:
        r = http_requests.get(f'{_C}/api/periods/active/', timeout=2)
        if r.status_code == 200:
            active_period = r.json()
    except Exception:
        pass

    # Secciones del profesor en el periodo activo
    sections = []
    if active_period:
        try:
            r = http_requests.get(f'{_C}/api/sections/', params={
                'professor': u.id,
                'period':    active_period['id'],
                'active':    'true',
            }, timeout=4)
            if r.status_code == 200:
                data = r.json()
                sections = data.get('results', data) if isinstance(data, dict) else data
        except Exception:
            pass

    return render(request, 'professor_dashboard.html', {
        'active_period': active_period,
        'sections':      sections,
    })


# ════════════════════════════════════════════════════════════════════
# Portal del Profesor — Carga de Notas por Seccion
# ════════════════════════════════════════════════════════════════════

@login_required
def professor_section_grades(request, section_id):
    """
    Vista de carga de notas parciales para una seccion.
    GET:  muestra lista de estudiantes con sus notas actuales.
    POST: actualiza (o crea) las calificaciones parciales.
    """
    u = request.user
    if u.role not in ('professor',) and not (u.is_superuser or u.role == 'admin'):
        return redirect('home')

    _C  = COURSES_SERVICE_URL
    _E  = ENROLLMENT_SERVICE_URL
    _G  = GRADES_SERVICE_URL
    _ST = STUDENTS_SERVICE_URL

    # Datos de la seccion
    section = None
    try:
        r = http_requests.get(f'{_C}/api/sections/{section_id}/', timeout=3)
        if r.status_code == 200:
            section = r.json()
    except Exception:
        pass

    if not section:
        messages.error(request, 'Seccion no encontrada.')
        return redirect('professor_dashboard')

    # Verificar que la seccion pertenece al profesor (o es admin)
    if not (u.is_superuser or u.role == 'admin'):
        if section.get('professor_user_id') != u.id:
            messages.error(request, 'No tienes acceso a esta seccion.')
            return redirect('professor_dashboard')

    # POST: guardar notas
    if request.method == 'POST':
        grade_ids   = request.POST.getlist('grade_id')
        student_ids = request.POST.getlist('student_id')
        partial1s   = request.POST.getlist('partial1')
        partial2s   = request.POST.getlist('partial2')
        partial3s   = request.POST.getlist('partial3')

        errors = []
        for i, sid in enumerate(student_ids):
            p1  = partial1s[i].strip()  if i < len(partial1s)  else ''
            p2  = partial2s[i].strip()  if i < len(partial2s)  else ''
            p3  = partial3s[i].strip()  if i < len(partial3s)  else ''
            gid = grade_ids[i].strip()  if i < len(grade_ids)  else ''

            payload = {}
            if p1 != '':
                payload['partial1'] = p1
            if p2 != '':
                payload['partial2'] = p2
            if p3 != '':
                payload['partial3'] = p3

            if not payload:
                continue

            try:
                if gid:
                    r = http_requests.patch(
                        f'{_G}/api/grades/{gid}/',
                        json=payload, timeout=4,
                    )
                    if not r.ok:
                        errors.append(f'Error actualizando nota (estudiante {sid}): {r.text[:80]}')
                else:
                    enroll_detail_id = request.POST.get(f'enrollment_detail_id_{sid}', '0')
                    stu_carnet       = request.POST.get(f'carnet_{sid}', '')
                    create_payload = {
                        'student_id':           int(sid),
                        'curricular_unit_id':   section.get('curricular_unit_id', 0),
                        'section_id':           int(section_id),
                        'period_id':            section.get('period'),
                        'enrollment_detail_id': int(enroll_detail_id) if enroll_detail_id else 0,
                        'student_carnet':       stu_carnet,
                        'uc_code':              section.get('uc_code', ''),
                        'uc_name':              section.get('uc_name', ''),
                        'uc_credits':           section.get('uc_credits', 0),
                        'period_name':          section.get('period_name', ''),
                        **payload,
                    }
                    r = http_requests.post(
                        f'{_G}/api/grades/',
                        json=create_payload, timeout=4,
                    )
                    if not r.ok:
                        errors.append(f'Error creando nota (estudiante {sid}): {r.text[:80]}')
            except Exception as exc:
                errors.append(f'Error de conexion: {exc}')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            messages.success(request, 'Notas guardadas exitosamente.')
        return redirect('professor_section_grades', section_id=section_id)

    # GET: construir tabla de estudiantes + notas

    # 1. Estudiantes inscritos
    enrolled_students = []
    try:
        r = http_requests.get(f'{_E}/api/enrollments/section/{section_id}/', timeout=4)
        if r.status_code == 200:
            enrolled_students = r.json().get('students', [])
    except Exception:
        pass

    # 2. Notas existentes indexadas por student_id
    existing_grades = {}
    try:
        r = http_requests.get(f'{_G}/api/grades/section/{section_id}/', timeout=4)
        if r.status_code == 200:
            for g in r.json().get('grades', []):
                existing_grades[g['student_id']] = g
    except Exception:
        pass

    # 3. Enriquecer con nombres (students_service + CustomUser local)
    student_ids_list = [s['student_id'] for s in enrolled_students]
    user_id_map = {}
    if student_ids_list:
        try:
            r = http_requests.get(f'{_ST}/api/students/', params={'page_size': 200}, timeout=4)
            if r.status_code == 200:
                raw = r.json()
                stu_list = raw.get('results', raw) if isinstance(raw, dict) else raw
                for s in stu_list:
                    if s['id'] in student_ids_list:
                        user_id_map[s['id']] = s.get('user_id')
        except Exception:
            pass

    user_ids = list(filter(None, user_id_map.values()))
    name_map = {}
    if user_ids:
        for cu in CustomUser.objects.filter(id__in=user_ids).values('id', 'first_name', 'last_name'):
            name_map[cu['id']] = f"{cu['first_name']} {cu['last_name']}".strip()

    rows = []
    for s in enrolled_students:
        sid   = s['student_id']
        uid   = user_id_map.get(sid)
        grade = existing_grades.get(sid, {})
        rows.append({
            'student_id':           sid,
            'student_carnet':       s['student_carnet'],
            'student_name':         name_map.get(uid, '') if uid else '',
            'enrollment_detail_id': s['enrollment_detail_id'],
            'grade_id':             grade.get('id', ''),
            'partial1':             grade.get('partial1', ''),
            'partial2':             grade.get('partial2', ''),
            'partial3':             grade.get('partial3', ''),
            'final_grade':          grade.get('final_grade', ''),
            'status':               grade.get('status', 'in_progress'),
            'status_display':       grade.get('status_display', 'En progreso'),
        })

    return render(request, 'professor_section_grades.html', {
        'section': section,
        'rows':    rows,
    })


# ─── Horario de Sección (Docente / Admin) ──────────────────────────────────

@login_required
def professor_section_schedule(request, section_id):
    """Vista FullCalendar para gestionar el horario de una sección."""
    u = request.user
    if u.role not in ('professor',) and not (u.is_superuser or u.role in ('admin', 'control_estudios')):
        return redirect('home')

    # Obtener datos de la sección (http_requests incluye Host: localhost automáticamente)
    try:
        resp = http_requests.get(
            f'{COURSES_SERVICE_URL}/api/sections/{section_id}/',
            timeout=5,
        )
        resp.raise_for_status()
        section = resp.json()
    except Exception:
        messages.error(request, 'No se pudo obtener la información de la sección.')
        return redirect('professor_dashboard')

    # Solo el profesor asignado puede ver (o admin/control_estudios)
    if u.role == 'professor' and section.get('professor_user_id') != u.id:
        return redirect('professor_dashboard')

    # Solo admin y control_estudios pueden modificar horarios
    can_edit = u.is_superuser or u.role in ('admin', 'control_estudios')

    return render(request, 'professor_section_schedule.html', {
        'section':    section,
        'section_id': section_id,
        'can_edit':   can_edit,
    })


# ─────────────────────────────────────────────────────────────
# Panel — Gestión de Horarios (SPA admin/control_estudios)
# ─────────────────────────────────────────────────────────────

@login_required
def panel_horarios(request):
    """
    SPA de gestión y asignación de franjas horarias.
    Acceso exclusivo para admin y control_estudios.
    Flujo: Especialidad → Período → UC tree → Sección → FullCalendar + conflictos.
    """
    u = request.user
    if not (u.is_superuser or u.role in ('admin', 'control_estudios')):
        messages.error(request, 'No tiene permiso para gestionar horarios.')
        return redirect('home')

    _C  = COURSES_SERVICE_URL
    _ST = STUDENTS_SERVICE_URL

    periods = _get_json(f'{_C}/api/periods/')
    careers = _get_json(f'{_ST}/api/careers/')

    import json as _json
    return render(request, 'schedule_management.html', {
        'periods_json': _json.dumps(periods  if isinstance(periods, list)  else []),
        'careers_json': _json.dumps(careers  if isinstance(careers, list)  else []),
    })


# ══════════════════════════════════════════════════════════════════════════════
# SPRINT 9 — PANEL DE HERRAMIENTAS DEL SISTEMA (solo superadmin)
# ══════════════════════════════════════════════════════════════════════════════

import subprocess
import uuid
import threading
import json as _tools_json

# Almacén en memoria para jobs (en producción usar Redis)
_TOOL_JOBS = {}  # { job_id: { status, lines, exit_code } }
_TOOL_JOBS_LOCK = threading.Lock()

# Directorio de skills (relativo al contenedor — montado desde zen-pascal)
_SKILLS_DIR = '/app/skills'

# Mapeo de nombre de herramienta → comando a ejecutar dentro del contenedor
_TOOLS = {
    'health-check': {
        'label': 'Health Check',
        'cmd': ['python', '-c',
            'import http.client\n'
            'svcs=[("auth_service","auth_service",8000,"/api/users/me/"),'
            '("students_service","students_service",8001,"/api/students/"),'
            '("courses_service","courses_service",8002,"/api/periods/"),'
            '("enrollment_service","enrollment_service",8003,"/api/enrollments/"),'
            '("grades_service","grades_service",8004,"/api/grades/"),'
            '("curriculum_service","curriculum_service",8005,"/api/curricular-units/")]\n'
            'print("\\n== BasePNew - Health Check ==")\n'
            'print("{:<25} {:<20} {}".format("SERVICE","HOST","STATUS"))\n'
            'print("-"*55)\n'
            'ok=0\n'
            'for n,h,p,path in svcs:\n'
            ' try:\n'
            '  c=http.client.HTTPConnection(h,p,timeout=3);c.request("GET",path);r=c.getresponse()\n'
            '  s="[OK] "+str(r.status);ok+=1\n'
            ' except Exception as e:\n'
            '  s="[DOWN] "+str(e)[:30]\n'
            ' print("{:<25} {:<20} {}".format(n,h+":"+str(p),s))\n'
            'print("\\nResultado: "+str(ok)+"/6 servicios disponibles")\n'
        ],
        'container': 'university_auth',
    },
    'validate-templates': {
        'label': 'Validar Templates Django',
        'cmd': ['python', f'{_SKILLS_DIR}/validate-templates.py'],
        'container': 'university_auth',
    },
    'quality-check': {
        'label': 'Quality Check',
        'cmd': ['python', f'{_SKILLS_DIR}/quality-check.py'],
        'container': 'university_auth',
    },
    'run-tests': {
        'label': 'Ejecutar Tests',
        'cmd': ['python', f'{_SKILLS_DIR}/run-tests.py'],
        'container': 'university_auth',
        'accepts_arg': True,
    },
    'check-conflicts': {
        'label': 'Verificar Conflictos de Horario',
        'cmd': ['python', f'{_SKILLS_DIR}/check-conflicts.py'],
        'container': 'university_auth',
    },
    'restart-service': {
        'label': 'Reiniciar Servicio',
        'cmd': ['docker', 'restart'],
        'is_docker_host': True,
        'accepts_arg': True,
    },
    'apply-migration': {
        'label': 'Aplicar Migración',
        'cmd': ['python', f'{_SKILLS_DIR}/apply-migration.py'],
        'container': 'university_auth',
        'accepts_arg': True,
    },
    'search-docs': {
        'label': 'Buscar en Documentación',
        'cmd': ['bash', f'{_SKILLS_DIR}/search-docs.sh'],
        'container': 'university_auth',
        'accepts_arg': True,
    },
    'ai-refactor': {
        'label': 'AI Refactor Suggester',
        'cmd': ['python', f'{_SKILLS_DIR}/ai-refactor.py'],
        'container': 'university_auth',
    },
    'generate-api-client': {
        'label': 'Generar API Client',
        'cmd': ['python', f'{_SKILLS_DIR}/generate-api-client.py'],
        'container': 'university_auth',
    },
    'update-knowledge-base': {
        'label': 'Actualizar Base de Conocimiento',
        'cmd': ['python', f'{_SKILLS_DIR}/update-knowledge-base.py'],
        'container': 'university_auth',
    },
    'sync-docs': {
        'label': 'Sincronizar Documentación',
        'cmd': ['python', f'{_SKILLS_DIR}/sync-docs.py'],
        'container': 'university_auth',
    },
}


def _run_tool_background(job_id, tool_key, arg=''):
    """Ejecuta el tool en un hilo de fondo y almacena el output."""
    tool = _TOOLS.get(tool_key)
    if not tool:
        with _TOOL_JOBS_LOCK:
            _TOOL_JOBS[job_id] = {'status': 'error', 'lines': [f'Tool desconocido: {tool_key}'], 'exit_code': 1}
        return

    with _TOOL_JOBS_LOCK:
        _TOOL_JOBS[job_id] = {'status': 'running', 'lines': [], 'exit_code': None}

    try:
        cmd = list(tool['cmd'])

        # Si el tool acepta argumento, agregarlo
        if tool.get('accepts_arg') and arg:
            cmd.append(arg)

        # Este código se ejecuta DENTRO del contenedor Django.
        # Si el tool está marcado como 'is_docker_host' (ej: restart-service),
        # no lo podemos ejecutar desde aquí — informar al usuario.
        if tool.get('is_docker_host'):
            with _TOOL_JOBS_LOCK:
                _TOOL_JOBS[job_id] = {
                    'status': 'done',
                    'lines': [
                        f'[WARN] La herramienta "{tool["label"]}" requiere acceso al host Docker.',
                        '[WARN] Esta operación debe ejecutarse desde la terminal del servidor.',
                        f'[INFO] Comando sugerido: {" ".join(cmd)}',
                    ],
                    'full_output': [
                        f'[WARN] La herramienta "{tool["label"]}" requiere acceso al host Docker.',
                        '[WARN] Esta operación debe ejecutarse desde la terminal del servidor.',
                        f'[INFO] Comando sugerido: {" ".join(cmd)}',
                    ],
                    'exit_code': 1,
                }
            return

        # Ejecutar directamente dentro de este contenedor (sin docker exec)
        final_cmd = cmd

        proc = subprocess.Popen(
            final_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        lines = []
        for line in proc.stdout:
            stripped = line.rstrip('\n')
            lines.append(stripped)
            with _TOOL_JOBS_LOCK:
                _TOOL_JOBS[job_id]['lines'] = list(lines)

        proc.wait()
        exit_code = proc.returncode

        with _TOOL_JOBS_LOCK:
            _TOOL_JOBS[job_id]['status'] = 'done'
            _TOOL_JOBS[job_id]['exit_code'] = exit_code
            _TOOL_JOBS[job_id]['full_output'] = lines

    except Exception as exc:
        with _TOOL_JOBS_LOCK:
            _TOOL_JOBS[job_id]['status'] = 'error'
            _TOOL_JOBS[job_id]['lines'] = [f'Error al ejecutar el proceso: {exc}']
            _TOOL_JOBS[job_id]['exit_code'] = -1


@login_required
def panel_tools(request):
    """
    Panel de Herramientas del Sistema.
    Solo accesible para superadmin (is_superuser).
    """
    if not request.user.is_superuser:
        messages.error(request, 'Acceso restringido a superadministradores.')
        return redirect('home')
    return render(request, 'admin_tools.html')


@login_required
def panel_tool_run(request):
    """
    Endpoint AJAX POST para lanzar un tool en background.
    Body JSON: { tool: str, arg: str }
    Respuesta: { job_id: str } o { error: str }
    Solo para superadmin.
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Sin permiso'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        body = _tools_json.loads(request.body)
        tool_key = body.get('tool', '').strip()
        arg = body.get('arg', '').strip()
    except Exception:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    if tool_key not in _TOOLS:
        return JsonResponse({'error': f'Herramienta no válida: {tool_key}'}, status=400)

    job_id = str(uuid.uuid4())
    t = threading.Thread(target=_run_tool_background, args=(job_id, tool_key, arg), daemon=True)
    t.start()

    return JsonResponse({'job_id': job_id})


@login_required
def panel_tool_status(request, job_id):
    """
    Endpoint AJAX GET para consultar el estado de un job en ejecución.
    Respuesta: { status, lines, full_output, exit_code }
    Solo para superadmin.
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Sin permiso'}, status=403)

    with _TOOL_JOBS_LOCK:
        job = _TOOL_JOBS.get(job_id)

    if not job:
        return JsonResponse({'status': 'not_found', 'lines': [], 'exit_code': None})

    return JsonResponse({
        'status':      job.get('status', 'unknown'),
        'lines':       job.get('lines', []),
        'full_output': job.get('full_output', job.get('lines', [])),
        'exit_code':   job.get('exit_code'),
    })

# ─────────────────────────────────────────────
# REST API — Constancias (Estudiantes y Admins)
# ─────────────────────────────────────────────

class CertificateRequestListCreateAPIView(generics.ListCreateAPIView):
    """
    Estudiantes: lista sus propias constancias o solicita una nueva.
    """
    serializer_class = CertificateRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return CertificateRequest.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdminCertificateRequestListAPIView(generics.ListAPIView):
    """
    Administrativos/Control de estudios: listar y filtrar constancias.
    """
    serializer_class = CertificateRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role not in ['admin', 'control_estudios', 'secretaria']:
            return CertificateRequest.objects.none()
        
        qs = CertificateRequest.objects.filter(**user.scope_filter_for('user')).select_related('user')
        
        status = self.request.query_params.get('status')
        cert_type = self.request.query_params.get('cert_type')
        if status:
            qs = qs.filter(status=status)
        if cert_type:
            qs = qs.filter(cert_type=cert_type)
            
        return qs


class AdminCertificateRequestDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Backend Admin / Personal: ver detalle o cambiar status de la constancia.
    """
    serializer_class = CertificateRequestSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'code'

    def get_queryset(self):
        user = self.request.user
        if user.role not in ['admin', 'control_estudios', 'secretaria']:
            return CertificateRequest.objects.none()
        return CertificateRequest.objects.filter(**user.scope_filter_for('user'))

    def perform_update(self, serializer):
        from django.utils import timezone
        
        instance = serializer.save()
        if instance.status != 'pending' and not instance.processed_by:
            instance.processed_by = self.request.user
            instance.processed_at = timezone.now()
            instance.save(update_fields=['processed_by', 'processed_at'])
