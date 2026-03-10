from django.db import models


class CurricularUnit(models.Model):
    """
    Unidad Curricular — componente atómico del plan de estudios.
    Se crea una sola vez (catálogo global) y se reutiliza en múltiples carreras.

    Componentes según diseño UPEL:
      CFPE – Formación Profesional Específico  (propio de cada carrera)
      CFD  – Formación Docente                 (compartida entre todas las carreras)
      CFC  – Formación Contextualizado         (compartida entre todas las carreras)
      ECU  – Eje Curricular                    (Investigación, TIC, Práctica Profesional)
    """
    COMPONENT_CHOICES = [
        ('CFPE', 'Formación Profesional Específico'),
        ('CFD',  'Formación Docente'),
        ('CFC',  'Formación Contextualizado'),
        ('ECU',  'Eje Curricular'),
    ]
    UC_TYPE_CHOICES = [
        ('UNCO',  'Obligatoria'),
        ('UNCLE', 'Libre Elección'),
    ]
    LEVEL_CHOICES = [
        ('FUND',  'Fundamentación'),
        ('INTEG', 'Integración'),
        ('PROF',  'Profundización'),
        ('',      'No especificado'),
    ]

    code           = models.CharField(max_length=20, unique=True, blank=True,
                                      help_text='Código institucional (ej: UC-CFD-001). Se auto-genera si queda vacío.')
    name           = models.CharField(max_length=300)
    component      = models.CharField(max_length=10, choices=COMPONENT_CHOICES)
    uc_type        = models.CharField(max_length=10, choices=UC_TYPE_CHOICES, default='UNCO',
                                      verbose_name='Tipo')
    level          = models.CharField(max_length=10, choices=LEVEL_CHOICES, blank=True,
                                      verbose_name='Nivel')
    area           = models.CharField(max_length=200, blank=True,
                                      help_text='Área temática (ej: Formación Ciudadana)')
    credits        = models.PositiveIntegerField(default=4, verbose_name='Créditos (CA)')
    teaching_hours = models.PositiveIntegerField(default=4, verbose_name='Horas Docente (HAD)')
    student_hours  = models.PositiveIntegerField(default=8, verbose_name='Horas Estudiante (HLE)')
    is_exit_req    = models.BooleanField(default=False,
                                         verbose_name='Requisito de Egreso (AE/SC)')
    description    = models.TextField(blank=True, verbose_name='Descripción / Fundamentación')
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['component', 'name']
        verbose_name = 'Unidad Curricular'
        verbose_name_plural = 'Unidades Curriculares'

    def __str__(self):
        return f'[{self.component}] {self.name}'

    def save(self, *args, **kwargs):
        # Auto-generate code if empty
        if not self.code:
            prefix = self.component
            last = CurricularUnit.objects.filter(
                code__startswith=prefix + '-'
            ).order_by('-id').first()
            if last and last.code:
                try:
                    num = int(last.code.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    num = 1
            else:
                num = 1
            self.code = f'{prefix}-{num:03d}'
        super().save(*args, **kwargs)

    @property
    def total_hours(self):
        return self.teaching_hours + self.student_hours

    @property
    def component_color(self):
        """Bootstrap color class for UI badges."""
        return {
            'CFPE': 'primary',
            'CFD':  'warning',
            'CFC':  'success',
            'ECU':  'info',
        }.get(self.component, 'secondary')


class CareerPlan(models.Model):
    """
    Ubica una Unidad Curricular dentro del plan de estudios de una carrera,
    en un período académico específico (1..8).
    career_id referencia la Carrera en students_service (cross-service, no FK).
    """
    career_id       = models.IntegerField(
        db_index=True,
        help_text='ID de la Carrera en students_service'
    )
    curricular_unit = models.ForeignKey(
        CurricularUnit,
        on_delete=models.CASCADE,
        related_name='career_plans',
        verbose_name='Unidad Curricular'
    )
    academic_period = models.PositiveIntegerField(
        help_text='Período académico (1=PA I … 8=PA VIII)'
    )
    order           = models.PositiveIntegerField(
        default=0,
        help_text='Orden dentro del período para la presentación visual'
    )

    class Meta:
        unique_together = ('career_id', 'curricular_unit', 'academic_period')
        ordering        = ['career_id', 'academic_period', 'order', 'curricular_unit__name']
        verbose_name        = 'Ítem del Plan Curricular'
        verbose_name_plural = 'Plan Curricular'

    def __str__(self):
        return f'Carrera {self.career_id} | PA{self.academic_period} | {self.curricular_unit.name}'


class Prerequisite(models.Model):
    """
    Prelación: una UC del plan de estudios requiere haber cursado previamente otra UC,
    dentro del contexto de la misma carrera.
    """
    career_plan_item = models.ForeignKey(
        CareerPlan,
        on_delete=models.CASCADE,
        related_name='prerequisites',
        verbose_name='Ítem del plan que tiene la prelación'
    )
    required_unit    = models.ForeignKey(
        CurricularUnit,
        on_delete=models.CASCADE,
        related_name='is_prerequisite_for',
        verbose_name='UC requerida (prelación)'
    )

    class Meta:
        unique_together     = ('career_plan_item', 'required_unit')
        verbose_name        = 'Prelación'
        verbose_name_plural = 'Prelaciones'

    def __str__(self):
        return f'{self.required_unit.name} → {self.career_plan_item}'


class CareerSede(models.Model):
    """
    Asignación de una Carrera a una Sede (operación exclusiva del nivel global).
    career_id y sede_id son referencias externas a students_service y auth_service respectivamente.
    """
    career_id      = models.IntegerField(db_index=True, help_text='ID Carrera (students_service)')
    sede_id        = models.IntegerField(db_index=True, help_text='ID Sede (auth_service)')
    is_active      = models.BooleanField(default=True)
    assigned_at    = models.DateTimeField(auto_now_add=True)
    assigned_by_id = models.IntegerField(
        null=True, blank=True,
        help_text='ID del usuario global que realizó la asignación (auth_service)'
    )

    class Meta:
        unique_together     = ('career_id', 'sede_id')
        ordering            = ['career_id', 'sede_id']
        verbose_name        = 'Carrera en Sede'
        verbose_name_plural = 'Carreras por Sede'

    def __str__(self):
        return f'Carrera {self.career_id} → Sede {self.sede_id}'


class CareerNucleo(models.Model):
    """
    Asignación de una Carrera a un Núcleo (operación exclusiva del nivel global).
    """
    career_id      = models.IntegerField(db_index=True, help_text='ID Carrera (students_service)')
    nucleo_id      = models.IntegerField(db_index=True, help_text='ID Núcleo (auth_service)')
    is_active      = models.BooleanField(default=True)
    assigned_at    = models.DateTimeField(auto_now_add=True)
    assigned_by_id = models.IntegerField(
        null=True, blank=True,
        help_text='ID del usuario global que realizó la asignación (auth_service)'
    )

    class Meta:
        unique_together     = ('career_id', 'nucleo_id')
        ordering            = ['career_id', 'nucleo_id']
        verbose_name        = 'Carrera en Núcleo'
        verbose_name_plural = 'Carreras por Núcleo'

    def __str__(self):
        return f'Carrera {self.career_id} → Núcleo {self.nucleo_id}'
