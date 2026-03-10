"""
Sprint 4 — Migración: elimina Course, refactoriza Section.

IMPORTANTE: El orden de operaciones es crítico.
  1. Limpiar unique_together viejo (referencia a 'course') ANTES de RemoveField.
  2. Luego RemoveField y agregar nuevos campos.
  3. Finalmente DeleteModel('Course').
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [

        # ── 1. Period: agregar period_type ────────────────────────────────
        migrations.AddField(
            model_name='period',
            name='period_type',
            field=models.CharField(
                choices=[
                    ('lapso_i',   'Lapso I'),
                    ('lapso_ii',  'Lapso II'),
                    ('intensivo', 'Intensivo de Verano'),
                ],
                default='lapso_i',
                max_length=20,
                verbose_name='Tipo de período',
            ),
        ),
        migrations.AlterField(
            model_name='period',
            name='name',
            field=models.CharField(
                help_text='Ej: Lapso I 2026-I',
                max_length=100,
                unique=True,
                verbose_name='Nombre del período',
            ),
        ),

        # ── 2. Limpiar unique_together ANTES de quitar 'course' ──────────
        migrations.AlterUniqueTogether(
            name='section',
            unique_together=set(),
        ),

        # ── 3. Limpiar ordering que depende de course__code ──────────────
        migrations.AlterModelOptions(
            name='section',
            options={
                'ordering': ['uc_code', 'section_number'],
                'verbose_name': 'Sección',
                'verbose_name_plural': 'Secciones',
            },
        ),

        # ── 4. Section: eliminar FK a Course ─────────────────────────────
        migrations.RemoveField(
            model_name='section',
            name='course',
        ),

        # ── 5. Section: agregar nuevos campos ────────────────────────────
        migrations.AddField(
            model_name='section',
            name='curricular_unit_id',
            field=models.IntegerField(
                db_index=True, default=0,
                help_text='Referencia a CurricularUnit en curriculum_service',
                verbose_name='ID de Unidad Curricular',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='section',
            name='career_id',
            field=models.IntegerField(
                db_index=True, default=0,
                help_text='Referencia a Career en students_service',
                verbose_name='ID de Carrera',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='section',
            name='sede_id',
            field=models.IntegerField(
                db_index=True, default=0,
                help_text='Referencia a Sede en auth_service',
                verbose_name='ID de Sede',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='section',
            name='nucleo_id',
            field=models.IntegerField(
                blank=True, db_index=True, null=True,
                help_text='Referencia a Nucleo en auth_service (null = nivel sede)',
                verbose_name='ID de Núcleo',
            ),
        ),
        migrations.AddField(
            model_name='section',
            name='professor_user_id',
            field=models.IntegerField(
                blank=True, null=True,
                help_text='Referencia a CustomUser en auth_service',
                verbose_name='ID de usuario del profesor',
            ),
        ),
        migrations.AddField(
            model_name='section',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Activa'),
        ),
        migrations.AddField(
            model_name='section',
            name='uc_code',
            field=models.CharField(blank=True, max_length=30, verbose_name='Código UC'),
        ),
        migrations.AddField(
            model_name='section',
            name='uc_name',
            field=models.CharField(blank=True, max_length=300, verbose_name='Nombre UC'),
        ),
        migrations.AddField(
            model_name='section',
            name='uc_credits',
            field=models.PositiveIntegerField(default=0, verbose_name='Créditos UC'),
        ),
        migrations.AddField(
            model_name='section',
            name='career_name',
            field=models.CharField(blank=True, max_length=300, verbose_name='Carrera'),
        ),
        migrations.AddField(
            model_name='section',
            name='sede_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Sede'),
        ),
        migrations.AddField(
            model_name='section',
            name='nucleo_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Núcleo'),
        ),
        migrations.AddField(
            model_name='section',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),

        # ── 6. Ajustar campos existentes ─────────────────────────────────
        migrations.AlterField(
            model_name='section',
            name='professor_name',
            field=models.CharField(
                blank=True, max_length=200,
                verbose_name='Nombre del profesor (denormalizado)',
            ),
        ),
        migrations.AlterField(
            model_name='section',
            name='schedule',
            field=models.CharField(
                blank=True, max_length=200,
                help_text='Ej: Lun-Mié 07:00–09:00',
                verbose_name='Horario',
            ),
        ),
        migrations.AlterField(
            model_name='section',
            name='classroom',
            field=models.CharField(blank=True, max_length=100, verbose_name='Aula'),
        ),
        migrations.AlterField(
            model_name='section',
            name='section_number',
            field=models.CharField(
                help_text='Ej: A, B, 01',
                max_length=10,
                verbose_name='Número / letra de sección',
            ),
        ),

        # ── 7. Nuevo unique_together ──────────────────────────────────────
        migrations.AlterUniqueTogether(
            name='section',
            unique_together={
                ('curricular_unit_id', 'career_id', 'period', 'sede_id', 'section_number'),
            },
        ),

        # ── 8. Ordering final ─────────────────────────────────────────────
        migrations.AlterModelOptions(
            name='section',
            options={
                'ordering': ['period', 'uc_code', 'section_number'],
                'verbose_name': 'Sección',
                'verbose_name_plural': 'Secciones',
            },
        ),

        # ── 9. Eliminar Course (ya sin dependencias de Section) ───────────
        migrations.DeleteModel(
            name='Course',
        ),
    ]
