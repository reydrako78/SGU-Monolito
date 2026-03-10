from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Enrollment, EnrollmentDetail
from .serializers import (
    EnrollmentSerializer, EnrollmentCreateSerializer, WithdrawSectionSerializer,
)
from . import services

_ADMIN_ROLES = {'admin', 'control_estudios', 'secretaria'}


class EnrollmentListView(generics.ListAPIView):
    queryset         = Enrollment.objects.prefetch_related('details').all()
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        qs        = super().get_queryset()
        p         = self.request.query_params
        if p.get('student_id'):
            qs = qs.filter(student_id=p['student_id'])
        if p.get('period_id'):
            qs = qs.filter(period_id=p['period_id'])
        if p.get('status'):
            qs = qs.filter(status=p['status'])
        return qs


class EnrollmentDetailView(generics.RetrieveAPIView):
    queryset         = Enrollment.objects.prefetch_related('details').all()
    serializer_class = EnrollmentSerializer


class EnrollStudentView(APIView):
    """
    Inscribe a un estudiante en un período asociándolo a una o más secciones.
    Valida disponibilidad comunicándose con courses_service.

    POST body:
    {
      "student_id": 1,
      "period_id":  2,
      "section_ids": [10, 11, 12]
    }
    """
    def post(self, request):
        serializer = EnrollmentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data        = serializer.validated_data
        student_id  = data['student_id']
        period_id   = data['period_id']
        section_ids = data['section_ids']

        # Verificar que el estudiante existe y está activo
        student = services.get_student(student_id)
        if not student:
            return Response({'detail': 'Estudiante no encontrado.'}, status=404)
        if student.get('status') != 'active':
            return Response({'detail': 'El estudiante no está activo.'}, status=400)

        # Verificar que el estudiante es el propio usuario (o tiene rol admin)
        user_role = getattr(request.user, 'role', None)
        if user_role not in _ADMIN_ROLES:
            if student.get('user_id') != request.user.id:
                return Response({'detail': 'No tienes permiso para inscribir a otro estudiante.'}, status=403)

        # Verificar que el período existe
        period = services.get_period(period_id)
        if not period:
            return Response({'detail': 'Período no encontrado.'}, status=404)

        # Verificar inscripción previa en este período
        existing = Enrollment.objects.filter(student_id=student_id, period_id=period_id).first()
        if existing:
            return Response({
                'detail':        'El estudiante ya está inscrito en este período.',
                'enrollment_id': existing.id,
            }, status=400)

        # Verificar disponibilidad de cada sección
        sections_data = []
        for section_id in section_ids:
            section = services.get_section(section_id)
            if not section:
                return Response({'detail': f'Sección {section_id} no encontrada.'}, status=404)
            if section.get('is_full'):
                return Response({
                    'detail': (
                        f'La sección {section_id} '
                        f'({section.get("uc_code", "")} — Sec {section.get("section_number", "")}) '
                        f'está llena.'
                    ),
                }, status=400)
            sections_data.append(section)

        # Crear la inscripción
        enrollment = Enrollment.objects.create(
            student_id     = student_id,
            period_id      = period_id,
            student_carnet = student.get('carnet', ''),
            period_name    = period.get('name', ''),
            status         = 'enrolled',
        )

        # Crear detalles y actualizar conteos en courses_service
        for section in sections_data:
            EnrollmentDetail.objects.create(
                enrollment         = enrollment,
                section_id         = section['id'],
                curricular_unit_id = section.get('curricular_unit_id', 0),
                uc_code            = section.get('uc_code', ''),
                uc_name            = section.get('uc_name', ''),
                uc_credits         = section.get('uc_credits', 0),
                section_number     = section.get('section_number', ''),
                career_name        = section.get('career_name', ''),
                professor_name     = section.get('professor_name', ''),
                status             = 'active',
            )
            services.update_section_enrollment(section['id'], 'increment')

        return Response(EnrollmentSerializer(enrollment).data, status=201)


class WithdrawSectionView(APIView):
    """Retira a un estudiante de una sección dentro de su inscripción."""
    def post(self, request, enrollment_id):
        serializer = WithdrawSectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        section_id = serializer.validated_data['section_id']

        try:
            enrollment = Enrollment.objects.get(pk=enrollment_id)
        except Enrollment.DoesNotExist:
            return Response({'detail': 'Inscripción no encontrada.'}, status=404)

        # Verificar propiedad (admins pueden retirar cualquier sección)
        user_role = getattr(request.user, 'role', None)
        if user_role not in _ADMIN_ROLES:
            student = services.get_student(enrollment.student_id)
            if not student or student.get('user_id') != request.user.id:
                return Response({'detail': 'No tienes permiso para modificar esta inscripción.'}, status=403)

        try:
            detail = enrollment.details.get(section_id=section_id, status='active')
        except EnrollmentDetail.DoesNotExist:
            return Response({'detail': 'No se encontró la sección en esta inscripción.'}, status=404)

        detail.status       = 'withdrawn'
        detail.withdrawn_at = timezone.now()
        detail.save()

        services.update_section_enrollment(section_id, 'decrement')

        # Si no quedan secciones activas, marcar inscripción como retirada
        if not enrollment.details.filter(status='active').exists():
            enrollment.status = 'withdrawn'
            enrollment.save()

        return Response({
            'detail':     'Sección retirada exitosamente.',
            'enrollment': EnrollmentSerializer(enrollment).data,
        })


class StudentEnrollmentsView(APIView):
    """Lista todas las inscripciones de un estudiante."""
    def get(self, request, student_id):
        enrollments = Enrollment.objects.filter(
            student_id=student_id,
        ).prefetch_related('details')
        return Response(EnrollmentSerializer(enrollments, many=True).data)


class EnrollmentsBySectionView(APIView):
    """Lista estudiantes activos inscritos en una sección (para uso del profesor)."""
    def get(self, request, section_id):
        details = (
            EnrollmentDetail.objects
            .filter(section_id=section_id, status='active')
            .select_related('enrollment')
            .order_by('enrollment__student_carnet')
        )
        students = [
            {
                'enrollment_id':        d.enrollment.id,
                'enrollment_detail_id': d.id,
                'student_id':           d.enrollment.student_id,
                'student_carnet':       d.enrollment.student_carnet,
                'uc_code':              d.uc_code,
                'uc_name':              d.uc_name,
                'uc_credits':           d.uc_credits,
            }
            for d in details
        ]
        return Response({'section_id': section_id, 'total': len(students), 'students': students})
