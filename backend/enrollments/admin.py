from django.contrib import admin
from .models import Enrollment, EnrollmentDetail


class EnrollmentDetailInline(admin.TabularInline):
    model          = EnrollmentDetail
    extra          = 0
    readonly_fields = ('enrolled_at', 'withdrawn_at')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display    = ('student_carnet', 'period_name', 'status', 'enrollment_date')
    list_filter     = ('status', 'period_name')
    search_fields   = ('student_carnet', 'student_id')
    inlines         = [EnrollmentDetailInline]
    readonly_fields = ('enrollment_date',)


@admin.register(EnrollmentDetail)
class EnrollmentDetailAdmin(admin.ModelAdmin):
    list_display    = ('enrollment', 'uc_code', 'uc_name', 'section_number', 'status')
    list_filter     = ('status',)
    search_fields   = ('uc_code', 'uc_name', 'section_number')
    readonly_fields = ('enrolled_at', 'withdrawn_at')
