from django.db import models


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('enrolled',  'Inscrito'),
        ('withdrawn', 'Retirado'),
        ('completed', 'Completado'),
    ]

    # Referencias externas
    student_id = models.IntegerField(verbose_name='ID de estudiante', db_index=True)
    period_id  = models.IntegerField(verbose_name='ID de período',    db_index=True)

    enrollment_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de inscripción')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='enrolled', verbose_name='Estado',
    )

    # Denormalizados para consultas rápidas
    student_carnet = models.CharField(max_length=20, blank=True, verbose_name='Carné del estudiante')
    period_name    = models.CharField(max_length=100, blank=True, verbose_name='Nombre del período')

    class Meta:
        verbose_name        = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        unique_together     = ('student_id', 'period_id')
        ordering            = ['-enrollment_date']

    def __str__(self):
        return f'Estudiante {self.student_carnet or self.student_id} — {self.period_name or self.period_id}'


class EnrollmentDetail(models.Model):
    STATUS_CHOICES = [
        ('active',    'Activo'),
        ('withdrawn', 'Retirado'),
    ]

    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE,
        related_name='details', verbose_name='Inscripción',
    )

    # Referencias externas (cross-service)
    section_id          = models.IntegerField(verbose_name='ID de sección',           db_index=True)
    curricular_unit_id  = models.IntegerField(verbose_name='ID de Unidad Curricular', db_index=True)

    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    enrolled_at  = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de retiro')

    # Denormalizados para consultas rápidas (datos de la sección al momento de inscripción)
    uc_code        = models.CharField(max_length=30,  blank=True, verbose_name='Código UC')
    uc_name        = models.CharField(max_length=300, blank=True, verbose_name='Nombre UC')
    uc_credits     = models.PositiveIntegerField(default=0, verbose_name='Créditos')
    section_number = models.CharField(max_length=10,  blank=True, verbose_name='Número de sección')
    career_name    = models.CharField(max_length=300, blank=True, verbose_name='Carrera')
    professor_name = models.CharField(max_length=200, blank=True, verbose_name='Profesor')

    class Meta:
        verbose_name        = 'Detalle de inscripción'
        verbose_name_plural = 'Detalles de inscripción'
        unique_together     = ('enrollment', 'section_id')

    def __str__(self):
        return f'{self.uc_code or f"UC-{self.curricular_unit_id}"} — Sección {self.section_number}'
