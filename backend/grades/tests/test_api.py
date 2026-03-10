"""
Integration tests for grades_service REST API.
Uses DRF APIClient — real DB (SQLite in tests), no mocks needed (no external calls).
"""
from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from grades.models import Grade


GRADE_LIST_URL = '/api/grades/'


def grade_detail_url(pk):
    return f'/api/grades/{pk}/'


def student_grades_url(student_id):
    return f'/api/grades/student/{student_id}/'


def section_grades_url(section_id):
    return f'/api/grades/section/{section_id}/'


GRADE_PAYLOAD = {
    'student_id': 1,
    'curricular_unit_id': 10,
    'section_id': 5,
    'period_id': 2,
    'enrollment_detail_id': 99,
    'student_carnet': 'V-11111111',
    'uc_code': 'MAT101',
    'uc_name': 'Matemáticas I',
    'uc_credits': 4,
    'period_name': '2026-I',
}


def paginated_results(r):
    """Helper: returns results list from paginated or plain response."""
    if isinstance(r.data, dict) and 'results' in r.data:
        return r.data['results']
    return r.data


class GradeCreateTest(APITestCase):
    """POST /api/grades/ — crea un registro de calificación."""

    def test_create_grade_without_partials(self):
        r = self.client.post(GRADE_LIST_URL, GRADE_PAYLOAD, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grade.objects.count(), 1)

    def test_create_grade_sets_in_progress(self):
        r = self.client.post(GRADE_LIST_URL, GRADE_PAYLOAD, format='json')
        grade = Grade.objects.get()
        self.assertEqual(grade.status, 'in_progress')
        self.assertIsNone(grade.final_grade)

    def test_create_duplicate_raises_400(self):
        self.client.post(GRADE_LIST_URL, GRADE_PAYLOAD, format='json')
        r = self.client.post(GRADE_LIST_URL, GRADE_PAYLOAD, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_required_field_returns_400(self):
        bad = {**GRADE_PAYLOAD}
        del bad['student_id']
        r = self.client.post(GRADE_LIST_URL, bad, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class GradeUpdateTest(APITestCase):
    """PATCH /api/grades/<pk>/ — actualiza parciales, recalcula final."""

    def setUp(self):
        r = self.client.post(GRADE_LIST_URL, GRADE_PAYLOAD, format='json')
        self.assertEqual(r.status_code, 201, msg=f"setUp POST failed: {r.data}")
        # GradeCreateSerializer doesn't expose 'id'; fetch from DB directly
        self.grade_id = Grade.objects.get(student_id=1, section_id=5).pk
        self.url = grade_detail_url(self.grade_id)

    def test_patch_partial1_calculates_final(self):
        r = self.client.patch(self.url, {'partial1': '75'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        grade = Grade.objects.get(pk=self.grade_id)
        self.assertEqual(grade.final_grade, Decimal('75.00'))
        self.assertEqual(grade.status, 'passed')

    def test_patch_three_partials_average(self):
        self.client.patch(self.url, {'partial1': '60', 'partial2': '70', 'partial3': '80'}, format='json')
        grade = Grade.objects.get(pk=self.grade_id)
        self.assertEqual(grade.final_grade, Decimal('70.00'))
        self.assertEqual(grade.status, 'passed')

    def test_patch_low_grade_fails(self):
        self.client.patch(self.url, {'partial1': '40', 'partial2': '50'}, format='json')
        grade = Grade.objects.get(pk=self.grade_id)
        self.assertEqual(grade.status, 'failed')

    def test_patch_grade_above_100_rejected(self):
        r = self.client.patch(self.url, {'partial1': '101'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_negative_grade_rejected(self):
        r = self.client.patch(self.url, {'partial1': '-1'}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_boundary_exactly_61_passes(self):
        self.client.patch(self.url, {'partial1': '61'}, format='json')
        grade = Grade.objects.get(pk=self.grade_id)
        self.assertEqual(grade.status, 'passed')

    def test_patch_60_fails(self):
        self.client.patch(self.url, {'partial1': '60'}, format='json')
        grade = Grade.objects.get(pk=self.grade_id)
        self.assertEqual(grade.status, 'failed')


class StudentGradesViewTest(APITestCase):
    """GET /api/grades/student/<id>/ — historial académico."""

    def setUp(self):
        # Crear 2 grades para student 1 en secciones distintas
        Grade.objects.create(**{**GRADE_PAYLOAD, 'partial1': Decimal('80'), 'section_id': 1, 'enrollment_detail_id': 1})
        Grade.objects.create(**{**GRADE_PAYLOAD, 'partial1': Decimal('40'), 'section_id': 2, 'enrollment_detail_id': 2,
                                'uc_code': 'FIS101', 'curricular_unit_id': 11})

    def test_returns_all_grades_for_student(self):
        r = self.client.get(student_grades_url(1))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['statistics']['total_courses'], 2)

    def test_statistics_passed_failed_count(self):
        r = self.client.get(student_grades_url(1))
        stats = r.data['statistics']
        self.assertEqual(stats['passed'], 1)
        self.assertEqual(stats['failed'], 1)

    def test_no_grades_returns_empty(self):
        r = self.client.get(student_grades_url(999))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['statistics']['total_courses'], 0)

    def test_filter_by_period(self):
        r = self.client.get(student_grades_url(1) + '?period_id=2')
        self.assertEqual(r.data['statistics']['total_courses'], 2)

    def test_different_student_returns_empty(self):
        r = self.client.get(student_grades_url(2))
        self.assertEqual(r.data['statistics']['total_courses'], 0)


class SectionGradesViewTest(APITestCase):
    """GET /api/grades/section/<id>/ — notas de una sección."""

    def setUp(self):
        Grade.objects.create(**{**GRADE_PAYLOAD, 'section_id': 7, 'enrollment_detail_id': 1})
        Grade.objects.create(**{**GRADE_PAYLOAD, 'section_id': 7, 'student_id': 2,
                                'student_carnet': 'V-22222222', 'enrollment_detail_id': 2})

    def test_returns_students_in_section(self):
        r = self.client.get(section_grades_url(7))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['total_students'], 2)
        self.assertEqual(r.data['section_id'], 7)

    def test_empty_section_returns_zero(self):
        r = self.client.get(section_grades_url(999))
        self.assertEqual(r.data['total_students'], 0)


class GradeListFilterTest(APITestCase):
    """GET /api/grades/ — filtros por student_id, period_id, status.
    Tests use unique student_id=91/92 to avoid collision with other TestCase setups.
    """
    PAYLOAD_91 = {**GRADE_PAYLOAD, 'student_id': 91, 'student_carnet': 'V-91000000',
                  'partial1': Decimal('70'), 'enrollment_detail_id': 91}
    PAYLOAD_92 = {**GRADE_PAYLOAD, 'student_id': 92, 'student_carnet': 'V-92000000',
                  'partial1': Decimal('40'), 'enrollment_detail_id': 92}

    def setUp(self):
        Grade.objects.create(**self.PAYLOAD_91)
        Grade.objects.create(**self.PAYLOAD_92)

    def test_filter_by_student_id_returns_only_that_student(self):
        r = self.client.get(GRADE_LIST_URL + '?student_id=91')
        results = paginated_results(r)
        student_ids = [g['student_id'] for g in results]
        self.assertIn(91, student_ids)
        self.assertNotIn(92, student_ids)

    def test_filter_by_status_passed_excludes_failed(self):
        r = self.client.get(GRADE_LIST_URL + '?status=passed&student_id=91')
        results = paginated_results(r)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'passed')

    def test_filter_by_status_failed_excludes_passed(self):
        r = self.client.get(GRADE_LIST_URL + '?status=failed&student_id=92')
        results = paginated_results(r)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'failed')
