"""
Sprint 4 — Migración: EnrollmentDetail refactorizado.

Cambios:
  - course_id  → curricular_unit_id
  - course_code → uc_code
  - course_name → uc_name
  + uc_credits (nuevo campo)
  + career_name (nuevo campo denormalizado)
  + professor_name (nuevo campo denormalizado)
  - period_name en Enrollment amplía a max_length=100
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollments', '0001_initial'),
    ]

    operations = [

        # ── 1. Enrollment.period_name: ampliar max_length ────────────────
        migrations.AlterField(
            model_name='enrollment',
            name='period_name',
            field=models.CharField(blank=True, max_length=100,
                                   verbose_name='Nombre del período'),
        ),

        # ── 2. EnrollmentDetail: eliminar campos viejos ──────────────────
        migrations.RemoveField(model_name='enrollmentdetail', name='course_id'),
        migrations.RemoveField(model_name='enrollmentdetail', name='course_code'),
        migrations.RemoveField(model_name='enrollmentdetail', name='course_name'),

        # ── 3. EnrollmentDetail: agregar nuevos campos ───────────────────
        migrations.AddField(
            model_name='enrollmentdetail',
            name='curricular_unit_id',
            field=models.IntegerField(
                db_index=True, default=0,
                verbose_name='ID de Unidad Curricular',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='enrollmentdetail',
            name='uc_code',
            field=models.CharField(blank=True, max_length=30, verbose_name='Código UC'),
        ),
        migrations.AddField(
            model_name='enrollmentdetail',
            name='uc_name',
            field=models.CharField(blank=True, max_length=300, verbose_name='Nombre UC'),
        ),
        migrations.AddField(
            model_name='enrollmentdetail',
            name='uc_credits',
            field=models.PositiveIntegerField(default=0, verbose_name='Créditos'),
        ),
        migrations.AddField(
            model_name='enrollmentdetail',
            name='career_name',
            field=models.CharField(blank=True, max_length=300, verbose_name='Carrera'),
        ),
        migrations.AddField(
            model_name='enrollmentdetail',
            name='professor_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Profesor'),
        ),

        # ── 4. EnrollmentDetail: db_index en section_id ─────────────────
        migrations.AlterField(
            model_name='enrollmentdetail',
            name='section_id',
            field=models.IntegerField(db_index=True, verbose_name='ID de sección'),
        ),
    ]
