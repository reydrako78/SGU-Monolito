from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_aspirant_admission_fields'),
    ]

    operations = [
        # ── Tipo de admisión ─────────────────────────────────────────────────
        migrations.AddField(
            model_name='aspirant',
            name='admission_type',
            field=models.CharField(
                choices=[('ordinario', 'Admisión Ordinaria'), ('convalidacion', 'Convalidación de Estudios')],
                default='ordinario',
                max_length=20,
                verbose_name='Tipo de admisión',
            ),
        ),
        # ── Institución de procedencia ────────────────────────────────────────
        migrations.AddField(
            model_name='aspirant',
            name='prev_institution',
            field=models.CharField(blank=True, max_length=300, verbose_name='Institución de procedencia'),
        ),
        migrations.AddField(
            model_name='aspirant',
            name='prev_career',
            field=models.CharField(blank=True, max_length=300, verbose_name='Carrera/Programa cursado'),
        ),
        migrations.AddField(
            model_name='aspirant',
            name='prev_degree',
            field=models.CharField(blank=True, max_length=100, verbose_name='Título/Grado obtenido'),
        ),
        migrations.AddField(
            model_name='aspirant',
            name='prev_graduation_year',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Año de egreso/retiro'),
        ),
        # ── Modelo ConvalidacionItem ──────────────────────────────────────────
        migrations.CreateModel(
            name='ConvalidacionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origin_subject_name', models.CharField(max_length=300, verbose_name='Asignatura (institución de origen)')),
                ('origin_subject_code', models.CharField(blank=True, max_length=50, verbose_name='Código (origen)')),
                ('origin_credits', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True, verbose_name='Unidades crédito (origen)')),
                ('origin_hours', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Horas académicas (origen)')),
                ('origin_grade', models.CharField(blank=True, help_text='Tal como aparece en el record: 18/20, A, 4.0, etc.', max_length=20, verbose_name='Calificación obtenida')),
                ('origin_year', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Año en que cursó la asignatura')),
                ('upel_course_id', models.IntegerField(blank=True, null=True, verbose_name='ID UC UPEL')),
                ('upel_course_name', models.CharField(blank=True, max_length=300, verbose_name='Unidad Curricular UPEL')),
                ('upel_course_code', models.CharField(blank=True, max_length=50, verbose_name='Código UC UPEL')),
                ('upel_credits', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True, verbose_name='Unidades crédito UPEL')),
                ('status', models.CharField(
                    choices=[
                        ('solicitada', 'Solicitada'),
                        ('en_revision', 'En revisión — Comisión'),
                        ('prueba_requerida', 'Prueba de suficiencia requerida'),
                        ('convalidada', 'Convalidada ✓'),
                        ('no_convalidada', 'No convalidada ✗'),
                        ('convalidada_condicion', 'Convalidada con condición'),
                    ],
                    default='solicitada',
                    max_length=25,
                    verbose_name='Estado',
                )),
                ('committee_notes', models.TextField(blank=True, verbose_name='Observaciones de la Comisión de Convalidaciones')),
                ('evaluated_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de evaluación')),
                ('council_resolution', models.CharField(blank=True, help_text='Ej: CD-0045-2026', max_length=100, verbose_name='Nro. Resolución — Consejo Directivo')),
                ('council_resolution_date', models.DateField(blank=True, null=True, verbose_name='Fecha de Resolución CD')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('aspirant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='convalidacion_items', to='core.aspirant', verbose_name='Aspirante')),
                ('evaluator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='evaluated_convalidaciones', to=settings.AUTH_USER_MODEL, verbose_name='Evaluado por')),
            ],
            options={
                'verbose_name': 'Item de Convalidación',
                'verbose_name_plural': 'Items de Convalidación',
                'ordering': ['aspirant', 'origin_subject_name'],
            },
        ),
    ]
