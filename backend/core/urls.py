from django.urls import path
from . import views

urlpatterns = [
    # ─── HTML views ───────────────────────────
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),

    # Aspirantes (HTML)
    path('aspirant/complete-profile/', views.aspirant_complete_profile, name='aspirant_complete_profile'),
    path('aspirant/dashboard/',        views.aspirant_dashboard,        name='aspirant_dashboard'),
    path('aspirant/documentos/subir/', views.aspirant_upload_document,  name='aspirant_upload_document'),
    path('aspirant/documentos/<int:doc_id>/eliminar/', views.aspirant_delete_document, name='aspirant_delete_document'),

    # Portal del Estudiante (HTML)
    path('student/dashboard/',    views.student_dashboard,    name='student_dashboard'),
    path('student/constancias/',  views.student_certificates, name='student_certificates'),
    path('student/inscripcion/',  views.student_enroll,       name='student_enroll'),

    # Portal del Profesor (HTML)
    path('professor/dashboard/', views.professor_dashboard, name='professor_dashboard'),
    path('professor/secciones/<int:section_id>/notas/',    views.professor_section_grades,    name='professor_section_grades'),
    path('professor/secciones/<int:section_id>/horario/', views.professor_section_schedule,  name='professor_section_schedule'),

    # ─── Panel de Administración (HTML) ───────
    path('panel/usuarios/',                       views.panel_users,        name='panel_users'),
    path('panel/usuarios/nuevo/',                 views.panel_user_create,  name='panel_user_create'),
    path('panel/usuarios/<int:user_id>/edit/',    views.panel_user_edit,    name='panel_user_edit'),
    path('panel/aspirantes/',                  views.panel_aspirants,     name='panel_aspirants'),
    path('panel/aspirantes/<int:aspirant_id>/edit/', views.panel_aspirant_edit, name='panel_aspirant_edit'),
    path('panel/estudiantes/',               views.panel_students,      name='panel_students'),
    path('panel/configuracion/', views.panel_settings,   name='panel_settings'),
    path('panel/sedes/',         views.panel_sedes,      name='panel_sedes'),
    path('panel/roles/',         views.panel_roles,      name='panel_roles'),

    # ─── Panel — Admisión ─────────────────────
    path('panel/admision/',              views.panel_admision,        name='panel_admision'),
    path('panel/admision/<str:code>/',   views.panel_admision_detail, name='panel_admision_detail'),

    # ─── Panel — Convalidación ────────────────
    path('panel/convalidacion/',              views.panel_convalidacion,        name='panel_convalidacion'),
    path('panel/convalidacion/<str:code>/',   views.panel_convalidacion_detail, name='panel_convalidacion_detail'),

    # ─── Panel — Constancias ──────────────────
    path('panel/constancias/',             views.panel_certificates,        name='panel_certificates'),
    path('panel/constancias/<str:code>/',  views.panel_certificate_detail,  name='panel_certificate_detail'),
    path('panel/constancias/<str:code>/pdf/', views.certificate_pdf,  name='panel_certificate_pdf'),

    # ─── Panel — Oferta Académica ─────────────
    path('panel/periodos/',   views.panel_periods,   name='panel_periods'),
    path('panel/secciones/',  views.panel_sections,  name='panel_sections'),
    path('panel/horarios/',   views.panel_horarios,  name='panel_horarios'),

    # ─── Panel — Inscripciones ────────────────
    path('panel/inscripciones/',              views.panel_enrollments,        name='panel_enrollments'),
    path('panel/inscripciones/<int:enrollment_id>/', views.panel_enrollment_detail, name='panel_enrollment_detail'),

    # ─── Panel — Gestión Curricular ───────────
    path('panel/carreras/',                        views.panel_careers,            name='panel_careers'),
    path('panel/unidades-curriculares/',           views.panel_curricular_units,   name='panel_curricular_units'),
    path('panel/plan-curricular/<int:career_id>/', views.panel_career_plan,        name='panel_career_plan'),
    path('panel/asignaciones/',                    views.panel_career_assignments,  name='panel_career_assignments'),

    # API REST — Sedes y Núcleos
    path('api/sedes/', views.SedeListAPIView.as_view(), name='api_sedes'),
    path('api/sedes/<int:pk>/', views.SedeDetailAPIView.as_view(), name='api_sede_detail'),
    path('api/nucleos/', views.NucleoListAPIView.as_view(), name='api_nucleos'),
    path('api/nucleos/<int:pk>/', views.NucleoDetailAPIView.as_view(), name='api_nucleo_detail'),
    path('api/sedes/<int:sede_id>/nucleos/', views.nucleos_by_sede, name='api_nucleos_by_sede'),
    path('api/authorities/', views.AuthorityListCreateAPIView.as_view(), name='api_authorities'),
    path('api/authorities/<int:pk>/', views.AuthorityDetailAPIView.as_view(), name='api_authority_detail'),

    # API AJAX — Profesores (búsqueda para asignación en secciones)
    path('api/professors/', views.ProfessorsAPIView.as_view(), name='api_professors'),

    # ─── REST API — Usuarios ──────────────────
    path('api/users/', views.UserListCreateAPIView.as_view(), name='api_users'),
    path('api/users/<int:pk>/', views.UserDetailAPIView.as_view(), name='api_user_detail'),
    path('api/users/me/', views.CurrentUserAPIView.as_view(), name='api_current_user'),
    path('api/validate/', views.ValidateTokenAPIView.as_view(), name='api_validate_token'),

    # ─── REST API — Configuración del Sistema ─
    path('api/settings/', views.SystemSettingsAPIView.as_view(), name='api_settings'),

    # ─── REST API — Aspirantes ────────────────
    path('api/aspirants/register/', views.AspirantRegisterAPIView.as_view(), name='api_aspirant_register'),
    path('api/aspirants/', views.AspirantListAPIView.as_view(), name='api_aspirants'),
    path('api/aspirants/<str:code>/', views.AspirantDetailAPIView.as_view(), name='api_aspirant_detail'),
    path('api/aspirants/<str:code>/submit/', views.AspirantSubmitAPIView.as_view(), name='api_aspirant_submit'),
    path('api/aspirants/<str:code>/documents/upload/', views.AspirantDocumentUploadAPIView.as_view(), name='api_aspirant_document_upload'),

    # ─── REST API — Constancias ───────────────
    path('api/student/constancias/', views.CertificateRequestListCreateAPIView.as_view(), name='api_student_constancias'),
    path('api/admin/constancias/', views.AdminCertificateRequestListAPIView.as_view(), name='api_admin_constancias_list'),
    path('api/admin/constancias/<str:code>/', views.AdminCertificateRequestDetailAPIView.as_view(), name='api_admin_constancias_detail'),
    path('api/constancias/<str:code>/pdf/', views.certificate_pdf, name='api_certificate_pdf'),


    # ─── Panel — Herramientas del Sistema (solo superadmin) ──
    path('panel/herramientas/',                          views.panel_tools,      name='panel_tools'),
    path('panel/herramientas/ejecutar/',                 views.panel_tool_run,   name='panel_tool_run'),
    path('panel/herramientas/estado/<str:job_id>/',      views.panel_tool_status,name='panel_tool_status'),

    # ─── REST API — Roles y Permisos RBAC ─────
    path('api/roles/', views.SystemRoleListCreateAPIView.as_view(), name='api_roles'),
    path('api/roles/<int:pk>/', views.SystemRoleDetailAPIView.as_view(), name='api_role_detail'),
    path('api/roles/<int:pk>/permissions/', views.RolePermissionBulkAPIView.as_view(), name='api_role_permissions'),
]
