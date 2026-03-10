from django.db import models


class Period(models.Model):
    PERIOD_TYPE_CHOICES = [
        ('lapso_i',   'Lapso I'),
        ('lapso_ii',  'Lapso II'),
        ('intensivo', 'Intensivo de Verano'),
    ]

    name        = models.CharField(
        max_length=100, unique=True, verbose_name='Nombre del período',
        help_text='Ej: Lapso I 2026-I',
    )
    period_type = models.CharField(
        max_length=20, choices=PERIOD_TYPE_CHOICES,
        default='lapso_i', verbose_name='Tipo de período',
    )
    start_date  = models.DateField(verbose_name='Fecha de inicio')
    end_date    = models.DateField(verbose_name='Fecha de fin')
    is_active   = models.BooleanField(default=False, verbose_name='Período activo')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Período académico'
        verbose_name_plural = 'Períodos académicos'
        ordering            = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Solo un período puede estar activo a la vez
        if self.is_active:
            Period.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Section(models.Model):
    """
    Sección = una Unidad Curricular ofertada por una sede/núcleo en un período.

    Referencias externas (cross-service — sin FK de base de datos):
      curricular_unit_id → curriculum_service.CurricularUnit
      career_id          → students_service.Career
      sede_id            → auth_service.Sede
      nucleo_id          → auth_service.Nucleo  (null = nivel sede)
      professor_user_id  → auth_service.CustomUser (null = sin asignar)
    """

    # ── ¿Qué se oferta? ───────────────────────────────────────────
    curricular_unit_id = models.IntegerField(
        db_index=True,
        verbose_name='ID de Unidad Curricular',
        help_text='Referencia a CurricularUnit en curriculum_service',
    )
    career_id = models.IntegerField(
        db_index=True,
        verbose_name='ID de Carrera',
        help_text='Referencia a Career en students_service',
    )

    # ── ¿Cuándo? ──────────────────────────────────────────────────
    period = models.ForeignKey(
        Period, on_delete=models.CASCADE,
        related_name='sections', verbose_name='Período académico',
    )

    # ── ¿Dónde? ───────────────────────────────────────────────────
    sede_id = models.IntegerField(
        db_index=True,
        verbose_name='ID de Sede',
        help_text='Referencia a Sede en auth_service',
    )
    nucleo_id = models.IntegerField(
        null=True, blank=True, db_index=True,
        verbose_name='ID de Núcleo',
        help_text='Referencia a Nucleo en auth_service (null = nivel sede)',
    )

    # ── Identificación de la sección ──────────────────────────────
    section_number = models.CharField(
        max_length=10,
        verbose_name='Número / letra de sección',
        help_text='Ej: A, B, 01',
    )

    # ── Docente ───────────────────────────────────────────────────
    professor_user_id = models.IntegerField(
        null=True, blank=True,
        verbose_name='ID de usuario del profesor',
        help_text='Referencia a CustomUser en auth_service',
    )
    professor_name = models.CharField(
        max_length=200, blank=True,
        verbose_name='Nombre del profesor (denormalizado)',
    )

    # ── Logística ─────────────────────────────────────────────────
    schedule   = models.CharField(
        max_length=200, blank=True,
        verbose_name='Horario', help_text='Ej: Lun-Mié 07:00–09:00',
    )
    classroom  = models.CharField(max_length=100, blank=True, verbose_name='Aula')
    max_students   = models.PositiveIntegerField(default=30, verbose_name='Cupo máximo')
    enrolled_count = models.PositiveIntegerField(default=0, verbose_name='Inscritos')
    is_active  = models.BooleanField(default=True, verbose_name='Activa')

    # ── Datos denormalizados ───────────────────────────────────────
    # Evitan llamadas cross-service en cada query de listado
    uc_code     = models.CharField(max_length=30,  blank=True, verbose_name='Código UC')
    uc_name     = models.CharField(max_length=300, blank=True, verbose_name='Nombre UC')
    uc_credits  = models.PositiveIntegerField(default=0, verbose_name='Créditos UC')
    career_name = models.CharField(max_length=300, blank=True, verbose_name='Carrera')
    sede_name   = models.CharField(max_length=200, blank=True, verbose_name='Sede')
    nucleo_name = models.CharField(max_length=200, blank=True, verbose_name='Núcleo')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Sección'
        verbose_name_plural = 'Secciones'
        ordering            = ['period', 'uc_code', 'section_number']
        unique_together     = (
            'curricular_unit_id', 'career_id',
            'period', 'sede_id', 'section_number',
        )

    def __str__(self):
        loc = self.nucleo_name or self.sede_name or f'Sede {self.sede_id}'
        code = self.uc_code or f'UC-{self.curricular_unit_id}'
        return f'{code} | Sec {self.section_number} | {self.period.name} | {loc}'

    @property
    def available_spots(self):
        return max(0, self.max_students - self.enrolled_count)

    @property
    def is_full(self):
        return self.enrolled_count >= self.max_students


class SectionSchedule(models.Model):
    """
    Franja horaria estructurada de una sección.
    Reemplaza el campo de texto libre Section.schedule.
    """

    DAY_CHOICES = [
        ('MON', 'Lunes'),
        ('TUE', 'Martes'),
        ('WED', 'Miércoles'),
        ('THU', 'Jueves'),
        ('FRI', 'Viernes'),
        ('SAT', 'Sábado'),
    ]
    SESSION_TYPE_CHOICES = [
        ('theory',   'Teórico'),
        ('practice', 'Práctico'),
        ('lab',      'Laboratorio'),
        ('virtual',  'Virtual'),
        ('hybrid',   'Híbrido'),
    ]
    # Color por tipo (FullCalendar eventColor)
    SESSION_COLOR = {
        'theory':   '#0891b2',
        'practice': '#7c3aed',
        'lab':      '#059669',
        'virtual':  '#d97706',
        'hybrid':   '#db2777',
    }

    section      = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='schedules',
    )
    day          = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time   = models.TimeField(verbose_name='Hora inicio')
    end_time     = models.TimeField(verbose_name='Hora fin')
    classroom    = models.CharField(max_length=100, blank=True, verbose_name='Aula')
    session_type = models.CharField(
        max_length=10, choices=SESSION_TYPE_CHOICES,
        default='theory', verbose_name='Tipo de sesión',
    )

    class Meta:
        verbose_name        = 'Horario de Sección'
        verbose_name_plural = 'Horarios de Sección'
        ordering            = ['day', 'start_time']

    def __str__(self):
        return (
            f'{self.section.uc_code or f"UC-{self.section.curricular_unit_id}"} '
            f'| {self.get_day_display()} {self.start_time.strftime("%H:%M")}'
            f'–{self.end_time.strftime("%H:%M")}'
        )

    @property
    def color(self):
        return self.SESSION_COLOR.get(self.session_type, '#6b7280')
