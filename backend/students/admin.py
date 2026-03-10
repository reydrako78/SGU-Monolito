from django.contrib import admin
from .models import Career, Student


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'faculty', 'duration_semesters', 'is_active')
    list_filter = ('is_active', 'faculty')
    search_fields = ('code', 'name', 'faculty')
    ordering = ('name',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('carnet', 'career', 'semester', 'status', 'enrollment_date', 'user_id')
    list_filter = ('status', 'career', 'semester')
    search_fields = ('carnet', 'national_id', 'phone')
    ordering = ('carnet',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Datos Académicos', {
            'fields': ('user_id', 'carnet', 'career', 'semester', 'status', 'enrollment_date')
        }),
        ('Datos Personales', {
            'fields': ('phone', 'address', 'birth_date', 'national_id')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
