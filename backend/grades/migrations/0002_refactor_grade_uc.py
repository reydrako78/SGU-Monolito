"""
Sprint 4 — Migración: Grade refactorizado.

Cambios:
  - course_id  → curricular_unit_id  (+ db_index)
  - course_code → uc_code  (max_length: 20 → 30)
  - course_name → uc_name  (max_length: 200 → 300)
  + uc_credits  (nuevo campo denormalizado)
  - period_name amplía max_length a 100
  - student_id, section_id, period_id reciben db_index=True
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0001_initial'),
    ]

    operations = [

        # ── 1. Renombrar course_id → curricular_unit_id ───────────
        migrations.RenameField(
            model_name='grade',
            old_name='course_id',
            new_name='curricular_unit_id',
        ),

        # ── 2. Renombrar course_code → uc_code ────────────────────
        migrations.RenameField(
            model_name='grade',
            old_name='course_code',
            new_name='uc_code',
        ),

        # ── 3. Renombrar course_name → uc_name ────────────────────
        migrations.RenameField(
            model_name='grade',
            old_name='course_name',
            new_name='uc_name',
        ),

        # ── 4. Ajustar curricular_unit_id: añadir db_index ────────
        migrations.AlterField(
            model_name='grade',
            name='curricular_unit_id',
            field=models.IntegerField(
                db_index=True,
                help_text='Referencia a CurricularUnit en curriculum_service',
                verbose_name='ID de Unidad Curricular',
            ),
        ),

        # ── 5. Ajustar uc_code: max_length 20 → 30 ────────────────
        migrations.AlterField(
            model_name='grade',
            name='uc_code',
            field=models.CharField(blank=True, max_length=30, verbose_name='Código UC'),
        ),

        # ── 6. Ajustar uc_name: max_length 200 → 300 ──────────────
        migrations.AlterField(
            model_name='grade',
            name='uc_name',
            field=models.CharField(blank=True, max_length=300, verbose_name='Nombre UC'),
        ),

        # ── 7. Agregar uc_credits ──────────────────────────────────
        migrations.AddField(
            model_name='grade',
            name='uc_credits',
            field=models.PositiveIntegerField(default=0, verbose_name='Créditos UC'),
        ),

        # ── 8. Ajustar period_name: max_length 50 → 100 ───────────
        migrations.AlterField(
            model_name='grade',
            name='period_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Período'),
        ),

        # ── 9. Añadir db_index a student_id, section_id, period_id ─
        migrations.AlterField(
            model_name='grade',
            name='student_id',
            field=models.IntegerField(db_index=True, verbose_name='ID de estudiante'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='section_id',
            field=models.IntegerField(db_index=True, verbose_name='ID de sección'),
        ),
        migrations.AlterField(
            model_name='grade',
            name='period_id',
            field=models.IntegerField(db_index=True, verbose_name='ID de período'),
        ),
    ]
