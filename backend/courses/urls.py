from django.urls import path
from . import views

urlpatterns = [
    # Períodos
    path('periods/',          views.PeriodListCreateView.as_view(),  name='period-list'),
    path('periods/active/',   views.ActivePeriodView.as_view(),      name='period-active'),
    path('periods/<int:pk>/', views.PeriodDetailView.as_view(),      name='period-detail'),

    # Secciones
    path('sections/',                         views.SectionListCreateView.as_view(),      name='section-list'),
    path('sections/oferta/',                  views.SectionsBySedeView.as_view(),          name='section-oferta'),
    path('sections/check-conflict/',          views.CheckConflictView.as_view(),           name='check-conflict'),
    path('sections/<int:pk>/',                views.SectionDetailView.as_view(),           name='section-detail'),
    path('sections/<int:pk>/enrollment/',     views.SectionEnrollmentUpdateView.as_view(), name='section-enrollment'),

    # Horarios de sección
    path('sections/<int:pk>/schedules/',      views.SectionScheduleView.as_view(),         name='section-schedules'),
    path('sections/schedules/<int:pk>/',      views.SectionScheduleDetailView.as_view(),   name='schedule-detail'),
]
