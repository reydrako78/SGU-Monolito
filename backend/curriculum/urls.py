from django.urls import path
from . import views

urlpatterns = [
    # Curricular Units
    path('curricular-units/',        views.CurricularUnitListCreateView.as_view(), name='uc-list'),
    path('curricular-units/<int:pk>/', views.CurricularUnitDetailView.as_view(),   name='uc-detail'),

    # Career Plan
    path('career-plan/',             views.CareerPlanListCreateView.as_view(),     name='plan-list'),
    path('career-plan/<int:pk>/',    views.CareerPlanDetailView.as_view(),         name='plan-detail'),

    # Career ↔ Sede assignments
    path('career-sede/',             views.CareerSedeListCreateView.as_view(),     name='career-sede-list'),
    path('career-sede/<int:pk>/',    views.CareerSedeDetailView.as_view(),         name='career-sede-detail'),
    path('career-sede/by-sede/<int:sede_id>/', views.CareersBySede.as_view(),     name='careers-by-sede'),

    # Career ↔ Nucleo assignments
    path('career-nucleo/',           views.CareerNucleoListCreateView.as_view(),   name='career-nucleo-list'),
    path('career-nucleo/<int:pk>/',  views.CareerNucleoDetailView.as_view(),       name='career-nucleo-detail'),
    path('career-nucleo/by-nucleo/<int:nucleo_id>/', views.CareersByNucleo.as_view(), name='careers-by-nucleo'),
]
