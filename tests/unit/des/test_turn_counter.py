"""Unit tests for TurnCounter component."""

from des.turn_counter import TurnCounter


class TestTurnCounter:
    """Test suite for TurnCounter functionality."""

    def test_initialize_counter_with_zero_turns(self):
        """TurnCounter should start with zero turns for a phase."""
        counter = TurnCounter()

        assert counter.get_current_turn("DISCOVER") == 0

    def test_increment_turn_updates_count(self):
        """increment_turn() should increase turn count by 1."""
        counter = TurnCounter()

        counter.increment_turn("DISCOVER")

        assert counter.get_current_turn("DISCOVER") == 1

    def test_increment_turn_multiple_times(self):
        """increment_turn() should track multiple increments."""
        counter = TurnCounter()

        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")

        assert counter.get_current_turn("DISCOVER") == 3

    def test_is_limit_exceeded_returns_false_when_under_limit(self):
        """is_limit_exceeded() should return False when under turn limit."""
        counter = TurnCounter()
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")

        assert counter.is_limit_exceeded("DISCOVER", max_turns=5) is False

    def test_is_limit_exceeded_returns_false_when_at_limit(self):
        """is_limit_exceeded() should return False when exactly at turn limit."""
        counter = TurnCounter()
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")

        assert counter.is_limit_exceeded("DISCOVER", max_turns=5) is False

    def test_is_limit_exceeded_returns_true_when_over_limit(self):
        """is_limit_exceeded() should return True when exceeding turn limit."""
        counter = TurnCounter()
        for _ in range(6):
            counter.increment_turn("DISCOVER")

        assert counter.is_limit_exceeded("DISCOVER", max_turns=5) is True

    def test_multiple_phases_tracked_independently(self):
        """Different phases should maintain independent turn counts."""
        counter = TurnCounter()

        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCUSS")

        assert counter.get_current_turn("DISCOVER") == 2
        assert counter.get_current_turn("DISCUSS") == 1

    def test_reset_turn_resets_specific_phase(self):
        """reset_turn() should reset turn count for specific phase to zero."""
        counter = TurnCounter()
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCUSS")

        counter.reset_turn("DISCOVER")

        assert counter.get_current_turn("DISCOVER") == 0
        assert counter.get_current_turn("DISCUSS") == 1
