import random
import string
from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


def _generate_code(prefix, model_class, field='code'):
    """Genera un código único no-secuencial: PREFIX-YYYY-XXXXXX"""
    year = datetime.now().year
    chars = string.ascii_uppercase + string.digits
    while True:
        suffix = ''.join(random.choices(chars, k=6))
        code = f"{prefix}-{year}-{suffix}"
        if not model_class.objects.filter(**{field: code}).exists():
            return code


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        # ── Roles académicos ──────────────────────
        ('admin',             'Administrador'),
        ('student',           'Estudiante'),
        ('professor',         'Profesor'),
        ('aspirant',          'Aspirante'),
        # ── Roles funcionales del personal ────────
        ('control_estudios',  'Control de Estudios'),
        ('docencia',          'Coordinación Docente'),
        ('secretaria',        'Secretaría'),
        ('otro',              'Otro / Personalizado'),
    ]

    # ── Ámbito organizacional ─────────────────────────────────────
    SCOPE_CHOICES = [
        ('global', 'Rectorado / Global'),
        ('sede',   'Sede'),
        ('nucleo', 'Núcleo'),
    ]

    code = models.CharField(
        max_length=20, unique=True, editable=False,
        null=True, blank=True, verbose_name='Código de usuario',
    )
    first_name = models.CharField(max_length=100, verbose_name='Nombre')
    last_name  = models.CharField(max_length=100, verbose_name='Apellido')
    email      = models.EmailField(max_length=254, unique=True, verbose_name='Correo electrónico')
    role       = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='student', verbose_name='Rol',
    )

    # ── Acceso al panel técnico (Django Admin) ────────────────────
    can_access_django_admin = models.BooleanField(
        default=False,
        verbose_name='Acceso al panel técnico',
        help_text=(
            'Otorga acceso al panel técnico en /system-admin/. '
            'Solo debe asignarse a personal técnico de TI. '
            'Los superusuarios siempre tienen acceso independientemente de este campo.'
        ),
    )

    # ── Scope / jerarquía organizacional ─────────────────────────
    scope_level = models.CharField(
        max_length=10, choices=SCOPE_CHOICES, default='global',
        verbose_name='Nivel organizacional',
        help_text='Define qué datos puede ver este usuario: global=todo, sede=su sede, núcleo=solo su núcleo.',
    )
    scope_sede = models.ForeignKey(
        'Sede', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='users', verbose_name='Sede asignada',
        help_text='Obligatorio cuando el nivel es "Sede" o "Núcleo".',
    )
    scope_nucleo = models.ForeignKey(
        'Nucleo', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='users', verbose_name='Núcleo asignado',
        help_text='Obligatorio cuando el nivel es "Núcleo".',
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = _generate_code('USR', CustomUser)
        # Sincronizar is_staff automáticamente:
        # Los superusuarios siempre conservan is_staff=True (convención Django).
        # Para los demás, is_staff refleja can_access_django_admin.
        if not self.is_superuser:
            self.is_staff = self.can_access_django_admin
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.get_full_name()} [{self.code}]'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.username

    # ── Scope helpers ─────────────────────────────────────────────

    @property
    def scope_display(self):
        """Descripción legible del ámbito organizacional del usuario."""
        if self.scope_level == 'global':
            return 'Rectorado / Global'
        if self.scope_level == 'sede' and self.scope_sede_id:
            return f'Sede: {self.scope_sede.name}'
        if self.scope_level == 'nucleo' and self.scope_nucleo_id:
            return f'Núcleo: {self.scope_nucleo.name}'
        return self.get_scope_level_display()

    @property
    def scope_icon(self):
        """Bootstrap-icon apropiado para el ámbito."""
        return {
            'global': 'bi-globe2',
            'sede':   'bi-building',
            'nucleo': 'bi-diagram-3',
        }.get(self.scope_level, 'bi-question-circle')

    def get_visible_sedes_qs(self):
        """QuerySet de Sedes que este usuario puede ver."""
        from .models import Sede  # evitar import circular en top-level
        if self.scope_level == 'global':
            return Sede.objects.all()
        if self.scope_level == 'sede' and self.scope_sede_id:
            return Sede.objects.filter(pk=self.scope_sede_id)
        if self.scope_level == 'nucleo' and self.scope_nucleo_id:
            return Sede.objects.filter(pk=self.scope_nucleo.sede_id)
        return Sede.objects.none()

    def get_visible_nucleos_qs(self):
        """QuerySet de Núcleos que este usuario puede ver."""
        from .models import Nucleo  # evitar import circular
        if self.scope_level == 'global':
            return Nucleo.objects.all()
        if self.scope_level == 'sede' and self.scope_sede_id:
            return Nucleo.objects.filter(sede_id=self.scope_sede_id)
        if self.scope_level == 'nucleo' and self.scope_nucleo_id:
            return Nucleo.objects.filter(pk=self.scope_nucleo_id)
        return Nucleo.objects.none()

    def scope_filter_for(self, resource: str) -> dict:
        """
        Retorna un dict de kwargs para filtrar QuerySets por ámbito.
        resource = 'aspirant' → filtra por sede/nucleo del aspirante
        resource = 'user'     → filtra por scope_sede/scope_nucleo del usuario
        """
        if self.scope_level == 'global':
            return {}
        if resource == 'aspirant':
            if self.scope_level == 'sede':
                return {'sede_id': self.scope_sede_id}
            if self.scope_level == 'nucleo':
                return {'nucleo_id': self.scope_nucleo_id}
        if resource == 'user':
            if self.scope_level == 'sede':
                return {'scope_sede_id': self.scope_sede_id}
            if self.scope_level == 'nucleo':
                return {'scope_nucleo_id': self.scope_nucleo_id}
        return {'pk__in': []}  # sin acceso


