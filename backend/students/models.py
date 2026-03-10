from django.db import models
from datetime import datetime
import random
import string


class Career(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='Código')
    name = models.CharField(max_length=200, verbose_name='Nombre de la carrera')
    faculty = models.CharField(max_length=200, verbose_name='Facultad')
    department = models.CharField(max_length=200, blank=True, verbose_name='Departamento')
    duration_semesters = models.PositiveIntegerField(default=10, verbose_name='Duración (semestres)')
    description = models.TextField(blank=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'
        ordering = ['name']

    def __str__(self):
        return f'{self.code} - {self.name}'


def generate_carnet():
    """Genera un código de carné único: YY-P-SEQ (Ej: 261-001)"""
    year_short = str(datetime.now().year)[2:]
    period = "1" if datetime.now().month < 6 else "2"
    random_str = ''.join(random.choices(string.digits, k=3))
    return f"{year_short}{period}-{random_str}"


class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('graduated', 'Egresado'),
        ('suspended', 'Suspendido'),
        ('withdrawn', 'Retirado'),
    ]

    from django.conf import settings

    # Referencia al usuario local (Monolito)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile', verbose_name='Usuario')

    carnet = models.CharField(max_length=20, unique=True, verbose_name='Carné')
    career = models.ForeignKey(Career, on_delete=models.PROTECT, verbose_name='Carrera')
    semester = models.PositiveIntegerField(default=1, verbose_name='Semestre actual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Estado')
    enrollment_date = models.DateField(verbose_name='Fecha de ingreso')

    # Datos personales adicionales
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    address = models.TextField(blank=True, verbose_name='Dirección')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Fecha de nacimiento')
    national_id = models.CharField(max_length=20, blank=True, verbose_name='DPI/Cédula')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.carnet:
            while True:
                new_carnet = generate_carnet()
                if not Student.objects.filter(carnet=new_carnet).exists():
                    self.carnet = new_carnet
                    break
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        ordering = ['carnet']

    def __str__(self):
        return f'{self.carnet} - Semestre {self.semester}'
