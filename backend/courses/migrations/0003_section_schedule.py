from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_refactor_section_drop_course'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectionSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(
                    choices=[
                        ('MON', 'Lunes'), ('TUE', 'Martes'), ('WED', 'Miércoles'),
                        ('THU', 'Jueves'), ('FRI', 'Viernes'), ('SAT', 'Sábado'),
                    ],
                    max_length=3,
                )),
                ('start_time', models.TimeField(verbose_name='Hora inicio')),
                ('end_time', models.TimeField(verbose_name='Hora fin')),
                ('classroom', models.CharField(blank=True, max_length=100, verbose_name='Aula')),
                ('session_type', models.CharField(
                    choices=[
                        ('theory', 'Teórico'), ('practice', 'Práctico'),
                        ('lab', 'Laboratorio'), ('virtual', 'Virtual'), ('hybrid', 'Híbrido'),
                    ],
                    default='theory', max_length=10, verbose_name='Tipo de sesión',
                )),
                ('section', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='schedules', to='courses.section',
                )),
            ],
            options={
                'verbose_name': 'Horario de Sección',
                'verbose_name_plural': 'Horarios de Sección',
                'ordering': ['day', 'start_time'],
            },
        ),
    ]
