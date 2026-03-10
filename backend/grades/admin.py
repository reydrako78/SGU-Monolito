from django.contrib import admin
from .models import Grade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = (
        'student_carnet', 'uc_code', 'uc_name', 'period_name',
        'partial1', 'partial2', 'partial3', 'final_grade', 'status'
    )
    list_filter = ('status', 'period_name')
    search_fields = ('student_carnet', 'uc_code', 'uc_name')
    ordering = ('-period_id', 'student_carnet')
    readonly_fields = ('final_grade', 'status', 'created_at', 'updated_at')

    fieldsets = (
        ('Identificación', {
            'fields': (
                'student_id', 'student_carnet',
                'curricular_unit_id', 'uc_code', 'uc_name', 'uc_credits',
                'section_id', 'period_id', 'period_name',
                'enrollment_detail_id',
            )
        }),
        ('Calificaciones', {
            'fields': ('partial1', 'partial2', 'partial3', 'final_grade', 'status')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