class SystemSettings(models.Model):
    """Configuración global del sistema — patrón singleton (solo pk=1)."""
    system_name = models.CharField(max_length=200, default='Sistema Universitario', verbose_name='Nombre del sistema')
    university_name = models.CharField(max_length=200, default='Mi Universidad', verbose_name='Nombre de la universidad')
    primary_color = models.CharField(max_length=7, default='#1a237e', verbose_name='Color primario (hex)')
    secondary_color = models.CharField(max_length=7, default='#283593', verbose_name='Color secundario (hex)')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, verbose_name='Logo de la universidad')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuración del Sistema'

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # No se puede eliminar

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f'Configuración: {self.university_name}'


class Sede(models.Model):
    """Sede (campus principal o regional) de la universidad."""
    name = models.CharField(max_length=200, verbose_name='Nombre de la sede')
    sigla = models.CharField(max_length=20, blank=True, verbose_name='Sigla', help_text="Ej: IPB, IPM, Rectorado")
    city = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
    address = models.TextField(blank=True, verbose_name='Dirección')
    is_active = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'
        ordering = ['name']

    def __str__(self):
        return self.name


class Nucleo(models.Model):
    """Núcleo académico que pertenece a una Sede."""
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='nucleos', verbose_name='Sede')
    name = models.CharField(max_length=200, verbose_name='Nombre del núcleo')
    address = models.TextField(blank=True, verbose_name='Dirección')
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Núcleo'
        verbose_name_plural = 'Núcleos'
        ordering = ['sede__name', 'name']

    def __str__(self):
        return f'{self.name} — {self.sede.name}'


class Authority(models.Model):
    """Autoridades de la Universidad (Rector, Directores, Secretarios) para emitir constancias."""
    name = models.CharField(max_length=200, verbose_name='Nombre completo', help_text="Ej: Dra. María García")
    position = models.CharField(max_length=200, verbose_name='Cargo', help_text="Ej: Rector, Vicerrector Académico, Secretario")
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    sede = models.ForeignKey(
        Sede, null=True, blank=True, on_delete=models.SET_NULL, related_name='authorities', 
        verbose_name='Sede', help_text="Dejar en blanco si es autoridad de Rectorado (nacional)"
    )
    order = models.IntegerField(default=0, verbose_name='Orden', help_text="Orden de aparición en documentos")

    class Meta:
        verbose_name = 'Autoridad'
        verbose_name_plural = 'Autoridades'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.position}: {self.name} ({self.sede.name if self.sede else 'Rectorado'})"


