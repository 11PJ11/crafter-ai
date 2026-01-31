"""
Test to verify RED→GREEN Slack notification flow.
This test will intentionally fail, then be fixed to trigger both notification types.
"""


def test_red_green_notification_flow():
    """
    Test to verify GREEN notification after fixing RED.

    Flow:
    1. THIS COMMIT: Test fails → RED notification with state tracking
    2. Next commit: Test fixed → GREEN notification with recovery time
    3. Final commit: Test file removed → Back to normal
    """
    assert False, "🔴 RED TEST: Intentional failure to test state tracking"
