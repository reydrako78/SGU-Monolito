from rest_framework import serializers
from .models import Grade


class GradeSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Grade
        fields = (
            'id', 'student_id', 'curricular_unit_id', 'section_id', 'period_id', 'enrollment_detail_id',
            'student_carnet', 'uc_code', 'uc_name', 'uc_credits', 'period_name',
            'partial1', 'partial2', 'partial3', 'final_grade',
            'status', 'status_display',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'final_grade', 'status', 'created_at', 'updated_at')


class GradeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = (
            'student_id', 'curricular_unit_id', 'section_id', 'period_id', 'enrollment_detail_id',
            'student_carnet', 'uc_code', 'uc_name', 'uc_credits', 'period_name',
        )


class GradeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ('partial1', 'partial2', 'partial3', 'status')

    def validate(self, attrs):
        for field in ('partial1', 'partial2', 'partial3'):
            value = attrs.get(field)
            if value is not None and not (0 <= float(value) <= 100):
                raise serializers.ValidationError({field: 'La nota debe estar entre 0 y 100.'})
        return attrs
