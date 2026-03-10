from rest_framework import serializers
from .models import Career, Student


class CareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    career_name = serializers.CharField(source='career.name', read_only=True)
    career_code = serializers.CharField(source='career.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Student
        fields = (
            'id', 'user_id', 'carnet', 'career', 'career_name', 'career_code',
            'semester', 'status', 'status_display', 'enrollment_date',
            'phone', 'address', 'birth_date', 'national_id',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = (
            'user_id', 'carnet', 'career', 'semester', 'status',
            'enrollment_date', 'phone', 'address', 'birth_date', 'national_id',
        )
