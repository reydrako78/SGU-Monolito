"""
Unit tests for AspirantSocialAccountAdapter and helper functions.
No real OAuth calls — all sociallogin objects are mocked.
"""
from unittest.mock import MagicMock, patch, PropertyMock

from django.test import TestCase, RequestFactory
from django.core.cache import cache

from core.adapters import (
    _is_disposable_email,
    _check_ip_rate_limit,
    _IP_SIGNUP_LIMIT,
    _IP_SIGNUP_WINDOW,
    AspirantSocialAccountAdapter,
)


def make_sociallogin(email='user@gmail.com', verified=True, provider='google'):
    sl = MagicMock()
    sl.account.extra_data = {'email': email, 'verified_email': verified}
    sl.account.provider = provider
    sl.user.email = email
    return sl


def make_request(ip='1.2.3.4', forwarded_for=None):
    factory = RequestFactory()
    request = factory.get('/')
    request.META['REMOTE_ADDR'] = ip
    if forwarded_for:
        request.META['HTTP_X_FORWARDED_FOR'] = forwarded_for
    return request


class IsDisposableEmailTest(TestCase):
    """_is_disposable_email() — blocked/allowed domains."""

    def test_known_disposable_blocked(self):
        self.assertTrue(_is_disposable_email('user@mailinator.com'))
        self.assertTrue(_is_disposable_email('x@guerrillamail.com'))
        self.assertTrue(_is_disposable_email('a@10minutemail.com'))
        self.assertTrue(_is_disposable_email('b@yopmail.com'))

    def test_institutional_email_allowed(self):
        self.assertFalse(_is_disposable_email('estudiante@upel.edu.ve'))
        self.assertFalse(_is_disposable_email('user@gmail.com'))
        self.assertFalse(_is_disposable_email('user@outlook.com'))
        self.assertFalse(_is_disposable_email('user@hotmail.com'))

    def test_case_insensitive(self):
        self.assertTrue(_is_disposable_email('user@MAILINATOR.COM'))
        self.assertTrue(_is_disposable_email('user@MailINATOR.com'))

    def test_email_with_spaces_stripped(self):
        self.assertTrue(_is_disposable_email('  user@mailinator.com  '))

    def test_malformed_email_no_at(self):
        self.assertFalse(_is_disposable_email('noatsign'))

    def test_empty_string(self):
        self.assertFalse(_is_disposable_email(''))


class CheckIpRateLimitTest(TestCase):
    """_check_ip_rate_limit() — blocks after _IP_SIGNUP_LIMIT attempts."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_first_request_not_blocked(self):
        req = make_request(ip='10.0.0.1')
        self.assertFalse(_check_ip_rate_limit(req))

    def test_under_limit_not_blocked(self):
        req = make_request(ip='10.0.0.2')
        for _ in range(_IP_SIGNUP_LIMIT - 1):
            result = _check_ip_rate_limit(req)
        self.assertFalse(result)

    def test_at_limit_blocked(self):
        req = make_request(ip='10.0.0.3')
        for _ in range(_IP_SIGNUP_LIMIT):
            _check_ip_rate_limit(req)
        # Next call should be blocked
        self.assertTrue(_check_ip_rate_limit(req))

    def test_different_ips_independent(self):
        req1 = make_request(ip='10.0.0.4')
        req2 = make_request(ip='10.0.0.5')
        for _ in range(_IP_SIGNUP_LIMIT):
            _check_ip_rate_limit(req1)
        # ip1 blocked, ip2 not
        self.assertTrue(_check_ip_rate_limit(req1))
        self.assertFalse(_check_ip_rate_limit(req2))

    def test_forwarded_for_used_when_present(self):
        # When X-Forwarded-For is set, the forwarded IP is used for rate limiting
        forwarded_ip = '203.0.113.1'
        req = make_request(ip='127.0.0.1', forwarded_for=f'{forwarded_ip}, 10.0.0.1')
        for _ in range(_IP_SIGNUP_LIMIT):
            _check_ip_rate_limit(req)
        self.assertTrue(_check_ip_rate_limit(req))
        # A completely different IP is not affected
        req_other = make_request(ip='192.168.5.5')
        self.assertFalse(_check_ip_rate_limit(req_other))


class AdapterIsOpenForSignupTest(TestCase):
    """AspirantSocialAccountAdapter.is_open_for_signup() — blocks disposable/unverified."""

    def setUp(self):
        self.adapter = AspirantSocialAccountAdapter()
        self.request = make_request()

    def test_valid_gmail_allowed(self):
        sl = make_sociallogin(email='user@gmail.com', verified=True)
        self.assertTrue(self.adapter.is_open_for_signup(self.request, sl))

    def test_disposable_email_blocked(self):
        sl = make_sociallogin(email='hacker@mailinator.com', verified=True)
        self.assertFalse(self.adapter.is_open_for_signup(self.request, sl))

    def test_unverified_email_blocked(self):
        sl = make_sociallogin(email='user@gmail.com', verified=False)
        self.assertFalse(self.adapter.is_open_for_signup(self.request, sl))

    def test_verified_true_string_not_blocked(self):
        # extra_data may return True (bool) — must still work
        sl = make_sociallogin(email='user@outlook.com', verified=True)
        self.assertTrue(self.adapter.is_open_for_signup(self.request, sl))

    def test_upel_institutional_email_allowed(self):
        sl = make_sociallogin(email='prof@upel.edu.ve', verified=True)
        self.assertTrue(self.adapter.is_open_for_signup(self.request, sl))

    def test_email_from_user_attribute_when_extra_data_empty(self):
        sl = MagicMock()
        sl.account.extra_data = {}
        sl.user.email = 'user@gmail.com'
        result = self.adapter.is_open_for_signup(self.request, sl)
        self.assertTrue(result)


class AdapterSaveUserTest(TestCase):
    """AspirantSocialAccountAdapter.save_user() — rate limit + role assignment."""

    def setUp(self):
        cache.clear()
        self.adapter = AspirantSocialAccountAdapter()

    def tearDown(self):
        cache.clear()

    @patch('core.adapters.DefaultSocialAccountAdapter.save_user')
    def test_save_assigns_aspirant_role(self, mock_super_save):
        mock_user = MagicMock()
        mock_user.role = 'student'
        mock_super_save.return_value = mock_user

        sl = make_sociallogin()
        req = make_request()
        result = self.adapter.save_user(req, sl)

        self.assertEqual(mock_user.role, 'aspirant')
        mock_user.save.assert_called_once_with(update_fields=['role'])

    @patch('core.adapters.DefaultSocialAccountAdapter.save_user')
    def test_save_does_not_overwrite_professor_role(self, mock_super_save):
        mock_user = MagicMock()
        mock_user.role = 'professor'
        mock_super_save.return_value = mock_user

        sl = make_sociallogin()
        req = make_request()
        result = self.adapter.save_user(req, sl)

        # professor role preserved
        self.assertEqual(mock_user.role, 'professor')

    def test_is_open_blocks_after_rate_limit(self):
        """Rate limit is enforced in is_open_for_signup (allauth 0.57 compat)."""
        req = make_request(ip='10.9.9.9')
        sl = make_sociallogin(email='user@gmail.com', verified=True)

        # Exhaust the rate limit counter directly in cache
        cache_key = 'oauth_signup_ip:10.9.9.9'
        cache.set(cache_key, _IP_SIGNUP_LIMIT, timeout=_IP_SIGNUP_WINDOW)

        result = self.adapter.is_open_for_signup(req, sl)
        self.assertFalse(result)
