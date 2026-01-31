"""
Temporary test file to trigger Slack notification.
This file will be deleted after testing the notification system.
"""

import pytest


def test_trigger_slack_notification():
    """
    This test intentionally fails to trigger a Slack notification.

    Expected behavior:
    1. Pipeline runs on installer branch
    2. This test fails
    3. Slack notification is sent to #cicd channel
    4. We verify the notification was received
    5. This test file will be deleted
    """
    assert False, "🔔 Intentional failure to test Slack notification system"
