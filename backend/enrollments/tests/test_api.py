"""
Integration tests for enrollment_service API.
External service calls (services.get_student, get_section, etc.) are mocked.
"""
from unittest.mock import patch, MagicMock

from rest_framework.test import APITestCase
from rest_framework import status

from enrollments.models import Enrollment, EnrollmentDetail


ENROLL_URL = '/api/enrollments/enroll/'
LIST_URL   = '/api/enrollments/'


def mock_student(student_id=1, carnet='V-11111111', active=True):
    return {'id': student_id, 'carnet': carnet, 'status': 'active' if active else 'inactive'}


def mock_period(period_id=1, name='2026-I'):
    return {'id': period_id, 'name': name, 'is_active': True}


def mock_section(section_id=10, uc_code='MAT101', is_full=False):
    return {
        'id': section_id,
        'curricular_unit_id': 5,
        'uc_code': uc_code,
        'uc_name': 'Matemáticas I',
        'uc_credits': 4,
        'section_number': '01',
        'career_name': 'Ingeniería',
        'professor_name': 'Dr. García',
        'is_full': is_full,
    }


ENROLL_PAYLOAD = {
    'student_id': 1,
    'period_id': 1,
    'section_ids': [10],
}


@patch('enrollments.services.update_section_enrollment', return_value=None)
@patch('enrollments.services.get_section', side_effect=lambda sid: mock_section(sid))
@patch('enrollments.services.get_period', return_value=mock_period())
@patch('enrollments.services.get_student', return_value=mock_student())
class EnrollStudentTest(APITestCase):
    """POST /api/enrollments/enroll/ — flujo de inscripción."""

    def test_enroll_creates_enrollment(self, ms, mp, msec, mupd):
        r = self.client.post(ENROLL_URL, ENROLL_PAYLOAD, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 1)
        self.assertEqual(EnrollmentDetail.objects.count(), 1)

    def test_enroll_creates_detail_with_uc_data(self, ms, mp, msec, mupd):
        self.client.post(ENROLL_URL, ENROLL_PAYLOAD, format='json')
        detail = EnrollmentDetail.objects.first()
        self.assertEqual(detail.uc_code, 'MAT101')
        self.assertEqual(detail.uc_credits, 4)
        self.assertEqual(detail.section_number, '01')

    def test_enroll_calls_increment(self, ms, mp, msec, mupd):
        self.client.post(ENROLL_URL, ENROLL_PAYLOAD, format='json')
        mupd.assert_called_once_with(10, 'increment')

    def test_enroll_multiple_sections(self, ms, mp, msec, mupd):
        payload = {**ENROLL_PAYLOAD, 'section_ids': [10, 11]}
        r = self.client.post(ENROLL_URL, payload, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EnrollmentDetail.objects.count(), 2)
        self.assertEqual(mupd.call_count, 2)

    def test_enroll_inactive_student_rejected(self, ms, mp, msec, mupd):
        ms.return_value = mock_student(active=False)
        r = self.client.post(ENROLL_URL, ENROLL_PAYLOAD, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('activo', r.data['detail'])

    def test_enroll_student_not_found_returns_404(self, ms, mp, msec, mupd):
        ms.return_value = None
        r = self.client.post(ENROLL_URL, ENROLL_PAYLOAD, format='json')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_enroll_period_not_found_returns_404(self, ms, mp, msec, mupd):
        mp.return_value = None
        r = self.client.post(ENROLL_URL, ENROLL_PAYLOAD, format='json')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_enroll_full_section_rejected(self, ms, mp, msec, mupd):
        msec.side_effect = lambda sid: mock_section(sid, is_full=True)
        r = self.client.post(ENROLL_URL, ENROLL_PAYLOAD, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('llena', r.data['detail'])

    def test_duplicate_enrollment_rejected(self, ms, mp, msec, mupd):
        self.client.post(ENROLL_URL, ENROLL_PAYLOAD, format='json')
        r = self.client.post(ENROLL_URL, ENROLL_PAYLOAD, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ya está inscrito', r.data['detail'])

    def test_missing_section_ids_returns_400(self, ms, mp, msec, mupd):
        r = self.client.post(ENROLL_URL, {'student_id': 1, 'period_id': 1}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


@patch('enrollments.services.update_section_enrollment', return_value=None)
class WithdrawSectionTest(APITestCase):
    """POST /api/enrollments/<id>/withdraw/ — retiro de sección."""

    def setUp(self):
        self.enrollment = Enrollment.objects.create(
            student_id=1, period_id=1, student_carnet='V-11111111', period_name='2026-I',
        )
        self.detail = EnrollmentDetail.objects.create(
            enrollment=self.enrollment,
            section_id=10,
            curricular_unit_id=5,
            uc_code='MAT101',
            status='active',
        )
        self.url = f'/api/enrollments/{self.enrollment.pk}/withdraw/'

    def test_withdraw_section_changes_status(self, mupd):
        r = self.client.post(self.url, {'section_id': 10}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.detail.refresh_from_db()
        self.assertEqual(self.detail.status, 'withdrawn')

    def test_withdraw_sets_withdrawn_at(self, mupd):
        self.client.post(self.url, {'section_id': 10}, format='json')
        self.detail.refresh_from_db()
        self.assertIsNotNone(self.detail.withdrawn_at)

    def test_withdraw_calls_decrement(self, mupd):
        self.client.post(self.url, {'section_id': 10}, format='json')
        mupd.assert_called_once_with(10, 'decrement')

    def test_withdraw_all_sections_marks_enrollment_withdrawn(self, mupd):
        self.client.post(self.url, {'section_id': 10}, format='json')
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, 'withdrawn')

    def test_withdraw_only_last_section_withdraws_enrollment(self, mupd):
        # Add a second active section
        EnrollmentDetail.objects.create(
            enrollment=self.enrollment, section_id=11, curricular_unit_id=6, status='active',
        )
        self.client.post(self.url, {'section_id': 10}, format='json')
        self.enrollment.refresh_from_db()
        # Still one active detail → enrollment stays 'enrolled'
        self.assertEqual(self.enrollment.status, 'enrolled')

    def test_withdraw_nonexistent_section_returns_404(self, mupd):
        r = self.client.post(self.url, {'section_id': 999}, format='json')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_withdraw_nonexistent_enrollment_returns_404(self, mupd):
        r = self.client.post('/api/enrollments/9999/withdraw/', {'section_id': 10}, format='json')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)


class EnrollmentsBySectionTest(APITestCase):
    """GET /api/enrollments/section/<id>/ — lista para el profesor."""

    def setUp(self):
        e1 = Enrollment.objects.create(student_id=1, period_id=1, student_carnet='V-11111111', period_name='2026-I')
        e2 = Enrollment.objects.create(student_id=2, period_id=1, student_carnet='V-22222222', period_name='2026-I')
        EnrollmentDetail.objects.create(enrollment=e1, section_id=5, curricular_unit_id=1,
                                        uc_code='MAT101', uc_name='Matemáticas I', uc_credits=4, status='active')
        EnrollmentDetail.objects.create(enrollment=e2, section_id=5, curricular_unit_id=1,
                                        uc_code='MAT101', uc_name='Matemáticas I', uc_credits=4, status='active')
        # withdrawn student — should NOT appear
        e3 = Enrollment.objects.create(student_id=3, period_id=1, student_carnet='V-33333333', period_name='2026-I')
        EnrollmentDetail.objects.create(enrollment=e3, section_id=5, curricular_unit_id=1,
                                        uc_code='MAT101', status='withdrawn')

    def test_returns_only_active_students(self):
        r = self.client.get('/api/enrollments/section/5/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['total'], 2)

    def test_response_contains_carnet(self):
        r = self.client.get('/api/enrollments/section/5/')
        carnets = [s['student_carnet'] for s in r.data['students']]
        self.assertIn('V-11111111', carnets)
        self.assertNotIn('V-33333333', carnets)

    def test_empty_section_returns_zero(self):
        r = self.client.get('/api/enrollments/section/999/')
        self.assertEqual(r.data['total'], 0)
        self.assertEqual(r.data['students'], [])
