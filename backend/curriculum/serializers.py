from rest_framework import serializers
from .models import CurricularUnit, CareerPlan, Prerequisite, CareerSede, CareerNucleo


# ─── Curricular Unit ──────────────────────────────────────────────────────────

class CurricularUnitSerializer(serializers.ModelSerializer):
    component_display   = serializers.CharField(source='get_component_display', read_only=True)
    uc_type_display     = serializers.CharField(source='get_uc_type_display',   read_only=True)
    level_display       = serializers.CharField(source='get_level_display',     read_only=True)
    total_hours         = serializers.IntegerField(read_only=True)
    component_color     = serializers.CharField(read_only=True)

    class Meta:
        model  = CurricularUnit
        fields = [
            'id', 'code', 'name',
            'component', 'component_display', 'component_color',
            'uc_type', 'uc_type_display',
            'level', 'level_display',
            'area', 'credits', 'teaching_hours', 'student_hours', 'total_hours',
            'is_exit_req', 'description', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class CurricularUnitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CurricularUnit
        fields = [
            'name', 'component', 'uc_type', 'level', 'area',
            'credits', 'teaching_hours', 'student_hours',
            'is_exit_req', 'description', 'is_active',
        ]


# ─── Prerequisites ────────────────────────────────────────────────────────────

class PrerequisiteSerializer(serializers.ModelSerializer):
    required_unit_name = serializers.CharField(source='required_unit.name', read_only=True)
    required_unit_code = serializers.CharField(source='required_unit.code', read_only=True)

    class Meta:
        model  = Prerequisite
        fields = ['id', 'required_unit', 'required_unit_name', 'required_unit_code']


# ─── Career Plan ──────────────────────────────────────────────────────────────

class CareerPlanSerializer(serializers.ModelSerializer):
    unit = CurricularUnitSerializer(source='curricular_unit', read_only=True)
    prerequisites = PrerequisiteSerializer(many=True, read_only=True)

    class Meta:
        model  = CareerPlan
        fields = [
            'id', 'career_id', 'academic_period', 'order',
            'curricular_unit', 'unit',
            'prerequisites',
        ]
        read_only_fields = ['id']


class CareerPlanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CareerPlan
        fields = ['career_id', 'curricular_unit', 'academic_period', 'order']

    def validate(self, attrs):
        career_id = attrs.get('career_id')
        unit      = attrs.get('curricular_unit')
        period    = attrs.get('academic_period')
        if CareerPlan.objects.filter(
            career_id=career_id,
            curricular_unit=unit,
            academic_period=period,
        ).exists():
            raise serializers.ValidationError(
                'Esta Unidad Curricular ya está en ese período académico para esta carrera.'
            )
        if not (1 <= period <= 8):
            raise serializers.ValidationError('El período académico debe estar entre 1 y 8.')
        return attrs


# ─── Career ↔ Sede ────────────────────────────────────────────────────────────

class CareerSedeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CareerSede
        fields = ['id', 'career_id', 'sede_id', 'is_active', 'assigned_at', 'assigned_by_id']
        read_only_fields = ['id', 'assigned_at']


class CareerSedeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CareerSede
        fields = ['career_id', 'sede_id', 'assigned_by_id']

    def validate(self, attrs):
        if CareerSede.objects.filter(
            career_id=attrs['career_id'],
            sede_id=attrs['sede_id'],
        ).exists():
            raise serializers.ValidationError('Esta carrera ya está asignada a esa sede.')
        return attrs


# ─── Career ↔ Nucleo ──────────────────────────────────────────────────────────

class CareerNucleoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CareerNucleo
        fields = ['id', 'career_id', 'nucleo_id', 'is_active', 'assigned_at', 'assigned_by_id']
        read_only_fields = ['id', 'assigned_at']


class CareerNucleoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CareerNucleo
        fields = ['career_id', 'nucleo_id', 'assigned_by_id']

    def validate(self, attrs):
        if CareerNucleo.objects.filter(
            career_id=attrs['career_id'],
            nucleo_id=attrs['nucleo_id'],
        ).exists():
            raise serializers.ValidationError('Esta carrera ya está asignada a ese núcleo.')
        return attrs
