from django.contrib import admin
from .models import CurricularUnit, CareerPlan, Prerequisite, CareerSede, CareerNucleo


class PrerequisiteInline(admin.TabularInline):
    model  = Prerequisite
    extra  = 1
    fk_name = 'career_plan_item'


@admin.register(CurricularUnit)
class CurricularUnitAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'component', 'uc_type', 'credits', 'teaching_hours', 'student_hours', 'is_active']
    list_filter   = ['component', 'uc_type', 'level', 'is_active']
    search_fields = ['name', 'code', 'area']
    ordering      = ['component', 'name']


@admin.register(CareerPlan)
class CareerPlanAdmin(admin.ModelAdmin):
    list_display  = ['career_id', 'academic_period', 'curricular_unit', 'order']
    list_filter   = ['career_id', 'academic_period']
    inlines       = [PrerequisiteInline]
    ordering      = ['career_id', 'academic_period', 'order']


@admin.register(CareerSede)
class CareerSedeAdmin(admin.ModelAdmin):
    list_display  = ['career_id', 'sede_id', 'is_active', 'assigned_at', 'assigned_by_id']
    list_filter   = ['is_active', 'sede_id']
    ordering      = ['career_id', 'sede_id']


@admin.register(CareerNucleo)
class CareerNucleoAdmin(admin.ModelAdmin):
    list_display  = ['career_id', 'nucleo_id', 'is_active', 'assigned_at', 'assigned_by_id']
    list_filter   = ['is_active', 'nucleo_id']
    ordering      = ['career_id', 'nucleo_id']
