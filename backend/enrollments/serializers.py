from rest_framework import serializers
from .models import Enrollment, EnrollmentDetail


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model  = EnrollmentDetail
        fields = (
            'id', 'enrollment',
            'section_id', 'curricular_unit_id',
            'status', 'status_display',
            'uc_code', 'uc_name', 'uc_credits',
            'section_number', 'career_name', 'professor_name',
            'enrolled_at', 'withdrawn_at',
        )
        read_only_fields = ('id', 'enrolled_at', 'withdrawn_at')


class EnrollmentSerializer(serializers.ModelSerializer):
    details        = EnrollmentDetailSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model  = Enrollment
        fields = (
            'id', 'student_id', 'period_id',
            'enrollment_date', 'status', 'status_display',
            'student_carnet', 'period_name',
            'details',
        )
        read_only_fields = ('id', 'enrollment_date', 'student_carnet', 'period_name')


class EnrollmentCreateSerializer(serializers.Serializer):
    """Inscribir un estudiante en una o más secciones."""
    student_id  = serializers.IntegerField()
    period_id   = serializers.IntegerField()
    section_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)


class WithdrawSectionSerializer(serializers.Serializer):
    section_id = serializers.IntegerField()
