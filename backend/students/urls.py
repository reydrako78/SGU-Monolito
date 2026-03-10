from django.urls import path
from . import views

urlpatterns = [
    path('careers/', views.CareerListCreateView.as_view(), name='career-list'),
    path('careers/<int:pk>/', views.CareerDetailView.as_view(), name='career-detail'),

    path('students/', views.StudentListCreateView.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('students/by-user/<int:user_id>/', views.StudentByUserIdView.as_view(), name='student-by-user'),
    path('students/<int:pk>/academic-summary/', views.StudentAcademicSummaryView.as_view(), name='student-summary'),
]
