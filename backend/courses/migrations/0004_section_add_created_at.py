"""
Adds the missing 'created_at' column to courses_section.
The 'updated_at' column already exists in the DB (from migration 0002).
"""
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_section_schedule'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
