from django.urls import path
from . import views

urlpatterns = [
    path('grades/', views.GradeListCreateView.as_view(), name='grade-list'),
    path('grades/<int:pk>/', views.GradeDetailView.as_view(), name='grade-detail'),
    path('grades/student/<int:student_id>/', views.StudentGradesView.as_view(), name='student-grades'),
    path('grades/section/<int:section_id>/', views.SectionGradesView.as_view(), name='section-grades'),
]
