from django.contrib import admin
from .models import Period, Section


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display  = ('name', 'period_type', 'start_date', 'end_date', 'is_active')
    list_filter   = ('is_active', 'period_type')
    ordering      = ('-start_date',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display   = ('uc_code', 'uc_name', 'section_number', 'period',
                      'sede_name', 'nucleo_name', 'professor_name',
                      'enrolled_count', 'max_students', 'is_active')
    list_filter    = ('period', 'is_active', 'career_id')
    search_fields  = ('uc_code', 'uc_name', 'professor_name', 'section_number',
                      'sede_name', 'career_name')
    ordering       = ('period', 'uc_code', 'section_number')
    readonly_fields = ('enrolled_count', 'created_at', 'updated_at')
    fieldsets = (
        ('Unidad Curricular y Carrera', {
            'fields': ('curricular_unit_id', 'uc_code', 'uc_name', 'uc_credits',
                       'career_id', 'career_name'),
        }),
        ('Ubicación', {
            'fields': ('period', 'sede_id', 'sede_name', 'nucleo_id', 'nucleo_name'),
        }),
        ('Sección', {
            'fields': ('section_number', 'professor_user_id', 'professor_name',
                       'schedule', 'classroom', 'max_students', 'enrolled_count',
                       'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
