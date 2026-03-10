"""
Unit tests for Grade model — no HTTP, no external services.
Tests cover: calculate_final_grade, update_status, save() auto-trigger.
"""
from decimal import Decimal

from django.test import TestCase

from grades.models import Grade


def make_grade(**kwargs):
    defaults = dict(
        student_id=1,
        curricular_unit_id=1,
        section_id=1,
        period_id=1,
        enrollment_detail_id=1,
        student_carnet='V-12345678',
        uc_code='MAT101',
        uc_name='Matemáticas I',
        uc_credits=4,
        period_name='2026-I',
    )
    defaults.update(kwargs)
    return Grade(**defaults)


class GradeCalculateFinalTest(TestCase):
    """Grade.calculate_final_grade() — promedio de parciales presentes."""

    def test_no_partials_returns_none(self):
        g = make_grade()
        self.assertIsNone(g.calculate_final_grade())

    def test_single_partial(self):
        g = make_grade(partial1=Decimal('70'))
        self.assertEqual(g.calculate_final_grade(), Decimal('70.00'))

    def test_two_partials_average(self):
        g = make_grade(partial1=Decimal('60'), partial2=Decimal('80'))
        self.assertEqual(g.calculate_final_grade(), Decimal('70.00'))

    def test_three_partials_average(self):
        g = make_grade(
            partial1=Decimal('60'),
            partial2=Decimal('70'),
            partial3=Decimal('80'),
        )
        # (60+70+80)/3 = 70.0
        self.assertEqual(g.calculate_final_grade(), Decimal('70.00'))

    def test_rounding_two_decimals(self):
        g = make_grade(
            partial1=Decimal('61'),
            partial2=Decimal('62'),
            partial3=Decimal('63'),
        )
        # (61+62+63)/3 = 62.0
        self.assertEqual(g.calculate_final_grade(), Decimal('62.00'))

    def test_partial_none_skipped(self):
        # solo partial1 y partial3, partial2=None
        g = make_grade(partial1=Decimal('80'), partial3=Decimal('60'))
        # (80+60)/2 = 70.0
        self.assertEqual(g.calculate_final_grade(), Decimal('70.00'))

    def test_boundary_exactly_61_passes(self):
        g = make_grade(partial1=Decimal('61'))
        self.assertEqual(g.calculate_final_grade(), Decimal('61.00'))

    def test_zero_grade(self):
        g = make_grade(partial1=Decimal('0'), partial2=Decimal('0'), partial3=Decimal('0'))
        self.assertEqual(g.calculate_final_grade(), Decimal('0.00'))

    def test_max_grade(self):
        g = make_grade(partial1=Decimal('100'), partial2=Decimal('100'), partial3=Decimal('100'))
        self.assertEqual(g.calculate_final_grade(), Decimal('100.00'))


class GradeUpdateStatusTest(TestCase):
    """Grade.update_status() — sets status and final_grade correctly."""

    def test_no_partials_in_progress(self):
        g = make_grade()
        g.update_status()
        self.assertEqual(g.status, 'in_progress')
        self.assertIsNone(g.final_grade)

    def test_avg_above_61_passed(self):
        g = make_grade(partial1=Decimal('70'), partial2=Decimal('80'))
        g.update_status()
        self.assertEqual(g.status, 'passed')
        self.assertEqual(g.final_grade, Decimal('75.00'))

    def test_avg_exactly_61_passed(self):
        g = make_grade(partial1=Decimal('61'))
        g.update_status()
        self.assertEqual(g.status, 'passed')

    def test_avg_below_61_failed(self):
        g = make_grade(partial1=Decimal('60'))
        g.update_status()
        self.assertEqual(g.status, 'failed')

    def test_avg_zero_failed(self):
        g = make_grade(partial1=Decimal('0'))
        g.update_status()
        self.assertEqual(g.status, 'failed')


class GradeSaveTest(TestCase):
    """Grade.save() — auto-triggers update_status() unless withdrawn/incomplete."""

    def test_save_calculates_status_on_create(self):
        g = make_grade(partial1=Decimal('80'), partial2=Decimal('90'))
        g.save()
        self.assertEqual(g.status, 'passed')
        self.assertEqual(g.final_grade, Decimal('85.00'))

    def test_save_failed_when_low_grade(self):
        g = make_grade(partial1=Decimal('30'))
        g.save()
        self.assertEqual(g.status, 'failed')

    def test_save_withdrawn_not_recalculated(self):
        g = make_grade(partial1=Decimal('90'), status='withdrawn')
        g.save()
        # withdrawn: update_status() skipped, status stays withdrawn
        g.refresh_from_db()
        self.assertEqual(g.status, 'withdrawn')

    def test_save_incomplete_not_recalculated(self):
        g = make_grade(partial1=Decimal('90'), status='incomplete')
        g.save()
        g.refresh_from_db()
        self.assertEqual(g.status, 'incomplete')

    def test_update_partials_recalculates(self):
        g = make_grade(partial1=Decimal('50'))
        g.save()
        self.assertEqual(g.status, 'failed')

        g.partial2 = Decimal('80')
        g.save()
        # (50+80)/2 = 65 → passed
        self.assertEqual(g.status, 'passed')

    def test_unique_together_enforced(self):
        from django.db import IntegrityError
        g1 = make_grade()
        g1.save()
        g2 = make_grade()  # same student_id, section_id, period_id
        with self.assertRaises(IntegrityError):
            g2.save()
