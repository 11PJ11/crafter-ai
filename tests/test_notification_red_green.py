"""
Test to verify RED→GREEN Slack notification flow.
This test will intentionally fail, then be fixed to trigger both notification types.
"""


def test_red_green_notification_flow():
    """
    Intentional failure to test RED notification.

    Expected flow:
    1. This test fails → RED notification sent to #cicd with @mention
    2. Test gets fixed → GREEN notification sent showing recovery
    3. Test file removed → Back to normal
    """
    assert False, "🔴 RED TEST: Intentional failure to test notification system"
