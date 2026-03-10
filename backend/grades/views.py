from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Grade
from .serializers import GradeSerializer, GradeCreateSerializer, GradeUpdateSerializer

_STAFF_ROLES = {'admin', 'control_estudios', 'docencia', 'secretaria'}


class GradeListCreateView(generics.ListCreateAPIView):
    queryset = Grade.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GradeCreateSerializer
        return GradeSerializer

    def create(self, request, *args, **kwargs):
        user_role = getattr(request.user, 'role', None)
        if user_role not in _STAFF_ROLES and user_role != 'professor':
            return Response({'detail': 'Solo profesores y administradores pueden registrar calificaciones.'}, status=403)
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        user_role = getattr(self.request.user, 'role', None)
        student_id = self.request.query_params.get('student_id')
        period_id = self.request.query_params.get('period_id')
        curricular_unit_id = self.request.query_params.get('curricular_unit_id') or self.request.query_params.get('course_id')
        status = self.request.query_params.get('status')

        # Non-staff users without a student_id filter get an empty queryset
        # (prevents listing all grades from the system)
        if user_role not in _STAFF_ROLES and not student_id:
            return qs.none()

        if student_id:
            qs = qs.filter(student_id=student_id)
        if period_id:
            qs = qs.filter(period_id=period_id)
        if curricular_unit_id:
            qs = qs.filter(curricular_unit_id=curricular_unit_id)
        if status:
            qs = qs.filter(status=status)
        return qs


class GradeDetailView(generics.RetrieveUpdateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return GradeUpdateSerializer
        return GradeSerializer

    def update(self, request, *args, **kwargs):
        user_role = getattr(request.user, 'role', None)
        if user_role not in _STAFF_ROLES and user_role != 'professor':
            return Response({'detail': 'Solo profesores y administradores pueden modificar calificaciones.'}, status=403)
        return super().update(request, *args, **kwargs)


class StudentGradesView(APIView):
    """Historial académico completo de un estudiante."""
    def get(self, request, student_id):
        grades = Grade.objects.filter(student_id=student_id).order_by('-period_id', 'uc_code')

        period_id = request.query_params.get('period_id')
        if period_id:
            grades = grades.filter(period_id=period_id)

        serializer = GradeSerializer(grades, many=True)

        # Calcular estadísticas
        completed = grades.filter(status__in=['passed', 'failed'])
        passed = grades.filter(status='passed')

        stats = {
            'total_courses': grades.count(),
            'passed': passed.count(),
            'failed': grades.filter(status='failed').count(),
            'in_progress': grades.filter(status='in_progress').count(),
        }

        if completed.exists():
            from django.db.models import Avg
            avg = completed.aggregate(avg=Avg('final_grade'))['avg']
            stats['average'] = round(float(avg), 2) if avg else None
        else:
            stats['average'] = None

        return Response({
            'student_id': student_id,
            'statistics': stats,
            'grades': serializer.data,
        })


class SectionGradesView(APIView):
    """Lista todas las calificaciones de una sección (para profesores/admin)."""
    def get(self, request, section_id):
        grades = Grade.objects.filter(section_id=section_id).order_by('student_carnet')
        serializer = GradeSerializer(grades, many=True)
        return Response({
            'section_id': section_id,
            'total_students': grades.count(),
            'grades': serializer.data,
        })
