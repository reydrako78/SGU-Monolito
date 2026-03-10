from django.db import models
from decimal import Decimal, ROUND_HALF_UP


class Grade(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'En progreso'),
        ('passed', 'Aprobado'),
        ('failed', 'Reprobado'),
        ('incomplete', 'Incompleto'),
        ('withdrawn', 'Retirado'),
    ]

    # Referencias externas (IDs de otros servicios)
    student_id           = models.IntegerField(verbose_name='ID de estudiante', db_index=True)
    curricular_unit_id   = models.IntegerField(
        verbose_name='ID de Unidad Curricular', db_index=True,
        help_text='Referencia a CurricularUnit en curriculum_service',
    )
    section_id           = models.IntegerField(verbose_name='ID de sección', db_index=True)
    period_id            = models.IntegerField(verbose_name='ID de período', db_index=True)
    enrollment_detail_id = models.IntegerField(verbose_name='ID de detalle de inscripción')

    # Datos denormalizados
    student_carnet = models.CharField(max_length=20, blank=True, verbose_name='Carné')
    uc_code        = models.CharField(max_length=30, blank=True, verbose_name='Código UC')
    uc_name        = models.CharField(max_length=300, blank=True, verbose_name='Nombre UC')
    uc_credits     = models.PositiveIntegerField(default=0, verbose_name='Créditos UC')
    period_name    = models.CharField(max_length=100, blank=True, verbose_name='Período')

    # Calificaciones parciales (escala 0-100)
    partial1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Parcial 1')
    partial2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Parcial 2')
    partial3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Parcial 3')
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Nota final')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress', verbose_name='Estado')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        unique_together = ('student_id', 'section_id', 'period_id')
        ordering = ['-period_id', 'student_carnet']

    def __str__(self):
        return f'{self.student_carnet} - {self.uc_code} ({self.period_name})'

    def calculate_final_grade(self):
        """Calcula el promedio de los parciales ingresados."""
        partials = [p for p in [self.partial1, self.partial2, self.partial3] if p is not None]
        if not partials:
            return None
        average = sum(partials) / len(partials)
        return float(Decimal(str(average)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    def update_status(self):
        """Actualiza el estado basado en la nota final calculada."""
        final = self.calculate_final_grade()
        if final is None:
            self.status = 'in_progress'
        elif final >= Decimal('61'):
            self.status = 'passed'
        else:
            self.status = 'failed'
        self.final_grade = final

    def save(self, *args, **kwargs):
        if self.status not in ('withdrawn', 'incomplete'):
            self.update_status()
        super().save(*args, **kwargs)
