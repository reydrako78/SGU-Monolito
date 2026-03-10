"""
Unit tests for Enrollment and EnrollmentDetail models.
"""
from django.test import TestCase
from django.db import IntegrityError

from enrollments.models import Enrollment, EnrollmentDetail


def make_enrollment(**kwargs):
    defaults = dict(student_id=1, period_id=1, student_carnet='V-11111111', period_name='2026-I')
    defaults.update(kwargs)
    return Enrollment.objects.create(**defaults)


class EnrollmentModelTest(TestCase):

    def test_create_enrollment(self):
        e = make_enrollment()
        self.assertEqual(e.status, 'enrolled')
        self.assertIsNotNone(e.enrollment_date)

    def test_str_representation(self):
        e = make_enrollment()
        self.assertIn('V-11111111', str(e))

    def test_unique_student_period(self):
        make_enrollment()
        with self.assertRaises(IntegrityError):
            make_enrollment()  # mismos student_id + period_id

    def test_different_periods_allowed(self):
        make_enrollment(period_id=1)
        make_enrollment(period_id=2)
        self.assertEqual(Enrollment.objects.count(), 2)

    def test_different_students_same_period_allowed(self):
        make_enrollment(student_id=1)
        make_enrollment(student_id=2, student_carnet='V-22222222')
        self.assertEqual(Enrollment.objects.count(), 2)


class EnrollmentDetailModelTest(TestCase):

    def setUp(self):
        self.enrollment = make_enrollment()

    def test_create_detail(self):
        detail = EnrollmentDetail.objects.create(
            enrollment=self.enrollment,
            section_id=10,
            curricular_unit_id=5,
            uc_code='MAT101',
            uc_name='Matemáticas I',
            uc_credits=4,
            section_number='01',
        )
        self.assertEqual(detail.status, 'active')

    def test_unique_enrollment_section(self):
        EnrollmentDetail.objects.create(enrollment=self.enrollment, section_id=10, curricular_unit_id=5)
        with self.assertRaises(IntegrityError):
            EnrollmentDetail.objects.create(enrollment=self.enrollment, section_id=10, curricular_unit_id=5)

    def test_withdrawn_detail(self):
        from django.utils import timezone
        detail = EnrollmentDetail.objects.create(
            enrollment=self.enrollment, section_id=10, curricular_unit_id=5, status='withdrawn',
            withdrawn_at=timezone.now(),
        )
        self.assertEqual(detail.status, 'withdrawn')
        self.assertIsNotNone(detail.withdrawn_at)
