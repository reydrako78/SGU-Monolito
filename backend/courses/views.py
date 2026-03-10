from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import F

from .models import Period, Section
from .serializers import PeriodSerializer, SectionSerializer, SectionCreateSerializer


# ─── Períodos ───────────────────────────────────────────────────────────────

class PeriodListCreateView(generics.ListCreateAPIView):
    queryset         = Period.objects.all()
    serializer_class = PeriodSerializer
    filter_backends  = [filters.OrderingFilter]
    ordering_fields  = ['start_date', 'name']


class PeriodDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Period.objects.all()
    serializer_class = PeriodSerializer


class ActivePeriodView(APIView):
    """Retorna el período académico activo actualmente."""
    def get(self, request):
        try:
            period = Period.objects.get(is_active=True)
            return Response(PeriodSerializer(period).data)
        except Period.DoesNotExist:
            return Response({'detail': 'No hay período activo.'}, status=404)


# ─── Secciones ──────────────────────────────────────────────────────────────

class SectionListCreateView(generics.ListCreateAPIView):
    """
    GET  → lista de secciones con filtros opcionales.
    POST → crear nueva sección.

    Filtros: ?period=id  ?curricular_unit=id  ?career=id
             ?sede=id    ?nucleo=id  ?available=true  ?active=true|false
    """
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields   = ['uc_code', 'uc_name', 'professor_name',
                       'section_number', 'career_name', 'sede_name']
    ordering_fields = ['uc_code', 'section_number', 'enrolled_count']

    def get_queryset(self):
        qs = Section.objects.select_related('period').all()
        p  = self.request.query_params
        if p.get('period'):
            qs = qs.filter(period_id=p['period'])
        if p.get('curricular_unit'):
            qs = qs.filter(curricular_unit_id=p['curricular_unit'])
        if p.get('career'):
            qs = qs.filter(career_id=p['career'])
        if p.get('sede'):
            qs = qs.filter(sede_id=p['sede'])
        if p.get('nucleo'):
            qs = qs.filter(nucleo_id=p['nucleo'])
        if p.get('available') == 'true':
            qs = qs.filter(enrolled_count__lt=F('max_students'))
        if p.get('professor'):
            qs = qs.filter(professor_user_id=p['professor'])
        if p.get('active') == 'true':
            qs = qs.filter(is_active=True)
        elif p.get('active') == 'false':
            qs = qs.filter(is_active=False)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SectionCreateSerializer
        return SectionSerializer


class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Section.objects.select_related('period').all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return SectionCreateSerializer
        return SectionSerializer


class SectionEnrollmentUpdateView(APIView):
    """Actualiza enrolled_count. Llamado por enrollment_service."""
    def post(self, request, pk):
        action = request.data.get('action')
        if action not in ('increment', 'decrement'):
            return Response({'detail': 'Acción inválida. Use "increment" o "decrement".'}, status=400)

        with transaction.atomic():
            try:
                section = Section.objects.select_for_update().get(pk=pk)
            except Section.DoesNotExist:
                return Response({'detail': 'Sección no encontrada.'}, status=404)

            if action == 'increment':
                if section.is_full:
                    return Response({'detail': 'La sección está llena.', 'is_full': True}, status=400)
                Section.objects.filter(pk=pk).update(enrolled_count=F('enrolled_count') + 1)
                section.refresh_from_db()
            else:
                if section.enrolled_count > 0:
                    Section.objects.filter(pk=pk).update(enrolled_count=F('enrolled_count') - 1)
                    section.refresh_from_db()

        return Response({'enrolled_count': section.enrolled_count,
                         'available_spots': section.available_spots})


class SectionsBySedeView(APIView):
    """
    Oferta académica de una sede/núcleo en el período activo.
    GET /api/sections/oferta/?sede=<id>&nucleo=<id>&career=<id>
    """
    def get(self, request):
        sede_id   = request.query_params.get('sede')
        nucleo_id = request.query_params.get('nucleo')
        career_id = request.query_params.get('career')
        if not sede_id:
            return Response({'detail': 'El parámetro sede es requerido.'}, status=400)
        try:
            period = Period.objects.get(is_active=True)
        except Period.DoesNotExist:
            return Response({'detail': 'No hay período académico activo.'}, status=404)
        qs = Section.objects.filter(period=period, sede_id=sede_id, is_active=True)
        if nucleo_id:
            qs = qs.filter(nucleo_id=nucleo_id)
        if career_id:
            qs = qs.filter(career_id=career_id)
        return Response(SectionSerializer(qs, many=True).data)


# ─── Horarios de Sección ─────────────────────────────────────────────────────

from itertools import combinations as _combinations
from .models import SectionSchedule
from .serializers import SectionScheduleSerializer


class SectionScheduleView(generics.ListCreateAPIView):
    """
    GET  /api/sections/<pk>/schedules/  → lista franjas horarias
    POST /api/sections/<pk>/schedules/  → agregar franja
    """
    serializer_class = SectionScheduleSerializer

    def get_queryset(self):
        return SectionSchedule.objects.filter(section_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(section_id=self.kwargs['pk'])


class SectionScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/sections/schedules/<pk>/
    """
    serializer_class = SectionScheduleSerializer
    queryset         = SectionSchedule.objects.all()


class CheckConflictView(APIView):
    """
    POST /api/sections/check-conflict/
    Body: { "section_ids": [1, 2, 3] }
    Detecta choques de horario entre las secciones dadas.
    """
    def post(self, request):
        section_ids = request.data.get('section_ids', [])
        if len(section_ids) < 2:
            return Response({'has_conflict': False, 'conflicts': []})

        schedules = {
            sid: list(SectionSchedule.objects.filter(section_id=sid))
            for sid in section_ids
        }

        conflicts = []
        for sid1, sid2 in _combinations(section_ids, 2):
            for s1 in schedules[sid1]:
                for s2 in schedules[sid2]:
                    if (s1.day == s2.day and
                            s1.start_time < s2.end_time and
                            s2.start_time < s1.end_time):
                        conflicts.append({
                            'section_1': sid1,
                            'section_2': sid2,
                            'day': s1.day,
                            'day_label': s1.get_day_display(),
                            'time_1': f'{s1.start_time.strftime("%H:%M")}-{s1.end_time.strftime("%H:%M")}',
                            'time_2': f'{s2.start_time.strftime("%H:%M")}-{s2.end_time.strftime("%H:%M")}',
                        })

        return Response({'has_conflict': bool(conflicts), 'conflicts': conflicts})
