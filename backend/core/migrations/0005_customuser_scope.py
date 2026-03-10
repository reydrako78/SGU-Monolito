from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_aspirant_career'),
    ]

    operations = [
        # ── Nuevos roles funcionales ──────────────────────────────
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin',            'Administrador'),
                    ('student',          'Estudiante'),
                    ('professor',        'Profesor'),
                    ('aspirant',         'Aspirante'),
                    ('control_estudios', 'Control de Estudios'),
                    ('docencia',         'Coordinación Docente'),
                    ('secretaria',       'Secretaría'),
                    ('otro',             'Otro / Personalizado'),
                ],
                default='student',
                max_length=20,
                verbose_name='Rol',
            ),
        ),

        # ── Campo: nivel organizacional ───────────────────────────
        migrations.AddField(
            model_name='customuser',
            name='scope_level',
            field=models.CharField(
                choices=[
                    ('global', 'Rectorado / Global'),
                    ('sede',   'Sede'),
                    ('nucleo', 'Núcleo'),
                ],
                default='global',
                max_length=10,
                verbose_name='Nivel organizacional',
                help_text='Define qué datos puede ver este usuario.',
            ),
        ),

        # ── Campo: sede asignada ──────────────────────────────────
        migrations.AddField(
            model_name='customuser',
            name='scope_sede',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='users',
                to='core.sede',
                verbose_name='Sede asignada',
            ),
        ),

        # ── Campo: núcleo asignado ────────────────────────────────
        migrations.AddField(
            model_name='customuser',
            name='scope_nucleo',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='users',
                to='core.nucleo',
                verbose_name='Núcleo asignado',
            ),
        ),
    ]