class Aspirant(models.Model):
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
    ]

    # ── Tipo de admisión ──────────────────────────────────────────
    ADMISSION_TYPE_CHOICES = [
        ('ordinario',        'Admisión Ordinaria'),
        ('convalidacion',    'Convalidación de Estudios'),
        ('traslado_interno', 'Traslado Interno'),
        ('traslado_externo', 'Traslado Externo'),
        ('reingreso',        'Reingreso'),
    ]

    code = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Código de aspirante')
    first_name = models.CharField(max_length=100, verbose_name='Nombre')
    last_name = models.CharField(max_length=100, verbose_name='Apellido')
    national_id = models.CharField(max_length=30, unique=True, null=True, blank=True, verbose_name='Cédula / Documento de identidad')
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Fecha de nacimiento')
    address = models.TextField(blank=True, verbose_name='Dirección')

    sede = models.ForeignKey(
        Sede, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='aspirants',
        verbose_name='Sede'
    )
    nucleo = models.ForeignKey(
        Nucleo, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='aspirants',
        verbose_name='Núcleo'
    )

    user = models.OneToOneField(
        CustomUser, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='aspirant_profile',
        verbose_name='Usuario del sistema'
    )

    # ── Opciones de carrera (1ª, 2ª y 3ª) ────────────────────────
    career_id   = models.IntegerField(null=True, blank=True, verbose_name='ID 1ª carrera deseada')
    career_name = models.CharField(max_length=200, blank=True, verbose_name='1ª Carrera deseada')
    career_id_2   = models.IntegerField(null=True, blank=True, verbose_name='ID 2ª carrera deseada')
    career_name_2 = models.CharField(max_length=200, blank=True, verbose_name='2ª Carrera deseada')
    career_id_3   = models.IntegerField(null=True, blank=True, verbose_name='ID 3ª carrera deseada')
    career_name_3 = models.CharField(max_length=200, blank=True, verbose_name='3ª Carrera deseada')

    # ── Tipo de admisión ──────────────────────────────────────────
    admission_type = models.CharField(
        max_length=20, choices=ADMISSION_TYPE_CHOICES, default='ordinario',
        verbose_name='Tipo de admisión',
    )

    # ── Datos de institución de procedencia (convalidación / traslado externo) ─
    prev_institution     = models.CharField(max_length=300, blank=True, verbose_name='Institución de procedencia')
    prev_career          = models.CharField(max_length=300, blank=True, verbose_name='Carrera/Programa cursado')
    prev_degree          = models.CharField(max_length=100, blank=True, verbose_name='Título/Grado obtenido')
    prev_graduation_year = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name='Año de egreso/retiro'
    )

    # ── Datos de traslado interno / externo / reingreso ───────────
    origin_carnet = models.CharField(
        max_length=30, blank=True,
        verbose_name='Carnet de origen',
        help_text='Carnet en la sede/institución de procedencia (traslado) o carnet anterior (reingreso).',
    )
    origin_sede = models.ForeignKey(
        'Sede', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='aspirants_traslado',
        verbose_name='Sede de origen (traslado interno)',
    )
    last_semester_completed = models.PositiveSmallIntegerField(
        null=True, blank=True,
        verbose_name='Último semestre aprobado',
        help_text='Semestre en el que quedó al momento del traslado o retiro.',
    )
    reinstatement_reason = models.TextField(
        blank=True,
        verbose_name='Motivo del reingreso',
        help_text='Explica brevemente el motivo por el que dejó de estudiar y por qué desea reingresar.',
    )

    # ── Proceso de admisión ───────────────────────────────────────
    ADMISSION_STATUS_CHOICES = [
        ('pending',    'Pendiente'),
        ('in_review',  'En revisión'),
        ('approved',   'Admitido'),
        ('rejected',   'No admitido'),
        ('waitlisted', 'En lista de espera'),
        ('accepted',   'Aceptado por el Aspirante'),
        ('declined',   'Rechazado por el Aspirante'),
    ]
    admission_status = models.CharField(
        max_length=20, choices=ADMISSION_STATUS_CHOICES, default='pending',
        verbose_name='Estado de admisión',
    )
    admitted_career_id   = models.IntegerField(null=True, blank=True, verbose_name='ID carrera admitida')
    admitted_career_name = models.CharField(max_length=200, blank=True, verbose_name='Carrera admitida')
    admitted_option      = models.PositiveSmallIntegerField(
        null=True, blank=True,
        verbose_name='Opción admitida',
        help_text='1=primera opción, 2=segunda opción, 3=tercera opción seleccionada por el aspirante.',
    )
    admission_notes = models.TextField(blank=True, verbose_name='Observaciones de admisión')
    reviewed_by     = models.ForeignKey(
        'CustomUser', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='reviewed_aspirants', verbose_name='Revisado por',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de revisión')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Estado')
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Aspirante'
        verbose_name_plural = 'Aspirantes'
        ordering = ['-registered_at']

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = _generate_code('ASP', Aspirant)
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def __str__(self):
        return f'{self.get_full_name()} [{self.code}]'


