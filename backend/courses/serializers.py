from rest_framework import serializers
from .models import Period, Section, SectionSchedule


class PeriodSerializer(serializers.ModelSerializer):
    period_type_display = serializers.CharField(
        source='get_period_type_display', read_only=True
    )

    class Meta:
        model  = Period
        fields = (
            'id', 'name', 'period_type', 'period_type_display',
            'start_date', 'end_date', 'is_active', 'created_at',
        )
        read_only_fields = ('id', 'created_at')


class SectionScheduleSerializer(serializers.ModelSerializer):
    day_display          = serializers.CharField(source='get_day_display',          read_only=True)
    session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
    color                = serializers.ReadOnlyField()

    class Meta:
        model  = SectionSchedule
        fields = (
            'id', 'section',
            'day', 'day_display',
            'start_time', 'end_time',
            'classroom',
            'session_type', 'session_type_display',
            'color',
        )
        read_only_fields = ('id', 'color')


class SectionSerializer(serializers.ModelSerializer):
    period_name     = serializers.CharField(source='period.name',        read_only=True)
    period_type     = serializers.CharField(source='period.period_type', read_only=True)
    available_spots = serializers.ReadOnlyField()
    is_full         = serializers.ReadOnlyField()
    schedules       = SectionScheduleSerializer(many=True, read_only=True)

    class Meta:
        model  = Section
        fields = (
            'id',
            'curricular_unit_id', 'career_id',
            'period', 'period_name', 'period_type',
            'sede_id', 'nucleo_id',
            'section_number',
            'professor_user_id', 'professor_name',
            'schedule', 'classroom',
            'max_students', 'enrolled_count',
            'available_spots', 'is_full',
            'is_active',
            'uc_code', 'uc_name', 'uc_credits',
            'career_name', 'sede_name', 'nucleo_name',
            'schedules',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'enrolled_count',
            'available_spots', 'is_full',
            'schedules',
            'created_at', 'updated_at',
        )


class SectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Section
        fields = (
            'curricular_unit_id', 'career_id',
            'period', 'sede_id', 'nucleo_id', 'section_number',
            'professor_user_id', 'professor_name',
            'schedule', 'classroom', 'max_students', 'is_active',
            'uc_code', 'uc_name', 'uc_credits',
            'career_name', 'sede_name', 'nucleo_name',
        )
