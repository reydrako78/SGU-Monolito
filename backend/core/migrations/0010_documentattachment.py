from django.db import migrations, models
import django.db.models.deletion
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_aspirant_convalidacion_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_type', models.CharField(
                    choices=[
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
                    ],
                    max_length=30,
                    verbose_name='Tipo de documento',
                )),
                ('file', models.FileField(upload_to=core.models.aspirant_doc_upload_path, verbose_name='Archivo')),
                ('original_filename', models.CharField(blank=True, max_length=255, verbose_name='Nombre original del archivo')),
                ('file_size', models.PositiveIntegerField(default=0, verbose_name='Tamaño (bytes)')),
                ('notes', models.CharField(blank=True, max_length=300, verbose_name='Observaciones')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Subido el')),
                ('aspirant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='documents',
                    to='core.aspirant',
                    verbose_name='Aspirante',
                )),
            ],
            options={
                'verbose_name': 'Documento del Expediente',
                'verbose_name_plural': 'Documentos del Expediente',
                'ordering': ['aspirant', 'doc_type'],
            },
        ),
    ]
