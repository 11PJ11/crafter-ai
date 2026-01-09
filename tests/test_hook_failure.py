"""Temporary test to verify pre-commit hook blocks failing tests"""

def test_intentional_failure():
    """This test intentionally fails to verify hook behavior"""
    assert False, "Intentional failure to test pre-commit hook"
