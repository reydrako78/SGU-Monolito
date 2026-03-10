"""
Management command: ensure_superuser
Crea o actualiza el superusuario admin desde variables de entorno.
Uso en entrypoint.sh: python manage.py ensure_superuser
Variables de entorno: SUPERUSER_USERNAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Crea o resetea el superusuario admin desde variables de entorno'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('SUPERUSER_USERNAME', 'admin')
        email    = os.environ.get('SUPERUSER_EMAIL',    'admin@upel.edu.ve')
        password = os.environ.get('SUPERUSER_PASSWORD', 'Admin2026@UPEL')

        try:
            user = User.objects.filter(email=email).first()
            if not user:
                user, created = User.objects.get_or_create(username=username)
            
            user.email        = email
            user.is_staff     = True
            user.is_superuser = True
            user.role         = 'admin'
            user.set_password(password)
            user.save()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Setup superusuario omitido: {e}"))
            return

        self.stdout.write(self.style.SUCCESS(
            f'Procesado superusuario: {username} / {email}'
        ))
