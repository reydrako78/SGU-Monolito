# Generated manually 2026-03-02 — Agrega campos de carrera deseada al modelo Aspirant

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_sede_alter_aspirant_national_id_nucleo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='aspirant',
            name='career_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID de carrera deseada'),
        ),
        migrations.AddField(
            model_name='aspirant',
            name='career_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Carrera deseada'),
        ),
    ]
