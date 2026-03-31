"""Form submission automation modules."""

from .captcha_handlers import detect_captcha, inject_recaptcha_token, wait_for_captcha_solution
from .form_discovery import (
    discover_forms,
    find_matching_field,
    auto_detect_field_type,
    auto_fill_form_without_template
)

__all__ = [
    'detect_captcha',
    'inject_recaptcha_token',
    'wait_for_captcha_solution',
    'discover_forms',
    'find_matching_field',
    'auto_detect_field_type',
    'auto_fill_form_without_template',
]

