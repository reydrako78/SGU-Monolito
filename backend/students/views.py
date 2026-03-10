from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Career, Student
from .serializers import CareerSerializer, StudentSerializer, StudentCreateSerializer


class CareerListCreateView(generics.ListCreateAPIView):
    queryset = Career.objects.filter(is_active=True)
    serializer_class = CareerSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'faculty']
    ordering_fields = ['name', 'code']


class CareerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Career.objects.all()
    serializer_class = CareerSerializer
    permission_classes = [IsAuthenticated]


class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.select_related('career').all()
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['carnet', 'national_id']
    ordering_fields = ['carnet', 'semester', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StudentCreateSerializer
        return StudentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        career = self.request.query_params.get('career')
        semester = self.request.query_params.get('semester')
        if status:
            qs = qs.filter(status=status)
        if career:
            qs = qs.filter(career_id=career)
        if semester:
            qs = qs.filter(semester=semester)
        return qs


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.select_related('career').all()
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]


class StudentByUserIdView(APIView):
    """Buscar estudiante por user_id del Auth Service."""
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            student = Student.objects.select_related('career').get(user_id=user_id)
            serializer = StudentSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'detail': 'Estudiante no encontrado.'}, status=404)


class StudentAcademicSummaryView(APIView):
    """Resumen académico del estudiante."""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            student = Student.objects.select_related('career').get(pk=pk)
        except Student.DoesNotExist:
            return Response({'detail': 'Estudiante no encontrado.'}, status=404)

        return Response({
            'student_id': student.id,
            'carnet': student.carnet,
            'career': student.career.name,
            'career_code': student.career.code,
            'semester': student.semester,
            'status': student.get_status_display(),
            'enrollment_date': student.enrollment_date,
        })
