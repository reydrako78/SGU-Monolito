"""
Panel técnico (Django Admin) — Sistema Universitario
─────────────────────────────────────────────────────
UniversityAdminSite:
    AdminSite personalizado que restringe el acceso a:
      - Superusuarios (is_superuser=True)
      - Usuarios con can_access_django_admin=True

Accesible en: /system-admin/
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import (
    CustomUser, SystemSettings, Aspirant,
    Sede, Nucleo, SystemRole, RolePermission, Authority
)


# ─────────────────────────────────────────────────────────────────
# AdminSite personalizado — acceso por rol
# ─────────────────────────────────────────────────────────────────

class UniversityAdminSite(AdminSite):
    """
    Panel técnico del sistema.
    Solo permite acceso a superusuarios o usuarios con
    el permiso explícito 'can_access_django_admin'.
    """
    site_header = 'Sistema Universitario — Panel Técnico'
    site_title  = 'Panel Técnico'
    index_title = 'Administración Técnica del Sistema'

    def has_permission(self, request):
        """Reemplaza la verificación estándar (is_staff) por una basada en roles."""
        if not request.user.is_active:
            return False
        return (
            request.user.is_superuser
            or getattr(request.user, 'can_access_django_admin', False)
        )


# Instancia global — importada en urls.py
university_admin_site = UniversityAdminSite(name='university_admin')


# ─────────────────────────────────────────────────────────────────
# Usuarios
# ─────────────────────────────────────────────────────────────────

class CustomUserAdmin(UserAdmin):
    list_display  = ('code', 'username', 'email', 'full_name', 'role',
                     'can_access_django_admin', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_active', 'can_access_django_admin')
    search_fields = ('code', 'username', 'email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)
    readonly_fields = ('code',)

    fieldsets = UserAdmin.fieldsets + (
        ('Información Universitaria', {
            'fields': ('role', 'code'),
        }),
        ('Permisos del Panel Técnico', {
            'fields': ('can_access_django_admin',),
            'description': (
                '⚠️ Otorga acceso al panel técnico (/system-admin/). '
                'Solo para personal de TI de confianza.'
            ),
        }),
        ('Ámbito Organizacional', {
            'fields': ('scope_level', 'scope_sede', 'scope_nucleo'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'role'),
        }),
    )

    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = 'Nombre completo'


university_admin_site.register(CustomUser, CustomUserAdmin)


# ─────────────────────────────────────────────────────────────────
# Configuración del Sistema (Singleton)
# ─────────────────────────────────────────────────────────────────

class SystemSettingsAdmin(admin.ModelAdmin):
    list_display  = ('university_name', 'system_name', 'color_preview', 'updated_at')
    readonly_fields = ('updated_at', 'color_preview')

    fieldsets = (
        ('Identidad de la Universidad', {
            'fields': ('university_name', 'system_name', 'logo'),
        }),
        ('Colores del Sistema', {
            'fields': ('primary_color', 'secondary_color', 'color_preview'),
            'description': 'Formato hexadecimal. Ej: #1a237e',
        }),
        ('Auditoría', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )

    def color_preview(self, obj):
        return format_html(
            '<div style="display:flex;gap:8px;align-items:center;">'
            '<div style="width:32px;height:32px;background:{};border-radius:4px;border:1px solid #ccc;" title="Primario: {}"></div>'
            '<div style="width:32px;height:32px;background:{};border-radius:4px;border:1px solid #ccc;" title="Secundario: {}"></div>'
            '<span style="color:#666;font-size:12px;">Primario: {} &nbsp; Secundario: {}</span>'
            '</div>',
            obj.primary_color, obj.primary_color,
            obj.secondary_color, obj.secondary_color,
            obj.primary_color, obj.secondary_color,
        )
    color_preview.short_description = 'Vista previa'

    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        obj = SystemSettings.load()
        return HttpResponseRedirect(
            reverse('university_admin:core_systemsettings_change', args=[obj.pk])
        )


university_admin_site.register(SystemSettings, SystemSettingsAdmin)


# ─────────────────────────────────────────────────────────────────
# Aspirantes
# ─────────────────────────────────────────────────────────────────

class AspirantAdmin(admin.ModelAdmin):
    list_display  = ('code', 'full_name_display', 'national_id', 'email',
                     'sede', 'nucleo', 'admission_status', 'status', 'registered_at')
    list_filter   = ('admission_status', 'status', 'sede')
    search_fields = ('code', 'national_id', 'email', 'first_name', 'last_name')
    ordering      = ('-registered_at',)
    readonly_fields = ('code', 'national_id', 'registered_at', 'updated_at', 'user', 'reviewed_at')

    fieldsets = (
        ('Identificación', {
            'fields': ('code', 'national_id', 'status'),
        }),
        ('Datos Personales', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'birth_date', 'address'),
        }),
        ('Sede y Núcleo', {
            'fields': ('sede', 'nucleo'),
        }),
        ('Opciones de Carrera', {
            'fields': ('career_id', 'career_name', 'career_id_2', 'career_name_2', 'career_id_3', 'career_name_3'),
            'description': 'Carreras seleccionadas por el aspirante en orden de preferencia.',
        }),
        ('Proceso de Admisión', {
            'fields': ('admission_status', 'admitted_career_id', 'admitted_career_name',
                       'admitted_option', 'admission_notes', 'reviewed_by', 'reviewed_at'),
        }),
        ('Sistema', {
            'fields': ('user', 'registered_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def full_name_display(self, obj):
        return obj.get_full_name()
    full_name_display.short_description = 'Nombre completo'


university_admin_site.register(Aspirant, AspirantAdmin)


# ─────────────────────────────────────────────────────────────────
# Sedes y Núcleos
# ─────────────────────────────────────────────────────────────────

class NucleoInline(admin.TabularInline):
    model  = Nucleo
    extra  = 1
    fields = ('name', 'address', 'is_active')


class SedeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'city', 'is_active', 'nucleos_count')
    list_filter   = ('is_active',)
    search_fields = ('name', 'city')
    inlines       = [NucleoInline]

    def nucleos_count(self, obj):
        count = obj.nucleos.filter(is_active=True).count()
        return format_html('<span style="color:#1565c0;">{} núcleo(s)</span>', count)
    nucleos_count.short_description = 'Núcleos activos'


class NucleoAdmin(admin.ModelAdmin):
    list_display  = ('name', 'sede', 'is_active')
    list_filter   = ('is_active', 'sede')
    search_fields = ('name', 'sede__name')
    raw_id_fields = ('sede',)


class AuthorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'sede_display', 'is_active', 'order')
    list_filter = ('is_active', 'sede')
    search_fields = ('name', 'position')
    list_editable = ('order', 'is_active')

    def sede_display(self, obj):
        return obj.sede.name if obj.sede else 'Rectorado (Nacional)'
    sede_display.short_description = 'Sede Asignada'


university_admin_site.register(Sede,   SedeAdmin)
university_admin_site.register(Nucleo, NucleoAdmin)
university_admin_site.register(Authority, AuthorityAdmin)


# ─────────────────────────────────────────────────────────────────
# Roles y Permisos RBAC
# ─────────────────────────────────────────────────────────────────

class RolePermissionInline(admin.TabularInline):
    model   = RolePermission
    extra   = 0
    fields  = ('service', 'action', 'allowed')
    ordering = ('service', 'action')


class SystemRoleAdmin(admin.ModelAdmin):
    list_display  = ('name', 'description', 'is_active', 'permissions_summary', 'created_at')
    list_filter   = ('is_active',)
    search_fields = ('name', 'description')
    inlines       = [RolePermissionInline]
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Información del Rol', {
            'fields': ('name', 'description', 'is_active'),
        }),
        ('Auditoría', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def permissions_summary(self, obj):
        allowed = obj.permissions.filter(allowed=True).count()
        total   = obj.permissions.count()
        return format_html(
            '<span style="color:{};">{}/{} permisos activos</span>',
            '#2e7d32' if allowed > 0 else '#c62828',
            allowed, total,
        )
    permissions_summary.short_description = 'Permisos'


university_admin_site.register(SystemRole, SystemRoleAdmin)