# ─────────────────────────────────────────────
# Convalidación de Estudios (UPEL)
# ─────────────────────────────────────────────

class ConvalidacionItem(models.Model):
    """
    Solicitud de convalidación de una asignatura individual.
    Un aspirante de tipo 'convalidacion' puede tener múltiples items,
    uno por cada asignatura que desea convalidar.

    Flujo UPEL real:
      solicitada → en_revision → (convalidada | no_convalidada | prueba_requerida)
    El Consejo Directivo emite la resolución final con número y fecha.
    """

    ITEM_STATUS_CHOICES = [
        ('solicitada',           'Solicitada'),
        ('en_revision',          'En revisión — Comisión'),
        ('prueba_requerida',     'Prueba de suficiencia requerida'),
        ('convalidada',          'Convalidada ✓'),
        ('no_convalidada',       'No convalidada ✗'),
        ('convalidada_condicion','Convalidada con condición'),
    ]

    aspirant = models.ForeignKey(
        Aspirant, on_delete=models.CASCADE,
        related_name='convalidacion_items',
        verbose_name='Aspirante',
    )

    # ── Asignatura en institución de origen ───────────────────────
    origin_subject_name = models.CharField(
        max_length=300, verbose_name='Asignatura (institución de origen)'
    )
    origin_subject_code = models.CharField(
        max_length=50, blank=True, verbose_name='Código (origen)'
    )
    origin_credits = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        verbose_name='Unidades crédito (origen)'
    )
    origin_hours = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name='Horas académicas (origen)'
    )
    origin_grade = models.CharField(
        max_length=20, blank=True,
        verbose_name='Calificación obtenida',
        help_text='Tal como aparece en el record: 18/20, A, 4.0, etc.',
    )
    origin_year = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name='Año en que cursó la asignatura'
    )

    # ── Unidad Curricular UPEL correspondiente ────────────────────
    upel_course_id   = models.IntegerField(null=True, blank=True, verbose_name='ID UC UPEL')
    upel_course_name = models.CharField(max_length=300, blank=True, verbose_name='Unidad Curricular UPEL')
    upel_course_code = models.CharField(max_length=50,  blank=True, verbose_name='Código UC UPEL')
    upel_credits     = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        verbose_name='Unidades crédito UPEL'
    )

    # ── Dictamen de la Comisión ───────────────────────────────────
    status = models.CharField(
        max_length=25, choices=ITEM_STATUS_CHOICES, default='solicitada',
        verbose_name='Estado',
    )
    committee_notes = models.TextField(
        blank=True, verbose_name='Observaciones de la Comisión de Convalidaciones'
    )
    evaluator = models.ForeignKey(
        'CustomUser', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='evaluated_convalidaciones',
        verbose_name='Evaluado por',
    )
    evaluated_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de evaluación')

    # ── Resolución del Consejo Directivo ──────────────────────────
    council_resolution      = models.CharField(
        max_length=100, blank=True,
        verbose_name='Nro. Resolución — Consejo Directivo',
        help_text='Ej: CD-0045-2026',
    )
    council_resolution_date = models.DateField(
        null=True, blank=True, verbose_name='Fecha de Resolución CD'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Item de Convalidación'
        verbose_name_plural = 'Items de Convalidación'
        ordering            = ['aspirant', 'origin_subject_name']

    def __str__(self):
        return (
            f'{self.aspirant.get_full_name()} — '
            f'{self.origin_subject_name} → {self.upel_course_name or "Sin asignar"}'
            f' [{self.get_status_display()}]'
        )


# ─────────────────────────────────────────────
# Documentos del Expediente (Aspirante)
# ─────────────────────────────────────────────

def aspirant_doc_upload_path(instance, filename):
    """Genera path: aspirant_docs/<año>/<código_aspirante>/<filename>"""
    import os
    code = instance.aspirant.code if instance.aspirant_id else 'unknown'
    ext  = os.path.splitext(filename)[1].lower()
    safe_name = f"{instance.doc_type}{ext}"
    from django.utils import timezone
    year = timezone.now().year
    return f"aspirant_docs/{year}/{code}/{safe_name}"


class DocumentAttachment(models.Model):
    DOC_TYPE_CHOICES = [
        ('cedula',           'Cédula de Identidad'),
        ('titulo',           'Título Universitario'),
        ('notas_cert',       'Notas Certificadas / Récord Académico'),
        ('foto',             'Fotografía tipo carnet'),
        ('partida',          'Partida de Nacimiento'),
        ('cv',               'Currículum Vitae'),
        ('carta_motivos',    'Carta de Exposición de Motivos'),
        ('buena_conducta',   'Carta / Declaración de Buena Conducta'),
        ('recomendacion',    'Carta de Recomendación'),
        ('constancia_trab',  'Constancia de Trabajo'),
        ('record_prev',      'Récord Académico (institución de origen)'),
        ('titulo_prev',      'Título de institución de origen'),
        ('comprobante_pago', 'Comprobante de Pago de Arancel'),
        ('otro',             'Otro Documento'),
    ]

    aspirant    = models.ForeignKey(
        Aspirant, on_delete=models.CASCADE,
        related_name='documents', verbose_name='Aspirante',
    )
    doc_type    = models.CharField(
        max_length=30, choices=DOC_TYPE_CHOICES,
        verbose_name='Tipo de documento',
    )
    file        = models.FileField(
        upload_to=aspirant_doc_upload_path,
        verbose_name='Archivo',
    )
    original_filename = models.CharField(
        max_length=255, blank=True,
        verbose_name='Nombre original del archivo',
    )
    file_size   = models.PositiveIntegerField(
        default=0, verbose_name='Tamaño (bytes)',
    )
    notes       = models.CharField(
        max_length=300, blank=True,
        verbose_name='Observaciones',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Subido el')

    class Meta:
        verbose_name        = 'Documento del Expediente'
        verbose_name_plural = 'Documentos del Expediente'
        ordering            = ['aspirant', 'doc_type']

    def __str__(self):
        return f'{self.aspirant.get_full_name()} — {self.get_doc_type_display()}'

    @property
    def file_size_display(self):
        size = self.file_size
        if size < 1024:
            return f'{size} B'
        elif size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        return f'{size / (1024*1024):.1f} MB'

    @property
    def is_image(self):
        name = self.original_filename.lower()
        return any(name.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp'))

    @property
    def is_pdf(self):
        return self.original_filename.lower().endswith('.pdf')


# ─────────────────────────────────────────────
# RBAC: Roles y Permisos
# ─────────────────────────────────────────────

SERVICE_CHOICES = [
    ('auth', 'Autenticación / Usuarios'),
    ('students', 'Estudiantes'),
    ('courses', 'Cursos'),
    ('enrollments', 'Inscripciones'),
    ('grades', 'Calificaciones'),
    ('settings', 'Configuración del Sistema'),
]

ACTION_CHOICES = [
    ('view', 'Ver'),
    ('create', 'Crear'),
    ('edit', 'Editar'),
    ('delete', 'Eliminar'),
]


class SystemRole(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre del rol')
    description = models.TextField(blank=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Rol del Sistema'
        verbose_name_plural = 'Roles del Sistema'
        ordering = ['name']

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(SystemRole, on_delete=models.CASCADE, related_name='permissions', verbose_name='Rol')
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, verbose_name='Servicio')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name='Acción')
    allowed = models.BooleanField(default=True, verbose_name='Permitido')

    class Meta:
        verbose_name = 'Permiso de Rol'
        verbose_name_plural = 'Permisos de Roles'
        unique_together = ('role', 'service', 'action')

    def __str__(self):
        status = '✓' if self.allowed else '✗'
        return f'{self.role.name} | {self.get_service_display()} | {self.get_action_display()} [{status}]'


# ─────────────────────────────────────────────
# Solicitud de Constancias (Portal del Estudiante)
# ─────────────────────────────────────────────

class CertificateRequest(models.Model):
    """
    Solicitud de constancia o certificación académica emitida por Control
    de Estudios o Secretaría. El estudiante la hace desde el portal; el
    personal la procesa desde el panel de administración.

    Flujo: pending → processing → ready → delivered
    """

    CERT_TYPE_CHOICES = [
        ('constancia_estudios',  'Constancia de Estudios'),
        ('record_notas',         'Récord Académico (constancia de notas)'),
        ('constancia_egresado',  'Constancia de Egresado'),
        ('buena_conducta',       'Constancia de Buena Conducta'),
        ('carga_academica',      'Constancia de Carga Académica'),
        ('otro',                 'Otro tipo de constancia'),
    ]

    PURPOSE_CHOICES = [
        ('beca',        'Solicitud de beca'),
        ('empleo',      'Trámites de empleo / empleador'),
        ('pasaporte',   'Trámites de pasaporte / visado'),
        ('banco',       'Trámites bancarios'),
        ('postgrado',   'Admisión a postgrado'),
        ('legal',       'Trámites legales / judiciales'),
        ('personal',    'Uso personal'),
        ('otro',        'Otro propósito'),
    ]

    STATUS_CHOICES = [
        ('pending',    'Pendiente de revisión'),
        ('processing', 'En proceso'),
        ('ready',      'Lista para retirar'),
        ('delivered',  'Entregada'),
        ('rejected',   'Rechazada'),
    ]

    code = models.CharField(
        max_length=20, unique=True, editable=False,
        verbose_name='Código de solicitud',
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='certificate_requests',
        verbose_name='Estudiante',
    )
    # Datos del estudiante (denormalizados para no depender del microservicio)
    student_carnet  = models.CharField(max_length=30, blank=True, verbose_name='Carnet')
    student_career  = models.CharField(max_length=200, blank=True, verbose_name='Carrera')
    student_semester = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Semestre')

    cert_type = models.CharField(
        max_length=30, choices=CERT_TYPE_CHOICES,
        verbose_name='Tipo de constancia',
    )
    purpose = models.CharField(
        max_length=30, choices=PURPOSE_CHOICES,
        verbose_name='Propósito',
    )
    copies = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Número de copias',
        help_text='Cuántas copias físicas necesita.',
    )
    period_ref = models.CharField(
        max_length=100, blank=True,
        verbose_name='Período de referencia',
        help_text='Ej: "Lapso I 2025" o dejar vacío para el período actual.',
    )
    student_notes = models.TextField(
        blank=True,
        verbose_name='Observaciones del estudiante',
        help_text='Indicaciones adicionales para Control de Estudios.',
    )

    # ── Procesamiento ──────────────────────────────────────────────
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending',
        verbose_name='Estado',
    )
    staff_notes = models.TextField(
        blank=True,
        verbose_name='Notas del personal',
        help_text='Observaciones internas — el estudiante puede verlas.',
    )
    processed_by = models.ForeignKey(
        CustomUser, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='processed_certificates',
        verbose_name='Procesado por',
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de proceso')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de solicitud')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Solicitud de Constancia'
        verbose_name_plural = 'Solicitudes de Constancias'
        ordering            = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = _generate_code('CERT', CertificateRequest)
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f'{self.get_cert_type_display()} — '
            f'{self.user.get_full_name()} [{self.code}]'
        )

    @property
    def status_color(self):
        return {
            'pending':    '#856404',
            'processing': '#0a6782',
            'ready':      '#155724',
            'delivered':  '#41464b',
            'rejected':   '#842029',
        }.get(self.status, '#343a40')

    @property
    def status_bg(self):
        return {
            'pending':    '#fff3cd',
            'processing': '#cff4fc',
            'ready':      '#d1e7dd',
            'delivered':  '#e2e3e5',
            'rejected':   '#f8d7da',
        }.get(self.status, '#e9ecef')


# ─────────────────────────────────────────────
# Señales
# ─────────────────────────────────────────────

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=CustomUser)
def auto_create_aspirant_profile(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil Aspirant cuando se crea un CustomUser
    con role='aspirant'. Cubre usuarios creados manualmente (Django Admin,
    panel custom) y no interfiere con el flujo OAuth que ya crea el perfil
    en aspirant_complete_profile.
    """
    if not created or instance.role != 'aspirant':
        return
    if not instance.email:
        return
    try:
        Aspirant.objects.get_or_create(
            user=instance,
            defaults={
                'email':      instance.email,
                'first_name': instance.first_name or '',
                'last_name':  instance.last_name or '',
            },
        )
    except Exception:
        # Si email ya existe en otro Aspirant, no crear duplicado
        pass
