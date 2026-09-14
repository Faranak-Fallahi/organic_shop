import secrets

from django.core.cache import cache

OTP_TTL_SECONDS = 120
OTP_MAX_ATTEMPTS = 5
OTP_REQUEST_LIMIT = 5
OTP_REQUEST_WINDOW_SECONDS = 3600

_RESEND_WAIT_KEY = "otp_resend_wait_{key}"
_ATTEMPTS_KEY = "otp_attempts_{key}"
_REQUEST_COUNT_KEY = "otp_request_count_{key}"


def generate_otp():
    return f"{secrets.randbelow(100000):05d}"


def _set(key, value, timeout):
    cache.set(key, value, timeout=timeout)


def _get(key):
    return cache.get(key)


def store_otp(key, code):
    _set(f"otp_code_{key}", code, OTP_TTL_SECONDS)


def get_otp(key):
    return _get(f"otp_code_{key}")


def delete_otp(key):
    cache.delete(f"otp_code_{key}")


def is_resend_blocked(key):
    return _get(_RESEND_WAIT_KEY.format(key=key)) is not None


def mark_resend_wait(key, seconds=30):
    _set(_RESEND_WAIT_KEY.format(key=key), True, seconds)


def too_many_requests(key):
    count = _get(_REQUEST_COUNT_KEY.format(key=key)) or 0
    return count >= OTP_REQUEST_LIMIT


def record_request(key):
    k = _REQUEST_COUNT_KEY.format(key=key)
    count = _get(k) or 0
    _set(k, count + 1, OTP_REQUEST_WINDOW_SECONDS)


def attempts_left(key):
    attempts = _get(_ATTEMPTS_KEY.format(key=key)) or 0
    return max(OTP_MAX_ATTEMPTS - attempts, 0)


def record_failed_attempt(key):
    k = _ATTEMPTS_KEY.format(key=key)
    attempts = _get(k) or 0
    _set(k, attempts + 1, OTP_TTL_SECONDS)


def clear_attempts(key):
    cache.delete(_ATTEMPTS_KEY.format(key=key))