from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import CurricularUnit, CareerPlan, Prerequisite, CareerSede, CareerNucleo
from .serializers import (
    CurricularUnitSerializer, CurricularUnitCreateSerializer,
    CareerPlanSerializer, CareerPlanCreateSerializer,
    CareerSedeSerializer, CareerSedeCreateSerializer,
    CareerNucleoSerializer, CareerNucleoCreateSerializer,
)


# ─── Curricular Units ─────────────────────────────────────────────────────────

@method_decorator(cache_page(60 * 60), name='list')  # 1 hora
class CurricularUnitListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['name', 'code', 'area']
    ordering_fields    = ['name', 'component', 'credits', 'created_at']

    def get_queryset(self):
        qs = CurricularUnit.objects.all()
        component = self.request.query_params.get('component')
        uc_type   = self.request.query_params.get('uc_type')
        active    = self.request.query_params.get('active')
        if component:
            qs = qs.filter(component=component)
        if uc_type:
            qs = qs.filter(uc_type=uc_type)
        if active is not None:
            qs = qs.filter(is_active=(active.lower() == 'true'))
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CurricularUnitCreateSerializer
        return CurricularUnitSerializer


class CurricularUnitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = CurricularUnit.objects.all()
    serializer_class   = CurricularUnitSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Soft delete: just deactivate
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Career Plan ──────────────────────────────────────────────────────────────

@method_decorator(cache_page(60 * 60), name='list')  # 1 hora
class CareerPlanListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = CareerPlan.objects.select_related(
            'curricular_unit'
        ).prefetch_related('prerequisites__required_unit')
        career_id = self.request.query_params.get('career_id')
        period    = self.request.query_params.get('period')
        if career_id:
            qs = qs.filter(career_id=career_id)
        if period:
            qs = qs.filter(academic_period=period)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CareerPlanCreateSerializer
        return CareerPlanSerializer


class CareerPlanDetailView(generics.RetrieveDestroyAPIView):
    queryset           = CareerPlan.objects.select_related('curricular_unit')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return CareerPlanSerializer


# ─── Career ↔ Sede ────────────────────────────────────────────────────────────

@method_decorator(cache_page(60 * 60), name='list')  # 1 hora
class CareerSedeListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = CareerSede.objects.all()
        career_id = self.request.query_params.get('career_id')
        sede_id   = self.request.query_params.get('sede_id')
        if career_id:
            qs = qs.filter(career_id=career_id)
        if sede_id:
            qs = qs.filter(sede_id=sede_id)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CareerSedeCreateSerializer
        return CareerSedeSerializer


class CareerSedeDetailView(generics.RetrieveDestroyAPIView):
    queryset           = CareerSede.objects.all()
    serializer_class   = CareerSedeSerializer
    permission_classes = [IsAuthenticated]


class CareersBySede(APIView):
    """GET /api/career-sede/by-sede/<sede_id>/ → lista de career_id asignados a la sede."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, sede_id):
        assignments = CareerSede.objects.filter(sede_id=sede_id, is_active=True)
        serializer  = CareerSedeSerializer(assignments, many=True)
        return Response(serializer.data)


# ─── Career ↔ Nucleo ──────────────────────────────────────────────────────────

@method_decorator(cache_page(60 * 60), name='list')  # 1 hora
class CareerNucleoListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = CareerNucleo.objects.all()
        career_id  = self.request.query_params.get('career_id')
        nucleo_id  = self.request.query_params.get('nucleo_id')
        if career_id:
            qs = qs.filter(career_id=career_id)
        if nucleo_id:
            qs = qs.filter(nucleo_id=nucleo_id)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CareerNucleoCreateSerializer
        return CareerNucleoSerializer


class CareerNucleoDetailView(generics.RetrieveDestroyAPIView):
    queryset           = CareerNucleo.objects.all()
    serializer_class   = CareerNucleoSerializer
    permission_classes = [IsAuthenticated]


class CareersByNucleo(APIView):
    """GET /api/career-nucleo/by-nucleo/<nucleo_id>/ → lista de career_id asignados al núcleo."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, nucleo_id):
        assignments = CareerNucleo.objects.filter(nucleo_id=nucleo_id, is_active=True)
        serializer  = CareerNucleoSerializer(assignments, many=True)
        return Response(serializer.data)
