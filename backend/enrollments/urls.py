from django.urls import path
from . import views

urlpatterns = [
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment-list'),
    path('enrollments/<int:pk>/', views.EnrollmentDetailView.as_view(), name='enrollment-detail'),
    path('enrollments/enroll/', views.EnrollStudentView.as_view(), name='enroll-student'),
    path('enrollments/<int:enrollment_id>/withdraw/', views.WithdrawSectionView.as_view(), name='withdraw-section'),
    path('enrollments/student/<int:student_id>/', views.StudentEnrollmentsView.as_view(), name='student-enrollments'),
    path('enrollments/section/<int:section_id>/', views.EnrollmentsBySectionView.as_view(), name='enrollments-by-section'),
]
